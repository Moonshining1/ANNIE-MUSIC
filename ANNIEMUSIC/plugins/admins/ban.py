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

async def kick_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.kick_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Ensure the bot has admin rights", False
    except UserAdminInvalid:
        return "Cannot kick an admin!", False
    except Exception as e:
        return f"Error:\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    return f"{user_mention} was kicked by {admin_mention}", True

async def ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None):
    try:
        await app.ban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Ensure the bot has admin rights", False
    except UserAdminInvalid:
        return "Cannot ban an admin!", False
    except Exception as e:
        return f"Error:\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was banned by {admin_mention}\n"
    if reason:
        msg_text += f"Reason: `{reason}`"
    return msg_text, True

async def mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None, time=None):
    try:
        mute_end_time = datetime.datetime.now() + time if time else None
        await app.restrict_chat_member(chat_id, user_id, ChatPermissions(), mute_end_time)
    except ChatAdminRequired:
        return "Ensure the bot has admin rights", False
    except UserAdminInvalid:
        return "Cannot mute an admin!", False
    except Exception as e:
        return f"Error:\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was muted by {admin_mention}\n"
    if reason:
        msg_text += f"Reason: `{reason}`"
    return msg_text, True

async def unban_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.unban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Ensure the bot has admin rights"
    except Exception as e:
        return f"Error:\n{e}"
    return f"{mention(user_id, first_name)} was unbanned by {mention(admin_id, admin_name)}"

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
        return "Ensure the bot has admin rights"
    except Exception as e:
        return f"Error:\n{e}"
    return f"{mention(user_id, first_name)} was unmuted by {mention(admin_id, admin_name)}"

@app.on_message(filters.command(["kick", "kickme", "ban", "sban", "unban", "mute", "unmute", "tmute", "tban"]))
async def handle_action(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await message.chat.get_member(admin_id)

    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or not member.privileges.can_restrict_members:
        return await message.reply_text("You don't have permission to perform this action.")

    command = message.text.split()[0][1:]  # Get the command
    user = message.reply_to_message.from_user if message.reply_to_message else None
    user_id = user.id if user else None
    first_name = user.first_name if user else None

    if not user:
        return await message.reply_text("Reply to a user to apply this action.")

    if command == "kick":
        msg_text, _ = await kick_user(user_id, first_name, admin_id, admin_name, chat_id)
    elif command == "kickme":
        msg_text, _ = await kick_user(admin_id, admin_name, admin_id, admin_name, chat_id)
    elif command in ["ban", "sban"]:
        reason = message.text.split(None, 2)[2] if len(message.text.split()) > 2 else None
        msg_text, _ = await ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason)
        if command == "sban":
            await message.delete()
            return
    elif command == "unban":
        msg_text = await unban_user(user_id, first_name, admin_id, admin_name, chat_id)
    elif command == "mute":
        msg_text, _ = await mute_user(user_id, first_name, admin_id, admin_name, chat_id)
    elif command == "unmute":
        msg_text = await unmute_user(user_id, first_name, admin_id, admin_name, chat_id)
    elif command in ["tmute", "tban"]:
        time_text = message.text.split()[1] if len(message.text.split()) > 1 else None
        if not time_text or not any(time_text.endswith(unit) for unit in ["m", "h", "d"]):
            return await message.reply_text("Invalid format! Use `/tmute <time>` where time is in m, h, or d.")
        
        time_amount = int(time_text[:-1])
        time_delta = {"m": "minutes", "h": "hours", "d": "days"}.get(time_text[-1])
        duration = datetime.timedelta(**{time_delta: time_amount})

        if command == "tmute":
            msg_text, _ = await mute_user(user_id, first_name, admin_id, admin_name, chat_id, time=duration)
        else:
            msg_text, _ = await ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None)

    await message.reply_text(msg_text)
