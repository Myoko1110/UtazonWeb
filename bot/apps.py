import threading

from config import settings
from . import client


def ready():
	bot_thread = threading.Thread(target=client.run, args=(settings.DISCORD_BOT_TOKEN,), daemon=True)
	bot_thread.start()
