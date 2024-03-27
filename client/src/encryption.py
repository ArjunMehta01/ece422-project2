import rsa
import os
import socket

MESSAGE_SIZE = 1024

PUB_KEY_FILE_PATH = '../.secrets/id_rsa.pub'
PRIV_KEY_FILE_PATH = '../.secrets/id_rsa'

class rsaSocket:
	def __init__(self, serverIp, serverPort):
		server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_connection.connect((serverIp, serverPort))
		self.connection = server_connection
		self.priv_key = load_priv_or_create_keys()
		self.pub_key = None
	
	def setPubKey(self, pub_key_string):
		self.pub_key = rsa.PublicKey.load_pkcs1(pub_key_string)

	def send(self, message):
		if self.pub_key == None:
			raise Exception('No pub key set')
		encrypted = rsa.encrypt(message.encode(), self.pub_key)
		self.connection.sendall(encrypted)
	
	def send_add_pubkey(self, message, pub_key_string):
		pub_key = rsa.PublicKey.load_pkcs1(pub_key_string)
		encrypted = rsa.encrypt(message.encode(), pub_key)
		self.connection.sendall(encrypted)
	
	def recv(self):
		encrypted = self.connection.recv(MESSAGE_SIZE)
		message = rsa.decrypt(encrypted, self.priv_key).decode()
		return message
	
def load_priv_or_create_keys():
	if os.path.exists(PRIV_KEY_FILE_PATH):
		with open(PRIV_KEY_FILE_PATH, 'rb') as f:
			private_key = rsa.PublicKey.load_pkcs1(f.read())
	else:
		(public_key, private_key) = rsa.newkeys(1024)

		with open(PUB_KEY_FILE_PATH, 'wb') as f:
			f.write(public_key.save_pkcs1())
		with open(PRIV_KEY_FILE_PATH, 'wb') as f:
			f.write(private_key.save_pkcs1())
	return private_key