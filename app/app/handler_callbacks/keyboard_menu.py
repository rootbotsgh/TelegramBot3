"""
The keyboard menu displayed to users on the app
"""

from telegram import Update
from telegram.ext import ContextTypes

from admin_permission import is_admin

from handler_callbacks.command_handlers import (
start,
tag_all_command,
tag_batch)
from handler_callbacks.other_callbacks import (
    remove_file_prompt,
    remove_subject_prompt)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    contains menu callback logic
    to be used by command_handler
    """
    text = update.message.text.strip()

    if text == "📤 Restart":
        await start(update, context)
    if not is_admin(update.effective_user.id):
        return  # ignore random users
    if text == "📤 Tag files":
        await tag_batch(update, context)
    elif text == "📦 Tag All Queued":
        await tag_all_command(update, context)
    elif text == "🗑 Remove File":
        context.user_data["remove_page"] = 0
        await remove_file_prompt(update, context, page=0)
    elif text == "🧹 Remove Subject":
        await remove_subject_prompt(update, context)
    elif text == "🗑 Remove File":
        await remove_file_prompt(update, context)
    elif text == "🎯 Set Subjects":
        await update.message.reply_text(
            "Send me the subject list separated by spaces.\nExample: `Math | English | Science`",
             parse_mode="Markdown")
        context.user_data["awaiting_subjects"] = True
