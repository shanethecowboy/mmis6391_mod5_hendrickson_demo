from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db

transactions = Blueprint('transactions', __name__)

@transactions.route('/transactions', methods=['GET', 'POST'])
def transaction():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new transaction
    if request.method == 'POST':
        transaction_date = request.form['transaction_date']
        quantity = request.form['quantity']
        price_paid = request.form['price_paid']
        ticker_id = request.form['ticker_id']
        account_id = request.form['account_id']

        # Insert the new transaction into the database
        cursor.execute('''INSERT INTO transactions 
                          (transaction_date, quantity, price_paid, ticker_id, account_id) 
                          VALUES (%s, %s, %s, %s, %s)''',
                       (transaction_date, quantity, price_paid, ticker_id, account_id))
        db.commit()

        flash('New transaction added successfully!', 'success')
        return redirect(url_for('transactions.transaction'))

    # Handle GET request to display all transactions
    cursor.execute('SELECT * FROM transactions')
    all_transactions = cursor.fetchall()
    return render_template('transactions.html', all_transactions=all_transactions)

@transactions.route('/update_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def update_transaction(transaction_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Update the transaction's details
        transaction_date = request.form['transaction_date']
        quantity = request.form['quantity']
        price_paid = request.form['price_paid']
        ticker_id = request.form['ticker_id']
        account_id = request.form['account_id']

        cursor.execute('''UPDATE transactions 
                          SET transaction_date = %s, quantity = %s, price_paid = %s, 
                              ticker_id = %s, account_id = %s 
                          WHERE transaction_id = %s''',
                       (transaction_date, quantity, price_paid, ticker_id, account_id, transaction_id))
        db.commit()

        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.transaction'))

    # GET method: fetch transaction's current data for pre-populating the form
    cursor.execute('SELECT * FROM transactions WHERE transaction_id = %s', (transaction_id,))
    current_transaction = cursor.fetchone()
    return render_template('update_transaction.html', current_transaction=current_transaction)

@transactions.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the transaction
    cursor.execute('DELETE FROM transactions WHERE transaction_id = %s', (transaction_id,))
    db.commit()

    flash('Transaction deleted successfully!', 'danger')
    return redirect(url_for('transactions.transaction'))
