# get all the permissions for the files/folders in root
# check which ones are owned by the user
# exactly one of them should be a folder named after the user -- encrypted
# decrypt all the names of all the files/folders in that folder
# if the username folder doesnt exist, create it
# set the user conn current directory into that folder

# get all the permissions for the files/folders in that folder
# check which ones are owned by the user
# decrypt the names of those and store them smwhere so they can be accessed later
# make sure to map encrypted names to unencrypted names

# PERMISSIONS class
# loads all permissions at launch
# gives methods to modify permissions for each filename

# FOLDER class
# - unencrypted path
# - load all files in the folder (assuming your user permission)
# keeps a dictionary of encrypted names to unencrypted names (if no permission, unencrypted is just encrypted)
# if no permission, just loads an encrypted name and content is CANNOT ACCESS!

# FILE class
# - unencrypted path (for displaying to user)
# - encrypted path (for use in file encryptor)
# content

from fileEncryptor import storeFile, getFile, decryptFileName, make_directory as _make_directory
from auth import getUsers
import os

class permissions:
    def __init__(self) -> None:
        self.permissions = {}
        self.load_permissions()
    
    def load_permissions(self):
        filename = '.perms'
        
        permsFileContent = getFile(filename)
        
        if not permsFileContent:
            storeFile('', filename, '', False)
            return # no permissions to load

        for line in permsFileContent.split('\n'):
            if line == '':
                continue
            encFileName, mode, owner = line.split('][')
            self.permissions[encFileName] = {'mode': mode, 'owner': owner}
    
    def save_permissions(self):
        fileContent = ''
        for encFileName, data in self.permissions.items():
            fileContent += f'{encFileName}][{data["mode"]}][{data["owner"]}\n'
        
        storeFile('', '.perms', fileContent, False)
    
    def get_permission_mode(self, encFileName):
        if encFileName in self.permissions:
            return self.permissions[encFileName]['mode']
        return None
    
    def get_owner(self, encFileName):
        if encFileName in self.permissions:
            return self.permissions[encFileName]['owner']
        return None
    
    def add_new_permission(self, encFileName, mode, owner):
        self.permissions[encFileName] = {'mode': mode, 'owner': owner}
        self.save_permissions()
    
    def set_permission_mode(self, encFileName, mode):
        if encFileName not in self.permissions:
            return None
        self.permissions[encFileName]['mode'] = mode
        self.save_permissions()

class folder:
    def __init__(self, encryptedPath, accessingUser):
        self.encryptedPath = encryptedPath
        self.unencryptedPath = decryptFileName(encryptedPath)
        self.accessingUser = accessingUser
        self.fileMap = {} # maps the encrypted names of files to the File objects
        self.authenticated = self.check_self_permissions()
        self.load_files()
    
    def check_self_permissions(self):
        if self.encryptedPath == '': # root folder
            return True
        perms = permissions()
        self.owner = perms.get_owner(self.encryptedPath)
        mode = perms.get_permission_mode(self.encryptedPath)
        if mode == 'ALL':
            return True
        
        if mode == 'USER':
            return self.accessingUser == self.owner
        
        if mode == 'GROUP':
            user_dict = getUsers()
            accessingUserGroup = user_dict[self.accessingUser].get_group()
            ownerGroup = user_dict[self.owner].get_group()
            return accessingUserGroup == ownerGroup
        
        raise Exception('Invalid permission mode')

    def load_files(self):
        
        decrypt = self.authenticated
        FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
        fullpath = os.path.join(FILE_SYSTEM_PATH, self.encryptedPath)
        files = os.listdir(fullpath)
        perms = permissions()
        for file in files:
            # if the file is a .sign skip it
            if file.endswith('.sign'):
                continue
            
            if file in ['.perms', '.user']:
                continue
            
            # append the folder's path to the start of the filename
            fullFilePath = os.path.join(self.encryptedPath, file)
            
            if not decrypt:
                self.fileMap[fullFilePath] = File(file, None, False)
                continue
            
            # get file permissions
            mode = perms.get_permission_mode(fullFilePath)
            owner = perms.get_owner(fullFilePath)
            
            # check if user has permission
            if mode == 'ALL':
                access = True
            elif mode == 'USER':
                access = self.accessingUser == owner
            elif mode == 'GROUP':
                user_dict = getUsers()
                accessingUserGroup = user_dict[self.accessingUser].get_group()
                ownerGroup = user_dict[owner].get_group()
                access = accessingUserGroup == ownerGroup
            else:
                raise Exception('Invalid permission mode')
            
            if access:
                decryptedFileName = decryptFileName(file)
                self.fileMap[fullFilePath] = File(fullFilePath, decryptedFileName, True)
            else:
                self.fileMap[fullFilePath] = File(fullFilePath, None, False)
    
    
    def list_files_in_folder(self):
        """Returns a list of the names of the files and folders in this folder."""
        files = []
        for file in self.fileMap.values():
            fullPath = file.get_unencrypted_name()
            if not fullPath:
                fullPath = file.get_encrypted_path()
            # pull out just the filename using this os's file seperator
            files.append(fullPath.split(os.sep)[-1])
        return files
    
    
    def get_file_content(self, filename):
        """filename will be the unencrypted name of the file. Returns the content of the file."""
        # need to get the encrypted name of the file by iterating over all the files in the folder
        encFileName = None
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == filename:
                encFileName = file.get_encrypted_path()
                break
        else:
            return 'FILE NOT FOUND'
        file = self.fileMap[encFileName]
        return file.get_content()
    
    def make_directory(self, dirname):
        """Given an unencrypted directory name, creates a new directory in the current folder."""
        encDirName = _make_directory(self.encryptedPath, dirname)
        perms = permissions()
        perms.add_new_permission(os.path.join(self.encryptedPath, encDirName), 'USER', self.accessingUser)
        self.load_files()
        
    def make_empty_file(self, name):
        """Given an unencrypted file name and content, creates a new file in the current folder."""
        encFileName = storeFile(self.encryptedPath, name, '', True)
        perms = permissions()
        perms.add_new_permission(os.path.join(self.encryptedPath, encFileName), 'USER', self.accessingUser)
        self.load_files()
    
    def make_file(self, name, content):
        """Given an unencrypted file name and content, creates a new file in the current folder."""
        storeFile(self.encryptedPath, name, content, True)
        perms = permissions()
        perms.set_permission_mode(os.path.join(self.encryptedPath, name), 'USER')
        self.load_files()
    
    def rename_file(self, oldName, newName):
        """Given the unencrypted names of the old and new files, renames the old file to the new file."""
        # gotta find the encrypted names of the files
        oldEncName = None
        
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == oldName:
                oldEncName = file.get_encrypted_path()
                break
        
        # load content of old file
        content = self.fileMap[oldEncName].get_content()
        
        # store content in new file
        self.make_file(newName, content)
        
        # delete old file
        os.remove(oldEncName)
        
    def get_enc_file_name(self, filename):
        """Given the unencrypted name of a file, returns the encrypted path of the file."""
        # look in the file map for the file
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == filename:
                return file.get_encrypted_path()
        return None
    
    def modify_file_permissions(self, filename, newMode):
        """Given the unencrypted name of a file and a new permission mode, changes the permission mode of the file."""
        # need to append the folder's path to the start of the filename
        filename = os.path.join(self.encryptedPath, filename)

        # find the encrypted name of the file
        encFileName = None
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == filename:
                encFileName = file.get_encrypted_path()
                break
        else:
            return 'FILE NOT FOUND'
        
        perms = permissions()
        perms.set_permission_mode(encFileName, newMode)
        self.load_files()
           
class File:
    def __init__(self, encryptedPath, unencryptedFileName = None, access = False):
        self.encryptedPath = encryptedPath
        self.unencryptedFileName = unencryptedFileName
        self.access = access
    
    def load_content(self):
        if self.access:
            self.content = getFile(self.encryptedPath)
        else:
            self.content = 'CANNOT ACCESS!'
    
    def get_content(self):
        self.load_content()
        return self.content
    
    def get_unencrypted_name(self):
        """Returns the whole unencrypted path of the file from the root of the filesystem."""
        return self.unencryptedFileName
    
    def get_encrypted_path(self):
        """Returns the whole encrypted path of the file from the root of the filesystem."""
        return self.encryptedPath