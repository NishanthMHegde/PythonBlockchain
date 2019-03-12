from flask import Flask,jsonify,request
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

		global blockchain
		blockchain = Blockchain(wallet.public_key)
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key,
		"Balance" : blockchain.calculate_balances()
		}
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
		
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key,
		"Balance" : blockchain.calculate_balances()
		}
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
		"wallet_setup" : wallet.public_key != None,
		"funds" : blockchain.calculate_balances()
		}
		return jsonify(message),200
	else:
		message = {
		"status" : "FAIL",
		"wallet_setup" : wallet.public_key != None
		}
		return jsonify(message),500

@app.route('/funds',methods = ['GET'])
def get_balance():
	balance = blockchain.calculate_balances()
	if balance is None:
		message = {
		"Error" : "Funds could not be retrieved"
		}
		return jsonify(message),400
	else:
		message = {
		"Owner" : wallet.public_key,
		"Balance" : balance
		}
		return jsonify(message),200


@app.route('/transactions',methods = ['POST'])

def add_transaction():
	values = request.get_json()
	if values is None:
		message = {
		"Message" : "No transaction value was sent"
		}
		return jsonify(message),500
	required_values =['recipient','amount']
	is_values_present = all([ field in required_values for field in values])
	if is_values_present is False:
		message = {
		"Message" : "All field values were not present"
		}
		return jsonify(message),500
	signature = wallet.sign(wallet.public_key,values['recipient'],values['amount'])
	transaction_status = blockchain.add_transaction(values['recipient'],values['amount'],signature,wallet.public_key)
	if transaction_status is True:
		message = {
		"status" : "Successfully added transaction",
		"transaction" : {
		"sender" : wallet.public_key,
		"recipient" : values['recipient'],
		"amount" : values['amount'],
		"signature" : signature
		}
		}
		return jsonify(message),201
	else:
		message = {
		"Error" : "Transaction failed"
		}
		return jsonify(message),500

@app.route('/transactions',methods = ['GET'])
def fetch_transactions():
	transactions = blockchain.get_open_transactions()
	message = {
	"Transactions" : [txn.__dict__.copy() for txn in transactions]
	}
	return jsonify(message),200
if __name__ == "__main__":
	app.run(host = "0.0.0.0",port = 5000)
