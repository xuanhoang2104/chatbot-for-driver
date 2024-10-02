import logging
import google.generativeai as genai

# Cấu hình API key cho Gemini
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
                return "Xin chào! Tôi là Chatbot hỗ trợ lái xe, tôi có thể giúp gì cho bạn."

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
