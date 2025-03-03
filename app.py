import streamlit as st
import pandas as pd
import requests
import re
from app.database import db, save_chat_message, get_chat_history
from app.auth import init_session_state, login_user, logout_user

# ✅ Set page config at the start
st.set_page_config(page_title="💬 DataWhisper", layout="wide")

# ✅ Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ✅ API Configuration
UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
API_KEY = st.secrets["upstage_api_key"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ✅ Initialize session state
init_session_state()

# ✅ Sidebar for authentication
if st.session_state.authenticated:
    if st.sidebar.button("🚪 Logout"):
        logout_user()
        st.session_state.page = 'landing'
        st.session_state.authenticated = False
        st.rerun()  # ✅ Updated rerun method
else:
    st.sidebar.warning("⚠️ Please login first.")

# ✅ Page Routing
if st.session_state.page == 'landing':
    st.title("🤖 Welcome to DataWhisper")

    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='font-size: 3rem;'>Chat with Your Data Using AI</h1>
        <p style='font-size: 1.2rem; margin: 1rem 0;'>
            Transform your data analysis workflow with natural language queries. 
            Upload your dataset and start asking questions instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()  # ✅ Updated rerun method
    with col2:
        if st.button("✨ Register", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()  # ✅ Updated rerun method

elif st.session_state.page == 'login':
    st.title("🔐 Login to DataWhisper")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("🔓 Login", use_container_width=True):
        if login_user(username, password):
            st.session_state.authenticated = True
            st.session_state.page = 'chat'
            st.rerun()  # ✅ Updated rerun method
        else:
            st.warning("⚠️ Invalid credentials. Please try again.")

elif not st.session_state.authenticated:
    st.warning("⚠️ Please login first.")
    st.session_state.page = 'login'
    st.rerun()

# ✅ Main Chat Page (After Authentication)
if st.session_state.authenticated:
    st.title(f"💬 DataWhisper - Welcome, {st.session_state.user['username']}")

    def load_data(file):
        try:
            if file.name.endswith(".csv"):
                return pd.read_csv(file)
            elif file.name.endswith((".xlsx", ".xls")):
                return pd.read_excel(file)
            else:
                st.error("❌ Unsupported file type! Please upload a CSV or Excel file.")
        except Exception as e:
            st.error(f"🚫 Error loading file: {e}")
        return None

    def generate_code_from_query(query, columns):
        prompt = (
            f"You are a Python data analyst. Given a dataset with columns: {columns}, "
            f"generate a pandas code snippet to answer this query: \"{query}\". "
            f"Use 'df' as the DataFrame and assign the result to a variable named 'result'. "
            "Return only the code without explanations and without any markdown formatting."
        )

        payload = {
            "model": "solar-1-mini-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for Python data analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 300
        }

        try:
            response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            raw_code = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()

            # ✅ Remove triple backticks and 'python' language specifier using regex
            cleaned_code = re.sub(r"```(?:python)?\s*([\s\S]*?)\s*```", r"\1", raw_code).strip()
            return cleaned_code
        except Exception as e:
            st.error(f"❌ Error generating code: {e}")
            return ""

    def execute_generated_code(code, df):
        local_vars = {"df": df}
        try:
            exec(code, {}, local_vars)
            return local_vars.get("result", "⚠️ No 'result' variable found in the generated code.")
        except Exception as e:
            st.error(f"🚫 Error executing code: {e}")
            return None

    # ✅ Sidebar for uploading files
    st.sidebar.header("📁 Upload Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        df = load_data(uploaded_file)

        if df is not None:
            st.success("✅ Dataset loaded successfully!")
            with st.expander("🔎 Preview Dataset"):
                st.dataframe(df.head())

            # ✅ Initialize chat history from MongoDB for the logged-in user
            if "messages" not in st.session_state:
                messages = get_chat_history(st.session_state.user['_id'])
                st.session_state.messages = messages if messages else [
                    {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
                ]
                
                if not messages:
                    save_chat_message(
                        st.session_state.user['_id'],
                        "assistant",
                        "Hi! Upload your dataset and ask me anything about it."
                    )

            # ✅ Display chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg.get("code"):
                        st.markdown("💻 **Generated Code:**")
                        st.code(msg["code"], language="python")
                    if msg.get("result"):
                        st.markdown("📊 **Query Result:**")
                        try:
                            result = eval(msg["result"])
                            if isinstance(result, pd.DataFrame):
                                st.dataframe(result)
                            else:
                                st.markdown(msg["result"])
                        except:
                            st.markdown(msg["result"])

            # ✅ Chat input and processing
            if user_query := st.chat_input("Ask a question about your dataset..."):
                save_chat_message(st.session_state.user['_id'], "user", user_query)
                st.session_state.messages.append({"role": "user", "content": user_query})
                
                with st.chat_message("user"):
                    st.markdown(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("🔎 Analyzing your query..."):
                        code = generate_code_from_query(user_query, list(df.columns))

                        if code:
                            result = execute_generated_code(code, df)
                            
                            st.markdown("💻 **Generated Code:**")
                            st.code(code, language="python")

                            st.markdown("📊 **Query Result:**")
                            if isinstance(result, pd.DataFrame):
                                st.dataframe(result)

                            save_chat_message(st.session_state.user['_id'], "assistant", "✅ Here are the results!", code, str(result))
                        else:
                            save_chat_message(st.session_state.user['_id'], "assistant", "⚠️ Failed to generate code.")

else:
    st.info("☝️ Please login to continue.")
