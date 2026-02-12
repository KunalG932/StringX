from Bot import bot
from Bot.core.decorators.error_handler import handle_errors
from Bot.core.session import PS, TS
from Bot.mongo.users import has_accepted_terms as hat
from pyrogram import filters
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LinkPreviewOptions,
)
import re
try:
    from pyrogram.enums import ButtonStyle as BS
except ImportError:
    BS = None

def _s(s):
    return {"style": s} if s and BS else {}

ss = {}
STYPES = {
    "pyrogram": {"name": "Pyrogram", "desc": "Pyrogram, Kurigram, Pyrofork, Hydrogram"},
    "telethon": {"name": "Telethon", "desc": "Telethon and Telethon forks"},
}

def c_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="sess_cancel", **_s(BS.DANGER if BS else None))]])

def t_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Pyrogram", callback_data="sess_type_pyrogram", **_s(BS.PRIMARY if BS else None)),
            InlineKeyboardButton("Telethon", callback_data="sess_type_telethon", **_s(BS.PRIMARY if BS else None)),
        ],
        [InlineKeyboardButton("Cancel", callback_data="sess_cancel", **_s(BS.DANGER if BS else None))],
    ])

async def _cl(uid: int):
    s = ss.pop(uid, None)
    if s and "co" in s:
        await s["co"].disconnect()

@bot.on_message(filters.command("session") & filters.private)
@handle_errors
async def s_cmd(_, m: Message):
    uid = m.from_user.id
    if not await hat(uid):
        await m.reply_text("You need to accept the privacy policy first.\nSend /start to get started.")
        return
    await _cl(uid)
    ss[uid] = {"step": "choose_type"}
    await m.reply_text("<b>Session String Generator</b>\n\nSelect which type of session to generate.\n\n<b>Pyrogram</b> - Pyrogram, Kurigram, Pyrofork, Hydrogram\n<b>Telethon</b> - Telethon and its forks", reply_markup=t_kb())

@bot.on_callback_query(filters.regex(r"^sess_type_(pyrogram|telethon)$"))
@handle_errors
async def st_cb(_, cb: CallbackQuery):
    uid = cb.from_user.id
    s = ss.get(uid)
    if not s or s.get("step") != "choose_type":
        await cb.answer("Session expired. Use /session", show_alert=True)
        return
    st = cb.data.split("_")[-1]
    tn = STYPES[st]["name"]
    ss[uid] = {"step": "api_id", "type": st}
    await cb.answer()
    await cb.message.edit_text(f"<b>{tn} Session</b>\n\n<b>Step 1 of 4</b> - API ID\n\nEnter your API ID (numeric).\nGet one from /generate if you don't have it.", reply_markup=c_kb(), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex(r"^sess_cancel$"))
@handle_errors
async def sc_cb(_, cb: CallbackQuery):
    await _cl(cb.from_user.id)
    await cb.answer("Cancelled")
    await cb.message.edit_text("Session generation cancelled.")

@bot.on_callback_query(filters.regex(r"^sess_again$"))
@handle_errors
async def sa_cb(_, cb: CallbackQuery):
    uid = cb.from_user.id
    if not await hat(uid):
        await cb.answer("Accept the privacy policy first. Send /start", show_alert=True)
        return
    await _cl(uid)
    ss[uid] = {"step": "choose_type"}
    await cb.answer()
    await cb.message.edit_text("<b>Session String Generator</b>\n\nSelect which type of session to generate.\n\n<b>Pyrogram</b> - Pyrogram, Kurigram, Pyrofork, Hydrogram\n<b>Telethon</b> - Telethon and its forks", reply_markup=t_kb())

@bot.on_message(filters.private & filters.text & ~filters.command(["start", "help", "info", "stats", "generate", "cancel", "session", "privacy"]) & filters.create(lambda _, __, m: m.from_user.id in ss))
@handle_errors
async def sth(_, m: Message):
    uid = m.from_user.id
    s = ss.get(uid)
    if not s: return
    step = s.get("step")
    if step == "api_id":
        t = m.text.strip()
        if not t.isdigit():
            await m.reply_text("API ID must be a number. Try again.", reply_markup=c_kb())
            return
        tn = STYPES[s["type"]]["name"]
        s["api_id"] = int(t)
        s["step"] = "api_hash"
        ss[uid] = s
        await m.reply_text(f"<b>{tn} Session</b>\n\n<b>Step 2 of 4</b> - API Hash\n\nEnter your API Hash (32 hex characters).", reply_markup=c_kb())
    elif step == "api_hash":
        t = m.text.strip()
        if not re.match(r"^[a-f0-9]{32}$", t, re.IGNORECASE):
            await m.reply_text("Invalid API Hash. Must be 32 hex characters.", reply_markup=c_kb())
            return
        tn = STYPES[s["type"]]["name"]
        s["api_hash"] = t
        s["step"] = "phone"
        ss[uid] = s
        await m.reply_text(f"<b>{tn} Session</b>\n\n<b>Step 3 of 4</b> - Phone Number\n\nEnter your phone number with country code.\nExample: <code>+919876543210</code>", reply_markup=c_kb())
    elif step == "phone":
        p = m.text.strip()
        if not re.match(r"^\+\d{7,15}$", p):
            await m.reply_text("Invalid format. Use country code:\n<code>+919876543210</code>", reply_markup=c_kb())
            return
        tn = STYPES[s["type"]]["name"]
        wm = await m.reply_text("Connecting...")
        co = PS(s["api_id"], s["api_hash"]) if s["type"] == "pyrogram" else TS(s["api_id"], s["api_hash"])
        try:
            await co.connect()
        except Exception as e:
            await wm.edit_text(f"<b>Connection failed</b>\n\n{e}\n\nCheck your API ID and Hash.\nUse /session to retry.")
            await _cl(uid)
            return
        res = await co.send_code(p)
        if not res.get("ok"):
            await wm.edit_text(f"<b>Error:</b> {res.get('error', 'Unknown error')}\n\nUse /session to retry.")
            await co.disconnect()
            ss.pop(uid, None)
            return
        s["phone"], s["co"], s["step"] = p, co, "code"
        ss[uid] = s
        await wm.edit_text(f"<b>{tn} Session</b>\n\n<b>Step 4 of 4</b> - Verification Code\n\nA code was sent to your Telegram app.\nEnter it below (spaces and dashes are ok).\n\nExample: <code>1 2 3 4 5</code> or <code>12345</code>", reply_markup=c_kb())
    elif step == "code":
        c = m.text.strip().replace(" ", "").replace("-", "")
        wm = await m.reply_text("Verifying...")
        co, p, st = s["co"], s["phone"], s["type"]
        tn = STYPES[st]["name"]
        res = await co.sign_in(p, c)
        if res.get("2fa"):
            s["step"] = "password"
            ss[uid] = s
            await wm.edit_text(f"<b>{tn} Session</b>\n\n<b>Two-Factor Authentication</b>\n\nYour account has 2FA enabled.\nEnter your cloud password.", reply_markup=c_kb())
            return
        if res.get("ok"):
            sust = res["session"]
            svd = await co.send_to_saved(sust, tn)
            await _cl(uid)
            await _sr(wm, st, sust, svd)
            return
        await _cl(uid)
        await wm.edit_text(f"<b>Error:</b> {res.get('error', 'Unknown error')}\n\nUse /session to retry.")
    elif step == "password":
        pwd = m.text.strip()
        wm = await m.reply_text("Checking password...")
        co, st = s["co"], s["type"]
        tn = STYPES[st]["name"]
        res = await co.check_password(pwd)
        if res.get("ok"):
            sust = res["session"]
            svd = await co.send_to_saved(sust, tn)
            await _cl(uid)
            await _sr(wm, st, sust, svd)
            return
        await _cl(uid)
        await wm.edit_text(f"<b>Error:</b> {res.get('error', 'Unknown error')}\n\nUse /session to retry.")

async def _sr(m, st: str, sust: str, svd: bool = False):
    tn, cmp = STYPES[st]["name"], STYPES[st]["desc"]
    sl = "\nSaved to your <b>Saved Messages</b>.\n" if svd else ""
    await m.edit_text(f"<b>{tn} Session Generated</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n  <b>Type</b>       :  {tn}\n  <b>Compatible</b> :  {cmp}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<code>{sust}</code>\n{sl}\nKeep this session string safe.\nNever share it with anyone.\nAnyone with this string can access your account.", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Generate Another", callback_data="sess_again", **_s(BS.PRIMARY if BS else None))],
        [InlineKeyboardButton("Delete This Message", callback_data="sess_delete", **_s(BS.DANGER if BS else None))],
    ]))

@bot.on_callback_query(filters.regex(r"^sess_delete$"))
@handle_errors
async def sd_cb(_, cb: CallbackQuery):
    await cb.answer("Deleted")
    await cb.message.delete()
