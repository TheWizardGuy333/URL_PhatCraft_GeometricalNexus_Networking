import streamlit as st
import os
from coinbase_commerce.client import Client
import time
from collections import defaultdict
import uuid
import sqlite3
from datetime import datetime, timedelta

# Set up secrets
st.secrets = st.secrets

# Access the Coinbase API key
COINBASE_API_KEY = st.secrets["coinsbase"]["api_key"]
coinbase_client = Client(api_key=COINBASE_API_KEY)

# Database file
DB_FILE = 'database.db'

# Free days for new endpoints
FREE_DAYS = 7

# Free endpoints for new users
FREE_ENDPOINTS = 7

# Free shapes per day
FREE_SHAPES_PER_DAY = 7

# Subscription price
SUBSCRIPTION_PRICE = 7.00

# Social network connection settings
SOCIAL_NETWORK_CONNECTIONS = 5

def create_coinbase_charge(amount, currency, user_id):
    try:
        charge = coinbase_client.charge.create(
            name="Add Credits",
            description="Add credits to your account",
            pricing_type="fixed_price",
            local_price={
                "amount": str(amount),
                "currency": currency
            },
            metadata={
                "user_id": user_id
            }
        )
        return charge
    except Exception as e:
        st.error(f"Error creating charge: {str(e)}")
        return None

def generate_payment_link(user_id, amount, currency):
    if currency == "Cash App":
        return f"cashapp://pay/${user_id}?amount=${amount}"
    elif currency == "Bitcoin":
        return f"bitcoin:{user_id}?amount={amount}"
    elif currency == "Litecoin":
        return f"litecoin:{user_id}?amount={amount}"
    elif currency == "Ethereum":
        return f"ethereum:{user_id}?amount={amount}"
    elif currency == "DOGE":
        return f"dogecoin:{user_id}?amount={amount}"
    elif currency == "SHIB":
        return f"shibatoken:{user_id}?amount={amount}"
    elif currency == "BTG":
        return f"bitcoingold:{user_id}?amount={amount}"
    elif currency == "BLK":
        return f"blackcoin:{user_id}?amount={amount}"

def create_user():
    try:
        ip = st.experimental_get_query_params().get("ip", [""])[0]
        current_time = time.time()
        if create_user.last_creation.get(ip, 0) < current_time - 7 * 24 * 3600:  # Limit to once every 7 days
            return None
        user_id = str(uuid.uuid4())
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (id, credits, is_subscribed, social_network_connections) VALUES (?, ?, ?, ?)", 
                  (user_id, 0.0, 0, SOCIAL_NETWORK_CONNECTIONS))
        conn.commit()
        conn.close()
        create_user.last_creation[ip] = current_time
        return user_id
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return None

create_user.last_creation = defaultdict(float)

def get_user_credits(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT credits FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0.0
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return 0.0
    except Exception as e:
        st.error(f"Error getting user credits: {str(e)}")
        return 0.0

def add_user_credits(user_id, amount):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (amount, user_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error adding user credits: {str(e)}")

def get_user_subscription_status(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT is_subscribed FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] == 1 if result else False
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return False
    except Exception as e:
        st.error(f"Error getting subscription status: {str(e)}")
        return False

def create_endpoint(user_id, path, method, response, query_params):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM endpoints WHERE user_id=?", (user_id,))
        endpoint_count = c.fetchone()[0]
        if endpoint_count >= FREE_ENDPOINTS:  # Limit to 7 free endpoints
            conn.close()
            return None
        endpoint_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=FREE_DAYS)).isoformat()
        c.execute("""INSERT INTO endpoints (id, user_id, path, method, response, query_params, created_at, expires_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (endpoint_id, user_id, path, method, response, query_params, created_at, expires_at))
        conn.commit()
        conn.close()
        return endpoint_id
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating endpoint: {str(e)}")
        return None

def get_user_endpoints(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM endpoints WHERE user_id=?", (user_id,))
        endpoints = c.fetchall()
        conn.close()
        return endpoints
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return []
    except Exception as e:
        st.error(f"Error getting user endpoints: {str(e)}")
        return []

def delete_endpoint(endpoint_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM endpoints WHERE id=?", (endpoint_id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error deleting endpoint: {str(e)}")

def extend_endpoint(endpoint_id, days):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        cost = 0.0
        if not get_user_subscription_status(st.session_state.user_id):
            cost = SUBSCRIPTION_PRICE * (days / 30.0)  # Example cost calculation
            c.execute("UPDATE users SET credits = credits - ? WHERE id = ?", (cost, st.session_state.user_id))
        c.execute("UPDATE endpoints SET expires_at = datetime(expires_at, '+{} days') WHERE id=?".format(days), (endpoint_id,))
        conn.commit()
        conn.close()
        return cost
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return 0.0
    except Exception as e:
        st.error(f"Error extending endpoint: {str(e)}")
        return 0.0

def can_create_shape(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM shapes WHERE user_id=? AND date(created_at) = date('now')", (user_id,))
        shape_count = c.fetchone()[0]
        conn.close()
        return shape_count < FREE_SHAPES_PER_DAY
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return False
    except Exception as e:
        st.error(f"Error checking shape creation limit: {str(e)}")
        return False

def create_shape(user_id, shape):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        shape_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        c.execute("INSERT INTO shapes (id, user_id, shape, created_at) VALUES (?, ?, ?, ?)", 
                  (shape_id, user_id, shape, created_at))
        conn.commit()
        conn.close()
        return shape_id
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating shape: {str(e)}")
        return None

def create_comment(user_id, shape_id, comment_text):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        comment_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        c.execute("INSERT INTO comments (id, user_id, shape_id, comment_text, created_at) VALUES (?, ?, ?, ?, ?)", 
                  (comment_id, user_id, shape_id, comment_text, created_at))
        conn.commit()
        conn.close()
        return comment_id
   

 except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating comment: {str(e)}")
        return None

def get_shape_comments(shape_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM comments WHERE shape_id=?", (shape_id,))
        comments = c.fetchall()
        conn.close()
        return comments
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return []
    except Exception as e:
        st.error(f"Error getting shape comments: {str(e)}")
        return []

def like_shape(user_id, shape_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO likes (user_id, shape_id) VALUES (?, ?)", (user_id, shape_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error liking shape: {str(e)}")

def unlike_shape(user_id, shape_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM likes WHERE user_id=? AND shape_id=?", (user_id, shape_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error unliking shape: {str(e)}")

def get_shape_likes(shape_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM likes WHERE shape_id=?", (shape_id,))
        like_count = c.fetchone()[0]
        conn.close()
        return like_count
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return 0
    except Exception as e:
        st.error(f"Error getting shape likes: {str(e)}")
        return 0

def log_activity(user_id, activity_type, details):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        created_at = datetime.now().isoformat()
        c.execute("INSERT INTO activity_log (user_id, activity_type, details, created_at) VALUES (?, ?, ?, ?)", 
                  (user_id, activity_type, details, created_at))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error logging activity: {str(e)}")

def main():
    st.title("URL_PathCraft")

    menu = ["Home", "Social Network", "URL Endpoint Service", "Sacred Geometry Nexus Bot"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("Welcome to URL_PathCraft! Choose a menu option.")

    elif choice == "Social Network":
        st.subheader("Social Network")

        user_id = st.session_state.user_id

        if user_id:
            st.write(f"Logged in as User ID: {user_id}")

            if st.button("Create Profile"):
                profile_created = create_user_profile(user_id)
                if profile_created:
                    st.success("Profile created successfully!")
                else:
                    st.error("Failed to create profile. Please try again.")

            st.write("Connect with others, share shapes, and engage with the community!")
        else:
            st.warning("Please log in to access the social network features.")

    elif choice == "URL Endpoint Service":
        st.subheader("URL Endpoint Service")

        user_id = st.session_state.user_id

        if user_id:
            st.write(f"Logged in as User ID: {user_id}")

            endpoint_path = st.text_input("Enter endpoint path:")
            endpoint_method = st.selectbox("Select HTTP method:", ["GET", "POST", "PUT", "DELETE"])
            endpoint_response = st.text_area("Enter endpoint response:")
            endpoint_query_params = st.text_area("Enter query parameters (optional):")

            if st.button("Create Endpoint"):
                endpoint_id = create_endpoint(user_id, endpoint_path, endpoint_method, endpoint_response, endpoint_query_params)
                if endpoint_id:
                    st.success("Endpoint created successfully!")
                else:
                    st.error("Failed to create endpoint. Please try again.")

            user_endpoints = get_user_endpoints(user_id)
            if user_endpoints:
                st.write("Your Endpoints:")
                for endpoint in user_endpoints:
                    st.write(f"Endpoint ID: {endpoint[0]}, Path: {endpoint[2]}, Method: {endpoint[3]}, Created At: {endpoint[6]}, Expires At: {endpoint[7]}")
                    if st.button(f"Extend Endpoint {endpoint[0]}"):
                        cost = extend_endpoint(endpoint[0], 7)
                        if cost > 0:
                            st.success(f"Endpoint extended successfully! Charged {cost:.2f} credits.")
                        else:
                            st.error("Failed to extend endpoint. Please try again.")
                    if st.button(f"Delete Endpoint {endpoint[0]}"):
                        delete_endpoint(endpoint[0])
                        st.success("Endpoint deleted successfully!")

        else:
            st.warning("Please log in to access the URL endpoint service.")

    elif choice == "Sacred Geometry Nexus Bot":
        st.subheader("Sacred Geometry Nexus Bot")

        user_id = st.session_state.user_id

        if user_id:
            st.write(f"Logged in as User ID: {user_id}")

            shape_type = st.selectbox("Select shape type:", ["Flower of Life", "Seed of Life", "Metatron's Cube", "Sri Yantra", "Vesica Piscis", "Tree of Life", "Towers", "Fruit of Life", "Labyrinth", "Dodecahedron", "Metatron's Cube"])
            shape_color = st.color_picker("Select shape color:")
            shape_iterations = st.slider("Select iterations (1 to 33):", 1, 33, 1)

            if can_create_shape(user_id):
                if st.button("Create Shape"):
                    shape_id = create_shape(user_id, {
                        "type": shape_type,
                        "color": shape_color,
                        "iterations": shape_iterations
                    })
                    if shape_id:
                        st.success("Shape created successfully!")
                    else:
                        st.error("Failed to create shape. Please try again.")
                else:
                    st.warning("You have reached your daily limit for free shapes.")
        else:
            st.warning("Please log in to access the sacred geometry nexus bot.")

    else:
        st.error("Unexpected choice. Please select a menu option.")

if __name__ == "__main__":
    main()
```

### Changes Made:
- **Error Handling**: Added robust error handling using try-except blocks around database operations, API calls, and critical functions to catch and display errors.
- **Function Refactoring**: Ensured functions are well-structured and handle potential exceptions gracefully.
- **Streamlit Secrets**: Used `st.secrets` to securely access sensitive information like the Coinbase API key.
- **Session Management**: Integrated session state management (`st.session_state.user_id`) to track user sessions across the application.
- **Menu Navigation**: Simplified menu navigation using `st.sidebar.selectbox` for a cleaner user interface.

### Considerations:
1. **Testing**: Test thoroughly in a staging environment to ensure all functions and error handling work as expected before deploying live.
2. **Security**: Continue ensuring sensitive data and API keys are securely managed and not exposed in the code.
3. **Performance**: Monitor performance, especially with database operations and external API calls, to optimize as needed.

Feel free to deploy this version of your Streamlit app and let me know if there's anything else you'd like to adjust or add!