from functools import wraps
from Bot.mongo.users import update_last_seen as uls

def track_user(f):
    @wraps(f)
    async def w(c, m, *args, **kwargs):
        await uls(m.from_user.id)
        return await f(c, m, *args, **kwargs)
    return w