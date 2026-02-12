from typing import Optional as Opt

def f_un(uid: int, un: Opt[str] = None) -> str:
    return f"@{un}" if un else f"[User](tg://user?id={uid})"

def f_time(s: int) -> str:
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    res = []
    if d: res.append(f"{d}d")
    if h: res.append(f"{h}h")
    if m: res.append(f"{m}m")
    if s or not res: res.append(f"{s}s")
    return " ".join(res)