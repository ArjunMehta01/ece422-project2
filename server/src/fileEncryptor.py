# provides methods to store and retrieve encrypted files from encrypted paths
from cryptography.fernet import Fernet
import os
import hashlib

FILE_SYSTEM_PATH = '../filesystem/'

def load_or_create_key():
    """
    Tries to load a Fernet key from a binary file. If the file does not exist,
    generates a new key, writes it to the file with read-only permissions for only the owner,
    and then loads the key.
    """
    # Try to load the key from the file
    filepath = '../.secrets/FERNET_KEY'
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

FERNET_KEY = load_or_create_key()


def storeFile(filename: str, content: str):
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    pathTokens = filename.split('\\')
    
    encPathTokens = [fernet.encrypt(token.encode()).decode() for token in pathTokens]
    
    encPath = FILE_SYSTEM_PATH + '\\'.join(encPathTokens)
    encSignPath = encPath + '.sign'
    encContent = fernet.encrypt(content.encode())
    
    hasher.update(content.encode())
    hashedContent = hasher.digest()
    signature = fernet.encrypt(hashedContent)
    
    try:
        with open(encPath, 'wb') as file:
            file.write(encContent)
        with open(encSignPath, 'wb') as file:
            file.write(signature)
    except:
        print('Error writing file')

# assumes the file exists and filename is pre encrypted
def getFile(filename):
    signatureFileName = filename + '.sign'
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    with open(FILE_SYSTEM_PATH + filename, 'rb') as file:
        content = file.read()
    with open (FILE_SYSTEM_PATH + signatureFileName, 'rb') as file:
        signature = file.read()
    
    hasher.update(content)
    hashedContent = hasher.digest()
    if fernet.decrypt(signature) == hashedContent:
        return fernet.decrypt(content).decode()
    else:
        return 'Signature does not match'
    
    