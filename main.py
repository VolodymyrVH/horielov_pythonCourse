import logging
import csv
import sqlite3

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', handlers=[logging.FileHandler('banking.log'), logging.StreamHandler()])

from databasework import (
    add_bank, add_user, add_account,
    add_bank_from_csv, add_user_from_csv, add_account_from_csv,
    modify_bank, modify_user, modify_account,
    delete_bank, delete_user, delete_account,
    transfer_money
)

from anly import (
    assign_random_discounts,
    get_users_with_debts,
    get_bank_with_highest_capital,
    get_bank_with_oldest_client,
    get_bank_with_most_unique_senders,
    delete_incomplete_data,
    get_user_transactions_last_3_months,
    get_bank_transaction_volume
)


def safe_execute(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        print(result)
        return result
    except Exception as e:
        logging.error(f"Error in {func.__name__}: {str(e)}")
        print(f"Error in {func.__name__}: {str(e)}")
        return None


def main():
    print("Starting banking system demonstration...")

    conn = sqlite3.connect('banking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    columns = ['id', 'Name', 'Surname', 'Birth_day', 'Accounts']
    with open('users.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for user in users:
            writer.writerow(user)
            print(user)
    conn.close()
    print("Data of users saved in users.csv")

    safe_execute(add_bank, {"name": "Bank A"})
    safe_execute(add_bank, {"name": "Bank B"})
    safe_execute(add_user, {"user_full_name": "John Doe", "Birth_day": "1990-01-01", "Accounts": "1,2"})
    safe_execute(add_user, {"user_full_name": "Jane Smith", "Birth_day": "1985-05-05", "Accounts": "3"})
    safe_execute(add_account, {
        "User_id": 1,
        "Type": "debit",
        "Account_Number": "ID--j3-q-432547-u9",
        "Bank_id": 1,
        "Currency": "USD",
        "Amount": 1000.0,
        "Status": "gold"
    })
    safe_execute(add_account, {
        "User_id": 2,
        "Type": "credit",
        "Account_Number": "ID--k2-p-987654-z8",
        "Bank_id": 2,
        "Currency": "EUR",
        "Amount": 500.0,
        "Status": "silver"
    })

    safe_execute(add_user, {"user_full_name": "Incomplete User", "Birth_day": "", "Accounts": ""})
    safe_execute(add_account, {
        "User_id": 3,
        "Type": "debit",
        "Account_Number": "ID--m1-r-123456-x7",
        "Bank_id": 1,
        "Currency": "USD",
        "Amount": 0.0,
        "Status": ""
    })

    safe_execute(transfer_money, 1, 2, 100.0, "USD")

    safe_execute(assign_random_discounts)
    safe_execute(get_users_with_debts)
    safe_execute(get_bank_with_highest_capital)
    safe_execute(get_bank_with_oldest_client)
    safe_execute(get_bank_with_most_unique_senders)
    safe_execute(get_user_transactions_last_3_months, 1)
    safe_execute(get_bank_transaction_volume)

    safe_execute(delete_incomplete_data)

    safe_execute(modify_bank, 1, {"name": "Bank A Updated"})
    safe_execute(modify_user, 1, {"user_full_name": "John Updated", "Birth_day": "1990-01-01", "Accounts": "1,2"})
    safe_execute(modify_account, 1, {
        "User_id": 1,
        "Type": "debit",
        "Account_Number": "ID--j3-q-432547-u9",
        "Bank_id": 1,
        "Currency": "USD",
        "Amount": 900.0,
        "Status": "platinum"
    })

    safe_execute(delete_account, 2)
    safe_execute(delete_user, 2)
    safe_execute(delete_bank, 2)

    print("Demonstration completed!")


if __name__ == "__main__":
    main()