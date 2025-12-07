import asyncio
import pytz
from datetime import datetime
from pyrogram.errors import UserNotParticipant
from RocksMusic import app
from RocksMusic.config.config import LOG_GROUP_ID   # 🔥 FIXED PATH

# -------------------------------------------------------------
# Storage for all groups where bot was added (Mode 2)
# Filled by joinlog.py using add_group(chat_id)
# -------------------------------------------------------------
GROUP_LIST = set()


# ------------------ ADD GROUP FROM JOINLOG --------------------
def add_group(chat_id: int):
    GROUP_LIST.add(chat_id)


# ---------------------- BUILD MESSAGE -------------------------
def build_log_message(chat, remover="Unknown Admin"):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    date = now.strftime("%d-%b-%Y")
    time = now.strftime("%I:%M %p")

    return f"""
⧈⧈⧈ Bᴏᴛ Dɪꜱᴄᴏɴɴᴇᴄᴛɪᴏɴ Aʟᴇʀᴛ ⧈⧈⧈
──────────────⟐
➤ Gʀᴏᴜᴘ : {chat.title}
➤ Iᴅ : {chat.id}
➤ Lɪɴᴋ : Pʀɪᴠᴀᴛᴇ / Uɴᴀᴠᴀɪʟᴀʙʟᴇ
──────────────⟐
➤ Aᴄᴛɪᴏɴ : Bᴏᴛ Wᴀꜱ Kɪᴄᴋᴇᴅ / Bᴀɴɴᴇᴅ
➤ Bʏ : {remover}
──────────────⟐
➤ Dᴀᴛᴇ : {date}
➤ Tɪᴍᴇ : {time}
──────────────⟐
⧉ Lᴏɢ : Gʀᴏᴜᴘ Rᴇᴍᴏᴠᴀʟ Cᴏɴꜰɪʀᴍᴇᴅ
"""


# ----------------- BACKGROUND CHECKER LOOP --------------------
async def check_bot_removal():
    await app.start()

    BOT_ID = (await app.get_me()).id

    while True:
        removed_groups = []

        for chat_id in list(GROUP_LIST):
            try:
                # Check if bot is still inside
                await app.get_chat_member(chat_id, BOT_ID)

            except UserNotParticipant:
                # BOT REMOVED → LOG IT
                try:
                    chat = await app.get_chat(chat_id)
                    msg = build_log_message(chat)
                    await app.send_message(LOG_GROUP_ID, msg)

                except Exception:
                    pass

                removed_groups.append(chat_id)

        # Cleanup
        for g in removed_groups:
            GROUP_LIST.discard(g)

        await asyncio.sleep(10)


# Start background scanner
asyncio.create_task(check_bot_removal())
