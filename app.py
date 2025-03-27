import tkinter as tk
from tkinter import scrolledtext, simpledialog
import chatbot
import speech_recognition as sr
# Gửi tin nhắn
def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return
    
    chat_log.config(state=tk.NORMAL)  
    chat_log.insert(tk.END, f"Bạn: {user_input}\n", "user")
    chat_log.config(state=tk.DISABLED)  
    chat_log.yview(tk.END) 
    entry.delete(0, tk.END)

    response, action = chatbot.get_response(user_input)
    
    chat_log.config(state=tk.NORMAL)
    if action == True:
        chat_log.insert(tk.END, f"Chatbot: {response}\n", "bot")
        root.quit()
    elif action == "request_url":
        new_url = simpledialog.askstring("Nhập URL", f"Nhập URL cho {user_input.replace('mở ', '').strip()}: ")
        if new_url:
            chatbot.save_url(user_input.replace("mở ", "").strip(), new_url)
            chat_log.insert(tk.END, f"Chatbot: Đã lưu và mở {user_input.replace('mở ', '').capitalize()}.\n", "bot")
    elif action == "learn":
        new_response = simpledialog.askstring("Học câu trả lời", "Bạn muốn tôi trả lời: ")
        if new_response:
            chatbot.train_chatbot(user_input, new_response)
            chat_log.insert(tk.END, "Chatbot: Cảm ơn! Tôi đã học câu trả lời mới.\n", "bot")
    else:
        chat_log.insert(tk.END, f"Chatbot: {response}\n", "bot")
    
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)  # Cuộn xuống dòng mới nhất

# Căn giữa cửa sổ
def center_window(win, width=500, height=600):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chatbot Tiếng Việt")
center_window(root)

# Tùy chỉnh màu sắc giao diện
BG_COLOR = "#f0f5f9"
TEXT_COLOR = "#000000"
USER_COLOR = "#007bff"
BOT_COLOR = "#28a745"
BUTTON_COLOR = "#4CAF50"
BUTTON_HOVER_COLOR = "#388E3C"
INPUT_BG = "#ffffff"

root.configure(bg=BG_COLOR)

# Tạo frame chính
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Khung chat
chat_log = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=20, font=("Arial", 12), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat")
chat_log.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
chat_log.config(state=tk.DISABLED)  # Ngăn nhập trực tiếp

# Tạo style cho tin nhắn
chat_log.tag_configure("user", foreground=USER_COLOR, font=("Arial", 12, "bold"))
chat_log.tag_configure("bot", foreground=BOT_COLOR, font=("Arial", 12))

# Hiển thị lời chào khi mở ứng dụng
chat_log.config(state=tk.NORMAL)
chat_log.insert(tk.END, "Chatbot: Xin chào bạn! Tôi là chatbot Tiếng Việt.\nChatbot: Tôi có thể giúp gì cho bạn?\n\n", "bot")
chat_log.config(state=tk.DISABLED)

# Khung nhập và nút gửi
input_frame = tk.Frame(main_frame, bg=BG_COLOR)
input_frame.pack(fill=tk.X, padx=10, pady=5)

# Thêm nút "Nghe"
status_label = tk.Label(root, text="Nhấn 'Nghe' để bắt đầu", fg="blue", bg=BG_COLOR)
status_label.pack()



entry = tk.Entry(input_frame, font=("Arial", 14), bg=INPUT_BG, fg=TEXT_COLOR, relief="solid", bd=2)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5, ipady=5)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(input_frame, text="Gửi", command=send_message, font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", relief="flat", width=10, height=1, bd=3, cursor="hand2")
send_button.pack(side=tk.RIGHT, padx=5, pady=5)


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎤 Đang nghe...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="vi-VN")
            status_label.config(text="✔ Bạn đã nói: " + text)

            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, f"Bạn: {text}\n", "user")
            chat_log.config(state=tk.DISABLED)
            chat_log.yview(tk.END)

            response, _ = chatbot.get_response(text)  
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, f"Chatbot: {response}\n", "bot")
            chat_log.config(state=tk.DISABLED)
            chat_log.yview(tk.END)
        except sr.UnknownValueError:
            status_label.config(text=" Không nghe rõ, thử lại!")
        except sr.RequestError:
            status_label.config(text=" Lỗi kết nối với dịch vụ!")
            
listen_button = tk.Button(root, text="🎙 Nghe", command=listen, font=("Arial", 12, "bold"),
                          bg=BUTTON_COLOR, fg="white", relief="flat", width=10, height=1, bd=3, cursor="hand2")
listen_button.pack(pady=5)
# Hiệu ứng hover cho nút gửi
def on_enter(e):
    send_button.config(bg=BUTTON_HOVER_COLOR)

def on_leave(e):
    send_button.config(bg=BUTTON_COLOR)

send_button.bind("<Enter>", on_enter)
send_button.bind("<Leave>", on_leave)

root.mainloop()
