from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db
from app.functions import get_portfolio_value

transactions = Blueprint('transactions', __name__)

@transactions.route('/transactions', methods=['GET', 'POST'])
def transaction():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Debugging: Check if form data is received
        print("Form data received:", request.form)

        # Retrieve form data
        try:
            transaction_date = request.form['transaction_date']
            quantity = request.form['quantity']
            price_paid = request.form['price_paid']
            ticker_id = request.form['ticker_id']
            account_id = request.form['account_id']

            # Debugging: Print the form data to verify it
            print("Transaction Date:", transaction_date)
            print("Quantity:", quantity)
            print("Price Paid:", price_paid)
            print("Ticker ID:", ticker_id)
            print("Account ID:", account_id)

            # Insert new transaction into the database
            cursor.execute('''
                INSERT INTO transactions (transaction_date, quantity, price_paid, ticker_id, account_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (transaction_date, quantity, price_paid, ticker_id, account_id))

            db.commit()

            if cursor.rowcount == 0:
                print("No rows were inserted.")
                flash('Transaction was not added. Please check your input.', 'warning')
            else:
                flash('Transaction added successfully!', 'success')

        except Exception as e:
            db.rollback()
            print("Error occurred:", e)
            flash('An error occurred while adding the transaction.', 'danger')

    # Fetch all transactions with JOIN to get ticker symbol, account name, and total cost
    cursor.execute('''
        SELECT transactions.transaction_id, transactions.transaction_date, transactions.quantity, transactions.price_paid, 
               transactions.quantity * transactions.price_paid AS total_cost, 
               tickers.ticker_symbol, accounts.account_name
        FROM transactions
        JOIN tickers ON transactions.ticker_id = tickers.ticker_id
        JOIN accounts ON transactions.account_id = accounts.account_id
        ORDER BY transactions.transaction_date ASC, accounts.account_name ASC
    ''')
    all_transactions = cursor.fetchall()

    total_portfolio_value = get_portfolio_value()

    # Fetch ticker symbols for dropdown
    cursor.execute('SELECT ticker_id, ticker_symbol FROM tickers')
    all_tickers = cursor.fetchall()

    # Fetch account names for dropdown
    cursor.execute('SELECT account_id, account_name FROM accounts')
    all_accounts = cursor.fetchall()

    return render_template('transactions.html',
                           all_transactions=all_transactions,
                           all_tickers=all_tickers,
                           all_accounts=all_accounts,
                           total_portfolio_value=total_portfolio_value)

@transactions.route('/update_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def update_transaction(transaction_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            # Get the data from the form
            transaction_date = request.form['transaction_date']
            quantity = request.form['quantity']
            price_paid = request.form['price_paid']
            ticker_id = request.form['ticker_id']
            account_id = request.form['account_id']

            # Debugging: print the values being updated
            print(f"Updating transaction_id: {transaction_id}")
            print(f"transaction_date: {transaction_date}, quantity: {quantity}, price_paid: {price_paid}, ticker_id: {ticker_id}, account_id: {account_id}")

            # Execute the update query
            cursor.execute('''
                UPDATE transactions 
                SET transaction_date = %s, quantity = %s, price_paid = %s, 
                    ticker_id = %s, account_id = %s 
                WHERE transaction_id = %s
            ''', (transaction_date, quantity, price_paid, ticker_id, account_id, transaction_id))

            # Commit the changes to the database
            db.commit()

            # Confirm the number of rows affected
            if cursor.rowcount == 0:
                print("No rows were updated. Please check the transaction_id.")
                flash('No transaction was updated. Please check the transaction ID.', 'warning')
            else:
                flash('Transaction updated successfully!', 'success')

        except Exception as e:
            db.rollback()  # Rollback in case of error
            print(f"An error occurred: {e}")
            flash('An error occurred while updating the transaction.', 'danger')

        return redirect(url_for('transactions.transaction'))

    # GET method: fetch transaction's current data for pre-populating the form
    cursor.execute('SELECT * FROM transactions WHERE transaction_id = %s', (transaction_id,))
    current_transaction = cursor.fetchone()

    if current_transaction is None:
        flash('Transaction not found!', 'warning')
        return redirect(url_for('transactions.transaction'))

    # Fetch ticker symbols for dropdown
    cursor.execute('SELECT ticker_id, ticker_symbol FROM tickers')
    all_tickers = cursor.fetchall()

    # Fetch account names for dropdown
    cursor.execute('SELECT account_id, account_name FROM accounts')
    all_accounts = cursor.fetchall()

    return render_template('update_transaction.html', current_transaction=current_transaction, all_tickers=all_tickers, all_accounts=all_accounts)

@transactions.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Execute the delete query
        cursor.execute('DELETE FROM transactions WHERE transaction_id = %s', (transaction_id,))
        db.commit()

        if cursor.rowcount == 0:
            print("No rows were deleted. Please check the transaction_id.")
            flash('No transaction was deleted. Please check the transaction ID.', 'warning')
        else:
            flash('Transaction deleted successfully!', 'danger')

    except Exception as e:
        db.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        flash('An error occurred while deleting the transaction.', 'danger')

    return redirect(url_for('transactions.transaction'))
