import re
from math import ceil
from typing import Union

from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from ANNIEMUSIC import HELPABLE, app
from ANNIEMUSIC.utils.databaset import get_lang, is_commanddelete_on
from ANNIEMUSIC.utils.decorators.language import LanguageStart
from ANNIEMUSIC.utils.inline.help import private_help_panel

### Command
HELP_COMMAND = ["help"]

COLUMN_SIZE = 4
NUM_COLUMNS = 3


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, chat=None, close: bool = False):
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{})".format(
                        prefix, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{},{})".format(
                        prefix, chat, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "❮",
                    callback_data="{}_prev({})".format(
                        prefix,
                        modulo_page - 1 if modulo_page > 0 else max_num_pages - 1,
                    ),
                ),
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
                EqInlineKeyboardButton(
                    "❯",
                    callback_data="{}_next({})".format(prefix, modulo_page + 1),
                ),
            )
        ]
    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
            ]
        )

    return pairs


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("feature") & ~BANNED_USERS)
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
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await update.edit_message_text(_["help_1"], reply_markup=keyboard)
    else:
        chat_id = update.chat.id
        if await is_commanddelete_on(update.chat.id):
            try:
                await update.delete()
            except:
                pass
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELPABLE, "help", close=True)
        )
        if START_IMG_URL:

            await update.reply_photo(
                photo=START_IMG_URL,
                caption=_["help_1"],
                reply_markup=keyboard,
            )

        else:

            await update.reply_text(
                text=_["help_1"],
                reply_markup=keyboard,
            )


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return keyboard


@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back\((\d+)\)", query.data)
    create_match = re.match(r"help_create", query.data)
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)
    top_text = _["help_1"]

    if mod_match:
        module = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        text = (
            f"<b><u>Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ {HELPABLE[module].__MODULE__}:</u></b>\n"
            + HELPABLE[module].__HELP__
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="↪️ ʙᴀᴄᴋ", callback_data=f"help_back({prev_page_num})"
                    ),
                    InlineKeyboardButton(text="🔄 ᴄʟᴏsᴇ", callback_data="close"),
                ],
            ]
        )

        await query.message.edit(
            text=text,
            reply_markup=key,
            disable_web_page_preview=True,
        )

    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=InlineKeyboardMarkup(out),
        )
        await query.message.delete()

    elif prev_match:
        curr_page = int(prev_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        prev_page_num = int(back_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(prev_page_num, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif create_match:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await query.message.edit(
            text=top_text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    await client.answer_callback_query(query.id)


# ===================================

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS
from strings import helpers
from ANNIEMUSIC import app
from ANNIEMUSIC.utils.decorators.language import languageCB


@app.on_callback_query(filters.regex("music_callback") & ~BANNED_USERS)
@languageCB
async def music_helper_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_music(_)

    if cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.HELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.HELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.HELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.HELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.HELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.HELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.HELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.HELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.HELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.HELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.HELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.HELP_12, reply_markup=keyboard)

    elif cb == "hb13":

        await CallbackQuery.edit_message_text(helpers.HELP_13, reply_markup=keyboard)

    elif cb == "hb14":

        await CallbackQuery.edit_message_text(helpers.HELP_14, reply_markup=keyboard)

    elif cb == "hb15":

        await CallbackQuery.edit_message_text(helpers.HELP_15, reply_markup=keyboard)


@app.on_callback_query(filters.regex("management_callback") & ~BANNED_USERS)
@languageCB
async def management_callback_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_management(_)

    if cb == "extra":

        await CallbackQuery.edit_message_text(helpers.EXTRA_1, reply_markup=keyboard)

    elif cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.MHELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.MHELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.MHELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.MHELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.MHELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.MHELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.MHELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.MHELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.MHELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.MHELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.MHELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.MHELP_12, reply_markup=keyboard)


@app.on_callback_query(filters.regex("tools_callback") & ~BANNED_USERS)
@languageCB
async def tools_callback_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_tools(_)

    if cb == "ai":

        await CallbackQuery.edit_message_text(helpers.AI_1, reply_markup=keyboard)

    elif cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.THELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.THELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.THELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.THELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.THELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.THELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.THELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.THELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.THELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.THELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.THELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.THELP_12, reply_markup=keyboard)


@app.on_callback_query(filters.regex("developer"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="🇲σ᭡፝֟ɳ🌙", url=f"https://t.me/about_ur_moonshining/5"),
            InlineKeyboardButton(
                text="Owner's clan 🎄", url=f"https://t.me/grandxmasti"
            ),
        ],
        [
            InlineKeyboardButton(text="🎄 Galaxy 🎄", callback_data="galaxy"),
            InlineKeyboardButton(text="⭐ Help ⭐", callback_data="features"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="about")
        ],  # Use a default label for the back button
    ]
    await callback_query.message.edit_text(
        "**Hey,**\n\n**I am Annie bot ✨**\n**I am created with love by my [🇲σ᭡፝֟ɳ](https://t.me/about_ur_moonshining/5)🌙 ❤.**",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex("feature"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎄 Galaxy 🎄",
                callback_data="galaxy",
            ),
        ],
        [
            InlineKeyboardButton(text="Music 🎧", callback_data="music"),
            InlineKeyboardButton(text="Managment ✔", callback_data="management"),
        ],
        [
            InlineKeyboardButton(text="Tools✨", callback_data="tools"),
            InlineKeyboardButton(text="Extra🦋", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="✯ Home ✯", callback_data="go_to_start")],
    ]
    k = f"""Annie bot 🦋 help menu ✨*"""
    await callback_query.message.edit_text(
        text=k, reply_markup=InlineKeyboardMarkup(keyboard)
    )


@app.on_callback_query(filters.regex("music"))
async def music_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Aᴅᴍɪɴ", callback_data="music_callback hb1"),
                InlineKeyboardButton(text="Aᴜᴛʜ", callback_data="music_callback hb2"),
                InlineKeyboardButton(
                    text="Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="music_callback hb3"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Bʟ-Cʜᴀᴛ", callback_data="music_callback hb4"
                ),
                InlineKeyboardButton(
                    text="Bʟ-Usᴇʀ", callback_data="music_callback hb5"
                ),
                InlineKeyboardButton(text="C-Pʟᴀʏ", callback_data="music_callback hb6"),
            ],
            [
                InlineKeyboardButton(text="G-Bᴀɴ", callback_data="music_callback hb7"),
                InlineKeyboardButton(text="Lᴏᴏᴘ", callback_data="music_callback hb8"),
                InlineKeyboardButton(
                    text="Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="music_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(text="Pɪɴɢ", callback_data="music_callback hb10"),
                InlineKeyboardButton(text="Pʟᴀʏ", callback_data="music_callback hb11"),
                InlineKeyboardButton(
                    text="Sʜᴜғғʟᴇ", callback_data="music_callback hb12"
                ),
            ],
            [
                InlineKeyboardButton(text="Sᴇᴇᴋ", callback_data="music_callback hb13"),
                InlineKeyboardButton(text="Sᴏɴɢ", callback_data="music_callback hb14"),
                InlineKeyboardButton(text="Sᴘᴇᴇᴅ", callback_data="music_callback hb15"),
            ],
            [InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](t.me/grandxmasti)**\n\n**Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("management"))
async def management_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="єxᴛʀᴧ", callback_data="management_callback extra"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ʙᴧη", callback_data="management_callback hb1"
                ),
                InlineKeyboardButton(
                    text="ᴋɪᴄᴋs", callback_data="management_callback hb2"
                ),
                InlineKeyboardButton(
                    text="ϻυᴛє", callback_data="management_callback hb3"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ᴘɪη", callback_data="management_callback hb4"
                ),
                InlineKeyboardButton(
                    text="sᴛᴧғғ", callback_data="management_callback hb5"
                ),
                InlineKeyboardButton(
                    text="sєᴛ υᴘ", callback_data="management_callback hb6"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="zσϻʙɪє", callback_data="management_callback hb7"
                ),
                InlineKeyboardButton(
                    text="ɢᴧϻє", callback_data="management_callback hb8"
                ),
                InlineKeyboardButton(
                    text="ɪϻᴘσsᴛєʀ", callback_data="management_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="sᴧηɢ ϻᴧᴛᴧ", callback_data="management_callback hb10"
                ),
                InlineKeyboardButton(
                    text="ᴛʀᴧηsʟᴧᴛє", callback_data="management_callback hb11"
                ),
                InlineKeyboardButton(
                    text="ᴛ-ɢʀᴧᴘʜ", callback_data="management_callback hb12"
                ),
            ],
            [InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](t.me/tg_friendsss)**\n\n**Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("tools"))
async def tools_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="ᴄʜᴧᴛɢᴘᴛ", callback_data="tools_callback ai")],
            [
                InlineKeyboardButton(text="ɢσσɢʟє", callback_data="tools_callback hb1"),
                InlineKeyboardButton(
                    text="ᴛᴛs-ᴠσɪᴄє", callback_data="tools_callback hb2"
                ),
                InlineKeyboardButton(text="ɪηꜰσ", callback_data="tools_callback hb3"),
            ],
            [
                InlineKeyboardButton(text="ғσηᴛ", callback_data="tools_callback hb4"),
                InlineKeyboardButton(text="ϻᴧᴛʜ", callback_data="tools_callback hb5"),
                InlineKeyboardButton(text="ᴛᴧɢᴧʟʟ", callback_data="tools_callback hb6"),
            ],
            [
                InlineKeyboardButton(text="ɪϻᴧɢє", callback_data="tools_callback hb7"),
                InlineKeyboardButton(text="ʜᴧsᴛᴧɢ", callback_data="tools_callback hb8"),
                InlineKeyboardButton(
                    text="sᴛɪᴄᴋєʀs", callback_data="tools_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(text="ғυη", callback_data="tools_callback hb10"),
                InlineKeyboardButton(
                    text="ǫυσᴛʟʏ", callback_data="tools_callback hb11"
                ),
                InlineKeyboardButton(
                    text="ᴛʀ - ᴅʜ", callback_data="tools_callback hb12"
                ),
            ],
            [InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](t.me/grandxmasti)**\n\n**Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("back_to_music"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎄 Galaxy 🎄",
                callback_data="galaxy",
            ),
        ],
        [
            InlineKeyboardButton(text="Music 🎧", callback_data="music"),
            InlineKeyboardButton(text="Managment ✔", callback_data="management"),
        ],
        [
            InlineKeyboardButton(text="Tools✨", callback_data="tools"),
            InlineKeyboardButton(text="Extra🦋", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]

    k = f"""Annie bot 🦋 help menu ✨"""
    await callback_query.message.edit_text(
        text=k,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def back_to_music(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"music",
                ),
            ]
        ]
    )
    return upl


def back_to_tools(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"tools",
                ),
            ]
        ]
    )
    return upl


def back_to_management(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"management",
                ),
            ]
        ]
    )
    return upl


@app.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(
                text="• Annie v2.0 •",
                callback_data="annie",
            ),
        ],
        [
            InlineKeyboardButton(text="⭐ Support ⭐", url=f"t.me/grandxmasti"),
            InlineKeyboardButton(text="👨‍💻Developer", callback_data="developer"),
        ],
        [
            InlineKeyboardButton(text="Guide 📃", callback_data="basic_guide"),
            InlineKeyboardButton(text="🥀Source", callback_data="source"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        f"Hi i am Annie bot 🦋\nA powerful and awesome telegram group management and music player that gives you spam-free and fun environment for your groups :)\n\n**ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴀɴᴅ ᴀᴡᴇsᴏᴍᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴀɴᴅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴛʜᴀᴛ ɢɪᴠᴇs ʏᴏᴜ sᴘᴀᴍ-ғʀᴇᴇ ᴀɴᴅ ғᴜɴ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘs :)\n\n● I can restrict users.\n● I can greet users with customizable welcome messages and even set a group's rules.\n● I have a music player system.\n● I have almost all awaited group managing features like ban, mute, welcome, kick, federation, and many more.\n● I have a note-keeping system, blacklists, and even predetermined replies on certain keywords.\n● I check for admins' permissions before executing any command and more stuff\n\n➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ Annie bot 🦋.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex("annie"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="Guide 📃", url=f"t.me/grandxmasti"),
            InlineKeyboardButton(text="👨‍💻Developer", callback_data="developer"),
        ],
        [
            InlineKeyboardButton(text="Guide 📃", callback_data="basic_guide"),
            InlineKeyboardButton(text="🥀Source", callback_data="source"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        f"We have added or upgraded the following plugins given below ✨\n\n• Added ai response and ai img(chat-gpt).\n• Added quotly.\n• Added emoji game.\n• Update howsall, judge, wish, afk feature.\n• Update write, bug and fedration tools.\n• Added gif and animated sticker kang also.\n• Added Website of bot for preview.\n• Added Pinterest,yt and Insta video downloader.\n• Added inbuilt music system.\n\nFor more info about Annie updates check website 🎄👀.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# If the back button has different meanings in various panels, you can set different callbacks
@app.on_callback_query(filters.regex("support"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(text="Developer 👨‍💻", user_id=config.OWNER_ID[0]),
            InlineKeyboardButton(
                text="🌱ɢɪᴛʜᴜʙ🌱",
                url="https://github.com/moonshining1/ANNIE-MUSIC",
            ),
        ],
        [
            InlineKeyboardButton(text="⛅Group⛅", url=f"https://t.me/grandxmasti"),
            InlineKeyboardButton(text="🎄Update🎄", url=f"https://t.me/kittyxupdates "),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]

    await callback_query.message.edit_text(
        "๏ Click on the button to get more about me.\n\nIf you find any error or bug on bot or want to give any feedback about the bot then you are welcome to support chat  (✿◠‿◠).",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@app.on_callback_query(filters.regex("galaxy"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(text="Developer 👨‍💻", callback_data="developer"),
            InlineKeyboardButton(
                text="🌱Github🌱",
                url="https://github.com/moonshining1/annie-music",
            ),
        ],
        [
            InlineKeyboardButton(text="Annie updates", url=f"https://t.me/kittyxupdates"),
            InlineKeyboardButton(text="Share ur query💡", url=f"https://t.me/pwmbothub"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        "Join our groups....🧊\n\nFor more info about meowsteric updates check support 🎄👀",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )    

@app.on_callback_query(filters.regex("source"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(text="Developer 👨‍💻", callback_data="developer"),
            InlineKeyboardButton(
                text="🌱Repo🌱",
                url="https://github.com/moonshining1/annie-music",
            ),
        ],
        [
            InlineKeyboardButton(text="Annie updates", url=f"https://t.me/kittyxupdates"),
            InlineKeyboardButton(text="Share ur query💡", url=f"https://t.me/pwmbothub"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]
    
    await callback_query.message.edit_text(
        "Hey,\nThis is Annie bot 🦋\n\nAn open source telegram group management+ music bot\nHere is my source code [Repo](https://github.com/moonshining1/ANNIE-MUSIC) (✿◠‿◠)",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

@app.on_callback_query(filters.regex("basic_guide"))
async def settings_back_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [[InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data="about")]]
    guide_text = f"**ʜᴇʏ! ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ᴀɴᴅ sɪᴍᴘʟᴇ ɢᴜɪᴅᴇ ᴛᴏ ᴜsɪɴɢ** {app.mention} **🎉**\n\n**1. ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 'ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʟᴀɴ' ʙᴜᴛᴛᴏɴ.**\n**2. sᴇʟᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɴᴀᴍᴇ.**\n**3. ɢʀᴀɴᴛ ᴛʜᴇ ʙᴏᴛ ᴀʟʟ ɴᴇᴄᴇssᴀʀʏ ᴘᴇʀᴍɪssɪᴏɴs ғᴏʀ sᴍᴏᴏᴛʜ ᴀɴᴅ ғᴜʟʟ ғᴜɴᴄᴛɪᴏɴᴀʟɪᴛʏ.**\n\n**ᴛᴏ ᴀᴄᴄᴇss ᴄᴏᴍᴍᴀɴᴅs, ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏsᴇ ʙᴇᴛᴡᴇᴇɴ ᴍᴜsɪᴄ ᴏʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇs.**\n**ɪғ ʏᴏᴜ sᴛɪʟʟ ғᴀᴄᴇ ᴀɴʏ ɪssᴜᴇs, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ʀᴇᴀᴄʜ ᴏᴜᴛ ғᴏʀ sᴜᴘᴘᴏʀᴛ ✨**"
    await callback_query.message.edit_text(
        text=guide_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

