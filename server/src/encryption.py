import rsa
import os

MESSAGE_SIZE = 1024

PUB_KEY_FILE_PATH = '../.secrets/id_rsa.pub'
PRIV_KEY_FILE_PATH = '../.secrets/id_rsa'

# takes a raw socket and gives sendall + recv methods that do communication with rsa encryption
# load up the private key from a local file
# include a method to set the client pubkey after construction since it only comes in on the first decrypted message
# send recv methods should include a standard buff size so we dont need to specify it - shit design but fuck it we go fast
class rsaSocket:
	def __init__(self, connection):
		self.connection = connection
		self.priv_key = load_priv_or_create_keys()
		self.pub_key = None
	
	def setPubKey(self, pub_key_string):
		self.pub_key = rsa.PublicKey.load_pkcs1(pub_key_string)

	def send(self, message):
		if self.pub_key == None:
			raise Exception('No pub key set')
		encrypted = rsa.encrypt(message.encode(), self.pub_key)
		self.connection.sendall(encrypted)
	
	def send(self, message, pub_key_string):
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
