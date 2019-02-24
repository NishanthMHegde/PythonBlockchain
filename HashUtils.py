import hashlib
import json
class HashUtils():
	def hash_block(self,block):
		hashable_block = block.__dict__.copy()
		hashable_block['transactions'] = [txn.__dict__ for txn in hashable_block['transactions']]
		return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()
