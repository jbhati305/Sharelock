import operator
from typing import Annotated, Any, Dict, List, Sequence, TypedDict, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from src.tools import get_stock_price, get_historical_data, get_scraped_data

def merge_reports(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    return {**a, **b}

# Define tools for LangChain
@tool
def stock_price_tool(ticker: str):
    """Get the current stock price and key metrics for a given ticker."""
    return get_stock_price(ticker)

@tool
def historical_data_tool(ticker: str, start_date: str = None, end_date: str = None):
    """Get historical price data for a stock ticker."""
    return get_historical_data(ticker, start_date, end_date)

@tool
def fundamental_data_tool(ticker: str):
    """Get comprehensive fundamental data (P&L, Balance Sheet, Ratios, etc.) for a ticker."""
    return get_scraped_data(ticker)

TOOLS = [stock_price_tool, historical_data_tool, fundamental_data_tool]

class AgentState(TypedDict):
    """The state of the multi-agent system."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    reports: Annotated[Dict[str, str], merge_reports]
    ticker: str
    verdict: str  # Final conclusion: Buy, Sell, Hold, Drop
    next_step: str

class BaseAgent:
    """Base class for agents in the LangGraph."""
    
    def __init__(self, name: str, system_prompt: str, model: str = "qwen2.5:14b"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = ChatOllama(model=model).bind_tools(TOOLS)
        
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Run the agent on the current state."""
        messages = [SystemMessage(content=self.system_prompt)] + state["messages"]
        
        # Add a specific instruction for the current analyst
        messages.append(HumanMessage(content=f"Perform your analysis for the ticker: {state['ticker']}"))
        
        response = self.model.invoke(messages)
        
        # Handle tool calls if any
        # Note: In a real LangGraph, we'd use a ToolNode, but for simplicity here 
        # we can handle immediate tool calls or keep it simple.
        # However, ChatOllama with bind_tools handles the generation of tool calls.
        
        return {
            "messages": [response],
            "reports": {self.name: response.content}
        }
