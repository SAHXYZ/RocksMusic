import asyncio
import pytz
from datetime import datetime
from pyrogram.errors import UserNotParticipant
from RocksMusic import app
from RocksMusic.config import LOG_GROUP_ID

# -------------------------------------------------------------
# Storage for all groups where bot was added (Mode 2)
# This list is filled by joinlog.py using add_group(chat_id)
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

    # Get main bot's ID
    BOT_ID = (await app.get_me()).id

    while True:
        removed_groups = []

        for chat_id in list(GROUP_LIST):
            try:
                # If bot is present → this works normally
                await app.get_chat_member(chat_id, BOT_ID)

            except UserNotParticipant:
                # BOT IS REMOVED → SEND LEAVE LOG
                try:
                    chat = await app.get_chat(chat_id)
                    msg = build_log_message(chat)

                    await app.send_message(LOG_GROUP_ID, msg)

                except Exception:
                    pass

                # Mark for cleanup
                removed_groups.append(chat_id)

        # Remove from list
        for g in removed_groups:
            GROUP_LIST.discard(g)

        await asyncio.sleep(10)   # scan interval


# Start background scanner
asyncio.create_task(check_bot_removal())
