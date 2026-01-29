#policy.py
blocked_keywords=["hack","bypass","illegal","cheat","salary","exploit","password","crack"]
def policy_check(question:str)->bool:
    q=question.lower()
    for word in blocked_keywords:
        if word in q:
            return False
    return True