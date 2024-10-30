from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.utils.database import get_lang, is_maintenance
from strings import get_string
from pyrogram.types import Message, CallbackQuery


def language(mystic):
    async def wrapper(_, message: Message, **kwargs):
        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                await message.reply_text(
                    text=f"{get_string('app_name')} is under maintenance. Please visit @grandxmasti for updates.",
                    disable_web_page_preview=True,
                )
                return
        await _delete_message(message)
        lang_code = await _get_language_code(message.chat.id)
        return await mystic(_, message, lang_code)

    return wrapper


def languageCB(mystic):
    async def wrapper(_, callback_query: CallbackQuery, **kwargs):
        if not await is_maintenance():
            if callback_query.from_user.id not in SUDOERS:
                await callback_query.answer(
                    f"{get_string('app_name')} is under maintenance. Visit support chat for more info.",
                    show_alert=True,
                )
                return
        lang_code = await _get_language_code(callback_query.message.chat.id)
        return await mystic(_, callback_query, lang_code)

    return wrapper


def LanguageStart(mystic):
    async def wrapper(_, message: Message, **kwargs):
        lang_code = await _get_language_code(message.chat.id)
        return await mystic(_, message, lang_code)

    return wrapper


async def _delete_message(message: Message):
    """Attempts to delete the message if possible."""
    try:
        await message.delete()
    except Exception:
        pass


async def _get_language_code(chat_id: int):
    """Fetches the language code for a specific chat. Defaults to 'en'."""
    try:
        lang_code = await get_lang(chat_id)
        return get_string(lang_code)
    except Exception:
        return get_string("en")
