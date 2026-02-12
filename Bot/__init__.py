from pyrogram import Client
from httpx import AsyncClient
import logging, platform, subprocess, sys
from Bot.config import C

if platform.system() != "Windows":
    try:
        import uvloop
        uvloop.install()
    except:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "uvloop"])
            import uvloop
            uvloop.install()
        except: pass

LOGGER = logging.getLogger(__name__)
bot = Client("bot", C.AID, C.AH, bot_token=C.BT)
session = AsyncClient(timeout=30)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
