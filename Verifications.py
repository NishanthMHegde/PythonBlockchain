import hashlib
from HashUtils import HashUtils
class Verifications():
	@staticmethod
	def valid_proof(transactions,previousBlockHash,proof):
		str_hash = str([txn.to_ordered_dict() for txn in transactions]) + str(previousBlockHash) + str(proof)
		str_hash = hashlib.sha256(str_hash.encode('utf-8')).hexdigest()
		
		return str_hash[0:2]=='00'
	@staticmethod
	def verify_transaction(transaction,calculate_balances):
		sender_balance = calculate_balances()
		if sender_balance >= transaction.amount:
			return True
		else:
			return False

	@classmethod
	def verify_transactions(cls,open_transactions,calculate_balances):
		return all([cls.verify_transaction(txn,calculate_balances) for txn in open_transactions])

	@classmethod
	def validate_chain(cls,blockchain):
		hu = HashUtils()
		for (index,block) in enumerate(blockchain):
			if index == 0:
				continue
			if blockchain[index].previousBlockHash != hu.hash_block(blockchain[index-1]):
				return False
			if not cls.valid_proof(block.transactions[:-1],block.previousBlockHash,block.proof):
				print("Proof of work failed")
				return False
		return True