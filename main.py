import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Другое"]

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("500x500")
        self.data = load_data()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        frm = tk.Frame(self)
        frm.pack(padx=10, pady=10)

        # Форма ввода
        tk.Label(frm, text="Сумма:").grid(row=0, column=0)
        self.amount_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.amount_var).grid(row=0, column=1)

        tk.Label(frm, text="Категория:").grid(row=1, column=0)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        tk.OptionMenu(frm, self.category_var, *CATEGORIES).grid(row=1, column=1)

        tk.Label(frm, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0)
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        tk.Entry(frm, textvariable=self.date_var).grid(row=2, column=1)

        tk.Button(frm, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=5)

        # Фильтрация
        filter_frm = tk.Frame(self)
        filter_frm.pack(pady=5)
        tk.Label(filter_frm, text="Категория:").grid(row=0, column=0)
        self.filter_cat_var = tk.StringVar(value="Все")
        tk.OptionMenu(filter_frm, self.filter_cat_var, "Все", *CATEGORIES).grid(row=0, column=1)
        tk.Label(filter_frm, text="Дата с:").grid(row=0, column=2)
        self.filter_date_from = tk.StringVar()
        tk.Entry(filter_frm, textvariable=self.filter_date_from, width=10).grid(row=0, column=3)
        tk.Label(filter_frm, text="по:").grid(row=0, column=4)
        self.filter_date_to = tk.StringVar()
        tk.Entry(filter_frm, textvariable=self.filter_date_to, width=10).grid(row=0, column=5)
        tk.Button(filter_frm, text="Показать", command=self.refresh_table).grid(row=0, column=6, padx=5)
        tk.Button(filter_frm, text="Сбросить", command=self.reset_filters).grid(row=0, column=7)

        # Таблица расходов
        self.tree = ttk.Treeview(self, columns=("amount", "category", "date"), show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Сумма
        self.sum_label = tk.Label(self, text="")
        self.sum_label.pack(pady=5)

    def add_expense(self):
        # Проверка суммы
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return
        # Проверка даты
        date_str = self.date_var.get()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return
        category = self.category_var.get()
        item = {"amount": amount, "category": category, "date": date_str}
        self.data.append(item)
        save_data(self.data)
        self.refresh_table()
        self.amount_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.date_var.set(datetime.today().strftime("%Y-%m-%d"))

    def refresh_table(self):
        # Очистка
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Получить фильтрованные данные
        filtered = self.filter_data()
        # Отображение
        for item in filtered:
            self.tree.insert("", tk.END, values=(item["amount"], item["category"], item["date"]))
        # Подсчёт суммы
        total = sum(item["amount"] for item in filtered)
        self.sum_label.config(text=f"Сумма расходов за выбранный период: {total:.2f} руб.")

    def filter_data(self):
        cat = self.filter_cat_var.get()
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()
        data = self.data
        if cat != "Все":
            data = [d for d in data if d["category"] == cat]
        # Фильтрация по дате
        if date_from:
            try:
                dt_from = datetime.strptime(date_from, "%Y-%m-%d")
                data = [d for d in data if datetime.strptime(d["date"], "%Y-%m-%d") >= dt_from]
            except ValueError:
                messagebox.showerror("Ошибка", "Дата с: неверный формат!")
        if date_to:
            try:
                dt_to = datetime.strptime(date_to, "%Y-%m-%d")
                data = [d for d in data if datetime.strptime(d["date"], "%Y-%m-%d") <= dt_to]
            except ValueError:
                messagebox.showerror("Ошибка", "Дата по: неверный формат!")
        return data

    def reset_filters(self):
        self.filter_cat_var.set("Все")
        self.filter_date_from.set("")
        self.filter_date_to.set("")
        self.refresh_table()

if __name__ == "__main__":
    ExpenseTracker().mainloop()
