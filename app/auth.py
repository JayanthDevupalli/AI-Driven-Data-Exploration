import streamlit as st
import bcrypt
from app.database import db  # Update import path
from datetime import datetime

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def login_user(email, password):
    if not email or not password:
        return False
        
    user = db.users.find_one({'email': email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        st.session_state.user = user
        st.session_state.authenticated = True
        return True
    return False

def logout_user():
    st.session_state.user = None
    st.session_state.authenticated = False
    if 'messages' in st.session_state:
        del st.session_state.messages

def register_user(username, email, password):
    if not all([username, email, password]):
        return False, "All fields are required"
    
    if db.users.find_one({'email': email}):
        return False, "Email already registered"
    
    if db.users.find_one({'username': username}):
        return False, "Username already taken"
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    }
    
    try:
        db.users.insert_one(user)
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"