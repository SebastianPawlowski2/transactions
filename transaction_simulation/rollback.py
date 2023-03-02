import sqlite3
import pytz
import datetime
import csv

"""
This script is used to implement the data from daily_transactions.csv the accounts.sqlite database.
After a first transaction for a client gets transfered, a new account is created.
If the withdrawal amount exceeds the account balance or the account does not exist, a proper message is shown.
The dabase consists of two tables and one view.

Tables
-------
accounts
    Displays client name and the amount in the deposit.

transactions
    Displays recorded time, client and amount for every transaction.

View
-----
localtransactions
    Displays recorded time, client and amount for every transaction in local time.

"""


db = sqlite3.connect("accounts.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
db.execute("CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY NOT NULL, balance INTEGER NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS transactions (time TIMESTAMP NOT NULL, account TEXT NOT NULL,"
            "amount INTEGER NOT NULL, PRIMARY KEY (time, account))")
db.execute("CREATE VIEW IF NOT EXISTS localtransactions AS SELECT strftime('%Y-%m-%d %H:%M:%f', transactions.time, 'localtime') AS localtime,"
            " transactions.account, transactions.amount FROM transactions ORDER BY transactions.time")

class Account(object):

    @staticmethod
    def _current_time():
        #return pytz.utc.localize(datetime.datetime.utcnow())
        local_time = pytz.utc.localize(datetime.datetime.utcnow())
        return local_time.astimezone()

    def __init__(self, name: str, opening_balance: int = 0):
        cursor = db.execute("SELECT name, balance FROM accounts WHERE (name = ?)", (name, ))
        row = cursor.fetchone()

        if row:
            self.name, self._balance = row
            print(f"Retrieved record for {self.name}", end=' ')
        else:
            self.name = name
            self._balance = opening_balance
            cursor.execute("INSERT INTO accounts VALUES(?, ? )", (name, opening_balance))
            cursor.connection.commit()
            print(f"Account created for {self.name}", end=' ')
        self.show_balance()
    
    def _save_update(self, amount):
        new_balance = self._balance + amount
        deposit_time = Account._current_time()

        try:
            db.execute("Update accounts SET balance = ? WHERE (name = ?)", (new_balance, self.name))
            db.execute("INSERT INTO transactions VALUES (?, ?, ?)", (deposit_time, self.name, amount))
        except sqlite3.Error:
            db.rollback()
        else: 
            self._balance = new_balance
            db.commit()

    def deposit(self, amount: int) -> int:
        if amount > 0.0:
            self._save_update(amount)
            print("{:.2f} deposited".format(amount / 100))
        return self._balance / 100

    def withdraw(self, amount: int) -> int:
        if 0 < amount <= self._balance:
            self._save_update(-amount)
            print("{:.2f} withdrawn".format(amount / 100))
            return amount
        else:
            print("The amount must be greater than zero and no more than your account balance")
            return 0

    def show_balance(self):
        print(f"Balance on account {self.name} is {self._balance/100}")

if __name__ == '__main__':

    with open("daily_transactions.csv", newline='') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            client = row["Client"]
            transact = int(row["Amount"])
            
            if transact <= 0:
                Account(client).withdraw(transact * -1)
            else:
                Account(client).deposit(transact)
            

    db.close()