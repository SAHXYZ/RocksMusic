from pyrogram import filters
from pyrogram.types import ChatMemberUpdated
from datetime import datetime
import pytz

from RocksMusic import app
from config import LOG_GROUP_ID


@app.on_chat_member_updated(filters.chat_member_updated)
async def bot_added_log(_, update: ChatMemberUpdated):
    try:
        new = update.new_chat_member
        old = update.old_chat_member

        # Only trigger when THIS bot is added
        if not new or not new.user or new.user.id != app.id:
            return

        # Ignore if bot was already a member earlier
        if old and old.status in ["member", "administrator"]:
            return

        chat = update.chat
        adder = update.from_user

        # Chat link if username exists
        if chat.username:
            chat_link = f"https://t.me/{chat.username}"
        else:
            chat_link = "No Public Link"

        # Date & Time (IST)
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

        text = f"""
⟐────────────────────────────⟐
  ⌬ Nᴇᴡ Gʀᴏᴜᴘ Aᴅᴅᴇᴅ Tᴏ Tʜᴇ Bᴏᴛ ⌬
⟐─────────────────────────────⟐

⟣ Cʜᴀᴛ Tɪᴛʟᴇ : {chat.title}
──────────────⟐
⟢ Cʜᴀᴛ Iᴅ : <code>{chat.id}</code>
──────────────⟐
⟡ Cʜᴀᴛ Lɪɴᴋ : {chat_link}
──────────────⟐
⟠ Aᴅᴅᴇᴅ Bʏ : {adder.mention if adder else "Unknown"}
──────────────⟐
⟡ Uꜱᴇʀ : {new.user.mention}
──────────────⟐
⟞ Dᴀᴛᴇ : {date}
⟟ Tɪᴍᴇ : {time}
⟪ Lᴏɢ : Nᴇᴡ Aᴄᴛɪᴠᴇ Gʀᴏᴜᴘ Aᴅᴅᴇᴅ
──────────────⟐
"""

        await app.send_message(
            LOG_GROUP_ID,
            text,
            disable_web_page_preview=True
        )

    except Exception as e:
        print(f"[JoinLogError] {e}")
