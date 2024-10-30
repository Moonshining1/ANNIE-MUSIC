import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from pyrogram.raw import types
import config
from config import OWNER_ID, adminlist, chatstats, clean, userstats
from ANNIEMUSIC import app
from ANNIEMUSIC.utils.cleanmode import protected_messages
from ANNIEMUSIC.utils.databaset import (
    get_active_chats,
    get_authuser_names,
    get_particular_top,
    get_served_chats,
    get_served_users,
    get_user_top,
    is_cleanmode_on,
    save_broadcast_stats,
    set_queries,
    update_particular_top,
    update_user_top,
)
from ANNIEMUSIC.utils.decorators.language import language
from ANNIEMUSIC.utils.formatters import alpha_to_int

broadcast = ["broadcast"]
AUTO_DELETE = config.CLEANMODE_DELETE_MINS
AUTO_SLEEP = 5
IS_BROADCASTING = False
cleanmode_group = 15

@app.on_message(filters.command(broadcast) & filters.user(OWNER_ID))
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING
    if IS_BROADCASTING:
        return await message.reply_text("A broadcast is already in progress. Please wait.")

    IS_BROADCASTING = True
    query = parse_message_query(message)
    if not query:
        return await message.reply_text("Please provide a broadcast message.")
    
    status_message = await message.reply_text("Broadcasting message, please wait...")

    try:
        await broadcast_to_chats(client, message, query)
        await broadcast_to_users(client, message, query)
        await broadcast_by_assistant(client, message, query)
    except Exception as e:
        print(f"Broadcast failed: {e}")
    finally:
        IS_BROADCASTING = False
        await status_message.delete()


def parse_message_query(message):
    if message.reply_to_message:
        query = message.reply_to_message.text
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    else:
        query = "Default broadcast message"
    for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]:
        query = query.replace(flag, "")
    return query.strip()


async def broadcast_to_chats(client, message, query):
    sent, pin_count = 0, 0
    schats = await get_served_chats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            msg = await send_message_to_chat(client, chat_id, message, query)
            sent += 1
            if "-pin" in message.text or "-pinloud" in message.text:
                pin_count += await pin_message(msg, loud=("-pinloud" in message.text))
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")
    await message.reply_text(f"Broadcast sent to {sent} chats, pinned in {pin_count} chats.")


async def send_message_to_chat(client, chat_id, message, query):
    if message.reply_to_message:
        return await client.forward_messages(chat_id, message.chat.id, message.reply_to_message.id)
    return await client.send_message(chat_id, text=query)


async def pin_message(message, loud=False):
    try:
        await message.pin(disable_notification=not loud)
        return 1
    except Exception:
        return 0


async def broadcast_to_users(client, message, query):
    if "-user" not in message.text:
        return
    susr = 0
    susers = await get_served_users()
    for user in susers:
        user_id = int(user["user_id"])
        try:
            await client.send_message(user_id, text=query)
            susr += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")
    await message.reply_text(f"Broadcast sent to {susr} users.")


async def broadcast_by_assistant(client, message, query):
    if "-assistant" not in message.text:
        return
    from ANNIEMUSIC.core.userbot import assistants
    for assistant in assistants:
        sent = 0
        async with assistant:
            async for dialog in assistant.get_dialogs():
                chat_id = dialog.chat.id
                if chat_id == config.LOGGER_ID:
                    continue
                try:
                    await assistant.send_message(chat_id, text=query)
                    sent += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception as e:
                    print(f"Assistant failed to send message to {chat_id}: {e}")
    await message.reply_text("Broadcast completed by assistants.")


asyncio.create_task(auto_clean())
