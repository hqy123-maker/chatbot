
import webbrowser
import time
import re
import sqlite3

import requests
import threading
import time

from underthesea import word_tokenize
import wikipedia
import pyttsx3  
import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
def preprocess_text(text):

    text = text.lower().strip()  
    text = word_tokenize(text, format="text")  
    return text


# Khởi tạo engine giọng nói
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Tốc độ đọc
engine.setProperty("volume", 1.0)  # Âm lượng
# Chọn giọng đọc (0: Nam, 1: Nữ)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id) 

def create_table():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



def preprocess_text(text):
    """Tiền xử lý văn bản bằng underthesea"""
    text = text.lower().strip()  
    text = word_tokenize(text, format="text")  
    return text


def speak(text):
    engine.say(text)
    engine.runAndWait()
# Danh sách URL có sẵn
predefined_urls = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "chatgpt": "https://chat.openai.com",
    "facebook": "https://www.facebook.com",
    "zalo": "https://chat.zalo.me",
    "tiktok": "https://www.tiktok.com"
}



def save_url(name, url):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO custom_urls (name, url) VALUES (?, ?)", (name, url))
    conn.commit()
    conn.close()

def get_url(name):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM custom_urls WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_news():
    url = "https://vnexpress.net/rss/tin-moi-nhat.rss"
    response = requests.get(url)
    if response.status_code == 200:
        from xml.etree import ElementTree as ET
        import re  # Dùng để loại bỏ HTML
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        news_list = []
        for item in items[:5]:
            title = item.find("title").text
            desc = re.sub(r'<[^>]*>', '', item.find("description").text)  # Xóa HTML
            news_list.append(f"- {title}: {desc}")
        return "\n".join(news_list)
    return "Không thể lấy tin tức lúc này."

def get_wiki_summary(query):
    wikipedia.set_lang("vi")  # Chuyển sang tiếng Việt
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError:
        return "Tôi tìm thấy nhiều kết quả, hãy nhập chính xác hơn!"
    except wikipedia.exceptions.PageError:
        return "Không tìm thấy thông tin trên Wikipedia."
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(" Đang nghe... Hãy nói gì đó!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="vi-VN")
            return f"Bạn đã nói: {text}"
        except sr.UnknownValueError:
            return " Không nghe rõ, hãy thử lại!"
        except sr.RequestError:
            return " Lỗi kết nối với dịch vụ nhận diện giọng nói!"
        
def set_timer(minutes, message):
    def countdown():
        time.sleep(minutes * 60)
        print(f" Nhắc nhở: {message}")

    thread = threading.Thread(target=countdown)
    thread.start()
    return f"Đã đặt hẹn giờ {minutes} phút: {message}"
# Tạo chatbot
chatbot = ChatBot(
    'VietnameseBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///db.sqlite3'

)
create_table()
trainer = ListTrainer(chatbot)
trainer.train([
    "Xin chào", "Chào bạn! Tôi có thể giúp gì?",
    "Bạn tên gì?", "Tôi là chatbot hỗ trợ tiếng Việt.",
    "Tạm biệt", "Hẹn gặp lại bạn sau!"
    "Bạn tên gì?", "Tôi là chatbot hỗ trợ tiếng Việt.",
    "Tên của bạn là gì?", "Tôi là trợ lý ảo của bạn.",
    "Gọi bạn là gì?", "Bạn có thể gọi tôi là Chatbot AI.",
])

def get_response(user_input):
    user_input = preprocess_text(user_input)
    user_input = user_input.strip().lower()
    
    print(f"User input: {user_input}")  
    # Cải thiện regex để nhận diện phép toán kể cả khi có chữ "tính" phía trước
    math_pattern = r'(?:tính\s*)?(\d+\s*[\+\-\*/]\s*\d+)'
    match = re.search(math_pattern, user_input)

    if match:
        expression = match.group(1) 
        try:
            result = eval(expression.replace(" ", ""))  # Loại bỏ khoảng trắng và tính toán
            return f"Kết quả: {result}", False
        except Exception:
            return "Lỗi khi tính toán. Vui lòng nhập đúng định dạng!", False
    if "wiki" in user_input:
        query = user_input.replace("wiki", "").strip()
        return get_wiki_summary(query), False
    if user_input in ["exit", "thoát", "tạm biệt"]:
        return "Hẹn gặp lại!", True
    
    if "hẹn giờ" in user_input:
        try:
            parts = user_input.replace("hẹn giờ", "").strip().split()
            minutes = int(parts[0])
            message = " ".join(parts[1:]) if len(parts) > 1 else "Hết giờ!"
            return set_timer(minutes, message), False
        except:
            return " Vui lòng nhập đúng định dạng: hẹn giờ [số phút] [nội dung]", False
    if "nghe" in user_input:
        return listen(), False
    elif "mấy giờ" in user_input:
        return f"Bây giờ là {time.strftime('%H:%M')}", False
    
    elif "tin tức" in user_input:
        return "Đây là một số tin tức mới nhất:\n" + get_news(), False
    
    elif any(kw in user_input for kw in ["tìm kiếm", "tìm trên web", "tra cứu", "tìm hiểu về"]):
        search_query = user_input.replace("tìm kiếm", "").replace("tìm trên web", "").replace("tra cứu", "").replace("tìm hiểu về", "").strip()
        if not search_query:
            return "Bạn muốn tìm kiếm gì?", "request_search"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Đang tìm kiếm '{search_query}' trên Google.", False
    
    elif "mở" in user_input:
        site_name = user_input.replace("mở ", "").strip()
        url = predefined_urls.get(site_name) or get_url(site_name)
        if url:
            webbrowser.open(url)
            return f"Đã mở {site_name.capitalize()}.", False
        else:
            return f"Tôi chưa biết {site_name}. Bạn có thể nhập URL không?", "request_url"
    else:
        
        response = chatbot.get_response(user_input)
        if response.confidence < 0.3:
            return "Tôi chưa biết câu trả lời. Bạn muốn tôi trả lời thế nào?", "learn"
        else:
            speak(response)
            return str(response), False
    
def train_chatbot(question, answer):
    question = preprocess_text(question)  
    answer = preprocess_text(answer) 
    trainer.train([question, answer])
    return "Đã học câu trả lời mới!"