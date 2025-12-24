# ==========================================================
# SUDO MANAGEMENT • ROCKS MUSIC
# Illusion → Authority → Real Control (FINAL)
# ==========================================================

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from RocksMusic import app
from RocksMusic.misc import SUDOERS
from RocksMusic.utils.database import add_sudo, remove_sudo
from RocksMusic.utils.decorators.language import language
from RocksMusic.utils.extraction import extract_user
from config import BANNED_USERS, OWNER_ID

# 🔧 BACKWARD COMPATIBILITY FIX
# Old modules import `sudoers_list`
sudoers_list = SUDOERS


CAPTION = """
<b>🜲 Sᴜᴅᴏ Aᴄᴄᴇss Pᴀɴᴇʟ</b>

Rᴏʟᴇs ᴀʀᴇ ᴅᴇғɪɴᴇᴅ.
Aᴄᴄᴇss ɪs ᴀssɪɢɴᴇᴅ.

Wʜᴀᴛ ʏᴏᴜ sᴇᴇ
ᴅᴇᴘᴇɴᴅs ᴏɴ ʏᴏᴜʀ ʟᴀʏᴇʀ.
"""


@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
@language
async def add_sudo_user(_, message: Message, _l):
    user = await extract_user(message)
    if not user:
        return
    if user.id in SUDOERS:
        return await message.reply_text(_l["sudo_1"].format(user.mention))
    if await add_sudo(user.id):
        SUDOERS.add(user.id)
        await message.reply_text(_l["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_l["sudo_8"])


@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def remove_sudo_user(_, message: Message, _l):
    user = await extract_user(message)
    if not user:
        return
    if user.id not in SUDOERS:
        return await message.reply_text(_l["sudo_3"].format(user.mention))
    if await remove_sudo(user.id):
        SUDOERS.remove(user.id)
        await message.reply_text(_l["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_l["sudo_8"])


@app.on_message(filters.command(["sudolist", "sudoers", "listsudo"]) & ~BANNED_USERS)
async def sudo_entry(_, message: Message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("◆ Eɴᴛᴇʀ Rᴇsᴛʀɪᴄᴛᴇᴅ Zᴏɴᴇ ◆", callback_data="gate_1")]]
    )
    await message.reply_photo(
        photo="https://files.catbox.moe/jd95ew.jpg",
        caption=CAPTION,
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("^gate_1$"))
async def gate_1(_, cq: CallbackQuery):
    await cq.message.edit_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("◆ Tʜɪɴᴋ Yᴏᴜ Qᴜᴀʟɪғʏ? ◆", callback_data="gate_2")]]
        )
    )


@app.on_callback_query(filters.regex("^gate_2$"))
async def gate_2(_, cq: CallbackQuery):
    await cq.message.edit_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("◆ Cʜᴇᴄᴋ Yᴏᴜʀ Lᴇᴠᴇʟ ◆", callback_data="gate_final")]]
        )
    )


AUTH_TITLES = [
    "🔒 Aʟᴘʜᴀ Aᴄᴄᴇss",
    "🔒 Oᴍɴɪ Aᴄᴄᴇss",
    "🔒 Pʀɪᴍᴇ Aᴄᴄᴇss",
    "🔒 Vᴀɴɢᴜᴀʀᴅ",
    "🔒 Sɪɢᴍᴀ Lᴀʏᴇʀ",
    "🔒 Cᴏʀᴇ Pʀᴏᴛᴏᴄᴏʟ",
    "🔒 Aᴜᴛʜᴏʀɪᴛʏ Nᴏᴅᴇ",
    "🔒 Cᴏᴍᴍᴀɴᴅ Lɪɴᴋ",
    "🔒 Rᴏᴏᴛ Lᴀʏᴇʀ",
    "🔒 Fɪɴᴀʟ Gᴀᴛᴇ",
]


@app.on_callback_query(filters.regex("^gate_final$"))
async def gate_final(_, cq: CallbackQuery):
    if cq.from_user.id not in SUDOERS:
        return await cq.answer(
            "Aᴄᴄᴇss Dᴇɴɪᴇᴅ.\nLᴇᴠᴇʟ Iɴsᴜғғɪᴄɪᴇɴᴛ.",
            show_alert=True,
        )

    keyboard = [
        [InlineKeyboardButton(
            "🜲 Fᴏᴜɴᴅᴀᴛɪᴏɴ ᴏᴡɴᴇʀ",
            url=f"tg://openmessage?user_id={OWNER_ID}"
        )]
    ]

    i = 0
    for uid in SUDOERS:
        if uid == OWNER_ID:
            continue
        if i >= len(AUTH_TITLES):
            break
        keyboard.append(
            [InlineKeyboardButton(
                AUTH_TITLES[i],
                url=f"tg://openmessage?user_id={uid}"
            )]
        )
        i += 1

    keyboard.append([InlineKeyboardButton("✖ Cʟᴏsᴇ", callback_data="close_panel")])
    await cq.message.edit_reply_markup(InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("^close_panel$"))
async def close_panel(_, cq: CallbackQuery):
    await cq.message.delete()
