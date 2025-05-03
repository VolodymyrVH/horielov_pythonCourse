import sqlite3
import logging
import random
from datetime import datetime, timedelta
from functools import wraps


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


@db_connection
def assign_random_discounts(cursor, conn):
    try:
        cursor.execute("SELECT id FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        if not user_ids:
            return {"status": "error", "message": "No users found"}

        num_users = min(random.randint(1, 10), len(user_ids))
        selected_users = random.sample(user_ids, num_users)
        discounts = [random.choice([25, 30, 50]) for _ in range(num_users)]

        result = [{"user_id": user_id, "discount": discount} for user_id, discount in zip(selected_users, discounts)]
        logging.info(f"Assigned discounts to {num_users} users: {result}")
        return {"status": "success", "message": f"Assigned discounts to {num_users} users", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_users_with_debts(cursor, conn):
    try:
        cursor.execute("""
            SELECT u.Name, u.Surname
            FROM User u
            JOIN Account a ON u.id = a.User_id
            WHERE a.Amount < 0
        """)
        users = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
        logging.info(f"Found {len(users)} users with debts: {users}")
        return {"status": "success", "message": f"Found {len(users)} users with debts", "data": users}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_bank_with_highest_capital(cursor, conn):
    try:
        cursor.execute("""
            SELECT b.name, SUM(a.Amount) as total
            FROM Bank b
            JOIN Account a ON b.id = a.Bank_id
            GROUP BY b.id, b.name
            ORDER BY total DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if not result:
            return {"status": "error", "message": "No banks with accounts found"}
        bank_name, total = result
        logging.info(f"Bank with highest capital: {bank_name} (${total})")
        return {"status": "success", "message": f"Bank with highest capital: {bank_name}",
                "data": {"name": bank_name, "capital": total}}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_bank_with_oldest_client(cursor, conn):
    try:
        cursor.execute("""
            SELECT b.name, MIN(u.Birth_day)
            FROM Bank b
            JOIN Account a ON b.id = a.Bank_id
            JOIN User u ON a.User_id = u.id
            WHERE u.Birth_day IS NOT NULL AND u.Birth_day != ''
            GROUP BY b.id, b.name
            ORDER BY MIN(u.Birth_day) ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if not result:
            return {"status": "error", "message": "No banks with valid user birth dates found"}
        bank_name, birth_day = result
        logging.info(f"Bank with oldest client: {bank_name} (client born {birth_day})")
        return {"status": "success", "message": f"Bank with oldest client: {bank_name}",
                "data": {"name": bank_name, "birth_day": birth_day}}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_bank_with_most_unique_senders(cursor, conn):
    try:
        cursor.execute("""
            SELECT b.name, COUNT(DISTINCT a.User_id) as user_count
            FROM Bank b
            JOIN Account a ON b.id = a.Bank_id
            JOIN Transaction t ON a.id = t.Account_sender_id
            GROUP BY b.id, b.name
            ORDER BY user_count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if not result:
            return {"status": "error", "message": "No banks with outbound transactions found"}
        bank_name, user_count = result
        logging.info(f"Bank with most unique senders: {bank_name} ({user_count} users)")
        return {"status": "success", "message": f"Bank with most unique senders: {bank_name}",
                "data": {"name": bank_name, "user_count": user_count}}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def delete_incomplete_data(cursor, conn):
    try:
        cursor.execute("DELETE FROM User WHERE Name IS NULL OR Name = '' OR Surname IS NULL OR Surname = ''")
        users_deleted = cursor.rowcount

        cursor.execute("""
            DELETE FROM Account
            WHERE User_id IS NULL
            OR Type IS NULL OR Type = ''
            OR Account_Number IS NULL OR Account_Number = ''
            OR Bank_id IS NULL
            OR Currency IS NULL OR Currency = ''
            OR Amount IS NULL
        """)
        accounts_deleted = cursor.rowcount

        logging.info(f"Deleted {users_deleted} incomplete users and {accounts_deleted} incomplete accounts")
        return {
            "status": "success",
            "message": f"Deleted {users_deleted} users and {accounts_deleted} accounts",
            "data": {"users_deleted": users_deleted, "accounts_deleted": accounts_deleted}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_user_transactions_last_3_months(cursor, conn, user_id):
    try:
        three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()
        cursor.execute("""
            SELECT t.*
            FROM Transaction t
            JOIN Account a ON t.Account_sender_id = a.id OR t.Account_receiver_id = a.id
            WHERE a.User_id = ? AND t.Datetime >= ?
        """, (user_id, three_months_ago))
        transactions = [
            {
                "id": row[0],
                "bank_sender_name": row[1],
                "account_sender_id": row[2],
                "bank_receiver_name": row[3],
                "account_receiver_id": row[4],
                "sent_currency": row[5],
                "sent_amount": row[6],
                "datetime": row[7]
            }
            for row in cursor.fetchall()
        ]
        logging.info(f"Retrieved {len(transactions)} transactions for user {user_id}")
        return {"status": "success", "message": f"Found {len(transactions)} transactions", "data": transactions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@db_connection
def get_bank_transaction_volume(cursor, conn):
    try:
        cursor.execute("""
            SELECT b.name, COALESCE(SUM(t.Sent_Amount), 0) as total_volume
            FROM Bank b
            LEFT JOIN Account a ON b.id = a.Bank_id
            LEFT JOIN Transaction t ON a.id = t.Account_sender_id
            GROUP BY b.id, b.name
            ORDER BY total_volume DESC
        """)
        volumes = [{"bank_name": row[0], "total_volume": row[1]} for row in cursor.fetchall()]
        logging.info(f"Calculated transaction volumes: {volumes}")
        return {"status": "success", "message": "Calculated transaction volumes", "data": volumes}
    except Exception as e:
        return {"status": "error", "message": str(e)}