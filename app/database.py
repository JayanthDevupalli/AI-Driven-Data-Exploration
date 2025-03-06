from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['chatbot_db']

# ------------------------- Chat Messages -------------------------
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

# ------------------------- User Datasets -------------------------
def save_user_dataset(email, dataset_name, dataset_path):
    """Stores dataset with the user email in MongoDB."""
    dataset = {
        'email': email,
        'dataset_name': dataset_name,
        'dataset_path': dataset_path,
        'uploaded_at': datetime.utcnow()
    }
    return db.datasets.insert_one(dataset)

def get_user_datasets(email):
    """Fetches datasets uploaded by a specific user."""
    return list(db.datasets.find(
        {'email': email},
        {'_id': 0}
    ))

def delete_user_dataset(email, dataset_name):
    """Deletes a dataset belonging to a user."""
    return db.datasets.delete_one({'email': email, 'dataset_name': dataset_name})
