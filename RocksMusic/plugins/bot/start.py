import time

from pyrogram import filters, types
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)
from youtubesearchpython.__future__ import VideosSearch

import config
from config import START_IMG_URL, BANNED_USERS
from RocksMusic import app
from RocksMusic.misc import _boot_
from RocksMusic.plugins.sudo.sudoers import sudoers_list
from RocksMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from RocksMusic.utils.decorators.language import LanguageStart
from RocksMusic.utils.formatters import get_readable_time
from RocksMusic.utils.inline import help_pannel, start_panel
from strings import get_string


# ============================================
# DEFAULT IMAGE FOR HELP & COMMANDS (FROM START)
# ============================================
START_HELP_IMG = "https://files.catbox.moe/u37c0f.jpg"


# ============================================
# 🔥 START TEXT (UNCHANGED — DO NOT TOUCH)
# ============================================
START_TEXT = """
✦✧ Hᴇʏ {0},

ʏᴏᴜ’ʀᴇ ɴᴏᴡ ᴄᴏɴɴᴇᴄᴛᴇᴅ.

{1}
ᴀɴ ᴀɪ-ғᴏʀᴍᴇᴅ ᴍᴜsɪᴄ sʏsᴛᴇᴍ
ʙᴜɪʟᴛ ғᴏʀ ᴄʟᴇᴀɴ • sᴛᴀʙʟᴇ • ᴄᴏɴsɪsᴛᴇɴᴛ ᴀᴜᴅɪᴏ.

✦ Rᴏᴄᴋs Oғғɪᴄɪᴀʟ
ғᴏᴄᴜsᴇs ᴏɴ ǫᴜᴀʟɪᴛʏ → ɴᴏᴛ ɴᴏɪsᴇ.
ʙᴜɪʟᴛ ᴀs ᴀ sᴛᴀɴᴅᴀʀᴅ, ɴᴏᴛ ᴀ ᴛʀᴇɴᴅ.

Rᴇʟɪᴀʙʟᴇ • Rᴇᴄᴏɢɴɪᴢᴀʙʟᴇ • Iɴᴅᴇᴘᴇɴᴅᴇɴᴛ

┏━━━─────────➣
╰➢ Rᴏᴄᴋs Eᴄᴏsʏsᴛᴇᴍ → Aᴄᴛɪᴠᴇ Nᴏᴅᴇs
╰➢ @rocks_music_bot
╰➢ @RocksMusicAIBot
╰➢ @ValerieMusicBot
╰➢ @ROCKSxKITTYxBOT
╰➢ @MiRcHixMuSiC_bot
┗━━━─────────➣

Mᴜʟᴛɪᴘʟᴇ ɴᴏᴅᴇs
Oɴᴇ sʜᴀʀᴇᴅ ᴄᴏʀᴇ • Oɴᴇ sᴛᴀɴᴅᴀʀᴅ

⎯⎯⎯⧉ Cʜᴇᴄᴋᴏᴜᴛ ɪɢ ⎯⎯⎯
𖤐 <a href="https://www.instagram.com/rocks_official_empire">Rᴏᴄᴋꜱ 𝕏 Eᴍᴘɪʀᴇ</a>

⎯⎯⎯⧉ Pᴏᴡᴇʀᴇᴅ ʙʏ ⎯⎯⎯
𖤐 <a href="https://t.me/ROCKS_OFFICIAL">Rᴏᴄᴋꜱ 𝕏 Eᴍᴘɪʀᴇ</a>
"""


# ============================================
# PRIVATE /start
# ============================================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                "♚ Aᴅᴅ Bᴏᴛ Tᴏ Gʀᴏᴜᴘ",
                url=f"https://t.me/{app.username}?startgroup=true"
            )],
            [
                InlineKeyboardButton("⟠ Aᴜᴛʜᴏʀɪᴛʏ", url="https://t.me/ROCKS_ROBOTS/73"),
                InlineKeyboardButton("⌬ Uᴘᴅᴀᴛᴇs", url="https://t.me/ROCKS_ROBOTS/6")
            ],
            [InlineKeyboardButton(
                "❓ Hᴇʟᴘ & Cᴏᴍᴍᴀɴᴅs",
                callback_data="start_help_open"
            )],
            [InlineKeyboardButton(
                "⟢ Cʜᴀᴛ Hᴜʙ",
                url="https://t.me/Shayari_Music_Lovers/16"
            )],
        ]
    )

    await message.reply_photo(
        photo=START_IMG_URL,
        caption=START_TEXT.format(message.from_user.mention, app.mention),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


# ============================================
# OPEN HELP & COMMANDS FROM START
# ============================================

@app.on_callback_query(filters.regex("^start_help_open$") & ~BANNED_USERS)
@LanguageStart
async def start_help_open_cb(client, cq: CallbackQuery, _):
    await cq.answer()
    keyboard = help_pannel(_, True)
    await cq.edit_message_media(
        types.InputMediaPhoto(
            media=START_HELP_IMG,
            caption=_["help_1"].format(config.SUPPORT_GROUP),
        ),
        reply_markup=keyboard,
    )


# ============================================
# BACK INSIDE HELP & COMMANDS
# ============================================

@app.on_callback_query(filters.regex("^settings_back_helper$") & ~BANNED_USERS)
@LanguageStart
async def start_help_back_cb(client, cq: CallbackQuery, _):
    await cq.answer()
    keyboard = help_pannel(_, True)
    await cq.edit_message_media(
        types.InputMediaPhoto(
            media=START_HELP_IMG,
            caption=_["help_1"].format(config.SUPPORT_GROUP),
        ),
        reply_markup=keyboard,
    )


# ============================================
# EXIT HELP & COMMANDS → BACK TO START
# ============================================

@app.on_callback_query(filters.regex("^start_back_main$") & ~BANNED_USERS)
@LanguageStart
async def start_back_main_cb(client, cq: CallbackQuery, _):
    await cq.answer()

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                "♚ Aᴅᴅ Bᴏᴛ Tᴏ Gʀᴏᴜᴘ",
                url=f"https://t.me/{app.username}?startgroup=true"
            )],
            [
                InlineKeyboardButton("⟠ Aᴜᴛʜᴏʀɪᴛʏ", url="https://t.me/ROCKS_ROBOTS/73"),
                InlineKeyboardButton("⌬ Uᴘᴅᴀᴛᴇs", url="https://t.me/ROCKS_ROBOTS/6")
            ],
            [InlineKeyboardButton(
                "❓ Hᴇʟᴘ & Cᴏᴍᴍᴀɴᴅs",
                callback_data="start_help_open"
            )],
            [InlineKeyboardButton(
                "⟢ Cʜᴀᴛ Hᴜʙ",
                url="https://t.me/Shayari_Music_Lovers/16"
            )],
        ]
    )

    await cq.edit_message_media(
        types.InputMediaPhoto(
            media=START_IMG_URL,
            caption=START_TEXT.format(cq.from_user.mention, app.mention),
        ),
        reply_markup=keyboard,
    )


# ============================================
# GROUP /start (UNCHANGED)
# ============================================

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
        parse_mode=ParseMode.HTML,
    )
    return await add_served_chat(message.chat.id)
