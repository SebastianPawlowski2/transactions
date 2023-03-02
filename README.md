# transactions
Simulates daily transactions and their implementation into SQL database using SQLite with Python.

Transactions generation
-----

First, artificial transactions are created with clients.py. The number of transactions and clients are random for each generation.
The amount of the transaction is a normally distributed random variable.

For each transaction, a (Client, Amount) tuple is appended into a list.
The list is next written into a csv file to be later implemented into accounts.sqlite database.

```python
import random
import numpy as np
import csv

clients = [
    "Adams", "Baker", "Clark", "Davis", "Evans", "Frank","Ghosh", "Hills", 
    "Irwin", "Jones", "Klein", "Lopez", "Mason", "Nalty", "Ochoa", "Patel", 
    "Quinn", "Reily", "Smith", "Trott", "Usman", "Valdo", "White", "Xiang",
    "Yakub", "Zafar"
]

columns = ["Client", "Amount"]

mu, sigma = 0, 1

transaction_number = random.randint(0, 101)
transactions=[]

for tr in range(0, transaction_number):

    transaction = ()
    transaction += (random.choice(clients),)
    amount = int(np.random.normal(mu, sigma) * 1000)
    if amount == 0:
        pass
    else:
        transaction += (amount,)
        transactions.append(transaction)

with open("daily_transactions.csv", "w", newline='') as fp:
    write = csv.writer(fp)
    write.writerow(columns)
    write.writerows(transactions)
```

Inserting csv data into SQLite database
-----

The csv file is then used in rollback.py to insert the data into accounts.sqlite. After a first transaction for a client gets transfered, a new account is created.
If the withdrawal amount exceeds the account balance or the account does not exist, a proper message is shown.
The dabase consists of two tables and one view.

Tables
-------
1. accounts
    Displays client name and the amount in the deposit.

2. transactions
    Displays recorded time, client and amount for every transaction.

View
-----
1. localtransactions
    Displays recorded time, client and amount for every transaction in local time.

```python
import sqlite3
import pytz
import datetime
import csv

db = sqlite3.connect("accounts.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
db.execute("CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY NOT NULL, balance INTEGER NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS transactions (time TIMESTAMP NOT NULL, account TEXT NOT NULL,"
            "amount INTEGER NOT NULL, PRIMARY KEY (time, account))")
db.execute("CREATE VIEW IF NOT EXISTS localtransactions AS SELECT strftime('%Y-%m-%d %H:%M:%f', transactions.time, 'localtime') AS localtime,"
            " transactions.account, transactions.amount FROM transactions ORDER BY transactions.time")

class Account(object):

    @staticmethod
    def _current_time():
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
```
Output
------
The output is shown in the pictures below. The inserted data can be selected from Command Prompt or SQLite GUI.

**1. accounts table after first transactions imput**

![image](https://user-images.githubusercontent.com/126695578/222451262-88ed64ea-340f-4bc3-b9cf-5dab1e57292f.png)

**2. transactions table after second transactions imput**

![image](https://user-images.githubusercontent.com/126695578/222452381-21697fdb-4882-4072-a94e-07df4659c673.png)

**3. localtransactions view after third transactions imput**

![image](https://user-images.githubusercontent.com/126695578/222452906-705c714b-71e2-455a-a9b0-116e51d83134.png)



