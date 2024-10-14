from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import logging
import time

app = Flask(__name__)
app.secret_key = "123"  # Bí mật dùng cho session

# Cấu hình SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Mô hình (Model) User để lưu trữ thông tin đăng ký
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Tạo bảng cơ sở dữ liệu (chỉ cần chạy lần đầu tiên)
with app.app_context():
    db.create_all()

# Cấu hình Google Gemini API Key
genai.configure(api_key='AIzaSyCIJ9dWQ_gO-ePyMTnGIKLsbgaZCA7SuAw')

class GeminiChatbot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        logging.basicConfig(level=logging.INFO)  # Set logging level

    def get_response(self, message):
        try:
            # Kiểm tra nếu tin nhắn là "xin chào"
            if message.lower() == "xin chào":
                return "Xin chào! Tôi là Chatbot hỗ trợ thời trang, tôi có thể giúp gì cho bạn."

            response = self.chat.send_message(message, stream=True)
            chatbot_reply = ""

            for chunk in response:
                if chunk.text:
                    chatbot_reply += chunk.text + " "
            
            logging.info(f"Response generated: {chatbot_reply.strip()}")
            return chatbot_reply.strip()
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "Sorry, something went wrong."


# Hàm để khởi tạo chatbot
def initialize_chatbot():
    return GeminiChatbot()


# Route để sinh nội dung từ Gemini
@app.route("/generate", methods=["POST"])
def generate_content():
    try:
        prompt = request.json.get("prompt", "")
        if not prompt:
            return {"error": "Prompt is required"}, 400

        model = genai.GenerativeModel("gemini-pro")
        # Thử lại API 3 lần nếu gặp lỗi
        for i in range(3):
            try:
                response = model.generate_content(prompt)
                break  # Nếu thành công, thoát vòng lặp
            except Exception as api_error:
                logging.error(f"API Error on attempt {i+1}: {api_error}")
                time.sleep(2)  # Đợi 2 giây trước khi thử lại
        else:
            return {"error": "API failed after 3 attempts"}, 500

        return {"text": response.text}, 200
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return {"error": "Internal server error occurred"}, 500



# Route trang chủ
@app.route("/")
def index():
    # Kiểm tra xem session có chứa fullname và username không
    if "username" in session and "fullname" in session:
        return render_template("index.html", fullname=session["fullname"])
    return redirect(url_for("login"))


# Route đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        # Kiểm tra xem username đã tồn tại hay chưa
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username đã tồn tại. Vui lòng chọn username khác."

        # Lưu thông tin người dùng mới vào cơ sở dữ liệu
        new_user = User(fullname=fullname, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


# Route đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Kiểm tra username và mật khẩu trong cơ sở dữ liệu
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = username
            session["fullname"] = user.fullname  # Lưu fullname vào session
            return redirect(url_for("index"))
        else:
            return "Sai username hoặc mật khẩu, vui lòng thử lại."
    return render_template("login.html")


# Route để đăng xuất
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("fullname", None)  # Xóa fullname khỏi session khi đăng xuất
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
