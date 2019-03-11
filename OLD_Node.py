from Verifications import Verifications
from Blockchain import Blockchain
from uuid import uuid4
from Wallet import Wallet
class Node():
	def __init__(self):
		self.id = str(uuid4())
		self.wallet = Wallet()
		self.wallet.create_keys()
		self.blockchain = Blockchain(self.wallet.public_key)
		# self.blockchain = Blockchain(self.id)
	
	def get_last_transaction(self):
		if len(self.blockchain.get_chain()) < 1:
				return None
		return self.blockchain.get_chain()[-1]
	def output_blockchain(self):
		
		print("There are %s blocks"%(len(self.blockchain.get_chain())))
		for block in self.blockchain.get_chain():
			print("Outputting block")
			print(block.__dict__)

			print('-'*30)
	def get_user_transaction(self):
		tx_recipient = input("Enter the name of the recipient")
		tx_amount = float(input("Enter the transaction amount"))
		return tx_recipient,tx_amount
	def get_user_choice(self):
		choice = input("Enter your choice")
		return choice
	def listen_for_input(self):
		is_user_interaction = True
		while is_user_interaction:
			
			print("Please select an appropriate choice")
			print("1. Add transaction")
			print("2. View blockchain")
			print("3. Verify Transactions")
			print("4. Validate block chain")
			print("5. Mine block")
			print("6. Print participants")
			print("7. Calculate balance of each participant")
			print("8.Create a Wallet")
			print("9. Load Wallet")
			print("10. Save Wallet")
			print("q. Quit")

			user_choice = self.get_user_choice()
			if user_choice == '1':
				recipient,amount = self.get_user_transaction()
				signature = self.wallet.sign(sender=self.wallet.public_key,recipient=recipient,amount=amount)
				if self.blockchain.add_transaction(recipient,amount=amount,sender = self.wallet.public_key,signature = signature):
					print("Transaction Successful")
				else:
					print("Transaction failed")
				
			elif user_choice == '2':
				self.output_blockchain()
			# elif user_choice == '3':
			# 	blockchain[0] = {
			# 	"previousBlockHash" : "",
			# 	"index" : 0,
			# 	"transactions": [{"recipient" : "Manu", "sender": "fsdf87df7dfbfshgh9834", "amount" : 120.0}]
			# 	}
			elif user_choice == '3':
				# verification = Verifications()
				if Verifications.verify_transactions(self.blockchain.get_open_transactions(),self.blockchain.calculate_balances):
					print("All transactions are valid and verified")
				else:
					print("Transacton verification failed")

			elif user_choice == '4':
				# verification = Verifications()
				is_valid_blockchain = Verifications.validate_chain(self.blockchain.get_chain())
				if is_valid_blockchain is True:
					print("Block chain is valid")
				else:
					print("Blockchain is invalid")
					break
			elif user_choice == '5':
				is_block_mined = self.blockchain.mine_block()
				if is_block_mined:
					print("Block was mined successfully")
				else:
					print("Block mining failed. GOt no wallet?")
				
			elif user_choice == '6':
				self.blockchain.print_participants()
			elif user_choice == '7':
				print("Balance of %s is %s"%(self.wallet.public_key,self.blockchain.calculate_balances()))

			elif user_choice == '8':
				
				self.wallet.create_keys()
				self.blockchain = Blockchain(self.wallet.public_key)
			elif user_choice == '9':
				
				self.wallet.load_keys()
				self.blockchain = Blockchain(self.wallet.public_key)
			elif user_choice == '10':
				self.wallet.save_keys()
				
			elif user_choice == 'q':
				is_user_interaction = False
				break
			# verification = Verifications()
			# if not Verifications.validate_chain(self.blockchain.get_chain()):
			# 	print("Invalid block")
			# 	break

node = Node()
node.listen_for_input()