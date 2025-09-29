"""
Responsible for handling the documents in the 
telegram storage channel
"""
from telegram import Update
from telegram.ext import ContextTypes
from json_config import load_index, save_index

# Handler for messages posted in a channel the bot is admin in
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post

    if not msg.document:
        return  # Ignore non-document messages

    # Try to extract caption metadata
    caption = msg.caption or ""
    parts = [p.strip() for p in caption.split("|")]
    metadata = {}
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

    year = metadata.get("year")
    subject = metadata.get("subject")
    filename = msg.document.file_name

    if not year or not subject:
        year = year if year else "unspecified"
        subject = subject if subject else "unspecified"
        return

    index = load_index()
    index.append({
        "year": year,
        "subject": subject,
        "filename": filename,
        "message_id": msg.message_id,
        "chat_id": update.channel_post.chat_id
    })
    save_index(index)

    print(f"✅ Indexed: {filename} ({year} - {subject})")
