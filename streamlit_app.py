import os
import re
import uuid
import datetime
import json
import sqlite3
import requests
import streamlit as st
from coinbase.wallet.client import Client

# Securely store API key as an environment variable
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')

# Initialize Coinbase client
if COINBASE_API_KEY and COINBASE_API_SECRET:
    coinbase_client = Client(api_key=COINBASE_API_KEY, api_secret=COINBASE_API_SECRET)
else:
    coinbase_client = None

# Load API key from Streamlit secrets
DEEP_AI_API_KEY = st.secrets["general"]["deep_ai_api_key"]
DEEP_AI_API_ENDPOINT = "https://api.deepai.org"
DB_FILE = 'database.db'

# Free days for new endpoints
FREE_DAYS = 7

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS endpoints
                 (id TEXT PRIMARY KEY, user_id TEXT, path TEXT, method TEXT, 
                  response TEXT, query_params TEXT, created_at TEXT, expires_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shapes
                 (user_id TEXT, shape TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, username TEXT, email TEXT, password TEXT, 
                  subscription_plan TEXT, subscription_expiry TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id TEXT PRIMARY KEY, user_id TEXT, content TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id TEXT PRIMARY KEY, post_id TEXT, user_id TEXT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Function to handle errors using Deep AI
def handle_error(error_message):
    try:
        headers = {
            "Authorization": f"Bearer {DEEP_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"text": error_message}
        response = requests.post(f"{DEEP_AI_API_ENDPOINT}/error-handling", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("handled_error", "No response from AI.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to optimize code using Deep AI
def optimize_code(code_snippet):
    try:
        headers = {
            "Authorization": f"Bearer {DEEP_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"code": code_snippet}
        response = requests.post(f"{DEEP_AI_API_ENDPOINT}/optimize-code", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("optimized_code", "No optimization performed.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate documentation using Deep AI
def generate_documentation(feature_description):
    try:
        headers = {
            "Authorization": f"Bearer {DEEP_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"description": feature_description}
        response = requests.post(f"{DEEP_AI_API_ENDPOINT}/generate-documentation", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("documentation", "No documentation generated.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to interact with user using Deep AI
def interact_with_user(message):
    try:
        headers = {
            "Authorization": f"Bearer {DEEP_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"text": message}
        response = requests.post(f"{DEEP_AI_API_ENDPOINT}/interact", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("response", "No response from AI.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to create shape in the database
def create_shape(user_id, shape):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO shapes (user_id, shape) VALUES (?, ?)", (user_id, shape))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
    finally:
        conn.close()

# Function to create an endpoint
def create_endpoint(user_id, path, method, response, query_params):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', user_id):
        raise ValueError("Invalid user ID")
    if not re.match(r'^/[a-zA-Z0-9/_\-]+$', path):
        raise ValueError("Invalid path")
    if method not in ['GET', 'POST', 'PUT', 'DELETE']:
        raise ValueError("Invalid method")
    if not isinstance(response, dict):
        raise ValueError("Invalid response")
    if not isinstance(query_params, dict):
        raise ValueError("Invalid query parameters")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO endpoints (id, user_id, path, method, response, query_params, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), user_id, path, method, json.dumps(response), json.dumps(query_params),
        datetime.datetime.now().isoformat(), (datetime.datetime.now() + datetime.timedelta(days=FREE_DAYS)).isoformat()
    ))
    conn.commit()
    conn.close()

# Function to get user endpoints
def get_user_endpoints(user_id):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', user_id):
        raise ValueError("Invalid user ID")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM endpoints WHERE user_id = ?", (user_id,))
    endpoints = c.fetchall()
    conn.close()
    return endpoints

# Function to extend an endpoint's expiration date
def extend_endpoint(endpoint_id, days):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', endpoint_id):
        raise ValueError("Invalid endpoint ID")
    if not isinstance(days, int) or days <= 0:
        raise ValueError("Invalid number of days")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE endpoints SET expires_at = ? WHERE id = ?", (
        (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat(), endpoint_id
    ))
    conn.commit()
    conn.close()

# Function to generate a payment link
def generate_payment_link(user_id, amount, currency):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', user_id):
        raise ValueError("Invalid user ID")
    if not isinstance(amount, float) or amount <= 0:
        raise ValueError("Invalid amount")
    if not re.match(r'^[A-Z]{3}$', currency):
        raise ValueError("Invalid currency")

    return f"https://example.com/pay/{user_id}?amount={amount}&currency={currency}"

# Function to handle user login
def handle_login(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Function to handle user registration
def handle_registration(username, email, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (id, username, email, password) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), username, email, password))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
    finally:
        conn.close()

# Function to create a new post
def create_post(user_id, content):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO posts (id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), user_id, content, datetime.datetime.now().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
    finally:
        conn.close()

# Function to get all posts
def get_all_posts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    conn.close()
    return posts

# Function to create a new comment
def

 create_comment(post_id, user_id, content):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO comments (id, post_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)",
                  (str(uuid.uuid4()), post_id, user_id, content, datetime.datetime.now().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
    finally:
        conn.close()

# Function to get comments for a post
def get_comments_for_post(post_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM comments WHERE post_id = ?", (post_id,))
    comments = c.fetchall()
    conn.close()
    return comments

# Streamlit app
def main():
    st.title("Sacred Geometry Nexus +")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Home", "Create Shape", "Manage Endpoints", "User Profile", "Debug Code", "Optimize Code", "Generate Documentation", "Interact with User"])

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to Sacred Geometry Nexus +!")

    elif choice == "Create Shape":
        create_shape_page()

    elif choice == "Manage Endpoints":
        manage_endpoints_page()

    elif choice == "User Profile":
        user_profile_page()

    elif choice == "Debug Code":
        debug_code_page()

    elif choice == "Optimize Code":
        optimize_code_page()

    elif choice == "Generate Documentation":
        generate_documentation_page()

    elif choice == "Interact with User":
        interact_with_user_page()

def create_shape_page():
    st.subheader("Create Shape")
    user_id = st.text_input("User ID")
    shape = st.text_input("Shape")
    if st.button("Create"):
        create_shape(user_id, shape)
        st.success("Shape created successfully.")

def manage_endpoints_page():
    st.subheader("Manage Endpoints")
    user_id = st.text_input("User ID")
    path = st.text_input("Path")
    method = st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"])
    response = st.text_area("Response (JSON format)")
    query_params = st.text_area("Query Parameters (JSON format)")
    if st.button("Create Endpoint"):
        try:
            response_dict = json.loads(response)
            query_params_dict = json.loads(query_params)
            create_endpoint(user_id, path, method, response_dict, query_params_dict)
            st.success("Endpoint created successfully.")
        except ValueError as e:
            st.error(str(e))
        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
    if st.button("Get Endpoints"):
        try:
            endpoints = get_user_endpoints(user_id)
            st.write(endpoints)
        except ValueError as e:
            st.error(str(e))

def user_profile_page():
    st.subheader("User Profile")
    st.write("User profile functionality will be implemented here.")

def debug_code_page():
    st.subheader("Debug Code")
    code_snippet = st.text_area("Enter code snippet to debug:")
    if st.button("Debug"):
        debug_info = handle_error(code_snippet)
        st.write("Debug Information:")
        st.write(debug_info)

def optimize_code_page():
    st.subheader("Optimize Code")
    code_snippet = st.text_area("Enter code snippet to optimize:")
    if st.button("Optimize"):
        optimized_code = optimize_code(code_snippet)
        st.write("Optimized Code:")
        st.code(optimized_code, language='python')

def generate_documentation_page():
    st.subheader("Generate Documentation")
    feature_description = st.text_area("Enter feature description:")
    if st.button("Generate"):
        documentation = generate_documentation(feature_description)
        st.write("Generated Documentation:")
        st.write(documentation)

def interact_with_user_page():
    st.subheader("Interact with User")
    message = st.text_area("Enter your message:")
    if st.button("Send"):
        response = interact_with_user(message)
        st.write("AI Response:")
        st.write(response)

if __name__ == "__main__":
    main()
