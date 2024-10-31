from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, Message
import config
import asyncio
from ANNIEMUSIC import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_11"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="🔎 How to use? Command Menu", callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(text="🎄 Update 🎄", url="https://t.me/kittyxupdates"),
            InlineKeyboardButton(text="📨 Support", url="https://t.me/grandxmasti"),
        ],
        [
            InlineKeyboardButton(
                text="+ Add me to your clan darlo +",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="❄ Owner ❄", url=f"https://t.me/about_ur_moonshining/5"),
            InlineKeyboardButton(text="💡 Git Repo", url="https://github.com/moonshining1/anniemusic"),
        ],
    ]
    return buttons


def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="+ Add me to your clan darlo +",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="⭐ About me⭐", callback_data="about"),
            InlineKeyboardButton(text="✨ Help ✨", callback_data="feature"),
        ],
        [
            InlineKeyboardButton(text="❄ Owner ❄", callback_data="developer"),
            InlineKeyboardButton(text="🎄 Update 🎄", url="https://t.me/kittyxupdates"),
        ],
    ]
    return buttons
    
