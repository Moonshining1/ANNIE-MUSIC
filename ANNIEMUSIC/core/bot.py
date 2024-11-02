from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from ..logging import LOGGER


class MOON(Client):
    def __init__(self):
        LOGGER(__name__).info("Annie is on the way...")
        super().__init__(
            name="𝐀𝐍𝐍𝐈𝐄 𝐗 𝐌𝐔𝐒𝐈𝐂",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        # Creating a single button layout
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "+ Add me to your clan darlo +", url=f"https://t.me/{self.username}?startgroup=true"
                    )
                ]
            ]
        )

        # Specify the image path or URL
        image_path = "https://envs.sh/_kf.png"  # Replace with actual path or URL of the image

        try:
            await self.send_photo(
                chat_id=config.LOGGER_ID,
                photo=image_path,
                caption=(
                    f"✨ <b>{self.mention}</b> is alive 🖤!\n\n"
                    f"<b>System Stats:</b>\n"
                    f"✨  Uptime: 3.11.5\n"
                    f"☁️  Ram: 13.15\n"
                    f"❄️  Cpu: 1.34.0\n"
                    f"🔮  Disk: 2.0.106\n\n"
                    f"<i>Made {self.mention} with love by ᴅᴇᴠᴇʟᴏᴘᴇʀs✨🥀</i>"
                ),
                reply_markup=keyboard  # Adding the single button
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot has failed to access the log group/channel. Make sure that you have added your bot to your log group/channel."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}."
            )
            exit()

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error(
                "Please promote your bot as an admin in your log group/channel."
            )
            exit()
        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
