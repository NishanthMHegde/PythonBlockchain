import hashlib
from HashUtils import HashUtils
class Verifications():
	def valid_proof(self,transactions,previousBlockHash,proof):
		str_hash = str([txn.to_ordered_dict() for txn in transactions]) + str(previousBlockHash) + str(proof)
		str_hash = hashlib.sha256(str_hash.encode('utf-8')).hexdigest()
		
		return str_hash[0:2]=='00'

	def verify_transaction(self,transaction,calculate_balances):
		sender_balance = calculate_balances(transaction.sender)
		if sender_balance >= transaction.amount:
			return True
		else:
			return False


	def verify_transactions(self,open_transactions,calculate_balances):
		return all([self.verify_transaction(txn,calculate_balances) for txn in open_transactions])

	def validate_chain(self,blockchain):
		hu = HashUtils()
		for (index,block) in enumerate(blockchain):
			if index == 0:
				continue
			if blockchain[index].previousBlockHash != hu.hash_block(blockchain[index-1]):
				return False
			if not self.valid_proof(block.transactions[:-1],block.previousBlockHash,block.proof):
				print("Proof of work failed")
				return False
		return True