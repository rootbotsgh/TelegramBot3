"""
Contains callbacks used directly by markup keyboard in this telegram
bot
"""
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TelegramError

from keyboard_buttons import admin_keyboard, user_keyboard
from admin_permission import is_admin
from json_config import load_index, save_index
from handler_callbacks.keyboard_menu import menu_handler
from handler_callbacks.other_callbacks import (
    next_file, ask_year)


# /start command for both admin and user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "there"

    if is_admin(update.effective_user.id):
        await clean_index(update, context, silent=True)
        await update.message.reply_text(
            "👋 Hello, Admin!, \n 📥 Send me your files.\nWhen done,"\
            " type /tag_batch to begin tagging and uploading.\nUse "\
            "/set_subjects to define your own subject list.",
            reply_markup=admin_keyboard
        )
    else:
        await update.message.reply_text(f"Hello {name}!", reply_markup=user_keyboard)
        years = sorted(list({item["year"] for item in load_index()}))
        keyboard = [[InlineKeyboardButton(y, callback_data=f"year|{y}")] for y in years]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📅 Choose a year:", reply_markup=reply_markup)

#### FOR ADMIN ONLY ###
async def set_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("Usage: Math | English | Science ...")
        return
    context.user_data["custom_subjects"] = context.args
    await update.message.reply_text(f"✅ Subject list updated: {', '.join(context.args)}")

async def tag_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    batch = context.user_data.get("batch_files", [])
    if not batch:
        await update.message.reply_text("⚠️ No files uploaded yet.")
        return

    context.user_data["tagging_index"] = 0
    await ask_year(update, context)

async def clean_index(update: Update, context: ContextTypes.DEFAULT_TYPE, silent=False):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("🧹 Cleaning index...")

    index = load_index()
    cleaned = []
    removed = []

    for entry in index:
        try:
            await context.bot.get_chat(entry["chat_id"])  # Ensure chat exists
            cleaned.append(entry)
        except BadRequest as e:
            if "message to forward not found" in str(e):
                removed.append(entry)
            else:
                print(f"⚠️ Unexpected error: {e}")
                cleaned.append(entry)
        except TelegramError as e:
            print(f"⚠️ Telegram error: {e}")
            cleaned.append(entry)

    save_index(cleaned)

    await update.message.reply_text(
        f"✅ Cleaned index.\n"
        f"Total checked: {len(index)}\n"
        f"Removed: {len(removed)} missing entries"
    )


async def tag_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Not authorized.")
        return

    batch = context.user_data.get("batch_files", [])
    if not batch:
        await update.message.reply_text("⚠️ No files queued for batch tagging.")
        return

    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"tagall_year|{i}")] for i in range(1, 7)
    ]
    await update.message.reply_text(
        "📅 Choose a year for all files:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def skip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏭ File skipped.")
    await next_file(update, context)

#this function is for both admin and user
