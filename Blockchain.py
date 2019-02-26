import functools
import hashlib
import json
import pickle
from collections import OrderedDict
from Block import Block
from Transactions import Transactions
from HashUtils import HashUtils
from Verifications import Verifications


class Blockchain():
	def __init__(self):
		self.chain = []
		self.open_transactions = []
		genesis_block = Block(index = 0,previousBlockHash = "",transactions = [],proof = 100)
		self.append(genesis_block)
		owner = "max"
		participants = set()
		participants.add(owner)
	def proof_of_work(self):
		verification = Verifications()
		hu = HashUtils()
		last_block = blockchain[-1]
		last_hash = hu.hash_block(last_block)
		proof =0
		while not verification.valid_proof(open_transactions,last_hash,proof):
			proof = proof + 1
		return proof
	def print_participants(self):
		print("Printing a list of participants")
		for participant in self.participants:
			print(participant)


	def calculate_balances(self,participant):
		tx_sent = [[ transaction.amount for transaction in block.transactions if transaction.sender == participant ]for block in self.chain]
		tx_open_sent = [transaction.amount for transaction in self.open_transactions if transaction['sender']==participant]
		tx_sent.append(tx_open_sent)

		amount_sent = functools.reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_sent,0)
		# amount_sent = 0
		# for amount in tx_sent:
		# 	if len(amount) > 0:
		# 		for amt in amount:
		# 			amount_sent = amount_sent + amt
		tx_received = [[ transaction.amount for transaction in block.transactions if transaction.recipient == participant ]for block in self.chain]
		amount_received = 0
		amount_received = functools.reduce(lambda tx_sum ,tx_amt : tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_received,0)
		# for amount in tx_received:
		# 	if len(amount) > 0:
		# 		for amt in amount:
		# 			amount_received = amount_received + amt
		return amount_received-amount_sent


	def mine_block(self):
		
		hu = HashUtils()
		last_block = self.chain[-1]
		block_hash = hu.hash_block(last_block)
		proof = proof_of_work()
		# reward_transaction = {
		# 'sender' : 'MINER',
		# 'recipient' : owner,
		# 'amount' : MINING_REWARD
		# }
		reward_transaction = Transactions('MINER',owner,MINING_REWARD)
		copied_transactions = self.open_transactions[:]
		copied_transactions.append(reward_transaction)
		block = Block(index = len(self.chain),previousBlockHash = block_hash,proof = proof,transactions = copied_transactions)
		
		print("Adding new block %s"%(block.__dict__))
		self.append(block)
		output_blockchain()
		print("New length of blockchain %s"%(len(self.chain)))
		
		return True

	def save_data(self):
		
		try:
			with open('blockchain_data.txt','w') as write_file:
				saveable_chain = [ block.__dict__  for block in [Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof) for block_el in self.chain]]
				# converted_blocks = []
				# for block_el in blockchain:
				# 	converted_block = Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof)
				# 	print("converted_block is %s"%(converted_block))
				# 	converted_blocks.append(converted_block.__dict__)
				write_file.write(json.dumps(saveable_chain))
				write_file.write('\n')
				write_file.write(json.dumps(self.open_transactions))
		except IOError:
			print("Error in saving data to the file")

		# with open('blockchain_data.p','wb') as write_file:
		# 	write_data = {
		# 	'chain' : blockchain,
		# 	'transactions' : open_transactions
		# 	}
		# 	write_file.write(pickle.dumps(write_data))



	def load_data(self):
		
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

				self.chain = updated_blockchain
				self.open_transactions = updated_transactions
		except (IOError,AttributeError,IndexError):
			print("Handled the error")
		finally:
			print("Blockchain loaded")
			
	

	

















	



	# with open('blockchain_data.p','rb') as read_file:
	# 	file_contents = pickle.loads(read_file.read())
	# 	global blockchain
	# 	global open_transactions
	# 	blockchain = file_contents['chain']
	# 	open_transactions = file_contents['transactions']
		

is_user_interaction = True





