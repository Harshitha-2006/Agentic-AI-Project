#ats_engine.py
from pypdf import PdfReader
ACTION_VERBS=["built","designed","developed","implemented","optimized","improved","created","managed"]
SECTIONS=["skills","experience","education","projects"]
def extract_text(uploaded_file):
    reader=PdfReader(uploaded_file)
    text=""
    for page in reader.pages:
        text+=page.extract_text()or""
    return text.lower()
def calculate_ats_score(uploaded_file):
    text=extract_text(uploaded_file)
    score=0
    breakdown={}
    keywords=["python","java","sql","api","project"]
    kw_score=sum(5 for k in keywords if k in text)
    breakdown["Keyword Match"]=min(40,kw_score)
    sec_score=sum(5 for s in SECTIONS if s in text)
    breakdown["Sections"]=min(20,sec_score)
    verb_score=sum(2 for v in ACTION_VERBS if v in text)
    breakdown["Action Verbs"]=min(10,verb_score)
    breakdown["Formatting"]=20 if len(text)>300 else 10
    score=sum(breakdown.values())
    return score,breakdown