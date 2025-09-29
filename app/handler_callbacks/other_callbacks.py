"""
Contains all other Callbacks used by other functions and not directly by button
or other user inputs
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import STORAGE_CHAT_ID, DEFAULT_SUBJECTS
from json_config import load_index, save_index

async def ask_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["tagging_index"]
    batch = context.user_data["batch_files"]
    current = batch[index]

    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"year|{i}") for i in range(1, 7)],
        [InlineKeyboardButton("⏭ Skip", callback_data="skip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📁 *{current['file_name']}*\nChoose a year:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def complete_tagging(update: Update, context: ContextTypes.DEFAULT_TYPE, subject):
    year = context.user_data.get("current_year", "unspecified")
    i = context.user_data["tagging_index"]
    batch = context.user_data["batch_files"]
    file = batch[i]

    msg = await context.bot.send_document(
        chat_id=STORAGE_CHAT_ID,
        document=file["file_id"],
        caption=file["file_name"]
    )

    index = load_index()
    index.append({
        "year": year,
        "subject": subject,
        "filename": file["file_name"],
        "message_id": msg.message_id,
        "chat_id": STORAGE_CHAT_ID
    })
    save_index(index)

    await update.callback_query.edit_message_text(
        f"✅ Saved '{file['file_name']}' to {year} - {subject}"
    )

    await next_file(update, context)

async def next_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tagging_index"] += 1
    batch = context.user_data["batch_files"]
    if context.user_data["tagging_index"] < len(batch):
        await ask_year(update, context)
    else:
        context.user_data["batch_files"] = []
        context.user_data["tagging_index"] = 0
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🎉 All files processed."
        )

async def remove_file_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    index = load_index()
    if not index:
        await update.message.reply_text("📁 No files to remove.")
        return

    page_size = 20
    total_pages = (len(index) - 1) // page_size + 1
    start = len(index) - (page + 1) * page_size
    end = len(index) - page * page_size

    page_items = index[max(start, 0):end]
    page_items.reverse()  # newest first

    keyboard = [
        [InlineKeyboardButton(item["filename"], callback_data=f"remove_file|{item['message_id']}")]
        for item in page_items
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅ Prev", callback_data=f"remove_nav|{page - 1}"))
    if (page + 1) * page_size < len(index):
        nav_buttons.append(InlineKeyboardButton("➡ Next", callback_data=f"remove_nav|{page + 1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    await update.message.reply_text(
        f"🗑 Select a file to remove from index (Page {page + 1}/{total_pages}):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def remove_subject_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subjects = context.user_data.get("custom_subjects", DEFAULT_SUBJECTS)
    if not subjects:
        await update.message.reply_text("⚠️ No subjects defined.")
        return

    keyboard = [
        [InlineKeyboardButton(sub, callback_data=f"remove_subject|{sub}")] for sub in subjects
    ]
    await update.message.reply_text(
        "🧹 Select a subject to remove:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
