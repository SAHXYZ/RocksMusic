from pyrogram.types import ChatMemberUpdated
from datetime import datetime, timedelta, timezone

from RocksMusic import app
from config import LOG_GROUP_ID

# Indian timezone (same as joinlog)
IST = timezone(timedelta(hours=5, minutes=30))


@app.on_chat_member_updated()
async def bot_removed_log(_, update: ChatMemberUpdated):
    try:
        old = update.old_chat_member
        new = update.new_chat_member

        # This event must be about THIS bot
        if not old or not old.user or old.user.id != app.id:
            return

        # Bot must have been removed/kicked/banned
        removed_states = ["kicked", "left", "banned"]

        if new.status not in removed_states:
            return

        chat = update.chat
        remover = update.from_user

        chat_title = chat.title
        chat_id = chat.id

        # Since bot is removed, link is always unavailable
        chat_link = "Pʀɪᴠᴀᴛᴇ / Uɴᴀᴠᴀɪʟᴀʙʟᴇ"

        # Date & Time (IST)
        now = datetime.now(IST)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

        # Final formatted message
        text = f"""
⧈⧈⧈ Bᴏᴛ Dɪꜱᴄᴏɴɴᴇᴄᴛɪᴏɴ Aʟᴇʀᴛ ⧈⧈⧈
──────────────⟐
➤ Gʀᴏᴜᴘ : {chat_title}
➤ Iᴅ : <code>{chat_id}</code>
➤ Lɪɴᴋ : {chat_link}
──────────────⟐
➤ Aᴄᴛɪᴏɴ : Bᴏᴛ Wᴀꜱ Kɪᴄᴋᴇᴅ / Bᴀɴɴᴇᴅ
➤ Bʏ : {remover.mention if remover else "Unknown"}
    ⟿   ᴜꜱᴇʀ ɪᴅ : {remover.id if remover else "Unknown"}
──────────────⟐
➤ Dᴀᴛᴇ : {date}
➤ Tɪᴍᴇ : {time}
──────────────⟐
⧉ Lᴏɢ : Gʀᴏᴜᴘ Rᴇᴍᴏᴠᴀʟ Cᴏɴꜰɪʀᴍᴇᴅ
"""

        await app.send_message(
            LOG_GROUP_ID,
            text,
            disable_web_page_preview=True
        )

    except Exception as e:
        print(f"[LeaveLogError] {e}")
