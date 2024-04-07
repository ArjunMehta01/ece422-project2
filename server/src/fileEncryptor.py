# provides methods to store and retrieve encrypted files from encrypted paths
from cryptography.fernet import Fernet
import os
import hashlib

FILE_SYSTEM_PATH = os.getenv('FILESYSTEM_PATH')

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

FERNET_KEY = load_or_create_key()

def storeFile(encFilepath: str, filename: str, content: str, encryptFileName = True):
    """Given an encrypted filepath and an unencrypted filename, stores the content of the file in the encrypted filepath."""
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
        os.makedirs(os.path.dirname(newFileFullPath), exist_ok=True)
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
    fernet = Fernet(FERNET_KEY)
    hasher = hashlib.sha256()
    
    # if file not found return None
    if not os.path.isfile(FILE_SYSTEM_PATH + filename):
        return None
    
    with open(FILE_SYSTEM_PATH + filename, 'rb') as file:
        content = file.read()
    with open (FILE_SYSTEM_PATH + signatureFileName, 'rb') as file:
        signature = file.read()
        
    # get the bytes signature
    # get the bytes content
    
    # decrypt the content -> that gets us the utdf8 encoded content
    # decrypt the signature -> that gets us the hash of the encoded content
    
    # hash the utf 8 encoded content
    # compare the hash to the decrypted signature
    
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
    fernet = Fernet(FERNET_KEY)
    return fernet.encrypt(text.encode()).decode()
    
    