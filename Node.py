from flask import Flask,jsonify 
from flask_cors import CORS 
from Blockchain import Blockchain
from Wallet import Wallet

app = Flask(__name__)
CORS(app)
wallet = Wallet()

blockchain = Blockchain(wallet.public_key)

@app.route('/wallet',methods = ['POST'])
def create_keys():
	wallet.create_keys()
	save_status = wallet.save_keys()
	if save_status is True:
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key
		}
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		return jsonify(message),200
	else:
		message = {
		"status": "FAILED to setup keys"
		}
		return jsonify(message),500

@app.route('/wallet',methods = ['GET'])
def load_keys():
	load_status = wallet.load_keys()
	if load_status == True:
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key
		}
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		return jsonify(message),200
	else:
		message = {
		"status": "FAILED to load keys"
		}
		return jsonify(message),500


@app.route('/',methods = ['GET'])
def get_ui():
	return "UI Page"
@app.route('/chain',methods = ['GET'])
def get_chain():
	chain_snapshot = blockchain.get_chain()
	dict_chain = [block.__dict__ for block in chain_snapshot]
	for dict_block in dict_chain:
		dict_block['transactions'] = [txn.__dict__ for txn in dict_block['transactions']]
	return jsonify(dict_chain),200

@app.route('/mine',methods = ['POST'])
def mine_block():
	block = blockchain.mine_block()
	if block is not None:
		dict_block =block.__dict__.copy()
		dict_block['transactions'] = [txn.__dict__ for txn in dict_block['transactions']]
		message = {
		"block": dict_block,
		"status" : "SUCCESS",
		"wallet_setup" : wallet.public_key != None
		}
		return jsonify(message),200
	else:
		message = {
		"status" : "FAIL",
		"wallet_setup" : wallet.public_key != None
		}
		return jsonify(message),500

if __name__ == "__main__":
	app.run(host = "0.0.0.0",port = 5000)
