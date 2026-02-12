from functools import wraps
from pyrogram.types import Message
from Bot import LOGGER

def handle_errors(f):
    @wraps(f)
    async def w(*args, **kwargs):
        try: return await f(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f"Err in {f.__name__}: {e}", exc_info=True)
            for a in args:
                if isinstance(a, Message):
                    await a.reply_text(f"Err: {str(e)}")
                    break
            return None
    return w
 