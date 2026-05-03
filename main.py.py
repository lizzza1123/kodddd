import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

HISTORY_FILE = "history.json"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Загрузка истории из JSON
        self.history = self.load_history()

        # ---------- Блок настроек ----------
        settings_frame = ttk.LabelFrame(root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(settings_frame, from_=1, to=128,
                                      orient="horizontal", variable=self.length_var,
                                      command=self.on_scale_change)
        self.length_scale.grid(row=0, column=1, sticky="ew", padx=5)
        self.length_label = ttk.Label(settings_frame, text="12", width=3)
        self.length_label.grid(row=0, column=2, padx=5)
        settings_frame.columnconfigure(1, weight=1)

        # Чекбоксы категорий символов
        self.use_letters = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        self.use_digits = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

        self.use_special = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Специальные символы (!@#$%^&*...)", variable=self.use_special).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        # Кнопка генерации
        ttk.Button(settings_frame, text="Сгенерировать", command=self.generate_password).grid(row=4, column=0, columnspan=3, pady=10)

        # ---------- Блок результата ----------
        result_frame = ttk.Frame(root)
        result_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(result_frame, text="Сгенерированный пароль:").pack(anchor="w")
        self.result_var = tk.StringVar()
        result_entry = ttk.Entry(result_frame, textvariable=self.result_var, state="readonly", font=("Consolas", 12))
        result_entry.pack(fill="x", pady=2)

        # ---------- Блок истории ----------
        history_frame = ttk.LabelFrame(root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица (Listbox) с прокруткой
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, height=10)
        self.history_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопка очистки истории
        ttk.Button(history_frame, text="Очистить историю", command=self.clear_history).pack(pady=5)

        # Заполнить историю из файла
        self.update_history_display()

    def on_scale_change(self, event=None):
        """Обновление метки длины при перемещении ползунка."""
        self.length_label.config(text=str(int(self.length_var.get())))

    def generate_password(self):
        """Генерация пароля с учётом выбранных параметров."""
        length = int(self.length_var.get())
        use_letters = self.use_letters.get()
        use_digits = self.use_digits.get()
        use_special = self.use_special.get()

        if not any([use_letters, use_digits, use_special]):
            messagebox.showerror("Ошибка", "Необходимо выбрать хотя бы один тип символов.")
            return

        # Составляем алфавит символов
        chars = ""
        if use_letters:
            chars += string.ascii_letters  # A-Z a-z
        if use_digits:
            chars += string.digits
        if use_special:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

        # Гарантируем, что каждый выбранный тип встретится хотя бы один раз
        password_list = []
        if use_letters:
            password_list.append(random.choice(string.ascii_letters))
        if use_digits:
            password_list.append(random.choice(string.digits))
        if use_special:
            password_list.append(random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?/~`"))

        # Дополняем до нужной длины случайными символами из общего алфавита
        remaining = length - len(password_list)
        password_list.extend(random.choice(chars) for _ in range(remaining))
        random.shuffle(password_list)
        password = "".join(password_list)

        # Отображаем результат
        self.result_var.set(password)

        # Сохраняем в историю и файл
        self.history.append(password)
        self.save_history()
        self.update_history_display()

    def load_history(self):
        """Чтение истории из JSON-файла."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        """Сохранение истории в JSON-файл."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def update_history_display(self):
        """Обновление Listbox истории."""
        self.history_listbox.delete(0, tk.END)
        for pwd in reversed(self.history[-50:]):  # показываем последние 50
            self.history_listbox.insert(tk.END, pwd)

    def clear_history(self):
        """Очистка истории с подтверждением."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить историю паролей?"):
            self.history.clear()
            self.save_history()
            self.update_history_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
    
