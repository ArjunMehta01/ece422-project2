# provides methods to store and retrieve encrypted files from encrypted paths
from cryptography.fernet import Fernet
import os
import hashlib

def load_or_create_key():
    """
    Tries to load a Fernet key from a binary file. If the file does not exist,
    generates a new key, writes it to the file with read-only permissions for only the owner,
    and then loads the key.
    """
    # Try to load the key from the file
    filepath = os.getenv('SECRETS_PATH') + 'FERNET_KEY'
    try:
        with open(filepath, "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        # Generate a new key
        key = Fernet.generate_key()
        # Write the key to the file with read-only permissions for the owner
        with open(filepath, "wb") as key_file:
            key_file.write(key)
        # Set read-only permissions for the owner
        os.chmod(filepath, 0o400)  # Octal representation of file permissions (r--------)

    # Return the loaded or newly generated key
    return key



def storeFile(encFilepath: str, filename: str, content: str, encryptFileName = True):
    """Given an encrypted filepath and an unencrypted filename, stores the content of the file in the encrypted filepath."""
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    if encryptFileName:
        encFileName = fernet.encrypt(filename.encode()).decode()
    else:
        encFileName = filename
    
    signFileName = encFileName + '.sign'
    
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    # print(FILE_SYSTEM_PATH)
    newFileFullPath = os.path.join(FILE_SYSTEM_PATH, encFilepath, encFileName)
    newSignFullPath = os.path.join(FILE_SYSTEM_PATH, encFilepath, signFileName)

    # Take string content and encode it utf 8
    # encrypt that encoded content
    # write that to a file
    # hash that encoded content
    # encrypt that hash
    # write that to a file
    encodedContent = content.encode()
    encryptedContent = fernet.encrypt(encodedContent)

    hasher.update(encodedContent)
    hashedContent = hasher.digest()
    signature = fernet.encrypt(hashedContent)
    
    try:
        os.makedirs(os.path.dirname(newFileFullPath), exist_ok=True) #update to use make_directory
        with open(newFileFullPath, 'wb') as file:
            file.write(encryptedContent)
        with open(newSignFullPath, 'wb') as file:
            file.write(signature)
    except Exception as e:
        print(f'Error writing file: {e}')
        
    return encFileName

def modifyFile(encFilepath, content):
    """Given an encrypted filepath and the new content of the file, modifies the content of the file in the encrypted filepath."""
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    encFileName = os.path.basename(encFilepath)
    signFileName = encFileName + '.sign'
    newFileFullPath = os.path.join(FILE_SYSTEM_PATH, encFilepath)
    newSignFullPath = os.path.join(FILE_SYSTEM_PATH, os.path.dirname(encFilepath), signFileName)
    
    # Take string content and encode it utf 8
    # encrypt that encoded content
    # write that to a file
    # hash that encoded content
    # encrypt that hash
    # write that to a file
    encodedContent = content.encode()
    encryptedContent = fernet.encrypt(encodedContent)

    hasher.update(encodedContent)
    hashedContent = hasher.digest()
    signature = fernet.encrypt(hashedContent)
    
    try:
        with open(newFileFullPath, 'wb') as file:
            file.write(encryptedContent)
        with open(newSignFullPath, 'wb') as file:
            file.write(signature)
    except Exception as e:
        print(f'Error writing file: {e}')

def getFile(filename):
    """Given an encrypted filename, returns the decrypted content of the file."""
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    signatureFileName = filename + '.sign'
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    # if file not found return None
    if not os.path.isfile(FILE_SYSTEM_PATH + filename):
        return None
    
    with open(FILE_SYSTEM_PATH + filename, 'rb') as file:
        content = file.read()
    with open (FILE_SYSTEM_PATH + signatureFileName, 'rb') as file:
        signature = file.read()
    
    utf8Content = fernet.decrypt(content)
    signhash = fernet.decrypt(signature)
    
    hasher.update(utf8Content)
    hashedContent = hasher.digest()
    
    if hashedContent == signhash:
        return utf8Content.decode()
    else:
        return None
    
def encryptText(text):
    """Given a string, returns the encrypted version of the string."""
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    return fernet.encrypt(text.encode()).decode()
    
def decryptFileName(encFileName):
    """Given an encrypted filename, returns the decrypted version of the filename."""
    if encFileName == '':
        return ''
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    return fernet.decrypt(encFileName.encode()).decode()

def decryptFilepath(encFilepath):
    """Given an encrypted filepath, returns the decrypted version of the filepath."""
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    # split the path into tokens
    pathTokens = encFilepath.split(os.sep)
    # decrypt each token
    decPathTokens = [fernet.decrypt(token.encode()).decode() for token in pathTokens]
    # rejoin the tokens
    return os.sep.join(decPathTokens)

def make_directory(filepath, dirname):
    """Given an encrypted filepath and an unencrypted directory name, creates a new directory in the encrypted filepath."""
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    encDirName = fernet.encrypt(dirname.encode()).decode()
    newDirFullPath = os.path.join(FILE_SYSTEM_PATH, filepath, encDirName)
    try:
        os.makedirs(newDirFullPath, exist_ok=True)
    except Exception as e:
        print(f'Error creating directory: {e}')
    
    # store a .sign file at the directory path where the contents are the hash of the directory name
    hasher = hashlib.sha256()
    hasher.update(newDirFullPath.encode())
    
    signFileName = encDirName + '.sign'
    newSignFullPath = os.path.join(FILE_SYSTEM_PATH, filepath, signFileName)
    
    signature = fernet.encrypt(hasher.digest())
    try:
        with open(newSignFullPath, 'wb') as file:
            file.write(signature)
    except Exception as e:
        print(f'Error writing sign file: {e}')
    
    return encDirName

def verify_folder_integrity(encFolderPath):
    """Given the encrypted path to a folder, compare it's filepath to the hash stored in the .sign file."""
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    signFileName = encFolderPath + '.sign'
    signFilePath = os.path.join(FILE_SYSTEM_PATH, signFileName)
    
    encFullPath = os.path.join(FILE_SYSTEM_PATH, encFolderPath)
    
    hasher.update(encFullPath.encode())
    
    # if the sign file is not found, return False
    if not os.path.isfile(signFilePath):
        return False
    
    with open(signFilePath, 'rb') as file:
        signature = file.read()
    
    signhash = fernet.decrypt(signature)
    hashedContent = hasher.digest()
    
    if hashedContent == signhash:
        return True
    else:
        return False

def verify_file_integrity(encFilePath):
    """Given the encrypted path to a file, compare it's content to the hash stored in the .sign file."""
    FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')
    FERNET_KEY = load_or_create_key()
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    signFileName = encFilePath + '.sign'
    signFilePath = os.path.join(FILE_SYSTEM_PATH, signFileName)
    
    fullFilePath = os.path.join(FILE_SYSTEM_PATH, encFilePath)
    
    # if either the file or the sign file is not found, return False
    if not os.path.isfile(fullFilePath) or not os.path.isfile(signFilePath):
        return False
    
    with open(fullFilePath, 'rb') as file:
        content = file.read()
    with open(signFilePath, 'rb') as file:
        signature = file.read()
    
    try:
        utf8Content = fernet.decrypt(content)
        signhash = fernet.decrypt(signature)
    except Exception as e:
        return False
    
    hasher.update(utf8Content)
    hashedContent = hasher.digest()
    
    if hashedContent == signhash:
        return True
    else:
        return False