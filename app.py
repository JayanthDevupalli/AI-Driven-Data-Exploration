import streamlit as st
import pandas as pd
import requests
import re
import json
import matplotlib.pyplot as plt
import seaborn as sns
from app.database import db, save_chat_message, get_chat_history, clear_chat_history
from app.auth import init_session_state, login_user, logout_user

# ✅ Set page config
st.set_page_config(page_title="💬 DataWhisper", layout="wide")

# ✅ Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
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
        st.session_state.page = "landing"
        st.session_state.authenticated = False
        st.rerun()
else:
    st.title("📊 Welcome to DataWhisper - Your AI-Driven Data Assistant")

    st.markdown("""
    ### 👋 What is DataWhisper?
    DataWhisper is an AI-powered tool designed to help you analyze and visualize your dataset effortlessly.  
    Simply upload a dataset, ask questions in natural language, and get instant insights!

    ### 🚀 How to Use DataWhisper:
    1. **Login** to access the platform.
    2. **Upload a CSV or Excel file** using the sidebar.
    3. **Ask questions** about your dataset in the chat.
    4. Get **instant results** with data tables and visualizations!

    ### 💡 Example Queries:
    - *"Show me the top 10 highest sales."*
    - *"Plot a bar chart of sales by region."*
    - *"Find the average price for each product category."*

    🔐 **Please log in to get started.**
    """)

    st.stop()


# ✅ Function to detect if query requires a chart
def is_chart_request(query):
    chart_keywords = ["bar chart", "plot", "graph", "visualize", "histogram", "scatter plot", "line chart"]
    return any(keyword in query.lower() for keyword in chart_keywords)

# ✅ Generate code from query
def generate_code_from_query(query, columns):
    if is_chart_request(query):
        prompt = (
            f"You are a Python data analyst. Given a dataset with columns: {columns}, "
            f"generate a pandas and matplotlib/seaborn code snippet to visualize this query: \"{query}\". "
            "Use 'df' as the DataFrame and return only the code without explanations. "
            "Ensure the visualization is created correctly and does not contain syntax errors. "
            "Assign the figure to a variable named 'fig'."
        )
    else:
        prompt = (
            f"You are a Python data analyst. Given a dataset with columns: {columns}, "
            f"generate a pandas code snippet to answer this query: \"{query}\". "
            "Use 'df' as the DataFrame and assign the result to a variable named 'result'. "
            "Return only the code without explanations."
        )

    payload = {
        "model": "solar-1-mini-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for Python data analysis."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        raw_code = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        cleaned_code = re.sub(r"```(?:python)?\s*([\s\S]*?)\s*```", r"\1", raw_code).strip()
        return cleaned_code
    except Exception as e:
        st.error(f"❌ Error generating code: {e}")
        return ""

# ✅ Execute generated code
def execute_generated_code(code, df):
    local_vars = {"df": df}
    try:
        exec(code, {}, local_vars)
        if "fig" in local_vars and isinstance(local_vars["fig"], plt.Figure):
            return "chart", local_vars["fig"]
        return "data", local_vars.get("result", "⚠️ No 'result' variable found.")
    except Exception as e:
        st.error(f"🚫 Error executing code: {e}")
        return None, None

# ✅ Main Chat Page
if st.session_state.authenticated:
    st.title(f"💬 DataWhisper - Welcome, {st.session_state.user['username']}")

    st.sidebar.header("📁 Upload Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        file_id = uploaded_file.name  # Using file name as a unique identifier
        st.session_state.current_file = file_id

        # Load dataset
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.success(f"✅ Dataset '{file_id}' loaded successfully!")

        # ✅ Fetch chat history from database (restore both user + assistant messages)
        st.session_state.messages = get_chat_history(st.session_state.user["email"])

        if not st.session_state.messages:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
            ]

        # ✅ Display chat history properly
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and msg.get("code"):
                    st.markdown("💻 **Generated Code:**")
                    st.code(msg["code"], language="python")

                if msg["role"] == "assistant" and msg.get("result"):
                    st.markdown("📊 **Query Result:**")
                    try:
                        if isinstance(msg["result"], str) and msg["result"].startswith("{"):
                            result = pd.read_json(msg["result"])
                            st.dataframe(result)
                        else:
                            st.markdown(msg["result"])
                    except Exception as e:
                        st.error(f"⚠️ Error displaying result: {e}")

        # ✅ Handle user input
        if user_query := st.chat_input("Ask a question about your dataset..."):
            st.session_state.messages.append({"role": "user", "content": user_query})

            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("🔎 Analyzing your query..."):
                    code = generate_code_from_query(user_query, list(df.columns))

                    if code:
                        result_type, result = execute_generated_code(code, df)
                        st.markdown("💻 **Generated Code:**")
                        st.code(code, language="python")

                        if result_type == "chart":
                            st.markdown("📊 **Generated Visualization:**")
                            st.pyplot(result)
                        else:
                            st.markdown("📊 **Query Result:**")
                            if isinstance(result, pd.DataFrame):
                                st.dataframe(result)
                            else:
                                st.markdown(result)

                        # ✅ Save chat history (User + Assistant)
                        save_chat_message(st.session_state.user["email"], "user", user_query)
                        save_chat_message(
                            st.session_state.user["email"], "assistant", "✅ Here are the results!", 
                            code=code, 
                            result=result.to_json() if isinstance(result, pd.DataFrame) else str(result)
                        )

                        st.session_state.messages.append(
                            {"role": "assistant", "content": "✅ Here are the results!", "code": code, 
                             "result": result.to_json() if isinstance(result, pd.DataFrame) else str(result)}
                        )

                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Failed to generate code."})

        # ✅ Button to clear chat history
        if st.sidebar.button("🗑️ Clear Chat History"):
            clear_chat_history(st.session_state.user["email"])
            st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Start a new query."}]
            st.rerun()

else:
    st.info("☝️ Please login to continue.")
