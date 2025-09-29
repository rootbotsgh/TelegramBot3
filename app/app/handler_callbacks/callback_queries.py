"""
Contains callbacks called when certain message inputs match a given
string pattern
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Document
from telegram.ext import ContextTypes

from admin_permission import is_admin
from json_config import load_index, save_index
from config import STORAGE_CHAT_ID, DEFAULT_SUBJECTS
from handler_callbacks.keyboard_menu import menu_handler
from handler_callbacks.other_callbacks import complete_tagging, remove_file_prompt


async def remove_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, message_id = query.data.split("|")
    message_id = int(message_id)
    index = load_index()
    new_index = [item for item in index if item["message_id"] != message_id]

    if len(new_index) == len(index):
        await query.edit_message_text("⚠️ File not found.")
        return

    save_index(new_index)
    await query.edit_message_text("✅ File removed from index.")

async def remove_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, new_page = query.data.split("|")
    new_page = int(new_page)

    await query.delete_message()  # remove old page
    await remove_file_prompt(update, context, page=new_page)

async def remove_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, subject = query.data.split("|")
    subjects = context.user_data.get("custom_subjects", [])

    if subject in subjects:
        subjects.remove(subject)
        context.user_data["custom_subjects"] = subjects
        await query.edit_message_text(f"✅ Removed subject: {subject}")
    else:
        await query.edit_message_text("⚠️ Subject not found.")

async def tagall_year_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, year = query.data.split("|")
    context.user_data["tagall_year"] = year

    subjects = context.user_data.get("custom_subjects", DEFAULT_SUBJECTS)
    keyboard = [
        [InlineKeyboardButton(sub, callback_data=f"tagall_subject|{sub}")] for sub in subjects
    ]

    await query.edit_message_text(
        f"📅 Year: {year}\nNow choose a subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def tagall_subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, subject = query.data.split("|")
    year = context.user_data.get("tagall_year", "unspecified")
    batch = context.user_data.get("batch_files", [])

    if not batch:
        await query.edit_message_text("⚠️ No files left to tag.")
        return

    index = load_index()
    count = 0

    for file in batch:
        try:
            msg = await context.bot.send_document(
                chat_id=STORAGE_CHAT_ID,
                document=file["file_id"],
                caption=file["file_name"]
            )
            index.append({
                "year": year,
                "subject": subject,
                "filename": file["file_name"],
                "message_id": msg.message_id,
                "chat_id": STORAGE_CHAT_ID
            })
            count += 1
        except Exception as e:
            print(f"❌ Error tagging file {file['file_name']}: {e}")

    save_index(index)
    context.user_data["batch_files"] = []
    context.user_data["tagging_index"] = 0

    await query.edit_message_text(
        f"✅ Tagged and uploaded {count} files to Year {year}, Subject: {subject}"
        )

###### BOTH ADMIN AND USERS #######

async def year_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        query = update.callback_query
        await query.answer()
        _, year = query.data.split("|")
        context.user_data["current_year"] = year
        subjects = context.user_data.get("custom_subjects", DEFAULT_SUBJECTS)
        keyboard = [
            [InlineKeyboardButton(sub, callback_data=f"subject|{sub}") for sub in subjects[i:i+2]]
            for i in range(0, len(subjects), 2)
        ]
        keyboard.append([InlineKeyboardButton("⏭ Skip", callback_data="skip")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📘 Year: {year}\nChoose a subject:",
            reply_markup=reply_markup
        )
    else:
        query = update.callback_query
        await query.answer()

        _, year = query.data.split("|")
        context.user_data["year"] = year

        # List subjects for selected year
        index = load_index()
        subjects = sorted(list({i["subject"] for i in index if i["year"] == year}))
        keyboard = [[InlineKeyboardButton(s, callback_data=f"subject|{s}")] for s in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"📘 Choose a subject for {year}:", reply_markup=reply_markup)

# When user selects a subject
async def subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        query = update.callback_query
        await query.answer()
        _, subject = query.data.split("|")
        await complete_tagging(update, context, subject)

    else:

        query = update.callback_query
        await query.answer()

        _, subject = query.data.split("|")
        year = context.user_data.get("year")

        if not year:
            await query.edit_message_text("❌ Year not selected. Please restart with /start")
            return

        index = load_index()
        matched = [i for i in index if i["year"] == year and i["subject"] == subject]

        await query.edit_message_text(f"📂 Sending files for {year} - {subject}...")

        for f in matched:
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=f["chat_id"],
                message_id=f["message_id"]
            )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await menu_handler(update, context)
        return

    if context.user_data.get("awaiting_subjects"):
        subjects = update.message.text.strip().split("|")
        context.user_data["custom_subjects"] = subjects
        context.user_data["awaiting_subjects"] = False
        await update.message.reply_text(f"✅ Subjects updated: {', '.join(subjects)}")
        return

    await menu_handler(update, context)  # fallback to menu handler


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    doc: Document = update.message.document
    if "batch_files" not in context.user_data:
        context.user_data["batch_files"] = []

    context.user_data["batch_files"].append({
        "file_id": doc.file_id,
        "file_name": doc.file_name,
        "uploaded_by": update.effective_user.id
    })
    await update.message.reply_text(f"✅ Queued: {doc.file_name}")
