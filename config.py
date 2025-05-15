import os
import dotenv
from telethon import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.collection import Collection

dotenv.load_dotenv('.env')

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
bot_username = os.environ.get('BOT_USERNAME')
db_url = os.environ.get('MONGO_DB_URL')
database_name = os.environ.get('DATABASE_NAME')
collection_name = os.environ.get('COLLECTION_NAME')
try:
    approved_users = os.environ.get('APPROVED_USERS').split(",")
except:
    approved_users = []
approved_users = list(map(int, approved_users))

temp_client = MongoClient(db_url, tls=True)


settings_col = Collection(temp_client[collection_name], f"{database_name}_Settings")
t = settings_col.find_one({"_id": "time_gap"})
if t == None:
    settings_col.insert_one(
        {
            "_id": "time_gap",
            "gap": 60
        }
    )


client = AsyncIOMotorClient(db_url)

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
