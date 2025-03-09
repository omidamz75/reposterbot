import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'bot.log'

# Scheduling Configuration
DEFAULT_TIMEZONE = 'Asia/Tehran'
POSTING_INTERVAL = int(os.getenv('POSTING_INTERVAL', '3600'))  # Default 1 hour
