import asyncio
from datetime import datetime, timedelta
from pyrogram import filters, Client
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


async def get_client(num):
    # Initialize client for assistant bots
    client = Client(f"assistant_{num}")
    await client.start()
    return client


@app.on_raw_update(group=cleanmode_group)
async def clean_mode(client, update, users, chats):
    global IS_BROADCASTING
    if IS_BROADCASTING:
        return
    if not isinstance(update, types.UpdateReadChannelOutbox):
        return
    if users or chats:
        return
    message_id = update.max_id
    chat_id = int(f"-100{update.channel_id}")
    if not await is_cleanmode_on(chat_id):
        return
    if chat_id not in clean:
        clean[chat_id] = []
    time_now = datetime.now()
    put = {
        "msg_id": message_id,
        "timer_after": time_now + timedelta(minutes=AUTO_DELETE),
    }
    clean[chat_id].append(put)
    await set_queries(1)


@app.on_message(filters.command(broadcast) & filters.user(OWNER_ID))
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
        query = message.reply_to_message.text
    else:
        query = " ".join(message.command[1:]) or "Default broadcast message"

    # Remove command flags
    for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]:
        query = query.replace(flag, "").strip()

    if not query:
        return await message.reply_text(_["broad_6"])

    IS_BROADCASTING = True
    ok = await message.reply_text(_["broad_8"])

    # Broadcast to group chats
    if "-nobot" not in message.text:
        sent, pin = 0, 0
        schats = await get_served_chats()
        for chat in schats:
            chat_id = int(chat["chat_id"])
            if chat_id == config.LOGGER_ID:
                continue
            try:
                m = (
                    await app.forward_messages(chat_id, y, x)
                    if message.reply_to_message
                    else await app.send_message(chat_id, text=query)
                )
                sent += 1
                if "-pin" in message.text:
                    await m.pin(disable_notification=True)
                    pin += 1
                elif "-pinloud" in message.text:
                    await m.pin(disable_notification=False)
                    pin += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue
        await ok.delete()
        await message.reply_text(_["broad_1"].format(sent, pin))
        await save_broadcast_stats(sent, 0)

    # Broadcast to users
    if "-user" in message.text:
        susr = 0
        susers = await get_served_users()
        for user in susers:
            user_id = int(user["user_id"])
            try:
                m = (
                    await app.forward_messages(user_id, y, x)
                    if message.reply_to_message
                    else await app.send_message(user_id, text=query)
                )
                susr += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue
        await message.reply_text(_["broad_7"].format(susr))
        await save_broadcast_stats(0, susr)

    # Broadcast by assistant bots
    if "-assistant" in message.text:
        from ANNIEMUSIC.core.userbot import assistants
        text = _["broad_3"]
        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                if dialog.chat.id == config.LOGGER_ID:
                    continue
                try:
                    (
                        await client.forward_messages(dialog.chat.id, y, x)
                        if message.reply_to_message
                        else await client.send_message(dialog.chat.id, text=query)
                    )
                    sent += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    continue
            text += _["broad_4"].format(num, sent)
        await message.reply_text(text)
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(AUTO_SLEEP):
        try:
            # Clear outdated messages
            for chat_id in clean:
                for x in clean[chat_id]:
                    if datetime.now() > x["timer_after"]:
                        if chat_id in protected_messages and x["msg_id"] in protected_messages[chat_id]:
                            continue
                        try:
                            await app.delete_messages(chat_id, x["msg_id"])
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                        except Exception:
                            continue
        except Exception:
            continue

        try:
            # Refresh admins and auth users
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    admins = app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    )
                    async for user in admins:
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except Exception:
            continue


asyncio.create_task(auto_clean())
