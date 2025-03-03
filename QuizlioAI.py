import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import re

class ChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Quizlio Chatbot")
        self.root.geometry("600x600")
        self.root.configure(bg="#343541")
        self.setup_gui()
        self.initialize_model()
        self.new_chat_session()

    def initialize_model(self):
        genai.configure(api_key="AIzaSyBQ7z269t9Lqs1RFCpGOVSLBnwXhqSEWy8")
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    def setup_gui(self):
        top_frame = tk.Frame(self.root, bg="#343541")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.new_chat_btn = tk.Button(
            top_frame, text="New Chat", command=self.new_chat_session,
            font=("Arial", 14, "bold"), bg="#10A37F", fg="white",
            relief=tk.FLAT, padx=15
        )
        self.new_chat_btn.pack(side=tk.LEFT)

        self.chat_display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Arial", 14),
            bg="#40414F", fg="white", insertbackground="white",
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0))
        self.chat_display.tag_configure('user', justify='right', foreground='white')
        self.chat_display.tag_configure('bot', justify='left', foreground='white')
        self.chat_display.tag_configure('bot_code', background="#2D2D2D", lmargin1=20, lmargin2=20, spacing3=5)

        input_frame = tk.Frame(self.root, bg="#343541")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Entry field with placeholder text
        self.entry = tk.Entry(
            input_frame, font=("Arial", 16), bg="#40414F",
            fg="gray", insertbackground="white", relief=tk.FLAT
        )
        self.entry.insert(0, "Ask anything...")  # Default placeholder text
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<FocusOut>", self.restore_placeholder)
        self.entry.bind("<Return>", self.send_message)  # Bind Enter key
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=5)

        self.send_button = tk.Button(
            input_frame, text="Go Now", command=lambda: self.send_message(None),
            font=("Arial", 14, "bold"), bg="#10A37F", fg="white",
            relief=tk.FLAT, padx=15
        )
        self.send_button.pack(side=tk.RIGHT)

    def clear_placeholder(self, event):
        """Clear placeholder text when the user clicks the input box."""
        if self.entry.get() == "Ask anything...":
            self.entry.delete(0, tk.END)
            self.entry.config(fg="white")

    def restore_placeholder(self, event):
        """Restore placeholder text if the user leaves the input box empty."""
        if self.entry.get() == "":
            self.entry.insert(0, "Ask anything...")
            self.entry.config(fg="gray")

    def new_chat_session(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.chat = self.model.start_chat(history=[])

    def send_message(self, event):
        user_input = self.entry.get().strip()
        if not user_input or user_input == "Ask anything...":
            return
        self.entry.delete(0, tk.END)
        self.update_display(f"You: {user_input}", "user")
        threading.Thread(target=self.get_bot_response, args=(user_input,)).start()

    def get_bot_response(self, user_input):
        try:
            response = self.chat.send_message(user_input)
            self.root.after(0, self.process_and_display_bot_message, response.text)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", str(e))

    def process_and_display_bot_message(self, bot_response):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "Quizlio Bot: ", 'bot')
        
        pattern = re.compile(r'```(.*?)```', re.DOTALL)
        parts = pattern.split(bot_response)
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                self.chat_display.insert(tk.END, part, 'bot')
            else:
                code = part.strip()
                self.chat_display.insert(tk.END, f"\n{code}\n", 'bot_code')
                copy_btn = tk.Button(
                    self.chat_display, text="Copy", 
                    command=lambda c=code: self.copy_to_clipboard(c),
                    bg="#10A37F", fg="white", relief=tk.FLAT, padx=5
                )
                self.chat_display.window_create(tk.END, window=copy_btn)
                self.chat_display.insert(tk.END, "\n")
        
        self.chat_display.insert(tk.END, "\n\n", 'bot')
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def copy_to_clipboard(self, code):
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()

    def update_display(self, text, tag=None):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, text + "\n\n", tag)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()
