import streamlit as st
import pandas as pd
import requests
import re
import matplotlib.pyplot as plt
from app.database import db, save_chat_message, get_chat_history, clear_chat_history
from app.auth import init_session_state, login_user, logout_user
from streamlit_lottie import st_lottie
from streamlit_extras.colored_header import colored_header

# Page config
st.set_page_config(page_title="💬 InsightPulse", layout="wide")

# Session state init
init_session_state()
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# API setup
UPSTAGE_API_URL = "https://api.upstage.ai/v1/chat/completions"
API_KEY = st.secrets["upstage_api_key"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load Lottie animation
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_animation = load_lottie_url("https://lottie.host/ea3695de-831e-4ac0-b67b-3b6e44b6a144/dWJrYeERa5.json")
import streamlit as st

st.set_page_config(page_title="Welcome to InsightPulse", layout="wide")

# Only show landing if not authenticated
if not st.session_state.get("authenticated", False):

    # 🌈 Gradient background and custom CSS
    st.markdown("""
        <style>
        body {
            background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        .main-title {
            font-size: 3em;
            text-align: center;
            font-weight: bold;
            margin-top: 30px;
            color: #ffffff;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            color: #dddddd;
            margin-bottom: 40px;
        }
        .feature-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(8px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transition: 0.3s;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .feature-box:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: scale(1.02);
        }
        .login-info {
            font-size: 1.1em;
            background: rgba(255, 255, 255, 0.08);
            color: white;
            padding: 1.2em;
            border-radius: 12px;
            text-align: center;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🎯 Title and Subtitle
    st.markdown("<div class='main-title'>Welcome to InsightPulse 💬</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Ask. Analyze. Visualize — All in One Click!</div>", unsafe_allow_html=True)

    # 🚀 Features Section with Glass Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🧠 AI-Powered Queries")
        st.markdown("<div class='feature-box'>Ask questions in plain English — no SQL or Python required!</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 Smart Visualizations")
        st.markdown("<div class='feature-box'>Get auto-generated charts: bar, pie, line, scatter, and more.</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("### 📁 Instant Dataset Upload")
        st.markdown("<div class='feature-box'>Upload your data and explore it interactively in seconds.</div>", unsafe_allow_html=True)

    # 📘 Interactive Guide
    with st.expander("📘 How to Use InsightPulse"):
        st.markdown("""
        **👣 Step-by-step Guide:**
        1. **Login** via the sidebar.
        2. **Upload your CSV or Excel file.**
        3. **Ask questions** like:
            - *"Top 5 products by revenue"*
            - *"Plot sales over time"*
        4. **View charts, tables, and answers** generated automatically.

        💡 Pro Tip: The better your data, the smarter the insights!
        """)

    # 🔐 CTA
    st.markdown("<div class='login-info'>🔒 Please log in using the sidebar to start exploring your data with InsightPulse.</div>", unsafe_allow_html=True)

    # 🛑 Prevent further rendering
    st.stop()
 



# --- LOGGED IN INTERFACE ---
if st.session_state.authenticated:
    if st.sidebar.button("🚪 Logout"):
        logout_user()
        st.session_state.page = "landing"
        st.session_state.authenticated = False
        st.rerun()

    st.title(f"💬 InsightPulse - Welcome, {st.session_state.user['username']}")

    st.sidebar.header("📁 Upload Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        file_id = f"{st.session_state.user['email']}_{uploaded_file.name}"
        st.session_state.current_file = file_id

        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.success(f"✅ Dataset '{uploaded_file.name}' loaded successfully!")

        st.session_state.messages = get_chat_history(file_id) or [
            {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
        ]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("code"):
                    st.markdown("💻 **Generated Code:**")
                    st.code(msg["code"], language="python")
                if msg["role"] == "assistant" and msg.get("result"):
                    st.markdown("📊 **Query Result:**")
                    try:
                        result = pd.read_json(msg["result"]) if isinstance(msg["result"], str) and msg["result"].startswith("{") else msg["result"]
                        st.dataframe(result) if isinstance(result, pd.DataFrame) else st.markdown(result)
                    except Exception as e:
                        st.error(f"⚠️ Error displaying result: {e}")

        # --- USER QUERY ---
        if user_query := st.chat_input("Ask a question about your dataset..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("🔎 Analyzing your query..."):
                    def is_chart_request(query):
                        return any(kw in query.lower() for kw in [
                            "bar chart", "plot", "graph", "pie chart", "visualize", "histogram", "scatter", "line chart"
                        ])

                    def generate_code(query, columns):
                        prompt = (
                            f"You are a Python data analyst. Given a dataset with columns: {columns}, "
                            f"generate {'visualization' if is_chart_request(query) else 'pandas analysis'} code using 'df'. "
                            f"Assign charts to 'fig' and analysis to 'result'. Only return code."
                        )
                        payload = {
                            "model": "solar-1-mini-chat",
                            "messages": [{"role": "system", "content": "You are a helpful data assistant."},
                                         {"role": "user", "content": prompt}],
                            "temperature": 0.3,
                            "max_tokens": 500
                        }
                        response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
                        response.raise_for_status()
                        content = response.json()['choices'][0]['message']['content'].strip()
                        return re.sub(r"```(?:python)?\s*([\s\S]*?)```", r"\1", content)

                    def run_code(code, df):
                        local_vars = {"df": df}
                        try:
                            exec(code, {}, local_vars)
                            return "chart", local_vars["fig"] if "fig" in local_vars else "data", local_vars.get("result")
                        except Exception as e:
                            st.error(f"❌ Execution error: {e}")
                            return None, None

                    code = generate_code(user_query, list(df.columns))
                    result_type, result = run_code(code, df)

                    st.markdown("💻 **Generated Code:**")
                    st.code(code, language="python")
                    if result_type == "chart":
                        st.markdown("📊 **Generated Visualization:**")
                        st.pyplot(result)
                    elif result_type == "data":
                        st.markdown("📊 **Query Result:**")
                        st.dataframe(result if isinstance(result, pd.DataFrame) else str(result))

                    save_chat_message(file_id, "user", user_query)
                    save_chat_message(file_id, "assistant", "✅ Here are the results!", code=code,
                                      result=result.to_json() if isinstance(result, pd.DataFrame) else str(result))
                    st.session_state.messages.append({
                        "role": "assistant", "content": "✅ Here are the results!",
                        "code": code, "result": result.to_json() if isinstance(result, pd.DataFrame) else str(result)
                    })

        if st.sidebar.button("🗑️ Clear Chat History"):
            clear_chat_history(file_id)
            st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Start a new query."}]
            st.rerun()
