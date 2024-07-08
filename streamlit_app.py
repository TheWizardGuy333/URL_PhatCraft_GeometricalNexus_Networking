import streamlit as st
import requests
import sqlite3

# Load API key from Streamlit secrets
DEEP_AI_API_KEY = st.secrets["deep_ai_api_key"]
DEEP_AI_API_ENDPOINT = "https://api.deepai.org"
DB_FILE = 'database.db'

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

# Streamlit app
def main():
    st.title("PhatCraft Geometrical Nexus Networking")

    choice = st.sidebar.selectbox("Menu", ["Home", "Create Shape", "Manage Endpoints", "User Profile", "Debug Code", "Optimize Code", "Generate Documentation", "Interact with User"])

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to PhatCraft Geometrical Nexus Networking!")

    elif choice == "Create Shape":
        st.subheader("Create Shape")
        user_id = st.text_input("User ID")
        shape = st.text_input("Shape")
        if st.button("Create"):
            create_shape(user_id, shape)
            st.success("Shape created successfully.")

    elif choice == "Manage Endpoints":
        st.subheader("Manage Endpoints")
        # Implement endpoint management functionality

    elif choice == "User Profile":
        st.subheader("User Profile")
        # Implement user profile functionality

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
