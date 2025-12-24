from typing import Union

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from RocksMusic import app
from RocksMusic.utils import help_pannel
from RocksMusic.utils.database import get_lang
from RocksMusic.utils.decorators.language import LanguageStart, languageCB
from RocksMusic.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_GROUP
from strings import get_string, helpers


# =====================
# HELP IMAGES
# =====================
ADMIN_HELP_IMG = "https://files.catbox.moe/rk9j9l.jpg"
BL_HELP_IMG = "https://files.catbox.moe/ofqznr.jpg"


# =====================
# MAIN /help MENU
# =====================
@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("^settings_back_helper$") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)

    if is_callback:
        try:
            await update.answer()
        except:
            pass

        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)

        keyboard = help_pannel(_, True)

        # Telegraph Maker button (only in main menu)
        keyboard.inline_keyboard.insert(
            -1,
            [
                InlineKeyboardButton(
                    "⟐ Tᴇʟᴇɢʀᴀᴘʜ Mᴀᴋᴇʀ",
                    callback_data="help_callback hb_tgm",
                )
            ]
        )

        # 🔥 IMPORTANT: restore MAIN IMAGE on back
        await update.edit_message_media(
            types.InputMediaPhoto(
                media=START_IMG_URL,
                caption=_["help_1"].format(SUPPORT_GROUP),
            ),
            reply_markup=keyboard,
        )

    else:
        try:
            await update.delete()
        except:
            pass

        language = await get_lang(update.chat.id)
        _ = get_string(language)

        keyboard = help_pannel(_)

        keyboard.inline_keyboard.insert(
            -1,
            [
                InlineKeyboardButton(
                    "⟐ Tᴇʟᴇɢʀᴀᴘʜ Mᴀᴋᴇʀ",
                    callback_data="help_callback hb_tgm",
                )
            ]
        )

        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_GROUP),
            reply_markup=keyboard,
        )


# =====================
# GROUP /help
# =====================
@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =====================
# HELP CALLBACKS
# =====================
@app.on_callback_query(filters.regex("^help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    cb = CallbackQuery.data.strip().split(None, 1)[1]
    keyboard = help_back_markup(_)

    # ADMIN → image
    if cb == "hb1":
        await CallbackQuery.edit_message_media(
            types.InputMediaPhoto(
                media=ADMIN_HELP_IMG,
                caption=helpers.HELP_1,
            ),
            reply_markup=keyboard,
        )
        return

    # BL-CHAT → image
    if cb == "hb4":
        await CallbackQuery.edit_message_media(
            types.InputMediaPhoto(
                media=BL_HELP_IMG,
                caption=helpers.HELP_4,
            ),
            reply_markup=keyboard,
        )
        return

    # BL-USER → image
    if cb == "hb5":
        await CallbackQuery.edit_message_media(
            types.InputMediaPhoto(
                media=BL_HELP_IMG,
                caption=helpers.HELP_5,
            ),
            reply_markup=keyboard,
        )
        return

    # Telegraph Maker → text only (image stays main one)
    if cb == "hb_tgm":
        await CallbackQuery.edit_message_text(
            """
⌁ Mᴇᴅɪᴀ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴏʀ ⌁
⟡━━━━━━━━━━━━━━━━⟡
  ↳ Tᴇʟᴇɢʀᴀᴘʜ & CᴀᴛʙᴏxLɪɴᴋ
────────⟡⟡────────
↳ Uꜱᴇ : ~ Rᴇᴘʟʏ /tgm ᴛᴏ ᴀɴʏ ᴍᴇᴅɪᴀ
━━━━━━━━━━━━━━━━━➤
            """,
            reply_markup=keyboard,
        )
        return

    # OTHER HELP → text only
    text = (
        helpers.HELP_16.format(app.name)
        if cb == "hb16"
        else getattr(helpers, f"HELP_{cb[2:]}")
    )

    await CallbackQuery.edit_message_text(text, reply_markup=keyboard)
