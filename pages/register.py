# import streamlit as st
# from app.auth import register_user
# st.set_page_config(page_title="Register - DataWhisper", layout="wide")
# st.title("Register for InsightPulse")
# with st.container():
#     username = st.text_input("Username")
#     email = st.text_input("Email Address")
#     password = st.text_input("Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")
#     if st.button("✨ Register", use_container_width=True):
#         if password != confirm_password:
#             st.error("❌ Passwords don't match")
#         else:
#             success, message = register_user(username, email, password)
#             if success:
#                 st.success(f"✅ {message}")
#                 st.switch_page("pages/login.py")
#             else:
#                 st.error(f"❌ {message}")

import streamlit as st
import re
from app.auth import register_user

st.set_page_config(page_title="Register - InsightPulse", layout="wide")
st.title("📝 Register for InsightPulse")

# --- Password strength functions ---
def get_password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    return score  # Score range: 0–5

def strength_label(score):
    if score <= 2:
        return "Weak", "🔴", 0.3
    elif score == 3 or score == 4:
        return "Moderate", "🟠", 0.6
    else:
        return "Strong", "🟢", 1.0

# --- UI ---
with st.container():
    username = st.text_input("Username")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Email lowercase check
    if email and email != email.lower():
        st.warning("⚠️ Please enter your valid email address")

    # Show password strength
    if password:
        score = get_password_strength(password)
        label, icon, progress = strength_label(score)
        st.write(f"**Password Strength: {icon} {label}**")
        st.progress(progress)

    # Register button
    if st.button("✨ Register", use_container_width=True):
        if email != email.lower():
            st.error("❌ Email must be in lowercase.")
        elif password != confirm_password:
            st.error("❌ Passwords don't match")
        elif get_password_strength(password) <= 2:
            st.error("❌ Password is too weak. Please choose a stronger one.")
        else:
            success, message = register_user(username, email, password)
            if success:
                st.success(f"✅ {message}")
                st.switch_page("pages/login.py")
            else:
                st.error(f"❌ {message}")
