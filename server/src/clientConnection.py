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
			self.current_folder.make_directory(self.username)
		encUserFolder = self.current_folder.get_enc_file_name(self.username)
		self.stepIntoDirectory(encUserFolder)
	
	def stepIntoDirectory(self, directory):
		current_directory = os.path.join(self.current_folder.encryptedPath, directory)
		self.current_folder = folder(current_directory, self.username)
	
	def stepOutOfDirectory(self):
		current_directory = os.sep.join(self.current_folder.encryptedPath.split('/')[:-2]) + os.sep
		self.current_folder = folder(current_directory, self.username)
	
	def getPubKey(self):
		return self.pub_key

	def getUsername(self):
		return self.username