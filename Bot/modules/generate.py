from Bot import bot
from Bot.core.decorators.error_handler import handle_errors
from Bot.core.scraper.telegram_org import send_code as sc, login_and_fetch as lf
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

us = {}

def c_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="gen_cancel", **_s(BS.DANGER if BS else None))]])

def r_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Generate Session", callback_data="sess_again", **_s(BS.PRIMARY if BS else None))],
        [
            InlineKeyboardButton("Generate Again", callback_data="gen_again", **_s(BS.DEFAULT if BS else None)),
            InlineKeyboardButton("Close", callback_data="close", **_s(BS.DANGER if BS else None)),
        ],
    ])

@bot.on_message(filters.command("generate") & filters.private)
@handle_errors
async def g_cmd(_, m: Message):
    uid = m.from_user.id
    if not await hat(uid):
        await m.reply_text("You need to accept the privacy policy first.\nSend /start to get started.")
        return
    us[uid] = {"step": "phone"}
    await m.reply_text("<b>Generate API Credentials</b>\n\n<b>Step 1 of 2</b> - Phone Number\n\nEnter your phone number with country code.\nExample: <code>+919876543210</code>", reply_markup=c_kb())

@bot.on_message(filters.command("cancel") & filters.private)
@handle_errors
async def cl_cmd(_, m: Message):
    uid = m.from_user.id
    c = False
    if uid in us:
        del us[uid]
        c = True
    from Bot.modules.session import ss, _cl
    if uid in ss:
        await _cl(uid)
        c = True
    await m.reply_text("Operation cancelled." if c else "Nothing to cancel.")

@bot.on_callback_query(filters.regex(r"^gen_cancel$"))
@handle_errors
async def gc_cb(_, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid in us: del us[uid]
    await cb.answer("Cancelled")
    await cb.message.edit_text("Operation cancelled.")

@bot.on_callback_query(filters.regex(r"^gen_again$"))
@handle_errors
async def ga_cb(_, cb: CallbackQuery):
    uid = cb.from_user.id
    if not await hat(uid):
        await cb.answer("Accept the privacy policy first. Send /start", show_alert=True)
        return
    us[uid] = {"step": "phone"}
    await cb.answer()
    await cb.message.edit_text("<b>Generate API Credentials</b>\n\n<b>Step 1 of 2</b> - Phone Number\n\nEnter your phone number with country code.\nExample: <code>+919876543210</code>", reply_markup=c_kb())

@bot.on_message(filters.private & filters.text & ~filters.command(["start", "help", "info", "stats", "generate", "cancel", "session", "privacy"]) & filters.create(lambda _, __, m: m.from_user.id in us))
@handle_errors
async def h_txt(_, m: Message):
    uid = m.from_user.id
    s = us.get(uid)
    if not s: return
    step = s.get("step")
    if step == "phone":
        p = m.text.strip()
        if not re.match(r"^\+\d{7,15}$", p):
            await m.reply_text("Invalid format. Use country code:\n<code>+919876543210</code>", reply_markup=c_kb())
            return
        wm = await m.reply_text("Sending verification code...")
        res = await sc(p)
        if not res or "random_hash" not in res:
            e = res.get("error", "") if res else ""
            await wm.edit_text(f"{f'<b>Error:</b> {e}' if e else 'Failed to send code.'}\n\nUse /generate to retry.")
            us.pop(uid, None)
            return
        us[uid] = {"step": "code", "phone": p, "rh": res["random_hash"]}
        await wm.edit_text("<b>Generate API Credentials</b>\n\n<b>Step 2 of 2</b> - Verification Code\n\nA code was sent to your Telegram app.\nEnter it below (spaces and dashes are ok).\n\nExample: <code>1 2 3 4 5</code> or <code>12345</code>", reply_markup=c_kb())
    elif step == "code":
        c = m.text.strip().replace(" ", "").replace("-", "")
        p, rh = s["phone"], s["rh"]
        wm = await m.reply_text("Verifying code...")
        us.pop(uid, None)
        creds = await lf(p, rh, c)
        if not creds:
            await wm.edit_text("<b>Verification Failed</b>\n\nThe code may be wrong or expired.\nUse /generate to try again.", link_preview_options=LinkPreviewOptions(is_disabled=True))
            return
        await wm.edit_text(f"<b>API Credentials Generated</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n  <b>API ID</b>   :  <code>{creds['api_id']}</code>\n  <b>API Hash</b> :  <code>{creds['api_hash']}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\nKeep these credentials safe.\nNever share them with anyone.\n\nYou can now generate a session string\nusing these credentials.", reply_markup=r_kb())
