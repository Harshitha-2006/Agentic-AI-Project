#memory_store.py
import re
_name_memory={}
_question_memory={}
_resume_memory={}
def save_name(session_id,name):
    _name_memory[session_id]=name
def get_name(session_id):
    return _name_memory.get(session_id)
def save_question(session_id,question):
    q=question.lower()
    if"did i ask"in q or"have i asked"in q:
        return
    _question_memory.setdefault(session_id,[]).append(q)
def has_asked(session_id,topic):
    topic=topic.lower()
    questions=_question_memory.get(session_id,[])
    for q in questions:
        if"did i ask"in q or"have i asked"in q:
            continue
        if topic in q:
            return True
    return False
def save_resume(session_id,uploaded_file):
    _resume_memory[session_id]=uploaded_file
def get_resume(session_id):
    return _resume_memory.get(session_id)
def has_resume(session_id):
    return session_id in _resume_memory