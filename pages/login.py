# import streamlit as st
# from app.auth import login_user

# st.set_page_config(page_title="Login - DataWhisper", layout="wide")
# st.title("Login to DataWhisper")

# with st.container():
#     email = st.text_input("Email Address")
#     password = st.text_input("Password", type="password")
    
#     if st.button("🔐 Login", use_container_width=True):
#         if login_user(email, password):
#             st.success("✅ Login successful!")
#             st.session_state.page = 'main'  # Add this line
#             st.rerun()  # Updated method
#         else:
#             st.error("❌ Invalid credentials")

#     if st.button("← Back to Home"):
#         st.session_state.page = 'landing'
#         st.rerun()  # Updated method


import streamlit as st
from app.auth import login_user

st.set_page_config(page_title="Login - DataWhisper", layout="wide")

# If already logged in, redirect to the main app page
if st.session_state.get("authenticated", False):
    st.switch_page("app.py")  # Directly navigate to the app page

st.title("🔐 Login to DataWhisper")

with st.container():
    email = st.text_input("📧 Email Address")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("🔓 Login", use_container_width=True):
        if login_user(email, password):
            st.success("✅ Login successful!")
            st.session_state.authenticated = True  # Set session state for authentication
            st.switch_page("app.py")  # Redirect user to main app page
        else:
            st.error("❌ Invalid credentials. Please try again.")

    if st.button("← Back to Home"):
        st.session_state.page = "landing"
        st.rerun()
