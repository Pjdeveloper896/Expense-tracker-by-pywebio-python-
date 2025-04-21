import sqlite3
import plotly.graph_objects as go
from pywebio.input import input, select
from pywebio.output import put_text, put_html
from pywebio import start_server
import datetime

# Initialize the SQLite database
conn = sqlite3.connect('expenses.db', check_same_thread=False)  # Required for PyWebIO
cursor = conn.cursor()

# Create the expenses table (if not exists)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense REAL,
        category TEXT,
        date TEXT
    )
''')
conn.commit()

# Function to insert expense into database
def insert_expense(expense_amount, category, date):
    cursor.execute('''
        INSERT INTO expenses (expense, category, date)
        VALUES (?, ?, ?)
    ''', (expense_amount, category, date))
    conn.commit()

# Function to get expenses from the database
def get_expenses():
    cursor.execute('SELECT expense, category, date FROM expenses')
    return cursor.fetchall()

# Function to generate the graph
def generate_graph():
    expenses_data = get_expenses()
    categories = {}
    
    # Aggregate expenses by category
    for expense, category, _ in expenses_data:
        if category not in categories:
            categories[category] = 0
        categories[category] += expense

    # Create bar graph
    fig = go.Figure([go.Bar(x=list(categories.keys()), y=list(categories.values()))])
    fig.update_layout(title='Expenses by Category', xaxis_title='Category', yaxis_title='Amount')
    
    # Convert the graph to HTML to display in PyWebIO
    graph_html = fig.to_html(full_html=False)
    return graph_html

def expense_tracker():
    put_html("<h2>Expense Tracker</h2>")
    
    while True:
        expense_amount = input("Enter your expense amount", type='float')
        category = select("In which field?", options=["food", "transport", "clothes", "medicines", "others"])
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        insert_expense(expense_amount, category, date)
        put_text(f"Added ₹{expense_amount} in {category} on {date}")
        
        show_summary = input("Show summary? (yes/no)", type="text").lower()
        if show_summary == "yes":
            data = get_expenses()
            total = sum([item[0] for item in data])
            put_text(f"Total Expenses: ₹{total}")
            
            category_totals = {}
            for expense, category, _ in data:
                category_totals[category] = category_totals.get(category, 0) + expense

            for cat, amt in category_totals.items():
                put_text(f"{cat}: ₹{amt}")

            # Show bar chart
            put_html(generate_graph())

        continue_tracking = input("Add another? (yes/no)", type="text").lower()
        if continue_tracking != "yes":
            break

if __name__ == '__main__':
    start_server(expense_tracker, port=8080)
