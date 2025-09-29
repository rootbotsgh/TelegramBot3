"""
I don't feel like writing a docstring
This is obviously a telegram bot
It's used to serve files stored by admins to users
It uses a private telegram channel as a database
"""

from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)

from config import BOT_TOKEN
from channels_rw import handle_channel_post
from handler_callbacks import (
    start, tag_batch, set_subjects, tag_all_command,
    clean_index, handle_text,
    handle_document, subject_selected, year_selected,
    skip_file, tagall_subject_selected, tagall_year_selected,
    remove_subject_callback, remove_file_callback, remove_nav_callback
)


def main():
    """
    Initializing app and all app handlers
    """
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    #admin commands
    app.add_handler(CommandHandler("tag_batch", tag_batch))
    app.add_handler(CommandHandler("set_subjects", set_subjects))
    app.add_handler(CommandHandler("tag_all", tag_all_command))
    app.add_handler(CommandHandler("clean_index", clean_index))

    #add document to channel/database
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS &
     filters.Document.ALL,
     handle_channel_post))
    # Used by admin to save details of the documents like subject and year etc
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

##--- Callback Queries ---- ##
    #both admin and user query handler
    app.add_handler(CallbackQueryHandler(subject_selected, pattern="^subject\\|"))
    app.add_handler(CallbackQueryHandler(year_selected, pattern="^year\\|"))
    #solely storage channel/admin message query handlers
    app.add_handler(CallbackQueryHandler(skip_file, pattern="^skip$"))
    app.add_handler(CallbackQueryHandler(tagall_year_selected, pattern="^tagall_year\\|"))
    app.add_handler(CallbackQueryHandler(tagall_subject_selected, pattern="^tagall_subject\\|"))
    app.add_handler(CallbackQueryHandler(remove_subject_callback, pattern="^remove_subject\\|"))
    app.add_handler(CallbackQueryHandler(remove_file_callback, pattern="^remove_file\\|"))
    app.add_handler(CallbackQueryHandler(remove_nav_callback, pattern="^remove_nav\\|"))


    print("📡 Bot is watching channel posts...")
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
