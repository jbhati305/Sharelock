from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama

from .base_worker import AgentState
from .analysts import (
    fundamental_analyst,
    technical_analyst,
    valuation_specialist,
    risk_manager,
    sentiment_analyst,
    macro_specialist
)

# Investment Committee (Orchestrator) Prompt
ORCHESTRATOR_PROMPT = """You are the Investment Committee Chair.
Your job is to review reports from several specialized analysts and reach a final conclusion for the stock.

CONCUSION CATEGORIES:
1. **Strong Buy**: High conviction, positive fundamentals, technicals, and valuation.
2. **Buy**: Positive outlook with minor risks.
3. **Hold**: Mixed signals or fairly valued.
4. **Sell**: Negative trends or high overvaluation.
5. **Drop**: Serious red flags or fundamental breakdown.

You will receive reports from:
- Fundamental Analyst
- Technical Analyst
- Valuation Specialist
- Risk Manager
- Sentiment Analyst
- Macro Specialist

Your final response must:
1. Summarize the key points from each analyst.
2. Address any conflicting signals.
3. Provide a clear Verdict (Strong Buy / Buy / Hold / Sell / Drop).
4. Provide a target reasoning."""

class InvestmentCommittee:
    def __init__(self, model: str = "qwen2.5:14b"):
        self.model = ChatOllama(model=model)
        
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Aggregate reports and make a decision."""
        reports_context = "\n\n".join([f"--- {name} ---\n{report}" for name, report in state["reports"].items()])
        
        messages = [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=f"Here are the reports for {state['ticker']}:\n\n{reports_context}\n\nPlease reach a final conclusion.")
        ]
        
        response = self.model.invoke(messages)
        
        return {
            "verdict": response.content,
            "messages": [response]
        }

# Define the graph
def create_stock_analysis_graph(model: str = "qwen2.5:14b"):
    workflow = StateGraph(AgentState)
    
    # Add nodes for each analyst
    workflow.add_node("fundamental_analyst", fundamental_analyst)
    workflow.add_node("technical_analyst", technical_analyst)
    workflow.add_node("valuation_specialist", valuation_specialist)
    workflow.add_node("risk_manager", risk_manager)
    workflow.add_node("sentiment_analyst", sentiment_analyst)
    workflow.add_node("macro_specialist", macro_specialist)
    
    # Add orchestrator node
    orchestrator = InvestmentCommittee(model=model)
    workflow.add_node("orchestrator", orchestrator)
    
    # Define edges: Parallel execution of analysts
    # In LangGraph, we can just connect START to all analyst nodes
    workflow.add_edge(START, "fundamental_analyst")
    workflow.add_edge(START, "technical_analyst")
    workflow.add_edge(START, "valuation_specialist")
    workflow.add_edge(START, "risk_manager")
    workflow.add_edge(START, "sentiment_analyst")
    workflow.add_edge(START, "macro_specialist")
    
    # Connect all analysts to orchestrator
    workflow.add_edge("fundamental_analyst", "orchestrator")
    workflow.add_edge("technical_analyst", "orchestrator")
    workflow.add_edge("valuation_specialist", "orchestrator")
    workflow.add_edge("risk_manager", "orchestrator")
    workflow.add_edge("sentiment_analyst", "orchestrator")
    workflow.add_edge("macro_specialist", "orchestrator")
    
    # Connect orchestrator to END
    workflow.add_edge("orchestrator", END)
    
    return workflow.compile()
