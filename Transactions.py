from collections import OrderedDict
from Printable import Printable
class Transactions(Printable):
	def __init__(self,sender,recipient,amount,signature):
		self.sender = sender
		self.recipient = recipient
		self.amount = amount
		self.signature = signature

	def to_ordered_dict(self):
		return OrderedDict([('sender',self.sender),('recipient',self.recipient),('amount',self.amount),('signature',self.signature)])