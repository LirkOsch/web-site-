import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import string
import random
import json
import uuid
import base64


def copy_to_clipboard(text):
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class PasswordGenerator(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build()

    def build(self):
        ctk.CTkLabel(self, text="Генератор паролей", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        len_frame = ctk.CTkFrame(self, fg_color="transparent")
        len_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(len_frame, text="Длина:").pack(side="left")
        self.length_var = tk.IntVar(value=16)
        ctk.CTkSlider(len_frame, from_=4, to=64, variable=self.length_var, command=lambda v: self.len_label.configure(text=str(int(v)))).pack(side="left", fill="x", expand=True, padx=10)
        self.len_label = ctk.CTkLabel(len_frame, text="16", width=30)
        self.len_label.pack(side="right")

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        ctk.CTkCheckBox(self, text="A-Z (верхний регистр)", variable=self.upper_var).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self, text="a-z (нижний регистр)", variable=self.lower_var).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self, text="0-9 (цифры)", variable=self.digits_var).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self, text="!@# (спецсимволы)", variable=self.special_var).pack(anchor="w", pady=2)

        ctk.CTkButton(self, text="Сгенерировать", command=self.generate).pack(pady=(15, 10))

        self.result = ctk.CTkEntry(self, state="normal")
        self.result.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Копировать", command=self.copy, fg_color="#00b894", hover_color="#00a381").pack(pady=5)

    def generate(self):
        chars = ""
        if self.upper_var.get():
            chars += string.ascii_uppercase
        if self.lower_var.get():
            chars += string.ascii_lowercase
        if self.digits_var.get():
            chars += string.digits
        if self.special_var.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not chars:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов")
            return
        length = self.length_var.get()
        password = "".join(random.choice(chars) for _ in range(length))
        self.result.delete(0, "end")
        self.result.insert(0, password)

    def copy(self):
        text = self.result.get()
        if text:
            copy_to_clipboard(text)


class TextAnalyzer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build()

    def build(self):
        ctk.CTkLabel(self, text="Анализатор текста", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        self.text_box = ctk.CTkTextbox(self, height=150)
        self.text_box.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Анализировать", command=self.analyze).pack(pady=5)

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=5)
        self.result_labels = {}
        stats = ["Символов:", "Символов без пробелов:", "Слов:", "Строк:", "Предложений:"]
        for s in stats:
            row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=s, anchor="w", width=180).pack(side="left")
            lbl = ctk.CTkLabel(row, text="0", anchor="e")
            lbl.pack(side="right")
            self.result_labels[s] = lbl

    def analyze(self):
        text = self.text_box.get("0.0", "end").rstrip("\n")
        chars = len(text)
        chars_no_space = len(text.replace(" ", "").replace("\n", ""))
        words = len(text.split()) if text.strip() else 0
        lines = text.count("\n") + (1 if text else 0)
        sentences = sum(1 for c in text if c in ".!?") if text.strip() else 0

        self.result_labels["Символов:"].configure(text=str(chars))
        self.result_labels["Символов без пробелов:"].configure(text=str(chars_no_space))
        self.result_labels["Слов:"].configure(text=str(words))
        self.result_labels["Строк:"].configure(text=str(lines))
        self.result_labels["Предложений:"].configure(text=str(sentences))


class UUIDGenerator(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build()

    def build(self):
        ctk.CTkLabel(self, text="Генератор UUID", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        self.count_var = tk.IntVar(value=1)
        ctk.CTkLabel(self, text="Количество:").pack(anchor="w")
        ctk.CTkSlider(self, from_=1, to=50, variable=self.count_var, command=lambda v: self.count_label.configure(text=str(int(v)))).pack(fill="x", pady=5)
        self.count_label = ctk.CTkLabel(self, text="1")
        self.count_label.pack()

        self.upper_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Верхний регистр", variable=self.upper_var).pack(anchor="w", pady=2)

        ctk.CTkButton(self, text="Сгенерировать", command=self.generate).pack(pady=(15, 10))

        self.result = ctk.CTkTextbox(self, height=120)
        self.result.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Копировать всё", command=self.copy, fg_color="#00b894", hover_color="#00a381").pack(pady=5)

    def generate(self):
        self.result.delete("0.0", "end")
        count = self.count_var.get()
        lines = []
        for _ in range(count):
            u = str(uuid.uuid4())
            if self.upper_var.get():
                u = u.upper()
            lines.append(u)
        self.result.insert("0.0", "\n".join(lines))

    def copy(self):
        text = self.result.get("0.0", "end").strip()
        if text:
            copy_to_clipboard(text)


class Base64Tool(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build()

    def build(self):
        ctk.CTkLabel(self, text="Base64", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Входной текст:").pack(anchor="w")
        self.input_text = ctk.CTkTextbox(self, height=100)
        self.input_text.pack(fill="x", pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Закодировать →", command=self.encode).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="← Декодировать", command=self.decode).pack(side="left", padx=5)

        ctk.CTkLabel(self, text="Результат:").pack(anchor="w")
        self.output_text = ctk.CTkTextbox(self, height=100)
        self.output_text.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Копировать результат", command=self.copy, fg_color="#00b894", hover_color="#00a381").pack(pady=5)

    def encode(self):
        text = self.input_text.get("0.0", "end").rstrip("\n")
        if not text:
            messagebox.showwarning("Ошибка", "Введите текст для кодирования")
            return
        encoded = base64.b64encode(text.encode()).decode()
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", encoded)

    def decode(self):
        text = self.input_text.get("0.0", "end").rstrip("\n")
        if not text:
            messagebox.showwarning("Ошибка", "Введите Base64 для декодирования")
            return
        try:
            decoded = base64.b64decode(text.encode()).decode()
        except Exception:
            messagebox.showerror("Ошибка", "Некорректная Base64 строка")
            return
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", decoded)

    def copy(self):
        text = self.output_text.get("0.0", "end").strip()
        if text:
            copy_to_clipboard(text)


class JSONFormatter(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build()

    def build(self):
        ctk.CTkLabel(self, text="JSON Formatter", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Введите JSON:").pack(anchor="w")
        self.input_text = ctk.CTkTextbox(self, height=150)
        self.input_text.pack(fill="x", pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Форматировать", command=self.format_json).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Сжать", command=self.minify_json).pack(side="left", padx=5)

        ctk.CTkLabel(self, text="Результат:").pack(anchor="w")
        self.output_text = ctk.CTkTextbox(self, height=150)
        self.output_text.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Копировать результат", command=self.copy, fg_color="#00b894", hover_color="#00a381").pack(pady=5)

    def format_json(self):
        text = self.input_text.get("0.0", "end").rstrip("\n")
        if not text:
            messagebox.showwarning("Ошибка", "Введите JSON")
            return
        try:
            parsed = json.loads(text)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", str(e))
            return
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", formatted)

    def minify_json(self):
        text = self.input_text.get("0.0", "end").rstrip("\n")
        if not text:
            messagebox.showwarning("Ошибка", "Введите JSON")
            return
        try:
            parsed = json.loads(text)
            minified = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", str(e))
            return
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", minified)

    def copy(self):
        text = self.output_text.get("0.0", "end").strip()
        if text:
            copy_to_clipboard(text)


class DevToolsPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DevTools Pro")
        self.geometry("700x580")
        self.minsize(600, 500)

        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        tools = [
            ("Пароли", PasswordGenerator),
            ("Текст", TextAnalyzer),
            ("UUID", UUIDGenerator),
            ("Base64", Base64Tool),
            ("JSON", JSONFormatter),
        ]

        for name, cls in tools:
            tab = self.tab_view.add(name)
            cls(tab).pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    app = DevToolsPro()
    app.mainloop()
