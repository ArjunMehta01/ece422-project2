from fileEncryptor import storeFile, getFile, decryptFileName, decryptFilepath, make_directory as _make_directory, modifyFile, verify_folder_integrity, verify_file_integrity
from auth import getUsers
import os
import hashlib

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
            encFileName, mode, owner, type = line.split('][')
            self.permissions[encFileName] = {'mode': mode, 'owner': owner, 'type': type}
    
    def save_permissions(self):
        fileContent = ''
        for encFileName, data in self.permissions.items():
            fileContent += f'{encFileName}][{data["mode"]}][{data["owner"]}][{data["type"]}\n'
        
        storeFile('', '.perms', fileContent, False)
    
    def get_permission_mode(self, encFileName):
        if encFileName in self.permissions:
            return self.permissions[encFileName]['mode']
        return None
    
    def get_owner(self, encFileName):
        if encFileName in self.permissions:
            return self.permissions[encFileName]['owner']
        return None
    
    def get_file_type(self, encFileName):
        if encFileName in self.permissions:
            return self.permissions[encFileName]['type']
        return None
    
    def add_new_permission(self, encFileName, mode, owner, type):
        self.permissions[encFileName] = {'mode': mode, 'owner': owner, 'type': type}
        self.save_permissions()
    
    def set_permission_mode(self, encFileName, mode):
        if encFileName not in self.permissions:
            return None
        self.permissions[encFileName]['mode'] = mode
        self.save_permissions()
    
    def remove_file(self, encFileName):
        if encFileName in self.permissions:
            del self.permissions[encFileName]
            self.save_permissions()

class folder:
    def __init__(self, encryptedPath, accessingUser):
        self.encryptedPath = encryptedPath
        # get path tokens from by seperating the path by the os's file seperator
        pathTokens = encryptedPath.split(os.sep)
        # decrypt all path tokens and rejoin with the os's file seperator
        self.unencryptedPath = os.sep.join([decryptFileName(token) for token in pathTokens])
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
        self.fileMap = {}
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
        """Returns a list of the names of the files and folders in this folder that the user has access to"""
        files = []
        for file in self.fileMap.values():
            fullPath = file.get_unencrypted_name()
            if not fullPath:
                fullPath = file.get_encrypted_path()
                fullPath = os.path.basename(fullPath)
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
        
        # TODO: MAKE SURE THE FILE IS NOT A FOLDER
        if permissions().get_file_type(encFileName) == 'FOLDER':
            return 'CANT GET CONTENT OF A FOLDER'
        
        file = self.fileMap[encFileName]
        return file.get_content()
    
    def make_directory(self, dirname, permission_mode='USER'):
        """Given an unencrypted directory name, creates a new directory in the current folder."""
        encDirName = _make_directory(self.encryptedPath, dirname)
        perms = permissions()
        perms.add_new_permission(os.path.join(self.encryptedPath, encDirName), permission_mode, self.accessingUser, 'FOLDER')
        self.load_files()
        
    def make_empty_file(self, name):
        """Given an unencrypted file name and content, creates a new file in the current folder."""
        encFileName = storeFile(self.encryptedPath, name, '', True)
        perms = permissions()
        perms.add_new_permission(os.path.join(self.encryptedPath, encFileName), 'USER', self.accessingUser, 'FILE')
        self.load_files()
    
    def make_file(self, name, content, permission = 'USER'):
        """Given an unencrypted file name and content, creates a new file in the current folder."""
        encFileName = storeFile(self.encryptedPath, name, content, True)
        perms = permissions()
        perms.add_new_permission(os.path.join(self.encryptedPath, encFileName), permission, self.accessingUser, 'FILE')
        self.load_files()

    def modify_file_content(self, name, content):
        """Given the unencrypted name of a file and new content, changes the content of the file."""
        # need to get the encrypted name of the file by iterating over all the files in the folder
        encFileName = None
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == name:
                encFileName = file.get_encrypted_path()
                break
        else:
            return 'FILE NOT FOUND'
        
        # TODO: MAKE SURE THE FILE IS NOT A FOLDER
        if permissions().get_file_type(encFileName) == 'FOLDER':
            return 'CANT MODIFY CONTENT OF A FOLDER'
        
        modifyFile(encFileName, content)
        self.load_files()
    
    def rename_file(self, oldName, newName):
        """Given the unencrypted names of the old and new files, renames the old file to the new file."""
        # gotta find the encrypted names of the files
        oldEncName = None
        
        # TODO: MAKE SURE THE FILE IS NOT A FOLDER
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == oldName:
                oldEncName = file.get_encrypted_path()
                oldPermission = permissions().get_permission_mode(oldEncName)
                break

        if not oldEncName:
            return 'FILE NOT FOUND'
        
        if permissions().get_file_type(oldEncName) == 'FOLDER':
            return 'CANT RENAME A FOLDER'
        
        # load content of old file
        content = self.fileMap[oldEncName].get_content()
        
        # store content in new file
        self.make_file(newName, content, oldPermission)
        
        # delete old file
        FILESYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
        signFileName = oldEncName + '.sign'
        
        os.remove(os.path.join(FILESYSTEM_PATH, oldEncName))
        os.remove(os.path.join(FILESYSTEM_PATH, signFileName))
        
        permissions().remove_file(oldEncName)
        
        self.load_files()
        
    def get_enc_file_name(self, filename):
        """Given the unencrypted name of a file, returns the encrypted path of the file."""
        # look in the file map for the file
        for file in self.fileMap.values():
            if file.get_unencrypted_name() == filename:
                return file.get_encrypted_path()
        return None
    
    def modify_file_permissions(self, filename, newMode):
        """Given the unencrypted name of a file and a new permission mode, changes the permission mode of the file."""
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
        """Returns just the unencrypted name of the file, without the path"""
        return self.unencryptedFileName
    
    def get_encrypted_path(self):
        """Returns the whole encrypted path of the file from the root of the filesystem."""
        return self.encryptedPath
    
def verify_integrity(user):
    # given the user's name
    # find all filepaths from permissions where user is the owner
    # for eeach file, read it, hash it, compare to the signature which is in the .sign file right beside it
    
    perms = permissions()
    integrity_failures = []
    for encFileName, data in perms.permissions.items():
        if data['owner'] == user:
            # read the file
            if data['type'] == 'FOLDER':
                # try to get the content of the associated .sign file
                result = verify_folder_integrity(encFileName)
                if not result:
                    integrity_failures.append(decryptFilepath(encFileName))
            else: # data type is file
                result = verify_file_integrity(encFileName)
                if not result:
                    integrity_failures.append(decryptFilepath(encFileName))
    
    return integrity_failures