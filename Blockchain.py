import functools
import hashlib
import json
import pickle
from collections import OrderedDict
from Block import Block
from Transactions import Transactions
from HashUtils import HashUtils
from Verifications import Verifications
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
	verification = Verifications()
	transaction = Transactions(sender,recipient,amount)
	if verification.verify_transaction(transaction,calculate_balances):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient)
		save_data()
		return True
	else:
		return False


	


def proof_of_work():
	verification = Verifications()
	hu = HashUtils()
	last_block = blockchain[-1]
	last_hash = hu.hash_block(last_block)
	proof =0
	while not verification.valid_proof(open_transactions,last_hash,proof):
		proof = proof + 1
	return proof
def print_participants():
	print("Printing a list of participants")
	for participant in participants:
		print(participant)


def calculate_balances(participant):
	tx_sent = [[ transaction.amount for transaction in block.transactions if transaction.sender == participant ]for block in blockchain]
	tx_open_sent = [transaction.amount for transaction in open_transactions if transaction['sender']==participant]
	tx_sent.append(tx_open_sent)

	amount_sent = functools.reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_sent,0)
	# amount_sent = 0
	# for amount in tx_sent:
	# 	if len(amount) > 0:
	# 		for amt in amount:
	# 			amount_sent = amount_sent + amt
	tx_received = [[ transaction.amount for transaction in block.transactions if transaction.recipient == participant ]for block in blockchain]
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
	hu = HashUtils()
	last_block = blockchain[-1]
	block_hash = hu.hash_block(last_block)
	proof = proof_of_work()
	# reward_transaction = {
	# 'sender' : 'MINER',
	# 'recipient' : owner,
	# 'amount' : MINING_REWARD
	# }
	reward_transaction = Transactions('MINER',owner,MINING_REWARD)
	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)
	block = Block(index = len(blockchain),previousBlockHash = block_hash,proof = proof,transactions = copied_transactions)
	
	print("Adding new block %s"%(block.__dict__))
	blockchain.append(block)
	output_blockchain()
	print("New length of blockchain %s"%(len(blockchain)))
	
	return True

def save_data():
	global blockchain
	try:
		with open('blockchain_data.txt','w') as write_file:
			saveable_chain = [ block.__dict__  for block in [Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof) for block_el in blockchain]]
			# converted_blocks = []
			# for block_el in blockchain:
			# 	converted_block = Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof)
			# 	print("converted_block is %s"%(converted_block))
			# 	converted_blocks.append(converted_block.__dict__)
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
				updated_block = Block(index = block['index'],previousBlockHash = block['previousBlockHash'],transactions = [Transactions(txn['sender'],txn['recipient'],txn['amount']) for txn in block['transactions']],proof = block['proof'])
				
				updated_blockchain.append(updated_block)

			for tx in open_transactions:
				updated_transaction = Transactions(tx.sender,tx.recipient,tx.amount)
				updated_transactions.append(updated_transaction)

			blockchain = updated_blockchain
			open_transactions = updated_transactions
	except (IOError,AttributeError,IndexError):
		print("Initialising genesis block")
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
	print("3. Verify Transactions")
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
	elif user_choice == '3':
		verification = Verifications()
		if verification.verify_transactions(open_transactions,calculate_balances):
			print("All transactions are valid and verified")

	elif user_choice == '4':
		verification = Verifications()
		is_valid_blockchain = verification.validate_chain(blockchain)
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
	verification = Verifications()
	if not verification.validate_chain(blockchain):
		print("Invalid block")
		break



