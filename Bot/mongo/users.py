from datetime import datetime as dt, timedelta as td
from typing import Optional as Opt, List, Dict, Any
from Bot.mongo import users_collection as uc

async def add_user(uid: int, un: str, fn: Opt[str] = None, ln: Opt[str] = None) -> bool:
    now = dt.utcnow()
    ex = await uc.find_one({"user_id": uid})
    if ex:
        await uc.update_one({"user_id": uid}, {"$set": {"username": un, "first_name": fn, "last_name": ln, "last_seen": now}})
        return False
    await uc.insert_one({"user_id": uid, "username": un, "first_name": fn, "last_name": ln, "join_date": now, "last_seen": now})
    return True

async def get_user(uid: int) -> Opt[Dict[str, Any]]:
    return await uc.find_one({"user_id": uid})

async def get_all_users() -> List[Dict[str, Any]]:
    return await uc.find().to_list(length=None)

async def update_last_seen(uid: int) -> bool:
    r = await uc.update_one({"user_id": uid}, {"$set": {"last_seen": dt.utcnow()}})
    return r.modified_count > 0

async def id_to_un(uid: int) -> Opt[str]:
    u = await uc.find_one({"user_id": uid}, {"username": 1})
    return u["username"] if u else None

async def get_user_count() -> int:
    return await uc.count_documents({})

async def get_active_users(d: int = 7) -> int:
    cd = dt.utcnow() - td(days=d)
    return await uc.count_documents({"last_seen": {"$gte": cd}})

async def has_accepted_terms(uid: int) -> bool:
    u = await uc.find_one({"user_id": uid}, {"terms_accepted": 1})
    return u.get("terms_accepted", False) if u else False

async def accept_terms(uid: int) -> None:
    await uc.update_one({"user_id": uid}, {"$set": {"terms_accepted": True, "terms_accepted_at": dt.utcnow()}}, upsert=True)

async def create_indexes():
    await uc.create_index("user_id", unique=True)
    await uc.create_index("last_seen")
