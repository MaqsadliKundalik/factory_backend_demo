import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ChatMemberHandler,
    ContextTypes,
    CallbackContext,
    CommandHandler,
)

from data.session.models import TgLocationSessions

class Bot:
    sessions = {}
    def __init__(self):

        self.token = os.getenv("TOKEN")

        self.app = ApplicationBuilder().token(self.token).build()

        self.app.add_handler(CommandHandler("start", self.start))

        self.app.add_handler(MessageHandler(filters.LOCATION, self.get_location))

    def run(self):
        self.app.run_polling()

    async def start(self, update: Update, context: CallbackContext):
        print(update)

        if update.message and update.message.text:
            split_text = update.message.text.split("session")
            if len(split_text) > 1:
                session_id = split_text[1].strip()
                if TgLocationSessions.objects.filter(id=session_id).exists():
                    self.sessions[update.message.from_user.id] = session_id
                    await update.message.reply_text("Lokatsyani yuboring.")
        
    async def get_location(self, update: Update, context: CallbackContext):
        print(update)

        if update.message and update.message.location:
            session_id = self.sessions.get(update.message.from_user.id)
            if session_id:
                TgLocationSessions.objects.filter(id=session_id).update(
                    latitude=update.message.location.latitude,
                    longitude=update.message.location.longitude,
                )
                await update.message.reply_text("Lokatsya qabul qilindi.")
            else:
                await update.message.reply_text("Lokatsya qabul qilinmadi.")
        