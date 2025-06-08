import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, Listbox
from socket import *
import threading
import time
import os
import json

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Kirrilgram")
        self.master.geometry("1200x900")
        self.master.configure(bg="#E6E6FA")

        self.server_ip = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.load_last_username()

        self.server_socket = None
        self.connected = False
        self.chat_windows = {}
        self.active_chat = None
        self.user_chats = {}
        self.unread_messages = {}

        self.setup_login_screen()

    def load_last_username(self):
        if os.path.exists("last_username.json"):
            with open("last_username.json", "r") as file:
                data = json.load(file)
                self.username.set(data.get("username", ""))

    def save_username(self):
        with open("last_username.json", "w") as file:
            json.dump({"username": self.username.get()}, file)

    def setup_login_screen(self):
        self.login_frame = tk.Frame(self.master, padx=60, pady=60, bg="#E6E6FA")  # світло-фіолетовий
        self.login_frame.pack(expand=True)

        label_font = ("Helvetica", 15)
        entry_font = ("Helvetica", 15)
        button_font = ("Helvetica", 14)

        tk.Label(
            self.login_frame,
            text="IP-адреса сервера:",
            font=label_font,
            bg="#F3E5F5"
        ).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        tk.Entry(self.login_frame, textvariable=self.server_ip, font=entry_font, width=25,bg="white").grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.login_frame, text="Ім'я користувача:", font=label_font,bg="#E6E6FA" ).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        tk.Entry(self.login_frame, textvariable=self.username,font=entry_font,width=25, bg="white").grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.login_frame, text="Пароль:",font=label_font,bg="#E6E6FA").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        tk.Entry( self.login_frame,textvariable=self.password,font=entry_font,width=25,show="*",bg="white").grid(row=2, column=1, padx=10, pady=10)

        self.register_button = tk.Button(self.login_frame, text="Реєстрація", font=button_font,bg="#E6E6FA",fg="white", activebackground="#9C27B0",  activeforeground="white",command=self.show_register_screen)
        self.register_button.grid(row=3, column=0, padx=10, pady=15, sticky=tk.E)

        self.login_button = tk.Button( self.login_frame, text="Увійти", font=button_font,  bg="#7B1FA2", fg="white",  activebackground="#9C27B0",   activeforeground="white",command=self.login_user)
        self.login_button.grid(row=3, column=1, padx=10, pady=15, sticky=tk.W)

        self.reset_button = tk.Button(self.login_frame,text="Забули пароль?",font=("Helvetica", 11, "underline"),bg="#F3E5F5",fg="#4A148C",bd=0,cursor="hand2",command=self.show_reset_screen)
        self.reset_button.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

    def show_register_screen(self):
        self.login_frame.pack_forget()
        self.register_frame = tk.Frame(self.master, padx=60, pady=60, bg="#F3E5F5")  # світло-фіолетовий
        self.register_frame.pack(expand=True)

        label_font = ("Helvetica", 15)
        entry_font = ("Helvetica", 15)
        button_font = ("Helvetica", 14)

        tk.Label(self.register_frame,text="IP-адреса сервера:",font=label_font, bg="#F3E5F5").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.register_frame, textvariable=self.server_ip,font=entry_font,width=25,bg="white").grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.register_frame, text="Ім'я користувача:",font=label_font,bg="#F3E5F5").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.register_frame,textvariable=self.username,font=entry_font,width=25,bg="white").grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.register_frame,text="Пароль:",font=label_font,bg="#F3E5F5").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.register_frame,textvariable=self.password,font=entry_font,width=25,show="*",bg="white").grid(row=2, column=1, padx=10, pady=10)

        self.password_requirements_label = tk.Label(self.register_frame, text="Пароль має містити щонайменше 8 символів, включати цифру та літеру.",font=("Helvetica", 11),bg="#F3E5F5",fg="#D32F2F")
        self.password_requirements_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.register_button = tk.Button(self.register_frame, text="Зареєструватися",font=button_font,bg="#7B1FA2",fg="white", activebackground="#9C27B0", activeforeground="white", command=self.register_user)
        self.register_button.grid(row=4, column=1, padx=10, pady=15, sticky=tk.E)

        self.back_button = tk.Button(  self.register_frame,text="Повернутися", font=button_font, bg="#7B1FA2", fg="white", activebackground="#9C27B0", activeforeground="white", command=self.back_to_login)
        self.back_button.grid(row=4, column=0, padx=10, pady=15, sticky=tk.W)

    def show_reset_screen(self):
        self.login_frame.pack_forget()
        self.reset_frame = tk.Frame(self.master, padx=60, pady=60, bg="#F3E5F5")  # світло-фіолетовий
        self.reset_frame.pack(expand=True)

        label_font = ("Helvetica", 15)
        entry_font = ("Helvetica", 15)
        button_font = ("Helvetica", 14)

        tk.Label(self.reset_frame,text="IP-адреса сервера:", font=label_font, bg="#F3E5F5").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.reset_frame,textvariable=self.server_ip,font=entry_font,width=25,bg="white").grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.reset_frame,text="Ім'я користувача:",font=label_font,bg="#F3E5F5").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.reset_frame,textvariable=self.username,font=entry_font,width=25,bg="white").grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.reset_frame,text="Новий пароль:",font=label_font, bg="#F3E5F5").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.reset_frame,textvariable=self.password,font=entry_font,width=25,show="*",bg="white").grid(row=2, column=1, padx=10, pady=10)

        self.password_requirements_label = tk.Label(self.reset_frame,text="Пароль має містити щонайменше 8 символів, включати цифру та літеру.",font=("Helvetica", 11),bg="#F3E5F5",fg="#D32F2F")
        self.password_requirements_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.reset_button = tk.Button(self.reset_frame,text="Скинути пароль",font=button_font,bg="#7B1FA2",fg="white",activebackground="#9C27B0",activeforeground="white",command=self.reset_password)
        self.reset_button.grid(row=4, column=1, padx=10, pady=15, sticky=tk.E)

        self.back_button = tk.Button(self.reset_frame,text="Повернутися",font=button_font,bg="#7B1FA2",fg="white",activebackground="#9C27B0",activeforeground="white",command=self.back_to_login)
        self.back_button.grid(row=4, column=0, padx=10, pady=15, sticky=tk.W)

    def back_to_login(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.pack_forget()
        if hasattr(self, 'reset_frame'):
            self.reset_frame.pack_forget()
        self.setup_login_screen()

    def register_user(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Помилка", "Будь ласка, введіть IP-адресу, ім'я користувача та пароль")
            return

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Помилка", "Пароль має містити щонайменше 8 символів, включати цифру та літеру")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"REGISTER:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "REGISTER_SUCCESS":
                messagebox.showinfo("Успіх", "Реєстрація успішна! Увійдіть у систему.")
                self.server_socket.close()
                self.back_to_login()
            else:
                messagebox.showerror("Помилка", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Помилка", "Не вдалося підключитися до сервера")
            self.server_socket.close()

    def login_user(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Помилка", "Будь ласка, введіть IP-адресу, ім'я користувача та пароль")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"LOGIN:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "LOGIN_SUCCESS":
                self.connected = True
                self.save_username()
                self.setup_chat_screen()
                threading.Thread(target=self.receive_messages).start()
                self.load_user_chats()
            else:
                messagebox.showerror("Помилка", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Помилка", "Не вдалося підключитися до сервера")
            self.server_socket.close()

    def reset_password(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Помилка", "Будь ласка, введіть IP-адресу, ім'я користувача та новий пароль")
            return

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Помилка", "Пароль має містити щонайменше 8 символів, включати цифру та літеру")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"RESET:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "RESET_SUCCESS":
                messagebox.showinfo("Успіх", "Пароль успішно змінено! Увійдіть у систему.")
                self.server_socket.close()
                self.back_to_login()
            else:
                messagebox.showerror("Помилка", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Помилка", "Не вдалося підключитися до сервера")
            self.server_socket.close()

    def setup_chat_screen(self):
        self.login_frame.destroy()
        if hasattr(self, 'register_frame'):
            self.register_frame.destroy()
        if hasattr(self, 'reset_frame'):
            self.reset_frame.destroy()

        self.chat_frame = tk.Frame(self.master, bg="#DDA0DD")
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.contact_list_frame = tk.Frame(self.chat_frame, width=250, bg="#E8EAF6")
        self.contact_list_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.header_frame = tk.Frame(self.contact_list_frame, bg="#DDA0DD")
        self.header_frame.pack(fill=tk.X)

        self.contacts_label = tk.Label(self.header_frame, text=self.username.get(), bg="#DDA0DD", fg="white",font=("Helvetica", 18, "bold"), pady=10)
        self.contacts_label.pack(side=tk.LEFT, padx=5)

        self.disconnect_button = tk.Button(self.header_frame, text="❌", font=("Helvetica", 14), bg="#3F51B5",fg="white", bd=0, command=self.disconnect_from_server)
        self.disconnect_button.pack(side=tk.RIGHT, padx=5)

        self.search_entry = tk.Entry(self.contact_list_frame, font=("Helvetica", 14), fg="gray", bg="#FFF", bd=0)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.insert(0, "Пошук")

        def on_entry_click(event):
            if self.search_entry.get() == "Пошук":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg="black")

        def on_focusout(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, "Пошук")
                self.search_entry.config(fg="gray")

        self.search_entry.bind("<FocusIn>", on_entry_click)
        self.search_entry.bind("<FocusOut>", on_focusout)

        self.contacts_listbox = tk.Listbox(self.contact_list_frame, font=("Helvetica", 14), bg="#E8EAF6", bd=0, selectbackground="#3F51B5", selectforeground="white")
        self.contacts_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.select_chat)

        self.message_frame = tk.Frame(self.chat_frame, bg="#DDA0DD")
        self.message_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.messages_text = scrolledtext.ScrolledText(self.message_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Helvetica", 14), bg="#FFF", bd=0, padx=10, pady=10)
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.entry_frame = tk.Frame(self.message_frame, bg="#FFF")
        self.entry_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.message_entry = tk.Entry(self.entry_frame, font=("Helvetica", 14), bg="#F0F0F0", bd=0)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.message_entry.bind('<Return>', lambda event: self.send_message())

        self.emoji_button = tk.Button(self.entry_frame, text="😊", font=("Helvetica", 14), bg="#663399", fg="white",
                                      bd=0, command=self.show_emoji_picker)
        self.emoji_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.send_button = tk.Button(self.entry_frame, text="Надіслати", font=("Helvetica", 14), bg="#4B0082", fg="white", bd=0, command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def show_emoji_picker(self):
        emoji_window = Toplevel(self.master)
        emoji_window.title("Смайлики")
        emoji_window.geometry("200x200")
        emoji_window.configure(bg="#663399")

        emojis = ["😊", "😂", "😍", "😭", "😒", "😘", "😔", "😁", "😢", "😎", "😡", "😴"]

        emoji_listbox = Listbox(emoji_window, font=("Helvetica", 14), bg="#EEE", fg="#000")
        emoji_listbox.pack(fill=tk.BOTH, expand=True)

        for emoji in emojis:
            emoji_listbox.insert(tk.END, emoji)

        def insert_selected_emoji(event):
            selected_emoji = emoji_listbox.get(emoji_listbox.curselection())
            self.message_entry.insert(tk.END, selected_emoji)
            emoji_window.destroy()

        emoji_listbox.bind('<<ListboxSelect>>', insert_selected_emoji)

    def disconnect_from_server(self):
        if self.connected:
            try:
                self.server_socket.send("DISCONNECT".encode())
            except:
                pass
            self.close_socket()
            self.connected = False
            self.master.quit()

    def close_socket(self):
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.server_socket.close()

    def load_user_chats(self):
        if os.path.exists(f"{self.username.get()}_chats.json"):
            with open(f"{self.username.get()}_chats.json", "r") as file:
                self.user_chats = json.load(file)
                sorted_users = sorted(
                    self.user_chats.keys(),
                    key=lambda u: self.user_chats[u][-1] if self.user_chats[u] else "",
                    reverse=True
                )
                for user in sorted_users:
                    self.contacts_listbox.insert(tk.END, user)

    def save_user_chats(self):
        with open(f"{self.username.get()}_chats.json", "w") as file:
            json.dump(self.user_chats, file)

    def select_chat(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            selected = event.widget.get(index)
            self.active_chat = selected.replace(" 🔴", "")  # Прибираємо позначку
            if self.active_chat in self.unread_messages:
                del self.unread_messages[self.active_chat]
            self.display_messages()

    def display_messages(self):
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete('1.0', tk.END)
        if self.active_chat in self.user_chats:
            current_date = ""
            for message in self.user_chats[self.active_chat]:
                msg_date = message.split("(")[-1].split(" ")[0]
                try:
                    msg_date_formatted = time.strftime("%B %d", time.strptime(msg_date, "%Y-%m-%d"))
                except ValueError:
                    msg_date_formatted = ""
                if current_date != msg_date_formatted:
                    self.messages_text.insert(tk.END, f"\n{msg_date_formatted}\n", "date_centered")
                    current_date = msg_date_formatted
                self.format_message(message)
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.yview(tk.END)

    def format_message(self, message):
        parts = message.split(": ", 1)
        sender = parts[0]
        rest = parts[1].rsplit("(", 1)
        msg = rest[0].strip()
        timestamp = rest[1].strip(")").split(" ")[1]

        is_sent = sender == "You"

        bubble_color = "#E0BBE4" if is_sent else "#D8E2DC"  # фіолетовий / світло-сірий
        align = "right" if is_sent else "left"
        tag = "sent" if is_sent else "received"

        self.messages_text.tag_configure(tag, justify=align, background=bubble_color, wrap='word', spacing3=5)
        self.messages_text.tag_configure(f"{tag}_timestamp", font=("Helvetica", 8), foreground="#999999", justify=align)
        self.messages_text.tag_configure("date_centered", font=("Helvetica", 10), foreground="#888888",
                                         justify="center")

        msg_lines = msg.split("\n")
        for line in msg_lines:
            self.messages_text.insert(tk.END, line + "\n", tag)
        self.messages_text.insert(tk.END, f"{timestamp}\n", f"{tag}_timestamp")

    def receive_messages(self):
        while self.connected:
            try:
                message = self.server_socket.recv(1024).decode()
                if message.startswith("USERS:"):
                    users = message[6:].split(',')
                    self.update_user_list(users)
                else:
                    self.process_message(message)
            except:
                self.connected = False
                self.close_socket()
                break

    def update_user_list(self, users):
        self.contacts_listbox.delete(0, tk.END)
        displayed = set()

        # Спочатку — онлайн користувачі
        for user in users:
            if user != self.username.get():
                label = user
                if user in self.unread_messages:
                    label += " 🔴"
                self.contacts_listbox.insert(tk.END, label)
                displayed.add(user)

        # Потім — інші, з історії
        for user in self.user_chats.keys():
            if user not in displayed and user != self.username.get():
                label = user
                if user in self.unread_messages:
                    label += " 🔴"
                self.contacts_listbox.insert(tk.END, label)

    def process_message(self, message):
        sender, msg = message.split(":", 1)
        timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        formatted_message = f"{sender}: {msg.strip()} ({timestamp})"
        if sender not in self.user_chats:
            self.user_chats[sender] = []
        self.user_chats[sender].append(formatted_message)
        if sender != self.active_chat:
            if sender not in self.unread_messages:
                self.unread_messages[sender] = 0
            self.unread_messages[sender] += 1
        self.save_user_chats()
        self.update_contacts_list()
        if self.active_chat == sender:
            self.display_messages()

    def update_contacts_list(self):
        self.contacts_listbox.delete(0, tk.END)
        for user in self.user_chats.keys():
            if user != self.username.get():
                display_name = user
                if user in self.unread_messages:
                    display_name += f" ({self.unread_messages[user]})"
                self.contacts_listbox.insert(tk.END, display_name)

    def send_message(self):
        if self.active_chat:
            msg = self.message_entry.get().strip()
            if msg:
                if self.active_chat not in self.user_chats:
                    self.user_chats[self.active_chat] = []
                timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                formatted_message = f"You: {msg} ({timestamp})"
                self.user_chats[self.active_chat].append(formatted_message)
                self.display_messages()
                self.server_socket.send(f"{self.active_chat}:{msg}".encode())
                self.message_entry.delete(0, tk.END)
                self.save_user_chats()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()