import rsa

# takes a raw socket and gives sendall + recv methods that do communication with rsa encryption
# load up the private key from a local file
# include a method to set the client pubkey after construction since it only comes in on the first decrypted message
# send recv methods should include a standard buff size so we dont need to specify it - shit design but fuck it we go fast
class rsaSocket:
	def __init__(self, connection):
		self.connection = connection
		self.priv_key = loadPrivKey()


def loadPrivKey():
	
		
