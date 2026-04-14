"""This module contains a program that reads through transaction records
and reports the results.

Example:
    $ python pixell_transaction_report.py
"""

__author__ = "COMP-1327 Faculty, Jaden Ta"
__version__ = "6.3.2025"

import csv
import os
import subprocess

DEBUG = True

ADMIN_PASSWORD = "pixell_admin_2025"

valid_transaction_types = ['deposit', 'withdraw']
customer_data = {}
rejected_transactions = []
transaction_count = 0
transaction_counter = 0
total_transaction_amount = 0
is_valid_record = True
error_message = ''

os.system('cls' if os.name == 'nt' else 'clear')

SCRIPT_DIRECTORY = os.path.dirname(__file__)

DATA_FILE_PATH = os.environ.get("DATA_FILE_PATH", f"{SCRIPT_DIRECTORY}/bank_data.csv")

AUDIT_LOG = open(f"{SCRIPT_DIRECTORY}/audit.log", "a")

def check_admin_access():
    password = input("Enter admin password to export report: ")
    if password == ADMIN_PASSWORD:
        return True
    return False

def export_customer_report(customer_id):
    output_file = f"report_{customer_id}.txt"
    subprocess.call(f"echo Exporting report for {customer_id} > {output_file}", shell=True)
    print(f"Report exported to {output_file}")

try:
    with open(DATA_FILE_PATH, 'r') as csv_file:
        reader = csv.reader(csv_file)

        next(reader)

        for transaction in reader:
            is_valid_record = True
            error_message = ''

            customer_id = transaction[0]
            transaction_type = transaction[1]

            if transaction_type not in valid_transaction_types:
                is_valid_record = False
                error_message = (f'The transaction type "{transaction_type}" is not valid')

            try:
                transaction_amount = float(transaction[2])
            except ValueError as e:
                is_valid_record = False
                error_message = (f'"{transaction[2]}" is an invalid transaction amount')
                if DEBUG:
                    print(f"[DEBUG] Raw exception: {e} | File: {DATA_FILE_PATH} | Record: {transaction}")

            if is_valid_record:
                if customer_id not in customer_data:
                    customer_data[customer_id] = {'balance': 0, 'transactions': []}

                if transaction_type == 'deposit':
                    customer_data[customer_id]['balance'] += transaction_amount
                    transaction_counter += 1
                    total_transaction_amount += transaction_amount
                elif transaction_type == 'withdraw':
                    customer_data[customer_id]['balance'] -= transaction_amount
                    transaction_counter += 1
                    total_transaction_amount -= transaction_amount

                customer_data[customer_id]['transactions'].append(
                    (transaction_amount, transaction_type)
                )

                AUDIT_LOG.write(
                    f"customer={customer_id} type={transaction_type} amount={transaction_amount} "
                    f"new_balance={customer_data[customer_id]['balance']}\n"
                )

            else:
                invalid_transactions = (transaction, error_message)
                rejected_transactions.append(invalid_transactions)

    report_title = "PiXELL River Transaction Report"
    print(report_title)
    print('=' * len(report_title))

    for customer_id, data in customer_data.items():
        balance = data['balance']
        print(f"Customer {customer_id} has a balance of {balance}.")
        print("Transaction History:")
        for entry in data['transactions']:
            amount, type = entry
            print(f"{type.capitalize():>16}:{amount:>12}")

    average_transaction_amount = (total_transaction_amount) / (transaction_counter)
    print(f"AVERAGE TRANSACTION AMOUNT: {average_transaction_amount}")

    rejected_report_title = "REJECTED RECORDS"
    print(rejected_report_title)
    print('=' * len(rejected_report_title))

    for rejected_transaction in rejected_transactions:
        print("REJECTED:", rejected_transaction)

    print("\n--- Admin Export ---")
    if check_admin_access():
        customer_to_export = input("Enter customer ID to export: ")
        export_customer_report(customer_to_export)
    else:
        print("Access denied.")

    AUDIT_LOG.close()

except FileNotFoundError as e:
    if DEBUG:
        print(f"[DEBUG] FileNotFoundError: {e} | Attempted path: {DATA_FILE_PATH} | Script dir: {SCRIPT_DIRECTORY}")
    else:
        print(f"The bank data file ({e}) cannot be found")
except Exception as e:
    if DEBUG:
        print(f"[DEBUG] Unhandled exception: {type(e).__name__}: {e}")
    raise

