from django.core.management.base import BaseCommand
from tg_bot import Bot

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Bot Ishga tushdi eeeeeeeuuuuu")
        bot = Bot()
        bot.run()
