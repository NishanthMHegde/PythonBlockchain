from Crypto.PublicKey import RSA
import Crypto.Random
import binascii

class Wallet():
	def __init__(self):
		self.public_key = None
		self.private_key = None

	def create_keys(self):
		self.private_key,self.public_key = self.generate_keys()
	def generate_keys(self):
		private_key = RSA.generate(1024,Crypto.Random.new().read)
		public_key = private_key.publickey()
		return (binascii.hexlify(private_key.exportKey(format = 'DER')).decode('ascii'),binascii.hexlify(public_key.exportKey(format = 'DER')).decode('ascii'))


	def save_keys(self):
		if self.public_key is not None and self.private_key is not None:
			try:
				with open("keys.txt",'w') as write_file:
					write_file.write(self.public_key)
					write_file.write("\n")
					write_file.write(self.private_key)
			except:
				print("Saving keys failed")

	def load_keys(self):
		try:
			with open("keys.txt",'r') as read_file:
				key_data = read_file.readlines()
				self.public_key = key_data[0][:-1]
				self.private_key = key_data[1]
		except:
			print("Loading keys failed")