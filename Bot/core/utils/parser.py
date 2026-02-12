from typing import List

def p_args(txt: str) -> List[str]:
    if not txt: return []
    res, cur, q = [], "", False
    for c in txt:
        if c == '"': q = not q
        elif c == ' ' and not q:
            if cur: res.append(cur); cur = ""
        else: cur += c
    if cur: res.append(cur)
    return res
 