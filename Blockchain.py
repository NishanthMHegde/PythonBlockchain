import functools
import hashlib
import json
import pickle
from collections import OrderedDict
from Block import Block
MINING_REWARD = 12.0
blockchain = []
open_transactions = []

owner = "max"
participants = set()
participants.add(owner)


def get_user_transaction():
	tx_recipient = input("Enter the name of the recipient")
	tx_amount = float(input("Enter the transaction amount"))
	return tx_recipient,tx_amount


def get_user_choice():
	choice = input("Enter your choice")
	return choice

def validate_chain():
	for (index,block) in enumerate(blockchain):
		if index == 0:
			continue
		if blockchain[index].previousBlockHash != hash_block(blockchain[index-1]):
			return False
		if not valid_proof(block.transactions[:-1],block.previousBlockHash,block.proof):
			print("Proof of work failed")
			return False
	return True

def verify_transaction(transaction):
	sender_balance = calculate_balances(transaction['sender'])
	if sender_balance >= transaction['amount']:
		return True
	else:
		return False

def output_blockchain():
	global blockchain
	print("There are %s blocks"%(len(blockchain)))
	for block in blockchain:
		print("Outputting block")
		print(block.__dict__)

	print('-'*30)

def get_last_transaction():
	if len(blockchain) < 1:
		return None
	return blockchain[-1]
def add_transaction(recipient, amount, sender = owner):
	# transaction = {
	# "sender" : sender,
	# "recipient" : recipient,
	# "amount" : amount
	# }
	transaction = OrderedDict([('sender',sender),('recipient',recipient),('amount',amount)])
	if verify_transaction(transaction):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient)
		save_data()
		return True
	else:
		return False

def hash_block(block):
	hashable_block = block.__dict__.copy()
	return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()
	
def valid_proof(transaction,previousBlockHash,proof):
	str_hash = str(transaction) + str(previousBlockHash) + str(proof)
	str_hash = hashlib.sha256(str_hash.encode('utf-8')).hexdigest()
	
	return str_hash[0:2]=='00'

def proof_of_work():
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof =0
	while not valid_proof(open_transactions,last_hash,proof):
		proof = proof + 1
	return proof
def print_participants():
	print("Printing a list of participants")
	for participant in participants:
		print(participant)


def calculate_balances(participant):
	tx_sent = [[ transaction['amount'] for transaction in block.transactions if transaction['sender'] == participant ]for block in blockchain]
	tx_open_sent = [transaction['amount'] for transaction in open_transactions if transaction['sender']==participant]
	tx_sent.append(tx_open_sent)

	amount_sent = functools.reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_sent,0)
	# amount_sent = 0
	# for amount in tx_sent:
	# 	if len(amount) > 0:
	# 		for amt in amount:
	# 			amount_sent = amount_sent + amt
	tx_received = [[ transaction['amount'] for transaction in block.transactions if transaction['recipient'] == participant ]for block in blockchain]
	amount_received = 0
	amount_received = functools.reduce(lambda tx_sum ,tx_amt : tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_received,0)
	# for amount in tx_received:
	# 	if len(amount) > 0:
	# 		for amt in amount:
	# 			amount_received = amount_received + amt
	return amount_received-amount_sent


def mine_block():
	global blockchain
	global open_transactions
	last_block = blockchain[-1]
	block_hash = hash_block(last_block)
	proof = proof_of_work()
	# reward_transaction = {
	# 'sender' : 'MINER',
	# 'recipient' : owner,
	# 'amount' : MINING_REWARD
	# }
	reward_transaction = OrderedDict([('sender','MINER'),('recipient',owner),('amount',MINING_REWARD)])
	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)
	block = Block(index = len(blockchain),previousBlockHash = block_hash,proof = proof,transactions = copied_transactions)
	
	print("Adding new block %s"%(block.__dict__))
	blockchain.append(block)
	print("New length of blockchain %s"%(len(blockchain)))
	
	return True

def save_data():
	try:
		with open('blockchain_data.txt','w') as write_file:
			saveable_chain = [ block.__dict__ for block in blockchain]
			write_file.write(json.dumps(saveable_chain))
			write_file.write('\n')
			write_file.write(json.dumps(open_transactions))
	except IOError:
		print("Error in saving data to the file")

	# with open('blockchain_data.p','wb') as write_file:
	# 	write_data = {
	# 	'chain' : blockchain,
	# 	'transactions' : open_transactions
	# 	}
	# 	write_file.write(pickle.dumps(write_data))



def load_data():
	global blockchain
	global open_transactions
	try:
		with open('blockchain_data.txt','r') as read_file:
			block_data = read_file.readlines()
			
			blockchain = json.loads(block_data[0][:-1])
			open_transactions = json.loads(block_data[1])

			updated_blockchain = []
			updated_transactions = []

			for block in blockchain:
				updated_block = Block(index = block['index'],previousBlockHash = block['previousBlockHash'],transactions = [OrderedDict([('sender',txn['sender']),('recipient',txn['recipient']),('amount',txn['amount'])]) for txn in block['transactions']],proof = block['proof'])
				
				updated_blockchain.append(updated_block)

			for tx in open_transactions:
				updated_transaction = OrderedDict([('sender',tx['sender']),('recipient',tx['recipient']),('amount',tx['amount'])])
				updated_transactions.append(updated_transaction)

			blockchain = updated_blockchain
			open_transactions = updated_transactions
	except (IOError,AttributeError,IndexError):
		blockchain = []
		genesis_block = Block(index = 0,previousBlockHash = "",transactions = [],proof = 100)
		
		open_transactions = []

		blockchain.append(genesis_block)
	# with open('blockchain_data.p','rb') as read_file:
	# 	file_contents = pickle.loads(read_file.read())
	# 	global blockchain
	# 	global open_transactions
	# 	blockchain = file_contents['chain']
	# 	open_transactions = file_contents['transactions']
		

is_user_interaction = True

while is_user_interaction:
	load_data()
	print("Please select an appropriate choice")
	print("1. Add transaction")
	print("2. View blockchain")
	# print("3. Corrupt the blockchain")
	print("4. Validate block chain")
	print("5. Mine block")
	print("6. Print participants")
	print("7. Calculate balance of each participant")
	print("q. Quit")

	user_choice = get_user_choice()
	if user_choice == '1':
		recipient,amount = get_user_transaction()
		if add_transaction(recipient,amount=amount):
			print("Transaction Successful")
		else:
			print("Transaction failed")
		print(open_transactions)
	elif user_choice == '2':
		output_blockchain()
	# elif user_choice == '3':
	# 	blockchain[0] = {
	# 	"previousBlockHash" : "",
	# 	"index" : 0,
	# 	"transactions": [{"recipient" : "Manu", "sender": "fsdf87df7dfbfshgh9834", "amount" : 120.0}]
	# 	}
	elif user_choice == '4':
		is_valid_blockchain = validate_chain()
		if is_valid_blockchain is True:
			print("Block chain is valid")
		else:
			print("Blockchain is invalid")
			break
	elif user_choice == '5':
		is_block_mined = mine_block()
		if is_block_mined == True:
			open_transactions = []
			print("Block was mined successfully")
			save_data()
	elif user_choice == '6':
		print_participants()
	elif user_choice == '7':
		for participant in participants:
			print("Balance of %s is %s "%(participant,calculate_balances(participant)))
		
	elif user_choice == 'q':
		is_user_interaction = False
		break

	if not validate_chain():
		print("Invalid block")
		break



