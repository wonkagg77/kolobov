import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.data_file = "trainings.json"
        self.trainings = self.load_data()

        # --- Создание виджетов ---
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(root, text="Добавить тренировку")
        input_frame.pack(padx=10, pady=5, fill="x")

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="we")

        # Тип тренировки
        ttk.Label(input_frame, text="Тип:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(input_frame, textvariable=self.type_var,
                                          values=["Кардио", "Сила", "Растяжка", "Йога"])
        self.type_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="we")

        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.duration_entry = ttk.Entry(input_frame)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=2, sticky="we")

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training) \
            .grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица для отображения тренировок
        self.tree = ttk.Treeview(root, columns=("Дата", "Тип", "Длительность"), show="headings")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Длительность", text="Длительность (мин)")
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(root, text="Фильтрация")
        filter_frame.pack(padx=10, pady=5, fill="x")

        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, padx=5, pady=2)
        self.filter_type_var = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                     values=["Все", "Кардио", "Сила", "Растяжка", "Йога"]) \
            .grid(row=0, column=1, padx=5, pady=2)

        # Фильтр по дате (с)
        ttk.Label(filter_frame, text="Дата с:").grid(row=1, column=0, padx=5, pady=2)
        self.filter_date_from = ttk.Entry(filter_frame)
        self.filter_date_from.grid(row=1, column=1, padx=5, pady=2)

        # Фильтр по дате (по)
        ttk.Label(filter_frame, text="Дата по:").grid(row=1, column=2, padx=5, pady=2)
        self.filter_date_to = ttk.Entry(filter_frame)
        self.filter_date_to.grid(row=1, column=3, padx=5, pady=2)

        # Кнопки фильтрации
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter) \
            .grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter) \
            .grid(row=2, column=2, columnspan=2, pady=5)

        # Загрузка данных в таблицу при старте
        self.update_table()

    def add_training(self):
        """Добавляет новую тренировку после валидации."""
        date_str = self.date_entry.get().strip()
        training_type = self.type_var.get().strip()
        duration_str = self.duration_entry.get().strip()

        # Валидация даты
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_str = date.isoformat()  # Приводим к стандартному виду
            if date > datetime.now().date():
                raise ValueError("Дата не может быть в будущем.")
            self.date_entry.config(style="TEntry")
            self.date_entry.update()
            self.date_entry.after(1000,
                                  lambda: self.date_entry.config(style=""))

            # Валидация длительности
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError("Длительность должна быть положительным числом.")
            self.duration_entry.config(style="TEntry")
            self.duration_entry.update()
            self.duration_entry.after(1000,
                                      lambda: self.duration_entry.config(style=""))

            # Добавление в список и сохранение
            new_training = {"date": date_str,
                            "type": training_type,
                            "duration": duration}
            self.trainings.append(new_training)
            self.save_data()
            self.update_table()

            # Очистка полей после успешного добавления
            self.date_entry.delete(0, tk.END)
            self.duration_entry.delete(0, tk.END)
            self.type_combobox.set('')

            messagebox.showinfo("Успех", "Тренировка добавлена!")

        except ValueError as e:
            messagebox.showerror("Ошибка валидации", str(e))

    def update_table(self):
        """Обновляет таблицу Treeview на основе текущих данных."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        for training in sorted(self.trainings,
                               key=lambda x: x['date'],
                               reverse=True):
            self.tree.insert("", tk.END,
                             values=(training['date'],
                                     training['type'],
                                     training['duration']))

    def apply_filter(self):
        """Применяет фильтр по типу и/или дате."""
        filtered_trainings = []

        filter_type = self.filter_type_var.get()
        date_from_str = self.filter_date_from.get().strip()
        date_to_str = self.filter_date_to.get().strip()

        for training in self.trainings:
            # Фильтр по типу
            if filter_type != "Все" and training['type'] != filter_type:
                continue

            # Фильтр по дате (с)
            if date_from_str:
                try:
                    date_from = datetime.strptime(date_from_str,
                                                  "%Y-%m-%d").date()
                    if datetime.strptime(training['date'],
                                         "%Y-%m-%d").date() < date_from:
                        continue
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты 'с'")
                    return

             # Фильтр по дате (по)
             if date_to_str:
                 try:
                     date_to = datetime.strptime(date_to_str,
                                                 "%Y-%m-%d").date()
                     if datetime.strptime(training['date'],
                                          "%Y-%m-%d").date() > date_to:
                         continue
                 except ValueError:
                     messagebox.showerror("Ошибка", "Неверный формат даты 'по'")
                     return

             filtered_trainings.append(training)

         self.display_filtered(filtered_trainings)

    def display_filtered(self, filtered_list):
         """Выводит отфильтрованный список в таблицу."""
         for i in self.tree.get_children():
             self.tree.delete(i)
         for training in sorted(filtered_list,
                                key=lambda x: x['date'],
                                reverse=True):
             self.tree.insert("", tk.END,
                              values=(training['date'],
                                      training['type'],
                                      training['duration']))

    def reset_filter(self):
         """Сбрасывает фильтры и показывает все тренировки."""
         self.filter_type_var.set("Все")
         self.filter_date_from.delete(0, tk.END)
         self.filter_date_to.delete(0, tk.END)
         self.update_table()

    def save_data(self):
         """Сохраняет данные в JSON-файл."""
         with open(self.data_file, 'w', encoding='utf-8') as f:
             json.dump(self.trainings, f,
                       ensure_ascii=False,
                       indent=4)

    def load_data(self):
         """Загружает данные из JSON-файла."""
         try:
             with open(self.data_file, 'r', encoding='utf-8') as f:
                 return json.load(f)
         except FileNotFoundError:
             return []


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()