#agentic_graph.py
from langgraph.graph import StateGraph,END
from .intent import get_intent,handle_intent
from .tools import ask as rag_ask
from .policy import policy_check
from .memory_store import save_question,has_resume,get_resume
from .ats_engine import calculate_ats_score
def intent_node(state):
    state["intent"]=get_intent(state["question"])
    state["logs"].append(f"Intent detected: {state['intent']}")
    return state
def risk_node(state):
    from .approval import risk_evaluator
    return risk_evaluator(state)
def tool_execution_node(state):
    if not state.get("approved",True):
        state["tool_output"]="Action blocked"
        return state
    if not policy_check(state["question"]):
        state["tool_output"]="This question violates usage policy."
        state["logs"].append("Blocked by policy guardrail")
        return state
    save_question(state["session_id"],state["question"])
    if state["intent"]=="ATS_CHECK":
        if not has_resume(state["session_id"]):
            state["tool_output"]="Please upload your resume first."
            state["logs"].append("ATS requested without resume")
            return state
        resume=get_resume(state["session_id"])
        score,breakdown=calculate_ats_score(resume)
        response=f"ATS Score: {score}/100\n\nBreakdown:\n"
        for k,v in breakdown.items():
            response+=f"- {k}: {v}\n"
        state["tool_output"]=response.strip()
        state["logs"].append("ATS score generated successfully")
        return state
    if state["intent"]in["GREETING","NAME_INTRO","NAME_RECALL","HISTORY_CHECK"]:
        state["tool_output"]=handle_intent(state["session_id"],state["question"],state["intent"])
    else:
        state["tool_output"]=rag_ask(state["question"])
    return state
def response_node(state):
    answer=state["tool_output"]
    if answer in["I don't know","This question violates usage policy."]:
        state["confidence"]=0.30
    elif len(answer)<20:
        state["confidence"]=0.50
    else:
        state["confidence"]=0.85
    state["final_response"]=answer
    state["logs"].append(f"Response generated with confidence {state['confidence']}")
    return state
graph=StateGraph(dict)
graph.add_node("intent",intent_node)
graph.add_node("risk",risk_node)
graph.add_node("tool",tool_execution_node)
graph.add_node("response",response_node)
graph.set_entry_point("intent")
graph.add_edge("intent","risk")
graph.add_edge("risk","tool")
graph.add_edge("tool","response")
graph.add_edge("response",END)
app=graph.compile()