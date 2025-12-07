# RocksMusic/plugins/misc/leavelog.py

import asyncio
from datetime import datetime, timedelta, timezone

from RocksMusic import app, userbot
from config import LOG_GROUP_ID

from pyrogram.errors import (
    ChatAdminRequired,
    PeerIdInvalid,
    UserNotParticipant,
)

# Timezone
IST = timezone(timedelta(hours=5, minutes=30))


async def check_bot_status():
    await asyncio.sleep(10)  # Wait for bot + assistant to fully start

    bot = await app.get_me()

    print("[LeaveLog] Background bot removal scanner started...")

    while True:
        try:
            # Iterate through ALL chats where assistant is present
            async for dialog in userbot.iter_dialogs():
                chat = dialog.chat
                chat_id = chat.id

                try:
                    # Check if the bot is still in that chat
                    member = await app.get_chat_member(chat_id, bot.id)

                    # Bot is still member/admin → skip
                    if member.status in ["member", "administrator"]:
                        continue

                except UserNotParticipant:
                    # Bot was removed OR banned
                    now = datetime.now(IST)
                    date = now.strftime("%d-%b-%Y")
                    time = now.strftime("%I:%M %p")

                    group_name = chat.title or "Unknown"
                    remover_name = "Unknown"
                    remover_id = "Unknown"

                    text = f"""
⧈⧈⧈ Bᴏᴛ Dɪꜱᴄᴏɴɴᴇᴄᴛɪᴏɴ Aʟᴇʀᴛ ⧈⧈⧈
──────────────⟐
➤ Gʀᴏᴜᴘ : {group_name}
➤ Iᴅ : <code>{chat_id}</code>
➤ Lɪɴᴋ : Private / Unavailable
──────────────⟐
➤ Aᴄᴛɪᴏɴ : Bᴏᴛ Wᴀꜱ Rᴇᴍᴏᴠᴇᴅ / Kɪᴄᴋᴇᴅ / Bᴀɴɴᴇᴅ
➤ Bʏ : {remover_name}
    ⟿   User ID : {remover_id}
──────────────⟐
➤ Dᴀᴛᴇ : {date}
➤ Tɪᴍᴇ : {time}
──────────────⟐
⧉ Lᴏɢ : Gʀᴏᴜᴘ Rᴇᴍᴏᴠᴀʟ Cᴏɴꜰɪʀᴍᴇᴅ
"""

                    try:
                        await app.send_message(
                            LOG_GROUP_ID,
                            text,
                            disable_web_page_preview=True,
                        )
                        print(f"[LeaveLog] Removal detected in {group_name}")

                    except Exception as e:
                        print(f"[LeaveLog] Failed to send log: {e}")

                except (ChatAdminRequired, PeerIdInvalid):
                    # No access, invalid chat, etc.
                    pass

        except Exception as e:
            print(f"[LeaveLog MAIN LOOP ERROR] {e}")

        # Check every 10 seconds
        await asyncio.sleep(10)


# Start background monitoring
app.loop.create_task(check_bot_status())
