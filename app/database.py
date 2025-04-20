from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import json

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['chatbot_db']

# ------------------------- Chat Messages -------------------------
def save_chat_message(user_id, role, content, code=None, result=None):
    try:
        message = {
            'user_id': user_id,
            'role': role,
            'content': content,
            'code': code,
            'result': result,
            'timestamp': datetime.utcnow()
        }
        return db.chat_messages.insert_one(message)
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return None

def get_chat_history(user_id):
    try:
        return list(db.chat_messages.find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('timestamp', 1))
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []

def clear_chat_history(user_id):
    try:
        return db.chat_messages.delete_many({'user_id': user_id})
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return None

# ------------------------- User Datasets -------------------------
def save_user_dataset(email, dataset_name, df):
    """Stores dataset with the user email in MongoDB."""
    try:
        # Split dataset into smaller chunks
        chunk_size = 100
        total_chunks = (len(df) + chunk_size - 1) // chunk_size
        
        dataset_chunks = []
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(df))
            chunk = df.iloc[start_idx:end_idx]
            
            chunk_data = {
                'email': email,
                'dataset_name': dataset_name,
                'chunk_index': i,
                'total_chunks': total_chunks,
                'data': json.loads(chunk.to_json(orient='records')),
                'uploaded_at': datetime.utcnow()
            }
            dataset_chunks.append(chunk_data)
        
        # Store all chunks
        db.dataset_chunks.insert_many(dataset_chunks)
        
        # Store dataset metadata
        dataset_meta = {
            'email': email,
            'dataset_name': dataset_name,
            'total_rows': len(df),
            'columns': list(df.columns),
            'uploaded_at': datetime.utcnow()
        }
        return db.datasets.insert_one(dataset_meta)
    except Exception as e:
        print(f"Error saving dataset: {e}")
        return None

def get_user_datasets(email):
    """Fetches datasets metadata uploaded by a specific user."""
    try:
        return list(db.datasets.find(
            {'email': email},
            {'_id': 0}
        ))
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return []

def get_user_dataset(email, dataset_name):
    """Retrieves complete dataset by reconstructing chunks."""
    try:
        chunks = list(db.dataset_chunks.find(
            {'email': email, 'dataset_name': dataset_name}
        ).sort('chunk_index', 1))
        
        if not chunks:
            return None
            
        all_data = []
        for chunk in chunks:
            all_data.extend(chunk['data'])
            
        return pd.DataFrame(all_data)
    except Exception as e:
        print(f"Error retrieving dataset: {e}")
        return None

def delete_user_dataset(email, dataset_name):
    """Deletes a dataset and its chunks."""
    try:
        # Delete all chunks
        db.dataset_chunks.delete_many({'email': email, 'dataset_name': dataset_name})
        # Delete metadata
        return db.datasets.delete_one({'email': email, 'dataset_name': dataset_name})
    except Exception as e:
        print(f"Error deleting dataset: {e}")
        return None
