from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['chatbot_db']

def save_chat_message(user_id, role, content, code=None, result=None):
    message = {
        'user_id': user_id,
        'role': role,
        'content': content,
        'code': code,
        'result': result,
        'timestamp': datetime.utcnow()
    }
    return db.chat_messages.insert_one(message)

def get_chat_history(user_id):
    return list(db.chat_messages.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('timestamp', 1))

def clear_chat_history(user_id):
    return db.chat_messages.delete_many({'user_id': user_id})