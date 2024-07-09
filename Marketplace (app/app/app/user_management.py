from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, subscribed=False):
        self.id = id
        self.email = email
        self.password = password
        self.subscribed = subscribed

class UserManager:
    def __init__(self, db, bcrypt):
        self.db = db
        self.bcrypt = bcrypt
        self.users = []

    def create_user(self, email, password):
        hashed_password = self.bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(len(self.users) + 1, email, hashed_password)
        self.users.append(user)
        return user

    def authenticate_user(self, email, password):
        user = next((u for u in self.users if u.email == email), None)
        if user and self.bcrypt.check_password_hash(user.password, password):
            return user
        return None

    def update_subscription_status(self, user_id, status):
        user = next((u for u in self.users if u.id == user_id), None)
        if user:
            user.subscribed = status
