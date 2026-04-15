from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import AgentState
from agent.nodes import select_story_node, convert_to_emoji_node, evaluate_guess_node, reveal_story_node, update_score_node

def route_request(state: AgentState):
    if not state.get("selected_story"):
        return "select_story_node"
    if state.get("selected_story") and not state.get("emoji_story"):
        return "convert_to_emoji_node"
    if state.get("user_guess") and not state.get("evaluation_result"):
        return "evaluate_guess_node"
    return END

def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("select_story_node", select_story_node)
    builder.add_node("convert_to_emoji_node", convert_to_emoji_node)
    builder.add_node("evaluate_guess_node", evaluate_guess_node)
    builder.add_node("reveal_story_node", reveal_story_node)
    builder.add_node("update_score_node", update_score_node)
    
    builder.add_conditional_edges(START, route_request)
    
    builder.add_edge("select_story_node", "convert_to_emoji_node")
    builder.add_edge("convert_to_emoji_node", END)
    
    builder.add_edge("evaluate_guess_node", "reveal_story_node")
    builder.add_edge("reveal_story_node", "update_score_node")
    builder.add_edge("update_score_node", END)
    
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

graph = build_graph()
