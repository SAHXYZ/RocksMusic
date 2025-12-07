from pyrogram.types import ChatMemberUpdated
from datetime import datetime, timedelta, timezone

from RocksMusic import app
from config import LOG_GROUP_ID

IST = timezone(timedelta(hours=5, minutes=30))


@app.on_my_chat_member()
async def bot_removed_log(_, update: ChatMemberUpdated):
    try:
        old = update.old_chat_member
        new = update.new_chat_member

        # Must be specifically about THIS bot (guaranteed in on_my_chat_member)
        if new.user.id != app.id:
            return

        # Bot must have been removed
        removed_statuses = ["kicked", "banned", "left"]

        if new.status not in removed_statuses:
            return

        chat = update.chat
        actor = update.from_user  # Admin who removed the bot (may be None)

        chat_title = chat.title
        chat_id = chat.id

        # No username because bot is kicked
        chat_link = "Pʀɪᴠᴀᴛᴇ / Uɴᴀᴠᴀɪʟᴀʙʟᴇ"

        now = datetime.now(IST)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

        actor_name = actor.mention if actor else "Unknown"
        actor_id = actor.id if actor else "Unknown"

        text = f"""
⧈⧈⧈ Bᴏᴛ Dɪꜱᴄᴏɴɴᴇᴄᴛɪᴏɴ Aʟᴇʀᴛ ⧈⧈⧈
──────────────⟐
➤ Gʀᴏᴜᴘ : {chat_title}
➤ Iᴅ : <code>{chat_id}</code>
➤ Lɪɴᴋ : {chat_link}
──────────────⟐
➤ Aᴄᴛɪᴏɴ : Bᴏᴛ Wᴀꜱ Rᴇᴍᴏᴠᴇᴅ / Kɪᴄᴋᴇᴅ / Bᴀɴɴᴇᴅ
➤ Bʏ : {actor_name}
    ⟿   ᴜꜱᴇʀ ɪᴅ : {actor_id}
──────────────⟐
➤ Dᴀᴛᴇ : {date}
➤ Tɪᴍᴇ : {time}
──────────────⟐
⧉ Lᴏɢ : Gʀᴏᴜᴘ Rᴇᴍᴏᴠᴀʟ Cᴏɴꜰɪʀᴍᴇᴅ
"""

        await app.send_message(LOG_GROUP_ID, text, disable_web_page_preview=True)

    except Exception as e:
        print(f"[LeaveLogError] {e}")
