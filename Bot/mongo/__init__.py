from motor.motor_asyncio import AsyncIOMotorClient
from Bot import LOGGER
from Bot.config import MONGO_URI, DB_NAME

client = None
db = None
users_collection = None

if MONGO_URI:
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        users_collection = db.users
        LOGGER.info("DB connected.")
    except Exception as e:
        LOGGER.error(f"DB err: {e}")
        client = db = users_collection = None
else:
    LOGGER.warning("No MONGO_URI.")
