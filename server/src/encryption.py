import rsa
import os
from Crypto.Cipher import AES
import struct

MESSAGE_SIZE = 1024

PUB_KEY_FILE_PATH = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\server\\.secrets\\id_rsa.pub'
PRIV_KEY_FILE_PATH = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\server\\.secrets\\id_rsa'

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


def load_priv_or_create_keys():
	if os.path.exists(PRIV_KEY_FILE_PATH):
		with open(PRIV_KEY_FILE_PATH, 'rb') as f:
			private_key = rsa.PrivateKey.load_pkcs1(f.read())
	else:
		(public_key, private_key) = rsa.newkeys(1024)

		with open(PUB_KEY_FILE_PATH, 'wb') as f:
			f.write(public_key.save_pkcs1())
		with open(PRIV_KEY_FILE_PATH, 'wb') as f:
			f.write(private_key.save_pkcs1())
	return private_key


def getRSAKey(str: str):
	"""Turns a string into an RSA key"""
	return rsa.PublicKey.load_pkcs1(str.encode())