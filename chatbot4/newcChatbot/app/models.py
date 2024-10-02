from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Bảng 'users' đã được định nghĩa là 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Sử dụng đúng tên bảng 'users' trong khóa ngoại
    journals = db.relationship('Journal', backref='author', lazy=True, cascade="all, delete-orphan")
    test_results = db.relationship('TestResults', backref='user', lazy=True, cascade="all, delete-orphan")

class Journal(db.Model):
    __tablename__ = 'journal'  # Thêm tên bảng vào
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Đảm bảo khóa ngoại tham chiếu đến bảng 'users' thay vì 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TestResults(db.Model):
    __tablename__ = 'test_results'  # Thêm tên bảng vào
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    
    # Đảm bảo khóa ngoại tham chiếu đến bảng 'users'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
