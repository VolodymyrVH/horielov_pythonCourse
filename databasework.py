import sqlite3
import logging
import csv
import requests
from functools import wraps
from valid import (
    validate_user_full_name,
    validate_restricted_field,
    validate_datetime,
    validate_account_number
)

API_KEY = "fca_live_Nzlnz91AgFoWQLTusN3mKFy3nIPPeEOiFu4F5P52"
CURRENCY_API_URL = "https://api.freecurrencyapi.com/v1/latest"


def db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('banking.db')
        cursor = conn.cursor()
        try:
            result = func(cursor, conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            logging.error(f"Database error in {func.__name__}: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()

    return wrapper


def get_exchange_rate(from_currency, to_currency):
    try:
        response = requests.get(CURRENCY_API_URL, params={"apikey": API_KEY, "base_currency": from_currency})
        if response.status_code == 429:
            logging.error("Currency API rate limit exceeded")
            return None
        data = response.json()
        rate = data['data'].get(to_currency)
        if not rate:
            logging.error(f"No exchange rate for {to_currency}")
            return None
        logging.info(f"Retrieved exchange rate: {from_currency} to {to_currency} = {rate}")
        return rate
    except Exception as e:
        logging.error(f"Currency API error: {str(e)}")
        return None


@db_connection
def add_bank(cursor, conn, banks):
    banks = [banks] if isinstance(banks, dict) else banks
    try:
        for bank in banks:
            cursor.execute("INSERT INTO Bank (name) VALUES (?)", (bank['name'],))
        return {"status": "success", "message": f"Added {len(banks)} banks"}
    except sqlite3.IntegrityError as e:
        return {"status": "error", "message": f"Bank name must be unique: {str(e)}"}


@db_connection
def add_user(cursor, conn, users):
    users = [users] if isinstance(users, dict) else users
    try:
        for user in users:
            name, surname = validate_user_full_name(user['user_full_name'])
            cursor.execute(
                "INSERT INTO User (Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?)",
                (name, surname, user.get('Birth_day', ''), user.get('Accounts', ''))
            )
        return {"status": "success", "message": f"Added {len(users)} users"}
    except (ValueError, sqlite3.IntegrityError) as e:
        return {"status": "error", "message": str(e)}


@db_connection
def add_account(cursor, conn, accounts):
    accounts = [accounts] if isinstance(accounts, dict) else accounts
    try:
        for account in accounts:
            validate_restricted_field('Type', account['Type'], ['credit', 'debit'])
            validate_restricted_field('Status', account.get('Status', 'silver'), ['gold', 'silver', 'platinum'])
            account_number = validate_account_number(account['Account_Number'])
            cursor.execute(
                "INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    account['User_id'],
                    account['Type'],
                    account_number,
                    account['Bank_id'],
                    account['Currency'],
                    account['Amount'],
                    account.get('Status', 'silver')
                )
            )
        return {"status": "success", "message": f"Added {len(accounts)} accounts"}
    except (ValueError, sqlite3.IntegrityError) as e:
        return {"status": "error", "message": str(e)}


@db_connection
def add_bank_from_csv(cursor, conn, file_path):
    try:
        count = 0
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'name' not in reader.fieldnames:
                raise ValueError("CSV must contain 'name' column")
            for row in reader:
                cursor.execute("INSERT INTO Bank (name) VALUES (?)", (row['name'],))
                count += 1
        return {"status": "success", "message": f"Added {count} banks from CSV"}
    except Exception as e:
        return {"status": "error", "message": f"CSV processing error: {str(e)}"}


@db_connection
def add_user_from_csv(cursor, conn, file_path):
    try:
        count = 0
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'user_full_name' not in reader.fieldnames:
                raise ValueError("CSV must contain 'user_full_name' column")
            for row in reader:
                name, surname = validate_user_full_name(row['user_full_name'])
                cursor.execute(
                    "INSERT INTO User (Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?)",
                    (name, surname, row.get('Birth_day', ''), row.get('Accounts', ''))
                )
                count += 1
        return {"status": "success", "message": f"Added {count} users from CSV"}
    except Exception as e:
        return {"status": "error", "message": f"CSV processing error: {str(e)}"}


@db_connection
def add_account_from_csv(cursor, conn, file_path):
    try:
        count = 0
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = ['User_id', 'Type', 'Account_Number', 'Bank_id', 'Currency', 'Amount']
            if not all(field in reader.fieldnames for field in required_fields):
                raise ValueError(f"CSV must contain required columns: {', '.join(required_fields)}")
            for row in reader:
                validate_restricted_field('Type', row['Type'], ['credit', 'debit'])
                validate_restricted_field('Status', row.get('Status', 'silver'), ['gold', 'silver', 'platinum'])
                account_number = validate_account_number(row['Account_Number'])
                cursor.execute(
                    "INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        int(row['User_id']),
                        row['Type'],
                        account_number,
                        int(row['Bank_id']),
                        row['Currency'],
                        float(row['Amount']),
                        row.get('Status', 'silver')
                    )
                )
                count += 1
        return {"status": "success", "message": f"Added {count} accounts from CSV"}
    except Exception as e:
        return {"status": "error", "message": f"CSV processing error: {str(e)}"}


@db_connection
def modify_bank(cursor, conn, bank_id, data):
    try:
        cursor.execute("UPDATE Bank SET name = ? WHERE id = ?", (data['name'], bank_id))
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Bank ID {bank_id} not found"}
        return {"status": "success", "message": f"Modified bank ID {bank_id}"}
    except sqlite3.IntegrityError as e:
        return {"status": "error", "message": f"Bank name must be unique: {str(e)}"}


@db_connection
def modify_user(cursor, conn, user_id, data):
    try:
        name, surname = validate_user_full_name(data['user_full_name'])
        cursor.execute(
            "UPDATE User SET Name = ?, Surname = ?, Birth_day = ?, Accounts = ? WHERE id = ?",
            (name, surname, data.get('Birth_day', ''), data.get('Accounts', ''), user_id)
        )
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"User ID {user_id} not found"}
        return {"status": "success", "message": f"Modified user ID {user_id}"}
    except (ValueError, sqlite3.IntegrityError) as e:
        return {"status": "error", "message": str(e)}


@db_connection
def modify_account(cursor, conn, account_id, data):
    try:
        validate_restricted_field('Type', data['Type'], ['credit', 'debit'])
        validate_restricted_field('Status', data.get('Status', 'silver'), ['gold', 'silver', 'platinum'])
        account_number = validate_account_number(data['Account_Number'])
        cursor.execute(
            "UPDATE Account SET User_id = ?, Type = ?, Account_Number = ?, Bank_id = ?, "
            "Currency = ?, Amount = ?, Status = ? WHERE id = ?",
            (
                data['User_id'],
                data['Type'],
                account_number,
                data['Bank_id'],
                data['Currency'],
                data['Amount'],
                data.get('Status', 'silver'),
                account_id
            )
        )
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Account ID {account_id} not found"}
        return {"status": "success", "message": f"Modified account ID {account_id}"}
    except (ValueError, sqlite3.IntegrityError) as e:
        return {"status": "error", "message": str(e)}


@db_connection
def delete_bank(cursor, conn, bank_id):
    cursor.execute("DELETE FROM Bank WHERE id = ?", (bank_id,))
    if cursor.rowcount == 0:
        return {"status": "error", "message": f"Bank ID {bank_id} not found"}
    return {"status": "success", "message": f"Deleted bank ID {bank_id}"}


@db_connection
def delete_user(cursor, conn, user_id):
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        return {"status": "error", "message": f"User ID {user_id} not found"}
    return {"status": "success", "message": f"Deleted user ID {user_id}"}


@db_connection
def delete_account(cursor, conn, account_id):
    cursor.execute("DELETE FROM Account WHERE id = ?", (account_id,))
    if cursor.rowcount == 0:
        return {"status": "error", "message": f"Account ID {account_id} not found"}
    return {"status": "success", "message": f"Deleted account ID {account_id}"}


@db_connection
def transfer_money(cursor, conn, sender_account_id, receiver_account_id, amount, currency, datetime_str=None):
    try:
        cursor.execute("SELECT Bank_id, Currency, Amount FROM Account WHERE id = ?", (sender_account_id,))
        sender = cursor.fetchone()
        if not sender:
            return {"status": "error", "message": f"Sender account ID {sender_account_id} not found"}

        cursor.execute("SELECT Bank_id, Currency FROM Account WHERE id = ?", (receiver_account_id,))
        receiver = cursor.fetchone()
        if not receiver:
            return {"status": "error", "message": f"Receiver account ID {receiver_account_id} not found"}

        cursor.execute("SELECT name FROM Bank WHERE id = ?", (sender[0],))
        sender_bank = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM Bank WHERE id = ?", (receiver[0],))
        receiver_bank = cursor.fetchone()[0]

        sender_currency = sender[1]
        receiver_currency = receiver[1]
        transfer_amount = amount

        if sender_currency != currency:
            rate = get_exchange_rate(currency, sender_currency)
            if not rate:
                return {"status": "error", "message": "Failed to get exchange rate"}
            transfer_amount = amount * rate

        if transfer_amount > sender[2]:
            return {"status": "error", "message": "Insufficient funds"}

        receiver_amount = transfer_amount
        if sender_currency != receiver_currency:
            rate = get_exchange_rate(sender_currency, receiver_currency)
            if not rate:
                return {"status": "error", "message": "Failed to get exchange rate"}
            receiver_amount = transfer_amount * rate

        cursor.execute(
            "UPDATE Account SET Amount = Amount - ? WHERE id = ?",
            (transfer_amount, sender_account_id)
        )
        cursor.execute(
            "UPDATE Account SET Amount = Amount + ? WHERE id = ?",
            (receiver_amount, receiver_account_id)
        )

        cursor.execute(
            "INSERT INTO Transaction (Bank_sender_name, Account_sender_id, Bank_receiver_name, "
            "Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                sender_bank,
                sender_account_id,
                receiver_bank,
                receiver_account_id,
                currency,
                amount,
                validate_datetime(datetime_str)
            )
        )

        return {"status": "success", "message": f"Transferred {amount} {currency}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}