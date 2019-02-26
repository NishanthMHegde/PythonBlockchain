from Verifications import verification
class Node():
	def __init__(self):
		self.blockchain = []
	def add_transaction(self,recipient, amount, sender = owner):
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
	def get_last_transaction(self):
		if len(self.blockchain) < 1:
				return None
		return self.blockchain[-1]
	def output_blockchain(self):
		
		print("There are %s blocks"%(len(self.blockchain)))
		for block in self.blockchain:
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
			print("q. Quit")

			user_choice = self.get_user_choice()
			if user_choice == '1':
				recipient,amount = self.get_user_transaction()
				if self.add_transaction(recipient,amount=amount):
					print("Transaction Successful")
				else:
					print("Transaction failed")
				print(open_transactions)
			elif user_choice == '2':
				self.output_blockchain()
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