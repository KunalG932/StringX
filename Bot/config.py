import os
from dotenv import load_dotenv

load_dotenv()

class C:
    BT = os.getenv("BOT_TOKEN", "")
    AID = int(os.getenv("API_ID", "0"))
    AH = os.getenv("API_HASH", "")
    MURI = os.getenv("MONGO_URI", os.getenv("MONGO_URL", ""))
    DB = os.getenv("DB_NAME", "")

MONGO_URI = C.MURI
DB_NAME = C.DB

