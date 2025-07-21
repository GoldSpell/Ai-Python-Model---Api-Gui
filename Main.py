import tkinter as tk
from tkinter import scrolledtext, messagebox
from google import genai
import api

client = genai.Client(api_key=api.api_key)

chatbot_name = "AI Bot"

FONT = ("Segoe UI", 11)
BOT_COLOR = "#00ffcc"
USER_COLOR = "#7df9ff"
TEXT_COLOR = "#ffffff"
ENTRY_BG = "#1e1e1e"
BUTTON_BG = "#00ffcc"
CODE_BG = "#1e1e1e"
CODE_FG = "#00ffff"

root = tk.Tk()
root.title("🤖 AI Chatbot")
root.geometry("700x600")
root.configure(bg="#0f0f0f")
root.resizable(False, False)

# Scrollable frame to hold chat messages (including frames with buttons)
container = tk.Frame(root, bg="#121212")
container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(container, bg="#121212", highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#121212")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

input_frame = tk.Frame(root, bg="#0f0f0f")
input_frame.pack(pady=10, fill=tk.X, padx=20)

user_input = tk.Entry(input_frame, font=FONT, bg=ENTRY_BG, fg=TEXT_COLOR,
                      insertbackground=TEXT_COLOR, borderwidth=0)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))

send_button = tk.Button(input_frame, text="➤", command=lambda e=None: send_message(),
                        bg=BUTTON_BG, fg="#000000", font=("Segoe UI", 12, "bold"),
                        width=4, borderwidth=0)
send_button.pack(side=tk.RIGHT)


def ask_name():
    def save_name():
        global chatbot_name
        chatbot_name = name_entry.get().strip() or "AI Bot"
        name_window.destroy()
        root.deiconify()

    root.withdraw()
    name_window = tk.Toplevel(root)
    name_window.title("Enter Chatbot Name")
    name_window.geometry("300x150")
    name_window.configure(bg="#0f0f0f")
    name_window.resizable(False, False)

    tk.Label(name_window, text="Enter your chatbot's name:", bg="#0f0f0f", fg=TEXT_COLOR, font=FONT).pack(pady=10)
    name_entry = tk.Entry(name_window, font=FONT, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
    name_entry.pack(pady=5, padx=20)
    name_entry.focus()

    tk.Button(name_window, text="Start Chat", command=save_name, bg=BUTTON_BG, font=FONT).pack(pady=10)

    name_window.bind("<Return>", lambda e: save_name())


def format_response(text: str) -> str:
    if "```" in text:
        return text
    keywords = ["def ", "class ", "print(", "import ", "return ", "if ", "else:", "for ", "while "]
    if any(kw in text.lower() for kw in keywords):
        return f"```python\n{text.strip()}\n```"
    return text


def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Code copied to clipboard!")


def open_edit_window(code_text):
    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Code")
    edit_win.geometry("600x400")
    edit_win.configure(bg="#0f0f0f")

    text_area = tk.Text(edit_win, font=("Courier New", 11), bg=CODE_BG, fg=CODE_FG, insertbackground=CODE_FG)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_area.insert(tk.END, code_text)

    def save_and_close():
        # You can handle saving the edited code here if you want
        edit_win.destroy()

    save_button = tk.Button(edit_win, text="Save & Close", command=save_and_close,
                            bg=BUTTON_BG, fg="#000000", font=FONT)
    save_button.pack(pady=5)


def append_chat(sender: str, message: str, color: str, temp=False):
    # Create a frame for each message for flexibility
    frame = tk.Frame(scrollable_frame, bg="#121212", pady=5)
    frame.pack(fill=tk.X, anchor="w" if sender == "You" else "e", padx=10)

    sender_label = tk.Label(frame, text=f"{sender}:", font=(FONT[0], FONT[1], "bold"), fg=color, bg="#121212")
    sender_label.pack(anchor="w")

    if "```" in message:
        # Extract code blocks
        parts = message.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Normal text part
                if part.strip():
                    msg_label = tk.Label(frame, text=part.strip(), font=FONT, fg=TEXT_COLOR, bg="#121212", justify="left", wraplength=600)
                    msg_label.pack(anchor="w", padx=5, pady=2)
            else:
                # Code block part
                code_frame = tk.Frame(frame, bg=CODE_BG, bd=1, relief="sunken")
                code_frame.pack(anchor="w", padx=5, pady=5, fill=tk.X)

                code_text = tk.Text(code_frame, height=8, font=("Courier New", 10), bg=CODE_BG, fg=CODE_FG,
                                    bd=0, wrap="word", padx=5, pady=5)
                code_text.insert("1.0", part.strip())
                code_text.config(state="disabled")
                code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Buttons frame
                btn_frame = tk.Frame(code_frame, bg=CODE_BG)
                btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

                copy_btn = tk.Button(btn_frame, text="Copy", width=6,
                                     command=lambda c=part.strip(): copy_to_clipboard(c),
                                     bg=BUTTON_BG, fg="#000000", font=("Segoe UI", 9, "bold"))
                copy_btn.pack(pady=2)

                edit_btn = tk.Button(btn_frame, text="Edit", width=6,
                                     command=lambda c=part.strip(): open_edit_window(c),
                                     bg=BUTTON_BG, fg="#000000", font=("Segoe UI", 9, "bold"))
                edit_btn.pack(pady=2)

    else:
        msg_label = tk.Label(frame, text=message, font=FONT, fg=TEXT_COLOR, bg="#121212", justify="left", wraplength=600)
        msg_label.pack(anchor="w", padx=5)

    if not temp:
        # Scroll to bottom
        root.after(100, lambda: canvas.yview_moveto(1.0))


def send_message(event=None):
    message = user_input.get().strip()
    if not message:
        return

    append_chat("You", message, USER_COLOR)
    user_input.delete(0, tk.END)

    if message.lower() in ['exit', 'quit']:
        append_chat(chatbot_name, "Goodbye!", BOT_COLOR)
        return

    append_chat(chatbot_name, "Typing...", BOT_COLOR, temp=True)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
        )
        # Remove last "Typing..." message by removing last child frame
        if scrollable_frame.winfo_children():
            scrollable_frame.winfo_children()[-1].destroy()

        formatted = format_response(response.text)
        append_chat(chatbot_name, formatted, BOT_COLOR)
    except Exception as e:
        if scrollable_frame.winfo_children():
            scrollable_frame.winfo_children()[-1].destroy()
        append_chat(chatbot_name, f"Error: {e}", BOT_COLOR)


user_input.bind("<Return>", send_message)

ask_name()
root.mainloop()
