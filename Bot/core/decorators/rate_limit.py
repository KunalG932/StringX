import time
from functools import wraps

def rate_limit(l: int, w: int = 60):
    def dec(f):
        lc = {}
        @wraps(f)
        async def wr(c, m, *args, **kwargs):
            uid = m.from_user.id
            if uid in lc:
                el = time.time() - lc[uid]
                if el < w:
                    await m.reply_text(f"Wait {int(w - el)}s.")
                    return
            lc[uid] = time.time()
            return await f(c, m, *args, **kwargs)
        return wr
    return dec