
import sqlite3
import os

try:
    from .expense_tracker import get_total_expenses
except ImportError:
    from expense_tracker import get_total_expenses


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
# 2. INITIALIZE BUDGET DATABASE TABLE
# ==========================================

def initialize_budget_database():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_budgets (
            user_id TEXT PRIMARY KEY,
            budget_amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'MYR',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# 3. SET TRAVEL BUDGET
# ==========================================

def set_travel_budget(user_id, budget_amount):

    if budget_amount <= 0:
        raise ValueError("Budget amount must be greater than zero.")

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO travel_budgets (
            user_id,
            budget_amount,
            currency
        )
        VALUES (?, ?, 'MYR')
        ON CONFLICT(user_id)
        DO UPDATE SET
            budget_amount = excluded.budget_amount,
            currency = excluded.currency,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, budget_amount))

    connection.commit()
    connection.close()

    return budget_amount


# ==========================================
# 4. GET TRAVEL BUDGET
# ==========================================

def get_travel_budget(user_id):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT budget_amount
        FROM travel_budgets
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


# ==========================================
# 5. GET BUDGET SUMMARY
# ==========================================

def get_budget_summary(user_id):

    budget = get_travel_budget(user_id)

    if budget is None:
        return None

    total_expenses = get_total_expenses(user_id)

    remaining_budget = budget - total_expenses

    if budget > 0:
        budget_used_percentage = (
            total_expenses / budget
        ) * 100
    else:
        budget_used_percentage = 0

    return {
        "total_budget": budget,
        "total_expenses": total_expenses,
        "remaining_budget": remaining_budget,
        "budget_used_percentage": round(
            budget_used_percentage, 2
        )
    }


# ==========================================
# 6. CHECK BUDGET STATUS
# ==========================================

def check_budget_status(user_id):

    summary = get_budget_summary(user_id)

    if summary is None:
        return "No travel budget has been set."

    remaining = summary["remaining_budget"]
    percentage = summary["budget_used_percentage"]

    if remaining < 0:
        return "You have exceeded your travel budget."

    elif remaining == 0:
        return "You have used your entire travel budget."

    elif percentage >= 80:
        return "Warning: You have used 80% or more of your travel budget."

    else:
        return "Your travel budget is within the limit."


# ==========================================
# 7. INITIALIZE DATABASE AUTOMATICALLY
# ==========================================

initialize_budget_database()
