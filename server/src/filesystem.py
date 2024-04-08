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

from fileEncryptor import storeFile, getFile, decryptFileName
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
    
    def set_permission_mode(self, encFileName, mode):
        self.permissions[encFileName]['mode'] = mode
        self.save_permissions()

class folder:
    def __init__(self, encryptedPath, accessingUser):
        self.encryptedPath = encryptedPath
        self.accessingUser = accessingUser
        self.fileMap = {}
        authenticated = self.check_self_permissions()
        if not authenticated:
            return
        self.load_files()
    
    def check_self_permissions(self):
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
        files = os.listdir(self.encryptedPath)
        perms = permissions()
        for file in files:
            if file in ['.perms', '.user', '.perms.sign', '.user.sign']:
                continue
            # get file permissions
            mode = perms.get_permission_mode(file)
            owner = perms.get_owner(file)
            
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
                self.fileMap[file] = File(file, decryptedFileName, True)
            else:
                self.fileMap[file] = File(file, None, False)
    
           
class File:
    def __init__(self, encryptedPath, unencryptedPath = None, access = False):
        self.encryptedPath = encryptedPath
        self.unencryptedPath = unencryptedPath
        self.access = access
    
    def load_content(self):
        if self.access:
            self.content = getFile(self.encryptedPath)
        else:
            self.content = 'CANNOT ACCESS!'
    
    def get_content(self):
        return self.content
    
    def get_unencrypted_path(self):
        return self.unencryptedPath