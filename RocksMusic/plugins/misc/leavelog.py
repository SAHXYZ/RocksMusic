from pyrogram.types import ChatMemberUpdated
from datetime import datetime, timedelta, timezone

from RocksMusic import app
from config import LOG_GROUP_ID

IST = timezone(timedelta(hours=5, minutes=30))


@app.on_chat_member_updated()
async def bot_removed_log(_, update: ChatMemberUpdated):
    try:
        old = update.old_chat_member
        new = update.new_chat_member

        # Event must be about THIS BOT
        if not old or not old.user or old.user.id != app.id:
            return

        # Valid removal statuses in Pyrogram v2
        removed_states = ["kicked", "left", "banned"]

        # Check if bot was removed
        if new.status not in removed_states:
            return

        chat = update.chat
        remover = update.from_user  # Might be None

        chat_title = chat.title
        chat_id = chat.id

        chat_link = "Pʀɪᴠᴀᴛᴇ / Uɴᴀᴠᴀɪʟᴀʙʟᴇ"

        # Date & time
        now = datetime.now(IST)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

        # Fix: Safe remover details
        remover_name = remover.mention if remover else "Unknown"
        remover_id = remover.id if remover else "Unknown"

        text = f"""
⧈⧈⧈ Bᴏᴛ Dɪꜱᴄᴏɴɴᴇᴄᴛɪᴏɴ Aʟᴇʀᴛ ⧈⧈⧈
──────────────⟐
➤ Gʀᴏᴜᴘ : {chat_title}
➤ Iᴅ : <code>{chat_id}</code>
➤ Lɪɴᴋ : {chat_link}
──────────────⟐
➤ Aᴄᴛɪᴏɴ : Bᴏᴛ Wᴀꜱ Rᴇᴍᴏᴠᴇᴅ / Kɪᴄᴋᴇᴅ / Bᴀɴɴᴇᴅ
➤ Bʏ : {remover_name}
    ⟿   ᴜꜱᴇʀ ɪᴅ : {remover_id}
──────────────⟐
➤ Dᴀᴛᴇ : {date}
➤ Tɪᴍᴇ : {time}
──────────────⟐
⧉ Lᴏɢ : Gʀᴏᴜᴘ Rᴇᴍᴏᴠᴀʟ Cᴏɴꜰɪʀᴍᴇᴅ
"""

        await app.send_message(LOG_GROUP_ID, text, disable_web_page_preview=True)

    except Exception as e:
        print(f"[LeaveLogError] {e}")
