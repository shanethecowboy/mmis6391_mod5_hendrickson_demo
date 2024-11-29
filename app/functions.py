from .db_connect import get_db

# make a function that gets the total portfolio value
def get_portfolio_value():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT SUM(transactions.quantity * transactions.price_paid) AS total_value
        FROM transactions
    ''')
    total_value = cursor.fetchone()

    return total_value['total_value']