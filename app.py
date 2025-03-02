import streamlit as st
import pandas as pd
import requests
import re

UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"  # Replace with actual Upstage endpoint
API_KEY = st.secrets["upstage_api_key"]  # Use Streamlit's secrets management for API key storage

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

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

st.set_page_config(page_title="💬 DataWhisper", layout="wide")
st.title("💬 DataWhisper - Chat with Your Dataset")

# Sidebar for uploading files
st.sidebar.header("📁 Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:
        st.success("✅ Dataset loaded successfully!")
        with st.expander("🔎 Preview Dataset"):
            st.dataframe(df.head())

        # Initialize chat history if not present
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
            ]

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input field
        user_query = st.chat_input("Ask a question about your dataset...")

        if user_query:
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
                            reply = "✅ Here are the results from your query!"
                        else:
                            st.markdown(result)
                            reply = "⚠️ Unable to retrieve a valid result."
                    else:
                        reply = "⚠️ Failed to generate code from your query. Please try again."

                st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("☝️ Please upload a dataset from the sidebar to get started.")