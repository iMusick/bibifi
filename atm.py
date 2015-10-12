import socket
from cryptography.fernet import Fernet
import argparse
import sys
import re
import random
import math
import json


BUFFER_SIZE = 1024


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-s",help = "authentication file",action = "store", dest='authfile', default="bank.auth")
parser.add_argument("-i",help = "bank's ip address",action = "store", dest = 'ip', default = "127.0.0.1")
parser.add_argument("-p",help = "bank's port number",action = "store", dest = 'port', type= int, default = 3000)
parser.add_argument("-c",help = "card-file",action = "store",dest='cardfile')
parser.add_argument("-a",help = "account",action = "store",required = "true",dest='account')
group.add_argument("-n",help = "balance when create an account",action = "store",dest = 'balance')
group.add_argument("-d",help = "amount when deposit",action = "store",dest='deposit')
group.add_argument("-w",help = "amount when withdraw",action = "store",dest='withdraw')
group.add_argument("-g",help = "get the information about account",action = "store_true",dest='getinfo')

args = parser.parse_args()

if args.cardfile == None:
	args.cardfile = args.account + ".card"

'''the amount range should be from 0 to 4294967295.99'''
amount = ""
if args.getinfo == False:
	if args.balance != None:
		amount = args.balance
	elif args.deposit != None:
		amount = args.deposit
	else:
		amount = args.withdraw
	if re.match("(0|[1-9][0-9]*).[0-9][0-9]", amount):
		amount_parts = amount.split(".")
		num1 = long(amount_parts[0])
		if(num1 > 4294967295 or num1 < 0):
			print '2551'
			sys.exit(0)
	else:
		print '2552'
		sys.exit(0)

''' open auth file to get the secret_key, open card file to get the card number'''
try:
	f_auth = open(args.authfile,'rb')
	'''
	if args.balance != None and args.getinfo == False:
		print '1'
		f_card = open(args.cardfile,'rb')
	'''
except IOError as e:
	print args.authfile
	print args.cardfile
	print "2553"
	sys.exit(0)
secret_key = f_auth.read().strip()
f_auth.close()
'''
if args.balance != None and args.getinfo == False:
	card_num = f_card.read().strip()
	f_card.close()
'''
#print secret_key

'''generate a random number for authentication with bank'''
token = int(math.ceil(random.random()*10000000))
operation = ""
if args.balance != None:
	operation = 'create'
elif args.deposit != None:
	operation = 'deposit'
elif args.withdraw != None:
	operation = 'withdraw'
else:
	operation = 'getinfo'

'''generate json format of request'''
json_auth={'counter':token}
json_obj={'counter':token+2, 'card_number':12342, 'operation':operation, 'amount':amount, 'name': args.account}
auth_string = json.dumps(json_auth)
json_string = json.dumps(json_obj)
#print json_string

'''encryption'''
fernet_obj = Fernet(secret_key)
ciphertext = fernet_obj.encrypt(auth_string)
#print ciphertext

'''send request through socket'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1",3000))
try:
    s.send(ciphertext)
    ciphertext = s.recv(BUFFER_SIZE)
    data = fernet_obj.decrypt(ciphertext)
    response = json.loads(data)
    print "response 1: " + json.dumps(response)
    ciphertext = fernet_obj.encrypt(json_string)
    s.send(ciphertext)
    ciphertext = s.recv(BUFFER_SIZE)
#    print ciphertext
    data = fernet_obj.decrypt(ciphertext)
    response = json.loads(data)
    print "response 2: " + json.dumps(response)
    s.close()
except:
    s.close()


'''
print 'authfile= ', args.authfile
print 'ip= ', args.ip
if args.cardfile == None:
	args.cardfile = args.account+".card"
print 'cardfile= ', args.cardfile
print 'account= ', args.account
print 'deposit= ', args.deposit
print 'withdraw= ', args.withdraw
print 'getinfo=', args.getinfo
print 'balance= ', args.balance



import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-s', action='store', dest='authfile',default="bank.auth",
                    help='authentication file')

results = parser.parse_args()
print 'simple_value     =', results.authfile
'''
