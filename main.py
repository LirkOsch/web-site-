import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
from collections import defaultdict
from pathlib import Path
import shutil
import threading


FILE_CATEGORIES = {
    "Изображения": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Документы": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"],
    "Архивы": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Аудио": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "Видео": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
    "Код": [".py", ".js", ".html", ".css", ".cpp", ".c", ".h", ".java", ".php", ".rb", ".go", ".ts", ".sql"],
    "Исполняемые": [".exe", ".msi", ".bat", ".sh", ".dll"],
}


class FolderOrganizer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_folder = None
        self.build()

    def build(self):
        path_frame = ttk.Frame(self)
        path_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(path_frame, text="Папка:").pack(side="left")
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(path_frame, text="Обзор", command=self.browse_folder).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.organize_frame = ttk.Frame(notebook)
        self.duplicate_frame = ttk.Frame(notebook)
        self.analyze_frame = ttk.Frame(notebook)

        notebook.add(self.organize_frame, text="Сортировка")
        notebook.add(self.duplicate_frame, text="Дубликаты")
        notebook.add(self.analyze_frame, text="Анализ")

        self.build_organize()
        self.build_duplicate()
        self.build_analyze()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.current_folder = folder

    def get_files_in_folder(self, folder):
        files = []
        for entry in os.scandir(folder):
            if entry.is_file():
                files.append(entry.path)
        return files

    def categorize_file(self, filepath):
        ext = Path(filepath).suffix.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return "Прочее"

    # ===== Organize Tab =====
    def build_organize(self):
        ttk.Label(self.organize_frame, text="Сортировка файлов по категориям",
                  font=("", 14, "bold")).pack(pady=(15, 5))
        ttk.Label(self.organize_frame,
                  text="Файлы будут перемещены в папки по типам (Изображения, Документы, ...)",
                  wraplength=500).pack(pady=5)
        ttk.Label(self.organize_frame, text="Несортированные файлы попадут в папку 'Прочее'",
                  wraplength=500, foreground="gray").pack(pady=2)

        preview_frame = ttk.Frame(self.organize_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)

        self.organize_text = tk.Text(preview_frame, height=8, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.organize_text.yview)
        self.organize_text.configure(yscrollcommand=scrollbar.set)
        self.organize_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.organize_progress = ttk.Progressbar(self.organize_frame, mode="determinate")
        self.organize_progress.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(self.organize_frame)
        btn_frame.pack(fill="x", pady=5)
        self.organize_btn = ttk.Button(btn_frame, text="Предпросмотр", command=self.preview_organize)
        self.organize_btn.pack(side="left", padx=5)
        self.run_organize_btn = ttk.Button(btn_frame, text="Выполнить сортировку",
                                           command=self.run_organize)
        self.run_organize_btn.pack(side="left", padx=5)

    def preview_organize(self):
        if not self.current_folder:
            messagebox.showwarning("Ошибка", "Выберите папку")
            return

        files = self.get_files_in_folder(self.current_folder)
        if not files:
            messagebox.showinfo("Инфо", "В папке нет файлов")
            return

        categorized = defaultdict(list)
        for f in files:
            cat = self.categorize_file(f)
            categorized[cat].append(os.path.basename(f))

        self.organize_text.configure(state="normal")
        self.organize_text.delete("1.0", "end")
        for cat in sorted(categorized.keys()):
            names = sorted(categorized[cat])
            self.organize_text.insert("end", f"📁 {cat} ({len(names)} файлов)\n")
            for fn in names[:10]:
                self.organize_text.insert("end", f"   ├ {fn}\n")
            if len(names) > 10:
                self.organize_text.insert("end", f"   └ ... и ещё {len(names) - 10}\n")
        self.organize_text.configure(state="disabled")

    def run_organize(self):
        if not self.current_folder:
            messagebox.showwarning("Ошибка", "Выберите папку")
            return
        self.organize_btn.configure(state="disabled")
        self.run_organize_btn.configure(state="disabled")
        self.organize_progress["value"] = 0
        threading.Thread(target=self._organize_thread, daemon=True).start()

    def _organize_thread(self):
        files = self.get_files_in_folder(self.current_folder)
        total = len(files)
        categorized = defaultdict(list)
        for f in files:
            cat = self.categorize_file(f)
            categorized[cat].append(f)

        processed = 0
        for cat, file_list in categorized.items():
            target_dir = os.path.join(self.current_folder, cat)
            os.makedirs(target_dir, exist_ok=True)
            for f in file_list:
                try:
                    dest = os.path.join(target_dir, os.path.basename(f))
                    if os.path.normpath(f) != os.path.normpath(dest):
                        shutil.move(f, dest)
                except Exception:
                    pass
                processed += 1
                self.organize_progress["value"] = (processed / total) * 100

        self.after(0, self._organize_done)

    def _organize_done(self):
        self.organize_btn.configure(state="normal")
        self.run_organize_btn.configure(state="normal")
        messagebox.showinfo("Готово", "Сортировка завершена!")
        self.preview_organize()

    # ===== Duplicate Tab =====
    def build_duplicate(self):
        ttk.Label(self.duplicate_frame, text="Поиск дубликатов файлов",
                  font=("", 14, "bold")).pack(pady=(15, 5))
        ttk.Label(self.duplicate_frame,
                  text="Поиск файлов с одинаковым содержимым (по MD5 хешу)",
                  wraplength=500).pack(pady=5)

        inner = ttk.Frame(self.duplicate_frame)
        inner.pack(fill="both", expand=True, pady=10)

        self.duplicate_text = tk.Text(inner, height=10, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(inner, orient="vertical", command=self.duplicate_text.yview)
        self.duplicate_text.configure(yscrollcommand=scrollbar.set)
        self.duplicate_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.dup_progress = ttk.Progressbar(self.duplicate_frame, mode="determinate")
        self.dup_progress.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(self.duplicate_frame)
        btn_frame.pack(fill="x", pady=5)
        self.dup_btn = ttk.Button(btn_frame, text="Найти дубликаты", command=self.find_duplicates)
        self.dup_btn.pack(side="left", padx=5)

    def find_duplicates(self):
        if not self.current_folder:
            messagebox.showwarning("Ошибка", "Выберите папку")
            return
        self.dup_btn.configure(state="disabled")
        self.dup_progress["value"] = 0
        threading.Thread(target=self._find_duplicates_thread, daemon=True).start()

    def _find_duplicates_thread(self):
        files = self.get_files_in_folder(self.current_folder)
        total = len(files)
        hash_map = {}
        duplicates = defaultdict(list)

        for i, f in enumerate(files):
            try:
                with open(f, "rb") as fh:
                    file_hash = hashlib.md5(fh.read()).hexdigest()
                if file_hash in hash_map:
                    duplicates[file_hash].append(os.path.basename(f))
                else:
                    hash_map[file_hash] = os.path.basename(f)
            except Exception:
                pass
            self.dup_progress["value"] = ((i + 1) / total) * 100

        self.after(0, lambda: self._display_duplicates(duplicates, hash_map))

    def _display_duplicates(self, duplicates, hash_map):
        self.duplicate_text.configure(state="normal")
        self.duplicate_text.delete("1.0", "end")
        found = False
        for file_hash, file_list in duplicates.items():
            if file_list:
                found = True
                original = hash_map[file_hash]
                self.duplicate_text.insert("end", f"🔄 Дубликаты ({len(file_list) + 1} шт):\n")
                self.duplicate_text.insert("end", f"   └ {original}\n")
                for fn in file_list:
                    self.duplicate_text.insert("end", f"   └ {fn}\n")
        if not found:
            self.duplicate_text.insert("end", "✅ Дубликаты не найдены")
        self.duplicate_text.configure(state="disabled")
        self.dup_btn.configure(state="normal")

    # ===== Analyze Tab =====
    def build_analyze(self):
        ttk.Label(self.analyze_frame, text="Анализ размера папки",
                  font=("", 14, "bold")).pack(pady=(15, 5))

        inner = ttk.Frame(self.analyze_frame)
        inner.pack(fill="both", expand=True, pady=10)

        self.analyze_text = tk.Text(inner, height=12, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(inner, orient="vertical", command=self.analyze_text.yview)
        self.analyze_text.configure(yscrollcommand=scrollbar.set)
        self.analyze_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.analyze_progress = ttk.Progressbar(self.analyze_frame, mode="determinate")
        self.analyze_progress.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(self.analyze_frame)
        btn_frame.pack(fill="x", pady=5)
        self.analyze_btn = ttk.Button(btn_frame, text="Анализировать", command=self.analyze_folder)
        self.analyze_btn.pack(side="left", padx=5)

    def analyze_folder(self):
        if not self.current_folder:
            messagebox.showwarning("Ошибка", "Выберите папку")
            return
        self.analyze_btn.configure(state="disabled")
        self.analyze_progress["value"] = 0
        threading.Thread(target=self._analyze_thread, daemon=True).start()

    def _analyze_thread(self):
        categories = defaultdict(list)
        for f in self.get_files_in_folder(self.current_folder):
            cat = self.categorize_file(f)
            categories[cat].append(f)

        results = []
        total_files = 0
        for cat, file_list in categories.items():
            size = sum(os.path.getsize(f) for f in file_list if os.path.exists(f))
            total_files += len(file_list)
            results.append((cat, len(file_list), size))

        results.sort(key=lambda x: x[2], reverse=True)
        self.after(0, lambda: self._display_analyze(results, total_files))

    def _display_analyze(self, results, total_files):
        self.analyze_text.configure(state="normal")
        self.analyze_text.delete("1.0", "end")
        self.analyze_text.insert("end", f"Всего файлов: {total_files}\n\n")
        for cat, count, size in results:
            size_str = self.format_size(size)
            max_bar = 20
            bar_len = max_bar if size > 0 else 1
            bar = "█" * int(bar_len)
            self.analyze_text.insert("end", f"{cat}:\n")
            self.analyze_text.insert("end", f"   Файлов: {count}  |  {size_str}\n")
            self.analyze_text.insert("end", f"   [{bar}]\n\n")
        self.analyze_text.configure(state="disabled")
        self.analyze_btn.configure(state="normal")

    def format_size(self, size):
        for unit in ["Б", "КБ", "МБ", "ГБ"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ТБ"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Folder Organizer")
        self.geometry("650x550")
        self.minsize(500, 400)

        style = ttk.Style()
        style.theme_use("vista")

        FolderOrganizer(self).pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
