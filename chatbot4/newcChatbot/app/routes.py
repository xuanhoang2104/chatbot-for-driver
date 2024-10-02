from flask import render_template, redirect, url_for, flash, request, jsonify, session
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from app.chatbot import initialize_chatbot
import logging

logging.basicConfig(level=logging.INFO)

# Initialize chatbot
chatbot = initialize_chatbot()

# Home route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))  # Redirect to chat if already logged in

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email đã được đăng ký. Vui lòng sử dụng email khác.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            session['session_id'] = str(user.id)
            flash(f'Tài khoản {form.username.data} đã được tạo thành công!', 'success')
            return redirect(url_for('chat'))  # Redirect to chatbot after successful registration
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating user: {e}")
            flash('Đã có lỗi xảy ra trong quá trình tạo tài khoản, vui lòng thử lại.', 'danger')
    
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect to chat
    if current_user.is_authenticated:
        return redirect(url_for('chat'))  # Redirect to chat if already logged in
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user exists
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Tài khoản không tồn tại, vui lòng đăng ký trước.', 'warning')
            return redirect(url_for('register'))  # Redirect to register if no account found
        
        # If user exists, check password and log them in
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['session_id'] = str(user.id)
            flash('Đăng nhập thành công!', 'success')
            logging.info(f"User {user.username} logged in successfully, session ID: {session['session_id']}")
            return redirect(url_for('chat'))  # Redirect directly to chat on successful login
        else:
            flash('Đăng nhập không thành công. Vui lòng kiểm tra tên đăng nhập và mật khẩu.', 'danger')
            logging.warning(f"Failed login attempt for user: {form.username.data}")
    
    return render_template('login.html', form=form)

# Chat route
@app.route('/chat', methods=['GET'])
@login_required
def chat():
    return render_template('chat.html')

# Route to handle POST request for sending a message to the chatbot
@app.route('/chat', methods=['POST'])
@login_required
def chat_post():
    try:
        print("Received POST request to /chat")

        # Get the user's message from the request
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'reply': 'Không có tin nhắn nào được nhận.'}), 400

        # Use the session ID if it exists, otherwise assign a default session
        user_session_id = session.get('session_id', 'default_session')
        session['session_id'] = user_session_id

        # Call the chatbot to get a response
        bot_response = chatbot.get_response(user_message)
        if not bot_response:
            bot_response = 'Xin lỗi, chatbot hiện không thể trả lời câu hỏi của bạn.'
        
        print(f"Phản hồi từ chatbot: {bot_response}")

        # Return the chatbot's response
        return jsonify({'reply': bot_response})

    except Exception as e:
        logging.error(f"Lỗi khi xử lý tin nhắn: {e}")
        return jsonify({'reply': 'Xin lỗi, đã xảy ra lỗi trong quá trình xử lý.'}), 500

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('session_id', None)  # Clear session ID
    logout_user()  # Log the user out
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('login'))  # Redirect to login page after logout
