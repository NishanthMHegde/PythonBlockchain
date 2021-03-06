import functools
import hashlib
import json
import pickle
from collections import OrderedDict
from Block import Block
from Transactions import Transactions
from HashUtils import HashUtils
from Verifications import Verifications
from Wallet import Wallet
import requests
class Blockchain():
	def __init__(self,hosting_id,port_id):
		self.hosting_id = hosting_id
		self.port_id = port_id
		self.__chain = []
		self.__open_transactions = []
		self.__peer_nodes = set()
		self.load_data()
		self.participants = {self.hosting_id}
		self.MINING_REWARD = 12
	
	def get_chain(self):
		return self.__chain[:]

	def get_open_transactions(self):
		return self.__open_transactions[:]
	def proof_of_work(self):
		# verification = Verifications()
		hu = HashUtils()
		last_block = self.__chain[-1]
		last_hash = hu.hash_block(last_block)
		proof =0
		while not Verifications.valid_proof(self.__open_transactions,last_hash,proof):
			proof = proof + 1
		return proof
	


	def calculate_balances(self,sender = None):
		# print("Calculating balance in chain %s"%(self.__chain))
		if sender is None:
			if self.hosting_id is None:
				return None
			else:
				participant = self.hosting_id
		else:
			participant = sender
		# print("participant is %s"%(self.hosting_id))
		tx_sent = [[ transaction.amount for transaction in block.transactions if transaction.sender == participant ]for block in self.__chain]
		tx_open_sent = [transaction.amount for transaction in self.__open_transactions if transaction.sender==participant]
		tx_sent.append(tx_open_sent)

		amount_sent = functools.reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_sent,0)
		# amount_sent = 0
		# for amount in tx_sent:
		# 	if len(amount) > 0:
		# 		for amt in amount:
		# 			amount_sent = amount_sent + amt
		tx_received = [[ transaction.amount for transaction in block.transactions if transaction.recipient == participant ]for block in self.__chain]
		amount_received = 0
		amount_received = functools.reduce(lambda tx_sum ,tx_amt : tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0,tx_received,0)
		# for amount in tx_received:
		# 	if len(amount) > 0:
		# 		for amt in amount:
		# 			amount_received = amount_received + amt
		# print("Amount received is %s and amount sent is %s"%(amount_received,amount_sent))
		return amount_received-amount_sent

	def add_transaction(self,recipient,amount,signature,sender=None,is_recieving = False):
		if self.hosting_id is None:
			return False
		if sender is None:
			sender = self.hosting_id
	# transaction = {
	# "sender" : sender,
	# "recipient" : recipient,
	# "amount" : amount
	# }
		# verification = Verifications()
		transaction = Transactions(sender,recipient,amount,signature)
		if not Verifications.verify_transaction(transaction,self.calculate_balances):
			return False
		if Verifications.verify_transaction(transaction,self.calculate_balances):
			self.__open_transactions.append(transaction)
			self.participants.add(sender)
			self.participants.add(recipient)
			self.save_data()
			if is_recieving is False:
				for node in self.__peer_nodes:
					url = "http://{}/broadcast-transactions".format(node)
					try:
						response = requests.post(url,json = {'sender': sender,'recipient':recipient,'signature': signature,'amount' : amount})
						if response.status_code == 400 or response.status_code == 500:
							print("Broadcasting transactions failed")
							return False
						else:
							print("Successfully broadcasted transaction with response %s"%(response))
					except requests.exceptions.ConnectionError:
						continue
			return True
		else:
			return False
	def mine_block(self):
		if self.hosting_id is not None:
			hu = HashUtils()
			last_block = self.__chain[-1]
			block_hash = hu.hash_block(last_block)
			proof = self.proof_of_work()
			# reward_transaction = {
			# 'sender' : 'MINER',
			# 'recipient' : owner,
			# 'amount' : MINING_REWARD
			# }
			reward_transaction = Transactions('MINER',self.hosting_id,self.MINING_REWARD,'')
			copied_transactions = self.__open_transactions[:]
			
			if not Verifications.verify_transactions(copied_transactions,self.calculate_balances):
				return None
			copied_transactions.append(reward_transaction)
			block = Block(index = len(self.__chain),previousBlockHash = block_hash,proof = proof,transactions = copied_transactions)
			
			
			
			self.__open_transactions = []
			
			for node in self.__peer_nodes:
				url = "http://{}/broadcast-block".format(node)
				broadcasted_block = block.__dict__.copy()
				broadcasted_block['transactions'] = [txn.__dict__ for txn in broadcasted_block['transactions']]
				response = requests.post(url,json = {'block': broadcasted_block})
				if response.status_code == 500 or response.status_code == 400:
					print(json.loads(response.text))
					print("Broadcasting block failed")
				else:
					print("Successfully broadcasted the block")
			print("New length of blockchain %s"%(len(self.__chain)))
			print("Adding new block %s"%(block.__dict__))
			self.__chain.append(block)
			self.save_data()
			return block
		else:
			return None

	def add_block(self,block):
		print("Broadcasting will add %s"%(block))
		transactions = [ Transactions(sender = txn['sender'], recipient = txn['recipient'], amount = txn['amount'], signature = txn['signature'] ) for txn in block['transactions']]
		is_valid_proof = Verifications.valid_proof(transactions[:-1],block['previousBlockHash'], block['proof'])
		hu = HashUtils()
		is_valid_hash = block['previousBlockHash'] == hu.hash_block(self.__chain[-1])
		if (is_valid_hash is False) or (is_valid_proof is False):
			return False
		else:
			self.save_data()
			return True
	def save_data(self):
		
		try:
			with open('blockchain_data-%s.txt'%(self.port_id),'w') as write_file:
				saveable_chain = [ block.__dict__  for block in [Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof) for block_el in self.__chain]]
				# converted_blocks = []
				# for block_el in blockchain:
				# 	converted_block = Block(index = block_el.index, previousBlockHash = block_el.previousBlockHash,transactions = [txn.__dict__ for txn in block_el.transactions], proof = block_el.proof)
				# 	print("converted_block is %s"%(converted_block))
				# 	converted_blocks.append(converted_block.__dict__)
				write_file.write(json.dumps(saveable_chain))
				write_file.write('\n')
				saveable_transactions = [txn.__dict__ for txn in self.__open_transactions]
				write_file.write(json.dumps(saveable_transactions))
				write_file.write("\n")
				write_file.write(json.dumps(list(self.__peer_nodes)))
				
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
			with open('blockchain_data-%s.txt'%(self.port_id),'r') as read_file:
				block_data = read_file.readlines()
				
				blockchain = json.loads(block_data[0][:-1])
				
				open_transactions = json.loads(block_data[1][:-1])
				self.__peer_nodes = set(json.loads(block_data[2]))

				updated_blockchain = []
				updated_transactions = []

				for block in blockchain:
					updated_block = Block(index = block['index'],previousBlockHash = block['previousBlockHash'],transactions = [Transactions(txn['sender'],txn['recipient'],txn['amount'],txn['signature']) for txn in block['transactions']],proof = block['proof'])
					
					updated_blockchain.append(updated_block)

				for tx in open_transactions:
					updated_transaction = Transactions(tx['sender'],tx['recipient'],tx['amount'],tx['signature'])
					updated_transactions.append(updated_transaction)

				self.__chain = updated_blockchain
				self.__open_transactions = updated_transactions
		except (IOError,AttributeError,IndexError):
			genesis_block = Block(index = 0,previousBlockHash = "",transactions = [],proof = 100)
			self.__chain.append(genesis_block)
			self.__open_transactions = []
			print("Handled the error")
		finally:
			print("Blockchain loaded")
			
	
	def add_peer_node(self,node):
		self.__peer_nodes.add(node)
		self.save_data()

	def remove_peer_node(self,node):
		self.__peer_nodes.discard(node)
		self.save_data()

	def get_peer_nodes(self):
		return list(self.__peer_nodes)[:]
	

















	



	# with open('blockchain_data.p','rb') as read_file:
	# 	file_contents = pickle.loads(read_file.read())
	# 	global blockchain
	# 	global open_transactions
	# 	blockchain = file_contents['chain']
	# 	open_transactions = file_contents['transactions']
		

is_user_interaction = True





