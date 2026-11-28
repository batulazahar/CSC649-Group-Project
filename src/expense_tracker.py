
import sqlite3
import os

from datetime import date


# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "expenses.db"
)


# ==========================================
# 2. INITIALIZE DATABASE
# ==========================================

def initialize_expense_database():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'MYR',
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# 3. RECORD EXPENSE
# ==========================================

def add_expense(
    user_id,
    amount,
    category,
    description,
    expense_date=None,
    currency="MYR"
):

    if expense_date is None:
        expense_date = date.today().isoformat()

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (
            user_id,
            amount,
            currency,
            category,
            description,
            expense_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        amount,
        currency,
        category,
        description,
        expense_date
    ))

    connection.commit()

    expense_id = cursor.lastrowid

    connection.close()

    return expense_id


# ==========================================
# 4. RETRIEVE USER EXPENSES
# ==========================================

def get_user_expenses(
    user_id,
    expense_date=None
):

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if expense_date:

        cursor.execute("""
            SELECT *
            FROM expenses
            WHERE user_id = ?
            AND expense_date = ?
            ORDER BY created_at DESC
        """, (user_id, expense_date))

    else:

        cursor.execute("""
            SELECT *
            FROM expenses
            WHERE user_id = ?
            ORDER BY expense_date DESC, created_at DESC
        """, (user_id,))

    expenses = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return expenses


# ==========================================
# 5. CALCULATE TOTAL EXPENSES
# ==========================================

def get_total_expenses(
    user_id,
    expense_date=None
):

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    if expense_date:

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ?
            AND expense_date = ?
            AND currency = 'MYR'
        """, (user_id, expense_date))

    else:

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ?
            AND currency = 'MYR'
        """, (user_id,))

    total = cursor.fetchone()[0]

    connection.close()

    return total


# ==========================================
# 6. INITIALIZE DATABASE AUTOMATICALLY
# ==========================================

initialize_expense_database()
