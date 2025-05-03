import sqlite3
import argparse
import logging

parser = argparse.ArgumentParser(description='Database setup script')
parser.add_argument('--unique-name-surname', action='store_true', help='Enforce uniqueness on User Name and Surname')
args = parser.parse_args()

conn = sqlite3.connect('banking.db')
cursor = conn.cursor()

logging.debug("Starting database structure creation")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    logging.info("Created Bank table")

    user_unique_constraint = ', UNIQUE(Name, Surname)' if args.unique_name_surname else ''
    logging.debug(f"User table unique constraint: {user_unique_constraint}")
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Surname TEXT NOT NULL,
            Birth_day TEXT,
            Accounts TEXT NOT NULL
            {user_unique_constraint}
        )
    ''')
    logging.info("Created User table")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            User_id INTEGER NOT NULL,
            Type TEXT NOT NULL CHECK(Type IN ('credit', 'debit')),
            Account_Number TEXT NOT NULL UNIQUE,
            Bank_id INTEGER NOT NULL,
            Currency TEXT NOT NULL,
            Amount REAL NOT NULL,
            Status TEXT CHECK(Status IN ('gold', 'silver', 'platinum')),
            FOREIGN KEY (User_id) REFERENCES User(id),
            FOREIGN KEY (Bank_id) REFERENCES Bank(id)
        )
    ''')
    logging.info("Created Account table")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS [Transaction] (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Bank_sender_name TEXT NOT NULL,
            Account_sender_id INTEGER NOT NULL,
            Bank_receiver_name TEXT NOT NULL,
            Account_receiver_id INTEGER NOT NULL,
            Sent_Currency TEXT NOT NULL,
            Sent_Amount REAL NOT NULL,
            Datetime TEXT,
            FOREIGN KEY (Account_sender_id) REFERENCES Account(id),
            FOREIGN KEY (Account_receiver_id) REFERENCES Account(id)
        )
    ''')
    logging.info("Created Transaction table")

    conn.commit()
    logging.info("Database structure created successfully")
    print("Database structure created successfully!")

except sqlite3.Error as e:
    logging.error(f"Failed to create database structure: {str(e)}")
    if "database is locked" in str(e):
        logging.critical("Database is locked, cannot proceed with setup")
    conn.rollback()

except Exception as e:
    logging.critical(f"Unexpected error during database setup: {str(e)}")

finally:
    conn.close()
    logging.debug("Database connection closed")