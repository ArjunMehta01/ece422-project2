import os
from filesystem import folder
# keep track of stuff like client pubkey current directory, any information for the currently active client connection
class clientConnection:
	def __init__(self, pub_key, username):
		self.pub_key = pub_key
		self.username = username
		self.current_folder = folder('', self.username)
		files = self.current_folder.list_files_in_folder()
		if self.username not in files:
			self.current_folder.make_directory(self.username, 'GROUP')
		self.stepIntoDirectory(self.username)
	
	def stepIntoDirectory(self, directory, getEncryptedName = True):
		"""Steps into the directory specified by the directory parameter. If getEncryptedName is True, the directory parameter is assumed to be an unencrypted directory name and the encrypted name is retrieved. If getEncryptedName is False, the directory parameter is assumed to be an encrypted directory name."""
		if getEncryptedName:
			directory = self.current_folder.get_enc_file_name(directory)
		if directory is None:
			print("Directory not found")
			return
		self.current_folder = folder(directory, self.username)
	
	def stepOutOfDirectory(self):
		pathTokens = self.current_folder.encryptedPath.split(os.sep)
		if len(pathTokens) == 0:
			print("Cannot step out of root directory")
			return
		# remove last element from path tokens
		pathTokens = pathTokens[:-1]
		# rejoin path tokens
		current_directory = os.sep.join(pathTokens)
		self.current_folder = folder(current_directory, self.username)
	
	def getPubKey(self):
		return self.pub_key

	def getUsername(self):
		return self.username