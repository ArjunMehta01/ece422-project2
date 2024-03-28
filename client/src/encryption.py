import rsa
import os
import socket

MESSAGE_SIZE = 1024

SERVER_PUB_KEY_PATH = "C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\client\\.secrets\\SERVER_PUB_KEY"
PUB_KEY_FILE_PATH = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\client\\.secrets\\id_rsa.pub'
PRIV_KEY_FILE_PATH = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\client\\.secrets\\id_rsa'

class rsaSocket:
	def __init__(self, serverIp, serverPort):
		server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_connection.connect((serverIp, serverPort))
		self.connection = server_connection
		priv, pub = load_keys_or_create_keys()
		self.priv_key = priv
		self.pub_key = pub
		self.server_pub_key = load_server_pub_key()
	
	def setServerPubKey(self, pub_key):
		'''Set the public key of the server to encrypt messages to the server, pub_key is the actual rsa binary pub_key'''
		self.server_pub_key = pub_key

	def send(self, message):
		if self.server_pub_key == None:
			raise Exception('No pub key set')
		encrypted = rsa.encrypt(message.encode(), self.server_pub_key)
		self.connection.sendall(encrypted)
	
	def send_add_pubkey(self, message, pub_key_string):
		pub_key = rsa.PublicKey.load_pkcs1(pub_key_string)
		encrypted = rsa.encrypt(message.encode(), pub_key)
		self.connection.sendall(encrypted)
	
	def recv(self):
		encrypted = self.connection.recv(MESSAGE_SIZE)
		message = rsa.decrypt(encrypted, self.priv_key).decode()
		return message
	
	def get_pub_key_string(self):
		return self.pub_key.save_pkcs1().decode()
	
def load_keys_or_create_keys():

	if os.path.exists(PRIV_KEY_FILE_PATH):
		with open(PRIV_KEY_FILE_PATH, 'rb') as f:
			private_key = rsa.PrivateKey.load_pkcs1(f.read())
		with open(PUB_KEY_FILE_PATH, 'rb') as f:
			public_key = rsa.PublicKey.load_pkcs1(f.read())
	else:
		(public_key, private_key) = rsa.newkeys(1024)

		os.makedirs(os.path.dirname(PUB_KEY_FILE_PATH), exist_ok=True)
		with open(PUB_KEY_FILE_PATH, 'wb') as f:
			f.write(public_key.save_pkcs1())
		with open(PRIV_KEY_FILE_PATH, 'wb') as f:
			f.write(private_key.save_pkcs1())

	return private_key, public_key

def load_server_pub_key():
	with open(SERVER_PUB_KEY_PATH, 'rb') as pub_key_file:  # Assuming the public key is stored in a file named 'public_key.pem'
		return rsa.PublicKey.load_pkcs1(pub_key_file.read())