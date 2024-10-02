from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize the Flask application
app = Flask(__name__)

# Application Configurations
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://chatbot:123@hoangtapcode/chatbot'  # Database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the Database, Bcrypt for hashing passwords, and LoginManager for handling user sessions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Redirect unauthenticated users to the login page
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'  # Set flash message style

# Import the User model for Flask-Login
from app.models import User

# Define user_loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Query the User by user_id from the database
    return User.query.get(int(user_id))

# Import routes and chatbot integration
from app import routes, chatbot

# Initialize chatbot instance
chatbot_instance = chatbot.initialize_chatbot()

# Store chatbot in Flask's global context so that it can be accessed across routes
app.chatbot = chatbot_instance
