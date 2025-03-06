# from datetime import datetime
# from app.database import db
# import bcrypt

# class User:
#     def __init__(self, username, email, password):
#         self.username = username
#         self.email = email
#         self.password = self._hash_password(password)
#         self.created_at = datetime.utcnow()

#     @staticmethod
#     def _hash_password(password):
#         salt = bcrypt.gensalt()
#         return bcrypt.hashpw(password.encode('utf-8'), salt)

#     def save(self):
#         user_data = {
#             'username': self.username,
#             'email': self.email,
#             'password': self.password,
#             'created_at': self.created_at
#         }
#         return db.users.insert_one(user_data)

#     @staticmethod
#     def find_by_email(email):
#         return db.users.find_one({'email': email})

#     @staticmethod
#     def verify_password(stored_password, provided_password):
#         return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

#     @staticmethod
#     def find_by_username(username):
#         return db.users.find_one({'username': username})

# class ChatMessage:
#     def __init__(self, user_id, role, content, code=None, result=None):
#         self.user_id = user_id
#         self.role = role
#         self.content = content
#         self.code = code
#         self.result = result
#         self.timestamp = datetime.utcnow()

#     def save(self):
#         message_data = {
#             'user_id': self.user_id,
#             'role': self.role,
#             'content': self.content,
#             'code': self.code,
#             'result': self.result,
#             'timestamp': self.timestamp
#         }
#         return db.chat_messages.insert_one(message_data)

#     @staticmethod
#     def get_user_messages(user_id):
#         return list(db.chat_messages.find(
#             {'user_id': user_id},
#             {'_id': 0}
#         ).sort('timestamp', 1))

#     @staticmethod
#     def clear_user_messages(user_id):
#         return db.chat_messages.delete_many({'user_id': user_id})

from datetime import datetime
from app.database import db
import bcrypt

# ------------------------- User Model -------------------------
class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = self._hash_password(password)
        self.created_at = datetime.utcnow()

    @staticmethod
    def _hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def save(self):
        user_data = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at
        }
        return db.users.insert_one(user_data)

    @staticmethod
    def find_by_email(email):
        return db.users.find_one({'email': email})

    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

    @staticmethod
    def find_by_username(username):
        return db.users.find_one({'username': username})

# ------------------------- Chat Message Model -------------------------
class ChatMessage:
    def __init__(self, user_id, role, content, code=None, result=None):
        self.user_id = user_id
        self.role = role
        self.content = content
        self.code = code
        self.result = result
        self.timestamp = datetime.utcnow()

    def save(self):
        message_data = {
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'code': self.code,
            'result': self.result,
            'timestamp': self.timestamp
        }
        return db.chat_messages.insert_one(message_data)

    @staticmethod
    def get_user_messages(user_id):
        return list(db.chat_messages.find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('timestamp', 1))

    @staticmethod
    def clear_user_messages(user_id):
        return db.chat_messages.delete_many({'user_id': user_id})

# ------------------------- User Dataset Model -------------------------
class UserDataset:
    def __init__(self, email, dataset_name, dataset_path):
        self.email = email
        self.dataset_name = dataset_name
        self.dataset_path = dataset_path
        self.uploaded_at = datetime.utcnow()

    def save(self):
        """Save dataset to MongoDB."""
        dataset_data = {
            'email': self.email,
            'dataset_name': self.dataset_name,
            'dataset_path': self.dataset_path,
            'uploaded_at': self.uploaded_at
        }
        return db.datasets.insert_one(dataset_data)

    @staticmethod
    def get_user_datasets(email):
        """Retrieve all datasets for a given user."""
        return list(db.datasets.find({'email': email}, {'_id': 0}))

    @staticmethod
    def delete_user_dataset(email, dataset_name):
        """Delete a specific dataset for a user."""
        return db.datasets.delete_one({'email': email, 'dataset_name': dataset_name})
