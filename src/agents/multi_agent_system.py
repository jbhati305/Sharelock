import asyncio
import sys
from .graph import create_stock_analysis_graph
from langchain_core.messages import HumanMessage

async def run_analysis(ticker: str):
    print(f"\n🚀 Starting Multi-Agent Analysis for: {ticker}")
    print("-" * 50)
    
    # Initialize the graph
    app = create_stock_analysis_graph()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=f"Analyze {ticker}")],
        "reports": {},
        "ticker": ticker,
        "verdict": "",
        "next_step": ""
    }
    
    # Run the graph
    async for output in app.astream(initial_state):
        for key, value in output.items():
            if key == "orchestrator":
                print("\n✅ Investment Committee Decision Reached!")
            elif key == "__metadata__":
                continue
            else:
                print(f"🔹 {key.replace('_', ' ').title()} finished report.")
                
    # Get final state
    final_state = await app.ainvoke(initial_state)
    
    print("\n" + "="*60)
    print(f"📊 FINAL REPORT FOR {ticker}")
    print("="*60)
    print(final_state["verdict"])
    print("="*60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.agents.multi_agent_system <ticker>")
        sys.exit(1)
        
    ticker = sys.argv[1]
    asyncio.run(run_analysis(ticker))

if __name__ == "__main__":
    main()
