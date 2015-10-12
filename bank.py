from cryptography.fernet import Fernet
import argparse
import json
import string
import random
import re
import sys
import socket

BUFFER_SIZE = 1024



def parse_money(money_string):
    parts = string.split(money_string, '.')
    amount = [0,0]
    amount[0] = int(parts[0])
    amount[1] = int(parts[1])
    return amount

class Account:
    def __init__(self, name, balance):
        self.card_number = random.randint(1000000, 9999999)
        self.name = name

        amount = parse_money(balance)

        self.dollars = amount[0]
        self.cents   = amount[1]
        
    def withdraw(self, amount_string):
        amount = parse(money(amount_string))
        if(amount[0] < self.dollars):
            self.dollars -= amount[0]
            self.cents -= amount[1]

            if(self.cents < 0):
                self.dollars -= 1
                self.cents += 100

            return amount

        elif((amount[0] == self.dollars) and (amount[1] <= self.cents)):
            self.dollars -= amount[0]
            self.cents -= amout[1]
            return amount

        else:
            return 0

    def deposit(self, amount_string):
        amount = parse_money(amount_string)
        self.dollars += amount()
        self.cents   += amount()
        
        if(self.cents >= 100):
            self.dollars += 1
            self.cents   -= 100

    def get_balance():
        balance_string = self.dollars + '.' + self.cents
        return balance_string



def authenticate(f, conn):
    ciphertext = conn.recv(BUFFER_SIZE)
    data = f.decrypt(ciphertext)
    request = json.loads(data)
    counter = request['counter']
    conn.send(f.encrypt(json.dumps({'counter' : counter + 1})))
    return counter

def create(accounts, card_number, name, amount):
    
    response = {'success':False}

    try:
        account = accounts[card_number]
    except KeyError:
        response['success'] = True

        for key in accounts:
            if(accounts[key].name == name):
                response = {'success': False}
        
        if(response['success']):
            account = Account(name, amount)
            accounts[account.card_number] = account
            response['summary'] = {'account':name, 'initial_balance': amount}
            response['card_number'] = account.card_number

    return response
    
def deposit(account, amount):
    account.deposit(amount)
    response = {'success': True, 'summary': {'account':account.name, 'deposit': amount}}
    return response

def withdraw(account, amount):
    r = account.withdraw(amount)
    if(r):
        response = {'success': True, 'summary': {'account': account.name, 'withdraw': amount}}
        return response
    else:
        response = {'success': Fales}
        return response

def getinfo(account):
    balance = account.get_balance()
    response = {'success': True, 'summary': {'account': account.name, 'balance': balance}}
    return response




def handle_request(f, conn, counter, accounts):
    ciphertext = conn.recv(BUFFER_SIZE)
    data = f.decrypt(ciphertext)
    request = json.loads(data)
    
    if(request['counter'] != counter + 2):
        print "protocol_error"
        return 0
    
    
    if(request['operation'] == "create"): 
        response = create(accounts, request['card_number'], request['name'], request['amount'])

    elif(request['operation'] == "deposit"):
        account = accounts[request['card_number']]
        response = deposit(account, request['amount'])

    elif(request['operation'] == "withdraw"):
        account = accounts[request['card_number']]
        response = withdraw(account, request['amount'])

    elif(request['operation'] == "getinfo"):
        account = accounts[request['card_number']]
        response = getinfo(account)

    else:
        return 0

    response['counter'] = counter + 3
    return response



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="port number", default=3000, type=int)
    parser.add_argument("-s", "--auth_file", help="auth file", nargs='?', default="bank.auth")

    args = parser.parse_args()

    if(args.port < 1024 or args.port > 65535):
        ArgumentParser.print_help()
        print "port must be between 1024 and 65535"
        sys.exit(255)

    pattern = re.compile('[_\-\.0-9a-z]{1,255}')
    auth_file_name = ""


    if args.auth_file:
        if not ( pattern.match(args.auth_file)):
            ArgumentParser.print_help()
            print "file name must match [_\-\.0-9a-z]{1,255}"
            sys.exit(255)
        else:
            auth_file_name = args.auth_file
    else:
        auth_file_name = "bank.auth"

    key = Fernet.generate_key()
    auth_file = open(auth_file_name, 'wb')
    auth_file.write(key)
    auth_file.close()

    f = Fernet(key)

    accounts = {}


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('', args.port))
    s.listen(1)

    while True:
        conn, addr = s.accept()
        counter = authenticate(f, conn) 
        response = handle_request(f, conn, counter, accounts)
        if(response):
            ciphertext = f.encrypt(json.dumps(response))
            conn.send(ciphertext)
            print json.dumps(response['summary'])



