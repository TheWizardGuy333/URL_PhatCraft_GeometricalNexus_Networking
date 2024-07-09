from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app.blockchain import Blockchain
from app.shapes import ShapeManager
from app.marketplace import Marketplace
from app.user_management import UserManager
from app.ai_integration import AIIntegration
import stripe

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

stripe_keys = {
    'secret_key': app.config['STRIPE_SECRET_KEY'],
    'publishable_key': app.config['STRIPE_PUBLISHABLE_KEY']
}
stripe.api_key = stripe_keys['secret_key']

blockchain = Blockchain()
shapes = ShapeManager()
marketplace = Marketplace(blockchain)
user_manager = UserManager(db, bcrypt)
ai_integration = AIIntegration(app.config['DEEPAI_API_KEY'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_manager.create_user(email, password)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_manager.authenticate_user(email, password)
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.subscribed:
        return redirect(url_for('subscribe'))
    return render_template('dashboard.html')

@app.route('/subscribe')
@login_required
def subscribe():
    return render_template('subscribe.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
@login_required
def charge():
    try:
        amount = 999  # Amount in cents
        customer = stripe.Customer.create(
            email=current_user.email,
            source=request.form['stripeToken']
        )
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Subscription Charge'
        )
        user_manager.update_subscription_status(current_user.id, True)
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('subscribe'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_shape', methods=['POST'])
@login_required
def create_shape():
    shape_data = request.json
    shape = shapes.create_shape(shape_data)
    return shape

@app.route('/marketplace')
@login_required
def view_marketplace():
    items = marketplace.get_items()
    return render_template('marketplace.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)
