#ui.py
import streamlit as st
import uuid
from streamlit.components.v1 import html
from agentic_ai.agentic_graph import app,tool_execution_node,response_node
from agentic_ai.approval import risk_evaluator
from agentic_ai.memory_store import save_resume
st.set_page_config(page_title="Agentic AI")
st.title("Agentic AI Assistant")
if"chat"not in st.session_state:
    st.session_state.chat=[]
if"session_id"not in st.session_state:
    st.session_state.session_id=str(uuid.uuid4())
if"pending_state"not in st.session_state:
    st.session_state.pending_state=None
uploaded_file=st.file_uploader("Upload your resume (PDF only)",type=["pdf"])
if uploaded_file:
    save_resume(st.session_state.session_id,uploaded_file)
    st.success("Resume uploaded successfully. ATS score will be calculated automatically.")
with st.form("chat_form",clear_on_submit=True):
    user_input=st.text_input("Ask a question:")
    submitted=st.form_submit_button("Send")
if submitted and user_input.strip():
    state={"session_id":st.session_state.session_id,"question":user_input.strip(),"intent":"","risk_level":"","approved":True,"tool_output":"","final_response":"","logs":[]}
    state=app.invoke(state)
    state=risk_evaluator(state)
    if state.get("risk_level")=="HIGH":
        st.session_state.pending_state=state
    else:
        state=tool_execution_node(state)
        state=response_node(state)
        confidence="High"if state["risk_level"]=="LOW"else"Medium"
        st.session_state.chat.append((user_input,state["final_response"],state["logs"],confidence))
if st.session_state.pending_state:
    st.markdown("⚠ High-risk question detected")
    st.markdown("Approve or reject:")
    state=st.session_state.pending_state
    col1,col2=st.columns(2)
    if col1.button("Approve",key=f"approve_{len(st.session_state.chat)}"):
        state["approved"]=True
        state["logs"].append("Human approved")
        state=tool_execution_node(state)
        state=response_node(state)
        st.session_state.chat.append((state["question"],state["final_response"],state["logs"],"High(HumanApproved)"))
        st.session_state.pending_state=None
    if col2.button("Reject",key=f"reject_{len(st.session_state.chat)}"):
        state["approved"]=False
        state["final_response"]="Response rejected"
        state["logs"].append("Human rejected")
        st.session_state.chat.append((state["question"],state["final_response"],state["logs"],"Low(Rejected)"))
        st.session_state.pending_state=None
for q,a,logs,confidence in reversed(st.session_state.chat):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Agent:** {a}")
    st.markdown(f"Confidence: {confidence}")
    with st.expander("Logs"):
        for log in logs:
            st.write(f"- {log}")
    st.markdown("---")
html("<script>window.scrollTo(0,document.body.scrollHeight);</script>",height=0)