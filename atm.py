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
		if args.balance != None and num1 < 10:
			print '25510'
			sys.exit(0)
		if(num1 > 4294967295 or num1 <= 0):
			print '2551'
			sys.exit(0)
	else:
		print '2552'
		sys.exit(0)

''' open auth file to get the secret_key, open card file to get the card number'''
try:
	f_auth = open(args.authfile,'rb')
except IOError as e:
	print '25530'
	sys.exit(0)

fcardfound = False
try:
	f_card = open(args.cardfile,'rb')
	fcardfound = True	
except IOError as e:
	print args.cardfile
	if args.balance != None:
		f_card = open(args.cardfile,'wb+')
	else:
		print "2553"
		sys.exit(0)

if args.balance != None and fcardfound == True:
	print '25532'
	sys.exit(0)

secret_key = f_auth.read().strip()
f_auth.close()

card_num = ""
if args.balance == None:
	card_num = f_card.read().strip()
	f_card.close()

print secret_key


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


'''encryption'''
fernet_obj = Fernet(secret_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.settimeout(10)
try:
	s.connect((args.ip,args.port))
except (socket.error, socket.timeout) as e:
	s.close()
	print '630'
	sys.exit(0)

json_obj1 = {'counter':token}
json_string1 = json.dumps(json_obj1)
try:
	s.send(fernet_obj.encrypt(json_string1))
except (socket.error, socket.timeout) as e:
	s.close()
	print '631'
	sys.exit(0)

try:
	json_string2 = s.recv(1024)
except (socket.error, socket.timeout) as e:
	s.close()
	print '632'
	sys.exit(0)

json_obj2 = json.loads(fernet_obj.decrypt(json_string2))
'''authenticate failure'''
if(json_obj2['counter'] != token+1):
	print '255'
	s.close()
	sys.exit(0)

json_obj3={'counter':token+2, 'card_number':card_num, 'operation':operation, 'amount':amount, 'name': args.account}
json_string3 = json.dumps(json_obj3)

try:
	s.send(fernet_obj.encrypt(json_string3))
except (socket.error, socket.timeout) as e:
	print '633'
	sys.exit(0)

try:
	json_string4 = s.recv(1024)
except (socket.error, socket.timeout) as e:
	s.close()
	print '634'
	sys.exit(0)

json_obj4 = json.loads(fernet_obj.decrypt(json_string4))
if(json_obj4['counter'] != token+3):
	print '255'
	s.close()
	sys.exit(0)
if(json_obj4['success'] == False):
	print '255'
	s.close()
	sys.exit(0)
print json_obj4
if args.balance != None:
	f_card.write(str(json_obj4['card_number']))
	f_card.close()
print json.dumps(json_obj4['summary'])
s.close()


'''json_result = {json_obj4['operation']:json_obj4['amount'], 'account':args.account}'''