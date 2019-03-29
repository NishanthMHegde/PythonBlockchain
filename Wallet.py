from Crypto.PublicKey import RSA
import Crypto.Random
import binascii
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
class Wallet():
    def __init__(self,port_id):
        self.public_key = None
        self.private_key = None
        self.port_id = port_id

    def create_keys(self):
        self.private_key,self.public_key = self.generate_keys()
    def generate_keys(self):
        private_key = RSA.generate(1024,Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format = 'DER')).decode('ascii'),binascii.hexlify(public_key.exportKey(format = 'DER')).decode('ascii'))


    def save_keys(self):
        if self.public_key is not None and self.private_key is not None:
            print(self.public_key,self.private_key)
            print("printint go %s"%("keys-%s.%s"%(self.port_id,'txt')))
            try:
                with open("keys-%s.%s"%(self.port_id,'txt'),'w') as write_file:

                    write_file.write(self.public_key)
                    write_file.write("\n")
                    write_file.write(self.private_key)
                return True
            except Exception as e:
                print("Saving keys failed with %s"%(e))
                return False


    def load_keys(self):
        try:
            with open("keys-%s.%s"%(self.port_id,'txt'),'r') as read_file:
                key_data = read_file.readlines()
                self.public_key = key_data[0][:-1]
                self.private_key = key_data[1]
            return True
        except:
            print("Loading keys failed")
            return False

    def sign(self,sender,recipient,amount):
        payload = (str(sender) + str(recipient) + str(amount)).encode('utf8')
        payload_hash = SHA256.new(payload)
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        signature = signer.sign(payload_hash)
        return binascii.hexlify(signature).decode('ascii')
    

    @staticmethod
    def verify_transaction(transaction):
        
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        payload = (str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8')
        payload_hash = SHA256.new(payload) 
        verifier = PKCS1_v1_5.new(public_key)
        return verifier.verify(payload_hash,binascii.unhexlify(transaction.signature))