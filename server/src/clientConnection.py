
# keep track of stuff like client pubkey current directory, any information for the currently active client connection
class clientConnection:
	def __init__(self, pub_key, username):
		self.pub_key = pub_key
		self.current_directory = ''
		self.username = username
	
	def stepIntoDirectory(self, directory):
		self.current_directory += directory + '/'
	
	def stepOutOfDirectory(self):
		self.current_directory = '/'.join(self.current_directory.split('/')[:-2]) + '/'
	
	def getPubKey(self):
		return self.pub_key

	def getUsername(self):
		return self.username