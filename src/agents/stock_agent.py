"""
Stock Analysis Agent using Ollama + MCP.

This agent connects to the MCP server to use tools,
allowing tools to be hosted on any machine.
"""

import json
import asyncio
import ollama
from typing import Any
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class StockAnalysisAgent:
    """
    AI Agent for stock market analysis using Ollama + MCP.
    
    Connects to MCP server to access tools remotely.
    """
    
    def __init__(self, model: str = "qwen2.5:14b"):
        """
        Initialize the agent.
        
        Args:
            model: Ollama model name (default: qwen2.5:14b)
        """
        self.model = model
        self.conversation_history = []
        self.tools = []  # Will be populated from MCP server
        self.session = None
        self.system_prompt = """You are a helpful stock market analysis assistant that ALWAYS responds in English.

You have access to tools via MCP server to fetch real-time stock data and comprehensive fundamental data.

IMPORTANT RULES:
1. For Indian stocks on NSE, ALWAYS add .NS suffix (e.g., RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS)
2. For US stocks, use regular ticker (e.g., AAPL, GOOGL, MSFT)
3. ALWAYS use the tools to fetch data before answering questions about stocks
4. Use `get_scraped_data` for comprehensive fundamental analysis (financials, ratios, shareholding, etc.)
5. ALWAYS respond in English only
6. Provide clear, actionable insights based on the data

When asked about a stock price, company, or analysis - USE THE TOOLS FIRST."""

    async def connect_to_mcp_server(self, server_script: str = "src/mcp_server/server.py"):
        """
        Connect to the MCP server and fetch available tools.
        
        Args:
            server_script: Path to the MCP server script
        """
        # Server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", server_script],
        )
        
        # Create client connection
        self._stdio_context = stdio_client(server_params)
        self._streams = await self._stdio_context.__aenter__()
        read_stream, write_stream = self._streams
        
        # Create session
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()
        
        # Initialize the session
        await self.session.initialize()
        
        # Fetch available tools from MCP server
        tools_response = await self.session.list_tools()
        
        # Convert MCP tools to Ollama tool format
        self.tools = []
        for tool in tools_response.tools:
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema if tool.inputSchema else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            self.tools.append(ollama_tool)
        
        print(f"✅ Connected to MCP server")
        print(f"📦 Available tools: {[t['function']['name'] for t in self.tools]}")

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if hasattr(self, '_session_context'):
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, '_stdio_context'):
            await self._stdio_context.__aexit__(None, None, None)
        self.session = None
        print("🔌 Disconnected from MCP server")

    async def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool on the MCP server."""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            # Extract content from the result
            if result.content:
                # MCP returns content as a list of content items
                content_text = ""
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_text += item.text
                
                # Try to parse as JSON
                try:
                    return json.loads(content_text)
                except json.JSONDecodeError:
                    return {"result": content_text}
            return {"result": "No content returned"}
        except Exception as e:
            return {"error": f"Tool call failed: {str(e)}"}

    async def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            user_message: The user's question or request
            
        Returns:
            The agent's response
        """
        if not self.session:
            return "Error: Not connected to MCP server. Call connect_to_mcp_server() first."
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        # Call Ollama with tools from MCP server
        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools=self.tools,
        )
        
        assistant_message = response["message"]
        
        # Check if the model wants to call tools
        if assistant_message.get("tool_calls"):
            # Execute each tool call via MCP
            tool_results = []
            for tool_call in assistant_message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = tool_call["function"]["arguments"]
                
                # Handle arguments - might be string or dict
                if isinstance(func_args, str):
                    try:
                        func_args = json.loads(func_args)
                    except json.JSONDecodeError:
                        func_args = {}
                
                # Clean up arguments - only keep 'ticker' and valid params
                clean_args = {}
                if "ticker" in func_args:
                    clean_args["ticker"] = func_args["ticker"]
                if "start_date" in func_args:
                    clean_args["start_date"] = func_args["start_date"]
                if "end_date" in func_args:
                    clean_args["end_date"] = func_args["end_date"]
                if "interval" in func_args:
                    clean_args["interval"] = func_args["interval"]
                
                print(f"🔧 Calling MCP tool: {func_name}({clean_args})")
                
                # Call tool via MCP server
                result = await self._call_tool(func_name, clean_args)
                tool_results.append({
                    "tool": func_name,
                    "result": result
                })
                
                print(f"✅ Got result from {func_name}")
            
            # Add assistant message with tool calls
            self.conversation_history.append({
                "role": "assistant",
                "content": "",
                "tool_calls": assistant_message["tool_calls"]
            })
            
            # Add tool results
            self.conversation_history.append({
                "role": "tool",
                "content": json.dumps(tool_results, indent=2, default=str)
            })
            
            # Get final response from the model
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
            
            final_response = ollama.chat(
                model=self.model,
                messages=messages,
            )
            
            final_content = final_response["message"]["content"]
            self.conversation_history.append({
                "role": "assistant",
                "content": final_content
            })
            
            return final_content
        else:
            # No tool calls, just return the response
            content = assistant_message.get("content", "")
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            return content

    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []
        print("✨ Conversation history cleared.")


async def run_agent_interactive():
    """Run the agent in interactive mode."""
    print("=" * 60)
    print("🤖 Stock Analysis Agent (Ollama + MCP)")
    print("=" * 60)
    print()
    
    agent = StockAnalysisAgent(model="qwen2.5:14b")
    
    try:
        # Connect to MCP server
        print("Connecting to MCP server...")
        await agent.connect_to_mcp_server()
        print()
        
        print("Commands:")
        print("  'quit' or 'exit' - Exit the program")
        print("  'reset' - Clear conversation history")
        print()
        print("Examples:")
        print("  • What is the current price of RELIANCE.NS?")
        print("  • Analyze TCS.NS for me")
        print("  • Get financial ratios for INFY.NS")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    break
                
                if user_input.lower() == "reset":
                    agent.reset()
                    continue
                
                print()
                response = await agent.chat(user_input)
                print(f"\n🤖 Assistant: {response}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    finally:
        await agent.disconnect()
        print("👋 Goodbye!")


def main():
    """Entry point for the agent."""
    asyncio.run(run_agent_interactive())


if __name__ == "__main__":
    main()
