import streamlit as st
from app.auth import register_user

st.set_page_config(page_title="Register - DataWhisper", layout="wide")
st.title("Register for DataWhisper")

with st.container():
    username = st.text_input("Username")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("✨ Register", use_container_width=True):
        if password != confirm_password:
            st.error("❌ Passwords don't match")
        else:
            success, message = register_user(username, email, password)
            if success:
                st.success(f"✅ {message}")
                st.switch_page("pages/login.py")
            else:
                st.error(f"❌ {message}")