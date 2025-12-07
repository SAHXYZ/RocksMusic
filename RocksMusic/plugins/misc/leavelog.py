from datetime import datetime, timedelta, timezone
from pyrogram.types import ChatMemberUpdated

from RocksMusic import app, userbot
from config import LOG_GROUP_ID

IST = timezone(timedelta(hours=5, minutes=30))


@userbot.on_chat_member_updated()
async def assistant_detect_bot_removal(_, update: ChatMemberUpdated):
    try:
        bot = await app.get_me()

        old = update.old_chat_member
        new = update.new_chat_member

        # Event must be about THIS main bot
        if not old or old.user.id != bot.id:
            return

        # Detect removal
        if new.status not in ["kicked", "left", "banned"]:
            return

        chat = update.chat
        remover = update.from_user

        chat_title = chat.title or "Unknown"
        chat_id = chat.id
        chat_link = "Pʀɪᴠᴀᴛᴇ / Uɴᴀᴠᴀɪʟᴀʙʟᴇ"

        now = datetime.now(IST)
        date = now.strftime("%d-%b-%Y")
        time = now.strftime("%I:%M %p")

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
