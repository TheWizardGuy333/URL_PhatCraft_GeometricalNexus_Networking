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

# Streamlit app
def main():
    st.title("Sacred Geometry Nexus +")

    choice = st.sidebar.selectbox("Menu", ["Home", "Create Shape", "Manage Endpoints", "User Profile", "Debug Code", "Optimize Code", "Generate Documentation", "Interact with User"])

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to Sacred Geometry Nexus +!")

    elif choice == "Create Shape":
        st.subheader("Create Shape")
        user_id = st.text_input("User ID")
        shape = st.text_input("Shape")
        if st.button("Create"):
            create_shape(user_id, shape)
            st.success("Shape created successfully.")

    elif choice == "Manage Endpoints":
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

    elif choice == "User Profile":
        st.subheader("User Profile")
        st.write("User profile functionality will be implemented here.")

    elif choice == "Debug Code":
        st.subheader("Debug Code")
        code_snippet = st.text_area("Enter code snippet to debug:")
        if st.button("Debug"):
            debug_info = handle_error(code_snippet)
            st.write("Debug Information:")
            st.write(debug_info)

    elif choice == "Optimize Code":
        st.subheader("Optimize Code")
        code_snippet = st.text_area("Enter code snippet to optimize:")
        if st.button("Optimize"):
            optimized_code = optimize_code(code_snippet)
            st.write("Optimized Code:")
            st.code(optimized_code, language='python')

    elif choice == "Generate Documentation":
        st.subheader("Generate Documentation")
        feature_description = st.text_area("Enter feature description:")
        if st.button("Generate"):
            documentation = generate_documentation(feature_description)
            st.write("Generated Documentation:")
            st.write(documentation)

    elif choice == "Interact with User":
        st.subheader("Interact with User")
        message = st.text_area("Enter your message:")
        if st.button("Send"):
            response = interact_with_user(message)
            st.write("AI Response:")
            st.write(response)

if __name__ == "__main__":
    main()
