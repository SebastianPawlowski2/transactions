import random
import numpy as np
import csv

"""
This script is a simple simulation of daily transactions of clients that would later be saved into SQL database.
The number of transactions and clients are random for each generation.
The amount of the transaction is a normally distributed random variable.

For each transaction, a (Client, Amount) tuple is appended into a list.
The list is next written into a csv file to be later implemented into accounts.sqlite database.

"""


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

