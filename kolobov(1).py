import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "training_data.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Данные тренировок
        self.trainings = []
        self.filtered_trainings = []

        # Поля ввода
        self.create_input_frame()
        self.create_table()
        self.create_filter_frame()

        # Загрузка данных при старте
        self.load_data()

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить тренировку", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e")
        self.date_entry = tk.Entry(frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Тип тренировки
        tk.Label(frame, text="Тип тренировки:").grid(row=0, column=2, sticky="e")
        self.type_entry = ttk.Combobox(frame, values=["Бег", "Велосипед", "Плавание", "Йога", "Силовая"], width=15)
        self.type_entry.grid(row=0, column=3, padx=5)
        self.type_entry.set("Бег")

        # Длительность
        tk.Label(frame, text="Длительность (мин):").grid(row=0, column=4, sticky="e")
        self.duration_entry = tk.Entry(frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления
        btn_add = tk.Button(frame, text="Добавить тренировку", command=self.add_training)
        btn_add.grid(row=0, column=6, padx=10)

    def create_table(self):
        # Таблица для отображения тренировок
        self.tree = ttk.Treeview(self.root, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        tk.Label(frame, text="Тип:").grid(row=0, column=0, sticky="e")
        self.filter_type = ttk.Combobox(frame, values=["Все"] + ["Бег", "Велосипед", "Плавание", "Йога", "Силовая"], width=15)
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")

        # Фильтр по дате
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="e")
        self.filter_date = tk.Entry(frame, width=15)
        self.filter_date.grid(row=0, column=3, padx=5)

        # Кнопка фильтрации
        btn_filter = tk.Button(frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)

        # Кнопка сброса фильтра
        btn_reset = tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter)
        btn_reset.grid(row=0, column=5, padx=10)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False

    def add_training(self):
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()

        if not date or not training_type or not duration:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        # Добавление в список
        new_entry = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        self.trainings.append(new_entry)
        self.save_data()
        self.apply_filter()  # обновить отображение с учётом текущего фильтра
        self.clear_input_fields()

    def clear_input_fields(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_entry.set("Бег")
        self.duration_entry.delete(0, tk.END)

    def apply_filter(self):
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()

        filtered = self.trainings[:]

        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]

        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтра!")
                return
            filtered = [t for t in filtered if t["date"] == filter_date]

        self.filtered_trainings = filtered
        self.update_table()

    def reset_filter(self):
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.apply_filter()

    def update_table(self):
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполнить отфильтрованными данными
        for training in self.filtered_trainings:
            self.tree.insert("", "end", values=(training["date"], training["type"], training["duration"]))

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
                self.apply_filter()  # отобразить загруженные данные
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Файл данных повреждён. Будет создан новый.")
                self.trainings = []
        else:
            self.trainings = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()