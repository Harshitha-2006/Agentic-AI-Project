#intent.py
import re
from .memory_store import save_name,get_name,has_asked
def get_intent(question:str)->str:
    q=question.lower().strip()
    if q in ["hi","hello","hey"]:
        return "GREETING"
    if "my name is" in q or q.startswith("i am"):
        return "NAME_INTRO"
    if "what is my name" in q:
        return "NAME_RECALL"
    if "have i asked" in q or "did i ask" in q:
        return "HISTORY_CHECK"
    if "fee" in q or "cost" in q:
        return "FEE_QUERY"
    if "policy" in q or "rule" in q or "guideline" in q:
        return "POLICY_QUERY"
    return "GENERAL"
def handle_intent(session_id,question,intent):
    q=question.lower()
    if intent=="GREETING":
        return "Hi How can I help you?"
    if intent=="NAME_INTRO":
        if "my name is" in q:
            name=q.split("my name is")[-1].strip().capitalize()
        else:
            name=q.replace("i am","").strip().capitalize()
        save_name(session_id,name)
        return f"Nice to meet you, {name}"
    if intent=="NAME_RECALL":
        name=get_name(session_id)
        return f"Your name is {name}"if name else "I don’t know your name yet"
    if intent=="HISTORY_CHECK":
        topic=re.sub(r'did i ask|have i asked|about','',question.lower()).strip()
        topic_word=topic.split()[-1]
        if has_asked(session_id,topic_word):
            return f"Yes you asked about {topic_word} before"
        else:
            return f"No you have not asked about {topic_word} yet"
    return None