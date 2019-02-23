class Block():
	def __init__(self,index,previousBlockHash,transactions,proof):
		self.previousBlockHash = previousBlockHash
		self.index = index
		self.transactions = transactions
		self.proof = proof
		