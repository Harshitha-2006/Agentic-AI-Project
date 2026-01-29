#approval.py
def risk_evaluator(state):
    high_risk_intents=["ATS_CHECK","POLICY_QUERY","ADMISSION_QUERY"]
    if state.get("intent")in high_risk_intents:
        state["risk_level"]="HIGH"
    else:
        state["risk_level"]="LOW"
    state["logs"].append(f"Risk level set to {state['risk_level']}")
    return state
def human_approval_node(state):
    print("\n==============================")
    print("HUMAN APPROVAL REQUIRED")
    print("==============================")
    print("Question:")
    print(state.get("question",""))
    print("\nProposed Answer:")
    print(state.get("tool_output",""))
    print("==============================")
    approval=input("Approve response? (yes/no): ").strip().lower()
    if approval=="yes":
        state["approved"]=True
        state["logs"].append("Human approved the response.")
    else:
        state["approved"]=False
        state["final_response"]="Response rejected by human reviewer."
        state["logs"].append("Human rejected the response.")
    return state
def process_response(state):
    state=risk_evaluator(state)
    if state["risk_level"]=="HIGH":
        state=human_approval_node(state)
    else:
        state["approved"]=True
        state["logs"].append("Auto-approved response (low risk).")
    return state