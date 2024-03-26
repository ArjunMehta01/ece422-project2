import rsa

MESSAGE_SIZE = 1024

class rsaSocket:
	def __init__(self, connection):
		self.connection = connection
		self.priv_key = loadPrivKey()
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
	
def loadPrivKey():
	with open('./.secrets/id_rsa', 'r') as priv_key_file:
		private_key_string = priv_key_file.read().strip()
		private_key = rsa.PrivateKey.load_pkcs1(private_key_string)
	return private_key