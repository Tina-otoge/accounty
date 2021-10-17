import csv
from dataclasses import dataclass
import datetime
import json
import logging
import sys

from app.models import Consumer, Payment
from app import db

# Run with `python -m app.import`

logging.basicConfig(level=logging.DEBUG)

@dataclass
class Transaction:
    FR_FORMAT = True

    id: str
    name: str
    gross: float
    from_email: str
    date: datetime.date
    notes: str
    currency: str

    def __init__(self, report_entry: dict):
        # ID
        self.id = report_entry['Transaction ID']

        # Name
        self.name = report_entry['Name']

        # Gross
        gross = report_entry['Gross']
        if self.FR_FORMAT:
            gross = gross.replace('.', '').replace(',', '.')
        else:
            gross = gross.replace(',', '')
        self.gross = float(gross)
        if self.gross < 0:
            self.gross = 0

        # From
        self.from_email = report_entry['From Email Address'].lower()

        # Date
        if self.FR_FORMAT:
            day, month, year = map(int, report_entry['Date'].split('/'))
            self.date = datetime.date(year, month, day)

        # Note
        self.notes = report_entry['Note']

        # Currency
        self.currency = report_entry['Currency']

def dump(data, to: str):
    with open(to, 'w') as f:
        json.dump(data, f, indent=2, default=str)

if __name__ == '__main__':
    # Read CSV
    target = sys.argv[1]
    with open(target) as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [x.strip().strip('\ufeff"') for x in reader.fieldnames]
        data = list(reader)
    dump(data, 'logs/dump_raw.json')

    # Order transactions by email
    transactions_by_email = {}
    for transaction in map(Transaction, data):
        transactions_by_email.setdefault(transaction.from_email, [])
        transactions_by_email[transaction.from_email].append(transaction)
    dump(transactions_by_email, 'logs/dump_by_mail.json')

    # Import to db
    for consumer in db.session.query(Consumer):
        logging.info(consumer)
        if consumer.paypal_email not in transactions_by_email:
            logging.info('Skipping consumer %s whose email does not match any transaction', consumer)
            continue
        transactions = transactions_by_email[consumer.paypal_email]
        for transaction in transactions:
            if transaction.currency != 'EUR':
                logging.warning('Skipping transaction %s with unsupported currency', transaction)
                continue
            if db.session.query(Payment).filter_by(paypal_transaction=transaction.id).first():
                logging.info('Skipping transaction %s already in db', transaction)
                continue
            payment = Payment(
                paypal_transaction=transaction.id,
                consumer=consumer,
                date=transaction.date,
                euros_amount=transaction.gross,
                notes=transaction.notes,
            )
            try:
                db.session.add(payment)
                db.session.commit()
                logging.info('Created payment %s from Paypal transaction %s', payment, transaction)
            except Exception as e:
                logging.error(e, exc_info=True)
