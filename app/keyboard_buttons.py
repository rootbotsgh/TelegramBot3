"""
Markup keyboard used by both user and admin to interact with the app
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📤 Restart")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📤 Tag files"), KeyboardButton("📦 Tag All Queued")],
        [KeyboardButton("🎯 Set Subjects"), KeyboardButton("📤 Restart")],
        [KeyboardButton("🧹 Remove Subject"), KeyboardButton("🗑 Remove File")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
