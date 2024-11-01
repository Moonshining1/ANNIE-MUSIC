from pyrogram import filters, enums
from pyrogram.types import ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid
import datetime
from ANNIEMUSIC import app

def mention(user_id, name, mention=True):
    if mention:
        link = f"[{name}](tg://openmessage?user_id={user_id})"
    else:
        link = f"[{name}](https://t.me/{user_id})"
    return link

async def get_userid_from_username(username):
    try:
        user = await app.get_users(username)
    except:
        return None
    return [user.id, user.first_name]

async def ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None):
    try:
        await app.ban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Make sure that you have given me that right", False
    except UserAdminInvalid:
        return "I won't ban an admin bruh!!", False
    except Exception as e:
        if user_id == 7297381612:
            return "Why should I ban myself? Sorry but I'm not stupid like you", False
        return f"Oops!!\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was banned by {admin_mention}\n"
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    return msg_text, True

async def unban_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.unban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Make sure that you have given me that right"
    except Exception as e:
        return f"Oops!!\n{e}"
    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    return f"{user_mention} was unbanned by {admin_mention}"

async def mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None, time=None):
    try:
        if time:
            mute_end_time = datetime.datetime.now() + time
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions(), mute_end_time)
        else:
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
    except ChatAdminRequired:
        return "Make sure that you have given me that right", False
    except UserAdminInvalid:
        return "I won't mute an admin bruh!!", False
    except Exception as e:
        if user_id == 7297381612:
            return "Why should I mute myself? Sorry but I'm not stupid like you", False
        return f"Oops!!\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was muted by {admin_mention}\n"
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    return msg_text, True

async def unmute_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.restrict_chat_member(chat_id, user_id, ChatPermissions(
            can_send_media_messages=True,
            can_send_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        ))
    except ChatAdminRequired:
        return "Make sure that you have given me that right"
    except Exception as e:
        return f"Oops!!\n{e}"
    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    return f"{user_mention} was unmuted by {admin_mention}"

@app.on_message(filters.command("ban"))
async def ban_command_handler(client, message):
    await handle_ban_or_mute(client, message, ban_user)

@app.on_message(filters.command("sban"))
async def silent_ban_command_handler(client, message):
    await handle_ban_or_mute(client, message, ban_user, silent=True)

@app.on_message(filters.command("unban"))
async def unban_command_handler(client, message):
    await handle_unban(client, message)

@app.on_message(filters.command("mute"))
async def mute_command_handler(client, message):
    await handle_ban_or_mute(client, message, mute_user)

@app.on_message(filters.command("unmute"))
async def unmute_command_handler(client, message):
    await handle_unmute(client, message)

@app.on_message(filters.command("tmute"))
async def timed_mute_command_handler(client, message):
    await handle_timed_action(client, message, mute_user)

@app.on_message(filters.command("tban"))
async def timed_ban_command_handler(client, message):
    await handle_timed_action(client, message, ban_user)

async def handle_ban_or_mute(client, message, action, silent=False):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)

    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
        else:
            return await message.reply_text("Please reply to a user's message.")

        msg_text, result = await action(user_id, first_name, admin_id, admin_name, chat_id)
        if not silent:
            await message.reply_text(msg_text)
        else:
            await message.delete()  # Delete the command message
    else:
        await message.reply_text("You don't have permission to perform this action.")

async def handle_unban(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)

    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
        else:
            return await message.reply_text("Please reply to a user's message.")

        msg_text = await unban_user(user_id, first_name, admin_id, admin_name, chat_id)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to unban someone.")

async def handle_timed_action(client, message, action):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)

    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
            time = message.text.split(None, 1)[1]

            try:
                time_amount = int(time[:-1])
            except ValueError:
                return await message.reply_text("Wrong format!!\nFormat: `/tmute 2m`")

            mute_duration = None
            if time[-1] == "m":
                mute_duration = datetime.timedelta(minutes=time_amount)
            elif time[-1] == "h":
                mute_duration = datetime.timedelta(hours=time_amount)
            elif time[-1] == "d":
                mute_duration = datetime.timedelta(days=time_amount)
            else:
                return await message.reply_text("Wrong format!!\nFormat:\nm: Minutes\nh: Hours\nd: Days")

            msg_text, _ = await action(user_id, first_name, admin_id, admin_name, chat_id, time=mute_duration)
            await message.reply_text(msg_text)
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message\nFormat: /tmute <username> <time>")
    else:
        await message.reply_text("You don't have permission to perform this action.")
