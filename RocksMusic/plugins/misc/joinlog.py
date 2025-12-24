from pyrogram.types import ChatMemberUpdated
from datetime import datetime, timedelta, timezone

from RocksMusic import app
from config import LOG_GROUP_ID


# Indian timezone (no pytz)
IST = timezone(timedelta(hours=5, minutes=30))


@app.on_chat_member_updated()
async def bot_status_log(_, update: ChatMemberUpdated):
    try:
        new = update.new_chat_member
        old = update.old_chat_member

        if not new or not new.user:
            return

        # Only for THIS bot
        if new.user.id != app.id:
            return

        chat = update.chat
        adder = update.from_user

        # Chat Link
        if chat.username:
            chat_link = f"https://t.me/{chat.username}"
        else:
            chat_link = "No Public Link"

        # Date & Time (IST)
        now = datetime.now(IST)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

        # -------------------------------
        # DEMOTED / REMOVED CASE
        # -------------------------------
        if old and old.status == "administrator" and new.status != "administrator":
            text = f"""
⟐────────────────────────────⟐
  ⌬ Bᴏᴛ Sᴛᴀᴛᴜꜱ Uᴘᴅᴀᴛᴇᴅ ⌬
⟐─────────────────────────────⟐

⟣ Cʜᴀᴛ Tɪᴛʟᴇ : {chat.title}
──────────────⟐
⟢ Cʜᴀᴛ Iᴅ : <code>{chat.id}</code>
──────────────⟐
⟡ Cʜᴀᴛ Lɪɴᴋ : {chat_link}
──────────────⟐
⟠ Aᴄᴛɪᴏɴ Bʏ : {adder.mention if adder else "Unknown"}
──────────────⟐
⟡ Bᴏᴛ : {new.user.mention}
──────────────⟐
⟞ Dᴀᴛᴇ : {date}
⟟ Tɪᴍᴇ : {time}
⟪ Lᴏɢ : Bᴏᴛ Rᴇᴍᴏᴠᴇᴅ / Dᴇᴍᴏᴛᴇᴅ
──────────────⟐
"""
            await app.send_message(LOG_GROUP_ID, text, disable_web_page_preview=True)
            return

        # -------------------------------
        # ADDED / PROMOTED CASE
        # -------------------------------
        text = f"""
⟐────────────────────────────⟐
  ⌬ Bᴏᴛ Sᴛᴀᴛᴜꜱ Uᴘᴅᴀᴛᴇᴅ ⌬
⟐─────────────────────────────⟐

⟣ Cʜᴀᴛ Tɪᴛʟᴇ : {chat.title}
──────────────⟐
⟢ Cʜᴀᴛ Iᴅ : <code>{chat.id}</code>
──────────────⟐
⟡ Cʜᴀᴛ Lɪɴᴋ : {chat_link}
──────────────⟐
⟠ Aᴄᴛɪᴏɴ Bʏ : {adder.mention if adder else "Unknown"}
──────────────⟐
⟡ Bᴏᴛ : {new.user.mention}
──────────────⟐
⟞ Dᴀᴛᴇ : {date}
⟟ Tɪᴍᴇ : {time}
⟪ Lᴏɢ : Bᴏᴛ Aᴅᴅᴇᴅ / Pʀᴏᴍᴏᴛᴇᴅ
──────────────⟐
"""
        await app.send_message(LOG_GROUP_ID, text, disable_web_page_preview=True)

    except Exception as e:
        print(f"[JoinLogError] {e}")
