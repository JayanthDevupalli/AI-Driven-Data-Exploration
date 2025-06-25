#1 Big issue with the codeeeee

# import streamlit as st
# import pandas as pd
# import requests
# import re
# import json
# import matplotlib.pyplot as plt
# import seaborn as sns
# from app.database import db, save_chat_message, get_chat_history, clear_chat_history
# from app.auth import init_session_state, login_user, logout_user

# # ✅ Set page config
# st.set_page_config(page_title="💬 InsightPulse", layout="wide")

# # ✅ Initialize session state
# if "page" not in st.session_state:
#     st.session_state.page = "landing"
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# # ✅ API Configuration
# UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
# API_KEY = st.secrets["upstage_api_key"]

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# # ✅ Initialize session state
# init_session_state()

# # ✅ Sidebar for authentication
# if st.session_state.authenticated:
#     if st.sidebar.button("🚪 Logout"):
#         logout_user()
#         st.session_state.page = "landing"
#         st.session_state.authenticated = False
#         st.rerun()
# else:
#     st.title("📊 Welcome to InsightPulse - Your AI-Driven Data Assistant")

#     st.markdown("""
#     ### 👋 What is InsightPulse?
#     InsightPulse is an AI-powered tool designed to help you analyze and visualize your dataset effortlessly.  
#     Simply upload a dataset, ask questions in natural language, and get instant insights!

#     ### 🚀 How to Use InsightPulse:
#     1. **Login** to access the platform.
#     2. **Upload a CSV or Excel file** using the sidebar.
#     3. **Ask questions** about your dataset in the chat.
#     4. Get **instant results** with data tables and visualizations!

#     ### 💡 Example Queries:
#     - *"Show me the top 10 highest sales."*
#     - *"Plot a bar chart of sales by region."*
#     - *"Find the average price for each product category."*

#     🔐 **Please log in to get started.**
#     """)

#     st.stop()


# # ✅ Function to detect if query requires a chart
# def is_chart_request(query):
#     chart_keywords = ["bar chart", "plot", "graph", "visualize", "histogram", "scatter plot", "line chart"]
#     return any(keyword in query.lower() for keyword in chart_keywords)

# # ✅ Generate code from query
# def generate_code_from_query(query, columns):
#     if is_chart_request(query):
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas and matplotlib/seaborn code snippet to visualize this query: \"{query}\". "
#             "Use 'df' as the DataFrame and return only the code without explanations. "
#             "Ensure the visualization is created correctly and does not contain syntax errors. "
#             "Assign the figure to a variable named 'fig'."
#         )
#     else:
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas code snippet to answer this query: \"{query}\". "
#             "Use 'df' as the DataFrame and assign the result to a variable named 'result'. "
#             "Return only the code without explanations."
#         )

#     payload = {
#         "model": "solar-1-mini-chat",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant for Python data analysis."},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.3,
#         "max_tokens": 500
#     }

#     try:
#         response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         raw_code = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
#         cleaned_code = re.sub(r"```(?:python)?\s*([\s\S]*?)\s*```", r"\1", raw_code).strip()
#         return cleaned_code
#     except Exception as e:
#         st.error(f"❌ Error generating code: {e}")
#         return ""

# # ✅ Execute generated code
# def execute_generated_code(code, df):
#     local_vars = {"df": df}
#     try:
#         exec(code, {}, local_vars)
#         if "fig" in local_vars and isinstance(local_vars["fig"], plt.Figure):
#             return "chart", local_vars["fig"]
#         return "data", local_vars.get("result", "⚠️ No 'result' variable found.")
#     except Exception as e:
#         st.error(f"🚫 Error executing code: {e}")
#         return None, None

# # ✅ Main Chat Page
# if st.session_state.authenticated:
#     st.title(f"💬 InsightPulse - Welcome, {st.session_state.user['username']}")

#     st.sidebar.header("📁 Upload Dataset")
#     uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

#     if uploaded_file:
#         file_id = uploaded_file.name  # Using file name as a unique identifier
#         st.session_state.current_file = file_id

#         # Load dataset
#         df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
#         st.success(f"✅ Dataset '{file_id}' loaded successfully!")

#         # ✅ Fetch chat history from database (restore both user + assistant messages)
#         st.session_state.messages = get_chat_history(st.session_state.user["email"])

#         if not st.session_state.messages:
#             st.session_state.messages = [
#                 {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
#             ]

#         # ✅ Display chat history properly
#         for msg in st.session_state.messages:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])

#                 if msg["role"] == "assistant" and msg.get("code"):
#                     st.markdown("💻 **Generated Code:**")
#                     st.code(msg["code"], language="python")

#                 if msg["role"] == "assistant" and msg.get("result"):
#                     st.markdown("📊 **Query Result:**")
#                     try:
#                         if isinstance(msg["result"], str) and msg["result"].startswith("{"):
#                             result = pd.read_json(msg["result"])
#                             st.dataframe(result)
#                         else:
#                             st.markdown(msg["result"])
#                     except Exception as e:
#                         st.error(f"⚠️ Error displaying result: {e}")

#         # ✅ Handle user input
#         if user_query := st.chat_input("Ask a question about your dataset..."):
#             st.session_state.messages.append({"role": "user", "content": user_query})

#             with st.chat_message("user"):
#                 st.markdown(user_query)

#             with st.chat_message("assistant"):
#                 with st.spinner("🔎 Analyzing your query..."):
#                     code = generate_code_from_query(user_query, list(df.columns))

#                     if code:
#                         result_type, result = execute_generated_code(code, df)
#                         st.markdown("💻 **Generated Code:**")
#                         st.code(code, language="python")

#                         if result_type == "chart":
#                             st.markdown("📊 **Generated Visualization:**")
#                             st.pyplot(result)
#                         else:
#                             st.markdown("📊 **Query Result:**")
#                             if isinstance(result, pd.DataFrame):
#                                 st.dataframe(result)
#                             else:
#                                 st.markdown(result)

#                         # ✅ Save chat history (User + Assistant)
#                         save_chat_message(st.session_state.user["email"], "user", user_query)
#                         save_chat_message(
#                             st.session_state.user["email"], "assistant", "✅ Here are the results!", 
#                             code=code, 
#                             result=result.to_json() if isinstance(result, pd.DataFrame) else str(result)
#                         )

#                         st.session_state.messages.append(
#                             {"role": "assistant", "content": "✅ Here are the results!", "code": code, 
#                              "result": result.to_json() if isinstance(result, pd.DataFrame) else str(result)}
#                         )

#                     else:
#                         st.session_state.messages.append({"role": "assistant", "content": "⚠️ Failed to generate code."})

#         # ✅ Button to clear chat history
#         if st.sidebar.button("🗑️ Clear Chat History"):
#             clear_chat_history(st.session_state.user["email"])
#             st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Start a new query."}]
#             st.rerun()

# else:
#     st.info("☝️ Please login to continue.")



# 2  MAIN Current Update without any JSON FORMAT Error
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
st.set_page_config(page_title="💬 InsightPulse", layout="wide")

# ✅ Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ✅ API Configuration
UPSTAGE_API_URL = "https://api.upstage.ai/v1/chat/completions"
# UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
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
        
if not st.session_state.get("authenticated", False):
    # 🌈 Custom CSS for styling
    st.markdown("""
        <style>
            .main-title {
                font-size: 3em;
                text-align: center;
                font-weight: bold;
                margin-top: 30px;
                color: white;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                color: #cccccc;
                margin-bottom: 50px;
            }
            .feature-box {
                padding: 20px;
                background: #1f1f2e;
                border-radius: 12px;
                box-shadow: 0 0 12px rgba(0,0,0,0.2);
                margin: 10px;
            }
            .login-info {
                font-size: 1.1em;
                background: #163555;
                color: white;
                padding: 1em;
                border-radius: 10px;
                text-align: center;
                margin-top: 40px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🎯 Hero Section
    st.markdown("<div class='main-title'>Welcome to InsightPulse 💬</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your AI-Powered Data Assistant to Analyze, Visualize, and Understand Your Data Effortlessly</div>", unsafe_allow_html=True)

    # 🧠 Features Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🔍 Natural Language")
        st.markdown("<div class='feature-box'>Ask questions like <i>“Top 10 products by sales”</i> using plain English. No code needed.</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("#### 📊 Instant Charts")
        st.markdown("<div class='feature-box'>Get auto-generated bar, line, pie, and scatter plots based on your questions.</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("#### ⚡ Fast Insights")
        st.markdown("<div class='feature-box'>See data summaries, trends, and tables instantly from your uploaded datasets.</div>", unsafe_allow_html=True)

    # 📘 Expandable Instructions
    with st.expander("📘 How to Use InsightPulse"):
        st.markdown("""
        **Step-by-step:**
        1. **Log in** using the sidebar.
        2. **Upload your dataset** (CSV or Excel).
        3. **Ask questions** like:
            - "Show sales by region"
            - "Top 5 profitable products"
        4. **See instant results** as visual charts or tables.

        ⚠️ Works best with clean, structured datasets (CSV/XLSX).
        """)

    # 🔐 Login Info
    st.markdown("<div class='login-info'>🔒 Please log in using the sidebar to begin exploring your data.</div>", unsafe_allow_html=True)

    st.stop()


# ✅ Function to detect if query requires a chart
def is_chart_request(query):
    chart_keywords = ["bar chart", "plot", "graph","pie chart", "visualize", "histogram", "scatter plot", "line chart"]
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
    st.title(f"💬 InsightPulse - Welcome, {st.session_state.user['username']}")

    st.sidebar.header("📁 Upload Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        file_id = f"{st.session_state.user['email']}_{uploaded_file.name}"  # Unique ID for user + dataset
        st.session_state.current_file = file_id

        # Load dataset
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.success(f"✅ Dataset '{uploaded_file.name}' loaded successfully!")

        # ✅ Fetch chat history per user + dataset
        st.session_state.messages = get_chat_history(file_id)

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
                        save_chat_message(file_id, "user", user_query)
                        save_chat_message(
                            file_id, "assistant", "✅ Here are the results!", 
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
            clear_chat_history(file_id)
            st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Start a new query."}]
            st.rerun()

else:
    st.info("☝️ Please login to continue.")


#4 This is Another layout with new logins...  issue is retriving the tables from DB Issued
# import streamlit as st
# import pandas as pd
# import requests
# import re
# import json
# import matplotlib.pyplot as plt
# import seaborn as sns
# # Assuming these are correctly implemented and accessible in app/
# from app.database import db, save_chat_message, get_chat_history, clear_chat_history
# from app.auth import init_session_state, login_user, logout_user # Assuming register_user might be here too

# # ✅ Set page config
# st.set_page_config(page_title="💬 InsightPulse", layout="wide")

# # ✅ Initialize session state for overall page control
# if "page" not in st.session_state:
#     st.session_state.page = "landing" # 'landing', 'login', 'register', 'chat'
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False
# if "user" not in st.session_state: # To store user details after login
#     st.session_state.user = None

# # Initialize auth session state variables (e.g., username, email)
# init_session_state()

# # ✅ API Configuration (kept as is)
# UPSTAGE_API_URL = "https://api.upstage.ai/v1/chat/completions"
# API_KEY = st.secrets["upstage_api_key"]

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# # ✅ Function to detect if query requires a chart (kept as is)
# def is_chart_request(query):
#     chart_keywords = ["bar chart", "plot", "graph","pie chart", "visualize", "histogram", "scatter plot", "line chart"]
#     return any(keyword in query.lower() for keyword in chart_keywords)

# # ✅ Generate code from query (kept as is)
# def generate_code_from_query(query, columns):
#     if is_chart_request(query):
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas and matplotlib/seaborn code snippet to visualize this query: \"{query}\". "
#             "Use 'df' as the DataFrame and return only the code without explanations. "
#             "Ensure the visualization is created correctly and does not contain syntax errors. "
#             "Assign the figure to a variable named 'fig'."
#         )
#     else:
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas code snippet to answer this query: \"{query}\". "
#             "Use 'df' as the DataFrame and assign the result to a variable named 'result'. "
#             "Return only the code without explanations."
#         )

#     payload = {
#         "model": "solar-1-mini-chat",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant for Python data analysis."},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.3,
#         "max_tokens": 500
#     }

#     try:
#         response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         raw_code = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
#         cleaned_code = re.sub(r"```(?:python)?\s*([\s\S]*?)\s*```", r"\1", raw_code).strip()
#         return cleaned_code
#     except Exception as e:
#         st.error(f"❌ Error generating code: {e}")
#         return ""

# # ✅ Execute generated code (kept as is)
# def execute_generated_code(code, df):
#     local_vars = {"df": df}
#     try:
#         # Pass globals() to exec for matplotlib/seaborn to work correctly in the executed code
#         exec(code, globals(), local_vars)
#         if "fig" in local_vars and isinstance(local_vars["fig"], plt.Figure):
#             return "chart", local_vars["fig"]
#         return "data", local_vars.get("result", "⚠️ No 'result' variable found.")
#     except Exception as e:
#         st.error(f"🚫 Error executing code: {e}")
#         return None, None

# # --- UI Functions for Page Routing ---

# def landing_page():
#     st.title("📊 Welcome to InsightPulse - Your AI-Driven Data Assistant")
#     st.markdown("""
#     ### 👋 What is InsightPulse?
#     InsightPulse is an AI-powered tool designed to help you analyze and visualize your dataset effortlessly. 
#     Simply upload a dataset, ask questions in natural language, and get instant insights!

#     ### 🚀 How to Use InsightPulse:
#     1. **Login** to access the platform.
#     2. **Upload a CSV or Excel file** using the sidebar (after login).
#     3. **Ask questions** about your dataset in the chat.
#     4. Get **instant results** with data tables and visualizations!

#     ### 💡 Example Queries:
#     - *"Show me the top 10 highest sales."*
#     - *"Plot a bar chart of sales by region."*
#     - *"Find the average price for each product category."*
#     """)

#     st.markdown("---") # Separator for better UI

#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("🔐 Login", use_container_width=True):
#             st.session_state.page = "login"
#             st.rerun()
#     with col2:
#         if st.button("📝 Register", use_container_width=True):
#             st.session_state.page = "register"
#             st.rerun()
#     st.info("🔐 Please log in or register to get started.")


# def login_page():
#     st.title("🔐 Login to InsightPulse")
#     st.markdown("Please enter your credentials to log in.")

#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             # Assuming login_user updates st.session_state.authenticated and st.session_state.user
#             # This function's implementation in app.auth is crucial for successful login
#             if login_user(username, password):
#                 st.success("Logged in successfully!")
#                 st.session_state.authenticated = True
#                 # Assuming login_user populates st.session_state.user with username and email
#                 # If not, you might need to manually set st.session_state.user here for the UI
#                 if not st.session_state.user:
#                      st.session_state.user = {"username": username, "email": f"{username}@example.com"} # Fallback/Placeholder
#                 st.session_state.page = "chat"
#                 st.rerun()
#             else:
#                 st.error("Invalid username or password.")
    
#     st.markdown("---")
#     if st.button("← Back to Landing"):
#         st.session_state.page = "landing"
#         st.rerun()
#     if st.button("Don't have an account? Register here."):
#         st.session_state.page = "register"
#         st.rerun()


# def register_page():
#     st.title("📝 Register for InsightPulse")
#     st.markdown("Create a new account.")

#     with st.form("register_form"):
#         new_username = st.text_input("Choose a Username")
#         new_email = st.text_input("Enter your Email")
#         new_password = st.text_input("Choose a Password", type="password")
#         confirm_password = st.text_input("Confirm Password", type="password")
#         submitted = st.form_submit_button("Register")

#         if submitted:
#             if not new_username or not new_email or not new_password or not confirm_password:
#                 st.error("Please fill in all fields.")
#             elif new_password != confirm_password:
#                 st.error("Passwords do not match!")
#             else:
#                 # This is a placeholder for your actual registration logic
#                 # You would typically call a function like app.auth.register_user(new_username, new_email, new_password)
#                 # and handle its success/failure.
#                 # For UI demonstration, we'll assume success and redirect to login.
#                 st.success(f"Account for '{new_username}' registered successfully! Please log in.")
#                 st.session_state.page = "login"
#                 st.rerun()
    
#     st.markdown("---")
#     if st.button("← Back to Landing"):
#         st.session_state.page = "landing"
#         st.rerun()
#     if st.button("Already have an account? Login here."):
#         st.session_state.page = "login"
#         st.rerun()


# def chat_page():
#     # Ensure user is available before accessing its properties
#     username_display = st.session_state.user.get('username', 'User') if st.session_state.user else 'User'
#     st.title(f"💬 InsightPulse - Welcome, {username_display}")

#     # ✅ Sidebar for authenticated users
#     with st.sidebar:
#         st.header("⚙️ Options")
#         if st.button("🚪 Logout"):
#             logout_user() # Your existing logout function
#             st.session_state.authenticated = False
#             st.session_state.user = None
#             st.session_state.page = "landing" # Redirect to landing page after logout
#             st.rerun()
        
#         st.markdown("---") # Separator
#         st.header("📁 Upload Dataset")
#         uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

#         if uploaded_file:
#             # Generate a unique ID for user + dataset combination
#             file_id = f"{st.session_state.user['email']}_{uploaded_file.name}"
#             st.session_state.current_file = file_id

#             # Load dataset
#             df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
#             st.success(f"✅ Dataset '{uploaded_file.name}' loaded successfully!")

#             # Display basic info about the dataset
#             st.write(f"**Loaded:** `{uploaded_file.name}`")
#             st.write(f"**Shape:** `{df.shape[0]} rows, {df.shape[1]} columns`")
#             st.dataframe(df.head(), use_container_width=True) # Show first few rows

#             # ✅ Fetch chat history per user + dataset
#             st.session_state.messages = get_chat_history(file_id)

#             if not st.session_state.messages:
#                 st.session_state.messages = [
#                     {"role": "assistant", "content": "Hi! Upload your dataset and ask me anything about it."}
#                 ]
            
#             # Button to clear chat history
#             st.markdown("---")
#             if st.button("🗑️ Clear Chat History"):
#                 clear_chat_history(file_id)
#                 st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Start a new query."}]
#                 st.rerun()
#         else:
#             # Clear current file and messages if no file is uploaded
#             if 'current_file' in st.session_state:
#                 del st.session_state['current_file']
#             st.session_state.messages = [{"role": "assistant", "content": "Hi! Upload your dataset from the sidebar to start analyzing."}]


#     # Main chat area conditional on file upload
#     if st.session_state.get('current_file') and 'df' in locals(): # Ensure df is loaded
#         # Display chat history properly
#         for msg in st.session_state.messages:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])

#                 if msg["role"] == "assistant" and msg.get("code"):
#                     st.markdown("💻 **Generated Code:**")
#                     st.code(msg["code"], language="python")

#                 if msg["role"] == "assistant" and msg.get("result"):
#                     st.markdown("📊 **Query Result:**")
#                     try:
#                         # Attempt to load result as DataFrame if it's a JSON string
#                         # Check for JSON string and if it looks like a DataFrame (contains "index")
#                         if isinstance(msg["result"], str) and msg["result"].strip().startswith("{") and '"index"' in msg["result"]:
#                             result_df = pd.read_json(msg["result"])
#                             st.dataframe(result_df)
#                         elif msg["result"] == "<Figure>": # Placeholder for saved figures
#                             st.warning("Note: Chart re-rendering from history is limited. The code for the chart is displayed above.")
#                         else:
#                             st.markdown(msg["result"])
#                     except Exception as e:
#                         st.error(f"⚠️ Error displaying result from history: {e}")

#         # ✅ Handle user input (scaled up visually by being prominent at the bottom)
#         user_query = st.chat_input("Ask a question about your dataset...")
#         if user_query:
#             # Add user query to session state and save
#             st.session_state.messages.append({"role": "user", "content": user_query})
#             save_chat_message(st.session_state.current_file, "user", user_query)

#             with st.chat_message("user"):
#                 st.markdown(user_query)

#             with st.chat_message("assistant"):
#                 with st.spinner("🔎 Analyzing your query..."):
#                     code = generate_code_from_query(user_query, list(df.columns)) # Use the loaded df

#                     if code:
#                         result_type, result = execute_generated_code(code, df)
#                         st.markdown("💻 **Generated Code:**")
#                         st.code(code, language="python")

#                         if result_type == "chart":
#                             st.markdown("📊 **Generated Visualization:**")
#                             st.pyplot(result)
#                             # It's good practice to close the figure to free up memory
#                             plt.close(result) 
#                         else:
#                             st.markdown("📊 **Query Result:**")
#                             if isinstance(result, pd.DataFrame):
#                                 st.dataframe(result)
#                             else:
#                                 st.markdown(str(result)) # Ensure it's a string for saving

#                         # ✅ Save chat history (Assistant's response)
#                         # Convert DataFrame result to JSON string for storage
#                         result_to_save = None
#                         if isinstance(result, pd.DataFrame):
#                             result_to_save = result.to_json()
#                         elif isinstance(result, plt.Figure):
#                             result_to_save = "<Figure>" # Store a placeholder for figures
#                         else:
#                             result_to_save = str(result)
                        
#                         save_chat_message(
#                             st.session_state.current_file, "assistant", "✅ Here are the results!",
#                             code=code,
#                             result=result_to_save
#                         )
#                         # Append to current session messages to display immediately
#                         st.session_state.messages.append(
#                             {"role": "assistant", "content": "✅ Here are the results!", "code": code,
#                              "result": result_to_save}
#                         )

#                     else:
#                         st.markdown("⚠️ Failed to generate code. Please try rephrasing your query.")
#                         save_chat_message(st.session_state.current_file, "assistant", "⚠️ Failed to generate code.")
#                         st.session_state.messages.append({"role": "assistant", "content": "⚠️ Failed to generate code."})

#     else:
#         # Message displayed when no file is uploaded yet in the chat page
#         st.info("⬆️ Please upload a dataset from the sidebar to start analyzing.")


# # --- Main Application Logic (Page Router) ---
# if st.session_state.authenticated:
#     # If authenticated, ensure we are on the chat page
#     if st.session_state.page != "chat":
#         st.session_state.page = "chat"
#     chat_page()
# else:
#     # If not authenticated, display the appropriate page based on session state
#     if st.session_state.page == "landing":
#         landing_page()
#     elif st.session_state.page == "login":
#         login_page()
#     elif st.session_state.page == "register":
#         register_page()
#     else: # Fallback in case of an unexpected page state
#         st.session_state.page = "landing"
#         landing_page() # Redirect to landing page







#5 
# import streamlit as st
# import pandas as pd
# import requests
# import re
# import matplotlib.pyplot as plt
# import seaborn as sns
# from app.database import db, save_chat_message, get_chat_history, clear_chat_history
# from app.auth import init_session_state, login_user, logout_user, register_user

# # ✅ Set page config with better visual appeal
# st.set_page_config(
#     page_title="💬 InsightPulse",
#     layout="wide",
#     initial_sidebar_state="collapsed",  # Start with sidebar collapsed
#     page_icon="📊"
# )

# # Custom CSS for better UI
# st.markdown("""
# <style>
#     .stChatInput {padding: 1rem; border-radius: 0.5rem;}
#     .stChatInput textarea {
#         min-height: 100px !important;
#         font-size: 16px !important;
#     }
#     .landing-button {padding: 0.75rem 1.5rem !important; font-size: 1rem !important;}
#     .landing-button-container {display: flex; gap: 1rem; margin-top: 2rem; justify-content: center;}
#     .landing-header {font-size: 2.5rem !important; margin-bottom: 1.5rem !important; text-align: center;}
#     .landing-subheader {font-size: 1.25rem !important; margin-bottom: 1rem !important; text-align: center;}
#     .feature-card {padding: 1.5rem; border-radius: 0.5rem; background: rgba(255,255,255,0.1); margin-bottom: 1rem;}
#     .chat-message {padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;}
#     .assistant-message {background: rgba(28, 131, 225, 0.1);}
#     .user-message {background: rgba(29, 178, 115, 0.1);}
#     .stSidebar {background: #f0f2f6 !important;}
# </style>
# """, unsafe_allow_html=True)

# # ✅ Initialize session state
# if "page" not in st.session_state:
#     st.session_state.page = "landing"
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# # ✅ API Configuration
# UPSTAGE_API_URL = "https://api.upstage.ai/v1/chat/completions"
# API_KEY = st.secrets["upstage_api_key"]

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# # ✅ Initialize session state
# init_session_state()

# # ✅ Function to detect if query requires a chart
# def is_chart_request(query):
#     chart_keywords = ["bar chart", "plot", "graph", "pie chart", "visualize", "histogram", "scatter plot", "line chart"]
#     return any(keyword in query.lower() for keyword in chart_keywords)

# # ✅ Generate code from query
# def generate_code_from_query(query, columns):
#     if is_chart_request(query):
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas and matplotlib/seaborn code snippet to visualize this query: \"{query}\". "
#             "Use 'df' as the DataFrame and return only the code without explanations. "
#             "Ensure the visualization is created correctly and does not contain syntax errors. "
#             "Assign the figure to a variable named 'fig'."
#         )
#     else:
#         prompt = (
#             f"You are a Python data analyst. Given a dataset with columns: {columns}, "
#             f"generate a pandas code snippet to answer this query: \"{query}\". "
#             "Use 'df' as the DataFrame and assign the result to a variable named 'result'. "
#             "Return only the code without explanations."
#         )

#     payload = {
#         "model": "solar-1-mini-chat",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant for Python data analysis."},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.3,
#         "max_tokens": 500
#     }

#     try:
#         response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         raw_code = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
#         cleaned_code = re.sub(r"```(?:python)?\s*([\s\S]*?)\s*```", r"\1", raw_code).strip()
#         return cleaned_code
#     except Exception as e:
#         st.error(f"❌ Error generating code: {e}")
#         return ""

# # ✅ Execute generated code
# def execute_generated_code(code, df):
#     local_vars = {"df": df, "plt": plt, "sns": sns, "pd": pd}
#     try:
#         exec(code, {}, local_vars)
#         if "fig" in local_vars and isinstance(local_vars["fig"], plt.Figure):
#             return "chart", local_vars["fig"]
#         return "data", local_vars.get("result", "⚠️ No 'result' variable found.")
#     except Exception as e:
#         st.error(f"🚫 Error executing code: {e}")
#         return None, None

# # ✅ Landing Page (Unauthenticated)
# if not st.session_state.authenticated:
#     # Full-width landing page with centered content
#     col1, col2, col3 = st.columns([1, 3, 1])
    
#     with col2:
#         st.markdown('<h1 class="landing-header">📊 Welcome to InsightPulse</h1>', unsafe_allow_html=True)
#         st.markdown('<h2 class="landing-subheader">Your AI-Driven Data Assistant</h2>', unsafe_allow_html=True)
        
#         # Feature cards
#         with st.container():
#             st.markdown('<div class="feature-card">', unsafe_allow_html=True)
#             st.subheader("🔍 Instant Data Insights")
#             st.write("Ask questions in natural language and get immediate answers from your dataset.")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#             st.markdown('<div class="feature-card">', unsafe_allow_html=True)
#             st.subheader("📈 Automatic Visualizations")
#             st.write("Get beautiful charts and graphs without writing any code.")
#             st.markdown('</div>', unsafe_allow_html=True)
            
#             st.markdown('<div class="feature-card">', unsafe_allow_html=True)
#             st.subheader("🤖 AI-Powered Analysis")
#             st.write("Our advanced AI understands your data and provides meaningful insights.")
#             st.markdown('</div>', unsafe_allow_html=True)
        
#         # Auth buttons centered
#         st.markdown('<div class="landing-button-container">', unsafe_allow_html=True)
#         if st.button("🔑 Login", key="login_btn", use_container_width=True, type="primary"):
#             st.session_state.page = "login"
#             st.rerun()
            
#         if st.button("✍️ Register", key="register_btn", use_container_width=True):
#             st.session_state.page = "register"
#             st.rerun()
#         st.markdown('</div>', unsafe_allow_html=True)
    
#     st.stop()

# # ✅ Handle Auth Pages
# if st.session_state.page == "login":
#     login_user()
#     st.stop()
# elif st.session_state.page == "register":
#     register_user()
#     st.stop()

# # ✅ Main App (Authenticated)
# if st.session_state.authenticated:
#     # Show sidebar now that user is authenticated
#     with st.sidebar:
#         st.markdown(f"### 👋 Welcome, {st.session_state.user['username']}")
        
#         # File upload section
#         st.header("📁 Data Management")
#         uploaded_file = st.file_uploader(
#             "Upload your dataset", 
#             type=["csv", "xlsx"],
#             label_visibility="collapsed"
#         )
        
#         st.markdown("---")
#         if st.button("🗑️ Clear Chat History", use_container_width=True):
#             if 'current_file' in st.session_state:
#                 clear_chat_history(st.session_state.current_file)
#                 st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Ask me anything about your data."}]
#                 st.rerun()
        
#         st.markdown("---")
#         if st.button("🚪 Logout", use_container_width=True, type="primary"):
#             logout_user()
#             st.session_state.page = "landing"
#             st.rerun()

#     # Main content area
#     st.title(f"💬 InsightPulse - Chat with Your Data")
    
#     if uploaded_file:
#         file_id = f"{st.session_state.user['email']}_{uploaded_file.name}"
#         st.session_state.current_file = file_id

#         # Load dataset
#         try:
#             df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
#             st.success(f"✅ Dataset '{uploaded_file.name}' loaded successfully!")
            
#             # Show dataset preview
#             with st.expander("🔍 Dataset Preview (First 5 rows)", expanded=False):
#                 st.dataframe(df.head())

#             # Chat history
#             st.session_state.messages = get_chat_history(file_id)
#             if not st.session_state.messages:
#                 st.session_state.messages = [
#                     {
#                         "role": "assistant", 
#                         "content": f"Hi! I'm ready to analyze your dataset with {len(df.columns)} columns and {len(df)} rows. Ask me anything!"
#                     }
#                 ]

#             # Display chat history
#             for msg in st.session_state.messages:
#                 with st.chat_message(msg["role"]):
#                     st.markdown(msg["content"])

#                     if msg["role"] == "assistant" and msg.get("code"):
#                         with st.expander("💻 Generated Code", expanded=False):
#                             st.code(msg["code"], language="python")

#                     if msg["role"] == "assistant" and msg.get("result"):
#                         st.markdown("📊 **Results**")
#                         try:
#                             if isinstance(msg["result"], str) and msg["result"].startswith("{"):
#                                 result = pd.read_json(msg["result"])
#                                 st.dataframe(result)
#                             elif isinstance(msg["result"], plt.Figure):
#                                 st.pyplot(msg["result"])
#                             else:
#                                 st.markdown(str(msg["result"]))
#                         except Exception as e:
#                             st.error(f"⚠️ Error displaying result: {e}")

#             # Enhanced chat input
#             chat_container = st.container()
#             with chat_container:
#                 user_query = st.chat_input(
#                     "Ask a question about your dataset...", 
#                     key="chat_input"
#                 )
                
#                 st.caption("Tip: Try asking 'Show me a bar chart of sales by region' or 'What are the top 5 products?'")

#             if user_query:
#                 st.session_state.messages.append({"role": "user", "content": user_query})
#                 with st.chat_message("user"):
#                     st.markdown(user_query)

#                 with st.chat_message("assistant"):
#                     with st.spinner("🔍 Analyzing your query..."):
#                         code = generate_code_from_query(user_query, list(df.columns))

#                         if code:
#                             result_type, result = execute_generated_code(code, df)
                            
#                             with st.expander("💻 Generated Code", expanded=False):
#                                 st.code(code, language="python")

#                             if result_type == "chart":
#                                 st.markdown("📊 **Visualization**")
#                                 st.pyplot(result)
#                             else:
#                                 st.markdown("📊 **Results**")
#                                 if isinstance(result, pd.DataFrame):
#                                     st.dataframe(result)
#                                 else:
#                                     st.markdown(str(result))

#                             # Save to history
#                             save_chat_message(
#                                 file_id, 
#                                 "assistant", 
#                                 "Here are the results!", 
#                                 code=code, 
#                                 result=result.to_json() if isinstance(result, pd.DataFrame) else str(result)
#                             )
#                             st.session_state.messages.append(
#                                 {
#                                     "role": "assistant", 
#                                     "content": "Here are the results!", 
#                                     "code": code, 
#                                     "result": result
#                                 }
#                             )
#                         else:
#                             st.error("⚠️ Failed to generate code for your query.")
#                             st.session_state.messages.append(
#                                 {"role": "assistant", "content": "Sorry, I couldn't process that request."}
#                             )

#         except Exception as e:
#             st.error(f"❌ Error loading file: {str(e)}")
#     else:
#         st.info("ℹ️ Please upload a dataset using the sidebar to get started.")