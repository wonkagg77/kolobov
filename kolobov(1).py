import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("850x550")

        # Данные о книгах
        self.books = []          # все книги
        self.filtered_books = [] # отфильтрованные

        # Создание интерфейса
        self.create_input_frame()
        self.create_table()
        self.create_filter_frame()

        # Загрузка сохранённых данных
        self.load_data()

    def create_input_frame(self):
        """Форма для добавления новой книги"""
        frame = tk.LabelFrame(self.root, text="Добавить книгу", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        # Название
        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="e", padx=2)
        self.title_entry = tk.Entry(frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        # Автор
        tk.Label(frame, text="Автор:").grid(row=0, column=2, sticky="e", padx=2)
        self.author_entry = tk.Entry(frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=2)

        # Жанр
        tk.Label(frame, text="Жанр:").grid(row=0, column=4, sticky="e", padx=2)
        self.genre_entry = tk.Entry(frame, width=15)
        self.genre_entry.grid(row=0, column=5, padx=5, pady=2)

        # Количество страниц
        tk.Label(frame, text="Страниц:").grid(row=0, column=6, sticky="e", padx=2)
        self.pages_entry = tk.Entry(frame, width=8)
        self.pages_entry.grid(row=0, column=7, padx=5, pady=2)

        # Кнопка добавления
        btn_add = tk.Button(frame, text="Добавить книгу", command=self.add_book)
        btn_add.grid(row=0, column=8, padx=10)

    def create_table(self):
        """Таблица для отображения списка книг"""
        self.tree = ttk.Treeview(self.root, columns=("title", "author", "genre", "pages"), show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)

    def create_filter_frame(self):
        """Панель фильтрации"""
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(frame, text="Жанр:").grid(row=0, column=0, sticky="e")
        self.filter_genre = tk.Entry(frame, width=15)
        self.filter_genre.grid(row=0, column=1, padx=5)

        # Фильтр по страницам (> указанного числа)
        tk.Label(frame, text="Страниц больше:").grid(row=0, column=2, sticky="e")
        self.filter_pages = tk.Entry(frame, width=8)
        self.filter_pages.grid(row=0, column=3, padx=5)

        # Кнопки
        btn_filter = tk.Button(frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)

        btn_reset = tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter)
        btn_reset.grid(row=0, column=5, padx=10)

    def validate_fields(self, title, author, genre, pages_str):
        """Проверка корректности ввода"""
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return False
        try:
            pages = int(pages_str)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return False
        return True

    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not self.validate_fields(title, author, genre, pages_str):
            return

        pages = int(pages_str)
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.save_data()
        self.apply_filter()   # обновить отображение с учётом фильтра
        self.clear_input_fields()

    def clear_input_fields(self):
        """Очистка полей ввода после добавления"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def apply_filter(self):
        """Фильтрация книг по жанру и/или количеству страниц"""
        genre_filter = self.filter_genre.get().strip()
        pages_filter_str = self.filter_pages.get().strip()

        filtered = self.books[:]

        # Фильтр по жанру (без учёта регистра)
        if genre_filter:
            filtered = [b for b in filtered if genre_filter.lower() in b["genre"].lower()]

        # Фильтр по страницам (больше указанного числа)
        if pages_filter_str:
            try:
                pages_limit = int(pages_filter_str)
                filtered = [b for b in filtered if b["pages"] > pages_limit]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр по страницам должен быть целым числом!")
                return

        self.filtered_books = filtered
        self.update_table()

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_genre.delete(0, tk.END)
        self.filter_pages.delete(0, tk.END)
        self.apply_filter()

    def update_table(self):
        """Обновление таблицы отфильтрованными данными"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for book in self.filtered_books:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def save_data(self):
        """Сохранение всех книг в JSON-файл"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=4, ensure_ascii=False)

    def load_data(self):
        """Загрузка данных из JSON-файла при запуске"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                self.apply_filter()
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Файл данных повреждён. Будет создан новый.")
                self.books = []

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
