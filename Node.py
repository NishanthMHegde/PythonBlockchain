from flask import Flask,jsonify,request
from flask_cors import CORS 
from Blockchain import Blockchain
from Wallet import Wallet
from argparse import ArgumentParser
app = Flask(__name__)
CORS(app)


@app.route('/wallet',methods = ['POST'])
def create_keys():
	wallet.create_keys()
	save_status = wallet.save_keys()
	if save_status is True:

		global blockchain
		blockchain = Blockchain(wallet.public_key,port)
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key,
		"Balance" : blockchain.calculate_balances(wallet.public_key)
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
		blockchain = Blockchain(wallet.public_key,port)
		message = {
		"public_key": wallet.public_key,
		"private_key" : wallet.private_key,
		"Balance" : blockchain.calculate_balances(wallet.public_key)
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
		"funds" : blockchain.calculate_balances(wallet.public_key)
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
	balance = blockchain.calculate_balances(wallet.public_key)
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
	transaction_status = blockchain.add_transaction(values['recipient'],values['amount'],signature,wallet.public_key,is_recieving = False)
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

@app.route('/node',methods = ['POST'])
def add_node():
	values = request.get_json()
	if values is None or 'node' not in values:
		message = {
		"Error" : "Node data was not found"
		}
		return jsonify(message),400
	else:
		blockchain.add_peer_node(values['node'])
		message = {
		"Message" : "Successfully added node",
		"all_nodes" : list(blockchain.get_peer_nodes())
		}
		return jsonify(message),201
@app.route('/node/<node_url>',methods = ['DELETE'])
def remove_node(node_url):
	if node_url is None:
		message = {
		"Error" : "Node to remove was not specified"
		}
		return jsonify(message),401
	else:
		blockchain.remove_peer_node(node_url)
		message = {
		"Message" : "Successfully removed peer node",
		"all_nodes" : list(blockchain.get_peer_nodes())
		}
		return jsonify(message),201
@app.route('/node',methods = ['GET'])
def get_all_nodes():
	peer_nodes = blockchain.get_peer_nodes()
	message = {
	'all_nodes' : list(peer_nodes)
	}
	return jsonify(message),201

@app.route('/broadcast-transactions', methods = ['POST'])
def broadcast_transactions():
	values = request.get_json()

	if values is None:
		message = {
		'Error' : "Broadcastd transaction was empty"
		}
		return jsonify(message),400
	required_values = ['sender','recipient','amount','signature']
	if not all([field in values for field in required_values]):
		message = {
		"Error" : "All fields were not present"
		}
		return jsonify(message),400

	success = blockchain.add_transaction(sender = values['sender'], recipient = values['recipient'], signature = values['signature'], amount = values['amount'],is_recieving=True)
	if success == True:
		message = {
		"Status" : "Successfully added transaction",
		"Transaction" : {
		"sender" : values['sender'],
		"recipient" : values['recipient'],
		"amount" : values['amount'],
		"signature" : values['signature']
		}
		}
		return jsonify(message),201
	else:
		message = {
		'Error' : "Broadcastd transaction failed"
		}
		return jsonify(message),500
@app.route('/broadcast-block',methods = ['POST'])
def broadcast_block():
	values = request.get_json()
	if values is None:
		message = {
		"Error" : "No values were received"
		}
		return jsonify(message),500
	if 'block' not in values:
		message = {
		"Error" : "Block was not received"
		}
		return jsonify(message),500
	block = values['block']
	if block['index'] == blockchain.get_chain()[-1].index + 1:
		success = blockchain.add_block(block)
		if success == True:
			message = {
			"Success" : "Block was broadcasted Successfully"
			}
			return jsonify(message),200
		else:
			message = {
			"Error" : "Block was not broadcasted due to some reasons"
			}
			return jsonify(message),400
	elif block['index'] > blockchain.get_chain()[-1].index:
		pass
	else:
		message = {
		"Error :": "Block recieved was from a shorted blockchain"
		}
		return jsonify(message),500

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('-p','--port',type = int,default = 5000)
	args = parser.parse_args()
	port = args.port
	print(port)
	wallet = Wallet(port)
	blockchain = Blockchain(wallet.public_key,port)
	app.run(host = "0.0.0.0",port = port)
