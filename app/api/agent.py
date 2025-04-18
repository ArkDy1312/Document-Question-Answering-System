from langgraph.prebuilt import create_react_agent
from app.api.tools import summarizer_tool, entity_tool
from app.config import get_llm

# Load Summarizer Model
llm = get_llm(type="agent")

# List of tools
tools = [summarizer_tool, entity_tool]

# Create the agent graph
graph = create_react_agent(model=llm, tools=tools)

# Create input for the graph
def run_agent(user_input: str):
    inputs = {"messages": [("user", user_input)]}
    final_state = graph.invoke(inputs)
    return final_state["messages"][-1].content  # Return last message from output