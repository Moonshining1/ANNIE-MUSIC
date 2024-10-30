from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.utils.database import add_off, add_on
from ANNIEMUSIC.utils.decorators.language import language
from ANNIEMUSIC.config import LOGGER_ID  # Import LOGGER_ID from config

# Mock function to check if cookies are valid
def are_cookies_valid():
    # Add your actual cookie validation logic here
    return True  # Return False if cookies are expired

# /logger command to enable or disable logging
@app.on_message(filters.command(["logger"]) & SUDOERS)
@language
async def logger_toggle(client, message, _):
    usage = _["log_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await add_on(2)
        await message.reply_text(_["log_2"])
    elif state == "disable":
        await add_off(2)
        await message.reply_text(_["log_3"])
    else:
        await message.reply_text(usage)

# /cookies command to check cookies and notify if expired
@app.on_message(filters.command(["cookies"]) & SUDOERS)
@language
async def logger_cookies(client: Client, message: Message, _):
    if are_cookies_valid():
        await message.reply_document("ANNIEMUSIC/cookies/logs.csv")
        await message.reply_text("Please check the file for cookie choosing logs.")
    else:
        # Notify the logger group about the expired cookies
        await client.send_message(
            LOGGER_ID,
            f"⚠️ Cookies have expired as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}! Please update them."
        )
        await message.reply_text("Cookies have expired. Notified the logger group to update them.")
