import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now we can import Django models
from telegram_bot.telegram_bot import main

if __name__ == "__main__":
    main()
