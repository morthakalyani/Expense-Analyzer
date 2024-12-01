
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Database setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  salary REAL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date TEXT,
                  category TEXT,
                  amount REAL,
                  description TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
conn.commit()

class ExpenseAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Analyzer")
        self.geometry("600x400")
        self.active_user = None
        self.switch_to_login()

    def switch_to_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        LoginPage(self)

    def switch_to_signup(self):
        for widget in self.winfo_children():
            widget.destroy()
        SignupPage(self)

    def switch_to_home(self):
        for widget in self.winfo_children():
            widget.destroy()
        HomePage(self)

class LoginPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack()
        tk.Label(self, text="Login", font=("Arial", 24)).pack(pady=10)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=5)
        tk.Button(self, text="Sign Up", command=parent.switch_to_signup).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            self.parent.active_user = user[0]
            self.parent.switch_to_home()
        else:
            messagebox.showerror("Error", "Invalid username or password")

class SignupPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack()
        tk.Label(self, text="Sign Up", font=("Arial", 24)).pack(pady=10)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Label(self, text="Salary:").pack()
        self.salary_entry = tk.Entry(self)
        self.salary_entry.pack()

        tk.Button(self, text="Sign Up", command=self.signup).pack(pady=5)
        tk.Button(self, text="Back to Login", command=parent.switch_to_login).pack()

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        salary = self.salary_entry.get()
        try:
            cursor.execute("INSERT INTO users (username, password, salary) VALUES (?, ?, ?)", (username, password, float(salary)))
            conn.commit()
            messagebox.showinfo("Success", "Account created!")
            self.parent.switch_to_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
class HomePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack()
        tk.Label(self, text="Expense Analyzer", font=("Arial", 24)).pack(pady=10)

        tk.Button(self, text="Add Expense", command=self.add_expense).pack(pady=5)
        tk.Button(self, text="View All Expenses", command=self.view_all_expenses).pack(pady=5)
        tk.Button(self, text="View Statistics", command=self.view_statistics).pack(pady=5)
        tk.Button(self, text="Logout", command=parent.switch_to_login).pack(pady=5)

        # Code Red button for deleting all data
        code_red_button = tk.Button(self, text="Code Red: Delete All Data", command=self.delete_all_data, fg="white", bg="red", font=("Arial", 12, "bold"))
        code_red_button.pack(pady=15)

    def add_expense(self):
        AddExpensePage(self.parent)

    def view_statistics(self):
        StatisticsPage(self.parent)

    def view_all_expenses(self):
        ViewExpensesPage(self.parent)

    def delete_all_data(self):
        """Prompt the user for confirmation and delete all expense data for the active user if confirmed."""
        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all your expense data? This action cannot be undone.")
        if response:
            user_id = self.parent.active_user
            cursor.execute("DELETE FROM expenses WHERE user_id=?", (user_id,))
            conn.commit()
            messagebox.showinfo("Data Deleted", "All your expense data has been permanently deleted.")


class AddExpensePage(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Expense")
        tk.Label(self, text="Date:").grid(row=0, column=0, padx=10, pady=5)
        self.date_entry = DateEntry(self, width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Category:").grid(row=1, column=0, padx=10, pady=5)
        self.category_entry = ttk.Combobox(self, values=["Food", "Transport", "Entertainment", "Bills", "Other"])
        self.category_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Amount:").grid(row=2, column=0, padx=10, pady=5)
        self.amount_entry = tk.Entry(self)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Description:").grid(row=3, column=0, padx=10, pady=5)
        self.description_entry = tk.Entry(self)
        self.description_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self, text="Add", command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=10)

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        user_id = self.master.active_user
        cursor.execute("INSERT INTO expenses (user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                       (user_id, date, category, float(amount), description))
        conn.commit()
        messagebox.showinfo("Success", "Expense added successfully")
        self.destroy()

class ViewExpensesPage(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("All Expenses")
        self.geometry("600x300")

        tk.Label(self, text="All Expenses", font=("Arial", 18)).pack(pady=10)

        # Table setup
        self.tree = ttk.Treeview(self, columns=("Date", "Category", "Amount", "Description"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Description", text="Description")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Fetching and inserting data
        self.load_expenses()

    def load_expenses(self):
        user_id = self.master.active_user
        cursor.execute("SELECT date, category, amount, description FROM expenses WHERE user_id=?", (user_id,))
        expenses = cursor.fetchall()
        for expense in expenses:
            self.tree.insert("", tk.END, values=expense)



class StatisticsPage(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Statistics")
        self.geometry("600x550")

        tk.Label(self, text="View Expense Statistics", font=("Arial", 18)).pack(pady=10)
        
        # Dropdown menus for Month, Year, and Category
        tk.Label(self, text="Select Month:").pack()
        self.month_var = tk.StringVar()
        self.month_var.set("All")
        self.month_menu = ttk.Combobox(self, textvariable=self.month_var, values=["All"] + [datetime(2023, m, 1).strftime('%B') for m in range(1, 13)])
        self.month_menu.pack()

        tk.Label(self, text="Select Year:").pack()
        self.year_var = tk.StringVar()
        self.year_var.set("All")
        self.year_menu = ttk.Combobox(self, textvariable=self.year_var, values=["All"] + [str(y) for y in range(2020, datetime.now().year + 1)])
        self.year_menu.pack()

        tk.Label(self, text="Select Category:").pack()
        self.category_var = tk.StringVar()
        self.category_var.set("All")
        self.category_menu = ttk.Combobox(self, textvariable=self.category_var, values=["All", "Food", "Transport", "Entertainment", "Bills", "Other"])
        self.category_menu.pack()
        
        # Buttons for Pie Chart and Bar Chart
        tk.Button(self, text="View Category Distribution (Pie Chart)", command=self.view_pie_chart).pack(pady=5)
        tk.Button(self, text="View Category Totals (Bar Chart)", command=self.view_bar_chart).pack(pady=5)

    
    def view_bar_chart(self):
    # Retrieve selected filter values
        selected_month = self.month_var.get()
        selected_year = self.year_var.get()
        selected_category = self.category_var.get()
        user_id = self.master.active_user

    # Build the base SQL query
        query = "SELECT category, SUM(amount) FROM expenses WHERE user_id=?"
        params = [user_id]

    # Apply filters for year, month, and category if specified
        if selected_year != "All":
            query += " AND strftime('%Y', date) = ?"
            params.append(selected_year)
        if selected_month != "All":
            month_num = datetime.strptime(selected_month, "%B").month
            query += " AND strftime('%m', date) = ?"
            params.append(f"{month_num:02}")  # Ensures two-digit month format
        if selected_category != "All":
            query += " AND category = ?"
            params.append(selected_category)

        query += " GROUP BY category"

    # Execute the query and fetch results
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

    # Prepare data for the bar chart
        categories = [row[0] for row in results]
        amounts = [row[1] for row in results]

    # Display bar chart if data is available, else show info message
        if amounts:
            fig, ax = plt.subplots()
            ax.bar(categories, amounts, color="skyblue")
            ax.set_title("Total Expenses by Category")
            ax.set_xlabel("Category")
            ax.set_ylabel("Total Amount")

        # Display chart in Tkinter window (ensure the previous chart is removed first)
            for widget in self.winfo_children():
                if isinstance(widget, FigureCanvasTkAgg):
                 widget.get_tk_widget().destroy()  # Remove old chart

            chart = FigureCanvasTkAgg(fig, self)
            chart.get_tk_widget().pack(pady=10)
            chart.draw()
        else:
            messagebox.showinfo("No Data", "No expenses found for the selected criteria.")

    def view_pie_chart(self):
    # Retrieve selected filter values
        selected_month = self.month_var.get()
        selected_year = self.year_var.get()
        selected_category = self.category_var.get()
        user_id = self.master.active_user

    # Build the base SQL query
        query = "SELECT category, SUM(amount) FROM expenses WHERE user_id=?"
        params = [user_id]

    # Apply filters for month, year, and category if not set to 'All'
        if selected_year != "All":
            query += " AND strftime('%Y', date) = ?"
            params.append(selected_year)
        if selected_month != "All":
            month_num = datetime.strptime(selected_month, '%B').month
            query += " AND strftime('%m', date) = ?"
            params.append(f"{month_num:02}")
        if selected_category != "All":
            query += " AND category = ?"
            params.append(selected_category)

        query += " GROUP BY category"

    # Execute the query
        cursor.execute(query, params)
        results = cursor.fetchall()

    # Prepare data for the pie chart
        categories = [row[0] for row in results]
        amounts = [row[1] for row in results]

        if amounts:
            plt.figure(figsize=(6, 6))
            plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
            plt.title(f"Expense Distribution ({selected_year}, {selected_month}, {selected_category})")
            plt.show()
        else:
            messagebox.showinfo("No Data", "No expenses match the selected criteria.")

if __name__ == "__main__":
    app = ExpenseAnalyzer()
    app.mainloop()