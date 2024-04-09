import rsa
import os
import socket
from Crypto.Cipher import AES
import struct

MESSAGE_SIZE = 1024

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
		
		aes_rand_key = rsa.randnum.read_random_bits(128)
		cipher = AES.new(aes_rand_key, AES.MODE_EAX)

		ciphertext, tag = cipher.encrypt_and_digest(message.encode())

		encrypted_aes_tag = rsa.encrypt(tag, self.server_pub_key)
		encrypted_aes_key = rsa.encrypt(aes_rand_key, self.server_pub_key)
		encrypted_aes_nonce = rsa.encrypt(cipher.nonce, self.server_pub_key)

		for var in [ciphertext, encrypted_aes_tag, encrypted_aes_key, encrypted_aes_nonce]:
			# Pack the length of the data (4 bytes integer)
			length = len(var)
			length_packed = struct.pack('!I', length)

			# Send the length
			self.connection.sendall(length_packed)

			# Send the data
			self.connection.sendall(var)

	
	def send_add_pubkey(self, message, pub_key_string):
		pub_key = rsa.PublicKey.load_pkcs1(pub_key_string)
		aes_rand_key = rsa.randnum.read_random_bits(128)
		cipher = AES.new(aes_rand_key, AES.MODE_EAX)

		ciphertext, tag = cipher.encrypt_and_digest(message.encode())

		encrypted_aes_tag = rsa.encrypt(tag, pub_key)
		encrypted_aes_key = rsa.encrypt(aes_rand_key, pub_key)
		encrypted_aes_nonce = rsa.encrypt(cipher.nonce, pub_key)

		for var in [ciphertext, encrypted_aes_tag, encrypted_aes_key, encrypted_aes_nonce]:
			# Pack the length of the data (4 bytes integer)
			length = len(var)
			length_packed = struct.pack('!I', length)

			# Send the length
			self.connection.sendall(length_packed)

			# Send the data
			self.connection.sendall(var)
	
	def recv(self):

		length_data = self.connection.recv(4)
		length = struct.unpack('!I', length_data)[0]
		ciphertext = self.connection.recv(length)

		length_data = self.connection.recv(4)
		length = struct.unpack('!I', length_data)[0]
		enc_aes_tag = self.connection.recv(length)

		length_data = self.connection.recv(4)
		length = struct.unpack('!I', length_data)[0]
		enc_aes_key = self.connection.recv(length)

		length_data = self.connection.recv(4)
		length = struct.unpack('!I', length_data)[0]
		enc_aes_nonce = self.connection.recv(length)
		
		aes_tag = rsa.decrypt(enc_aes_tag, self.priv_key)
		aes_key = rsa.decrypt(enc_aes_key, self.priv_key)
		aes_nonce = rsa.decrypt(enc_aes_nonce, self.priv_key)

		cipher = AES.new(aes_key, AES.MODE_EAX, nonce=aes_nonce)
		plaintext = cipher.decrypt(ciphertext)

		try:
			cipher.verify(aes_tag)
			return plaintext.decode()
		except ValueError:
			return None
	
	def get_pub_key_string(self):
		return self.pub_key.save_pkcs1().decode()
	
def load_keys_or_create_keys():
	PUB_KEY_FILE_PATH = os.getenv('SECRETS_PATH') + 'id_rsa.pub'
	PRIV_KEY_FILE_PATH = os.getenv('SECRETS_PATH') + 'id_rsa'
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
	SERVER_PUB_KEY_PATH = os.getenv('SECRETS_PATH') + 'SERVER_PUB_KEY'
	with open(SERVER_PUB_KEY_PATH, 'rb') as pub_key_file:  # Assuming the public key is stored in a file named 'public_key.pem'
		return rsa.PublicKey.load_pkcs1(pub_key_file.read())