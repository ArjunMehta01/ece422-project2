# provide functions for authenticating login requests
# creating users
# creating groups
# modifying users and adding them to groups

from fileEncryptor import storeFile, getFile
from argon2 import PasswordHasher
from clientConnection import clientConnection
from encryption import getRSAKey
import random

class user:
    def __init__(self, username, password, groups):
        self.username = username
        self.salt = getRandomSalt()
        self.passHash = PasswordHasher().hash(password, salt=self.salt)
        self.groups = groups
    
    def __repr__(self) -> str:
        return f'===\nusername: {self.username}\npassHash: {self.passHash}\nsalt: {self.salt}\ngroups: {self.groups}\n'
    
    def get_username(self):
        return self.username
    
    def get_passHash(self):
        return self.passHash
    
    def get_salt(self):
        return self.salt
    
    def get_salt_str(self):
        return self.salt.decode()
    
    def get_groups(self):
        return self.groups
    
    def add_group(self, group):
        self.groups.append(group)

def login(login_string):
	username, password, pub_key_str = login_string.split('][')

	user_dict = getUsers()
	if username not in user_dict:
		return (False, None)
	else:
		user = user_dict[username]
		acc_pass_hash = user.get_passHash()
		salt = user.get_salt()
		test_pass_hash = PasswordHasher.hash(password, salt)

		if acc_pass_hash == test_pass_hash:
			clientConn = clientConnection(getRSAKey(pub_key_str), username)
			return (True, clientConn)
		else:
			return (False, None)

def init_auth():
    filename = '.user'
    ADMIN_USERNAME = "admin"
    ADMIN_PASS = "admin"
    ADMIN_GROUPS = ["admin"]
    
    admin_user = user(ADMIN_USERNAME, ADMIN_PASS, ADMIN_GROUPS)
    
    try:
        storeFile('', filename, '', False)
        print('balls')
        modify_user(admin_user)
    except Exception as e:
        print(f'Error initializing file: {e}')
     
def getUsers() -> dict[str, user]:
    filename = '.user'
    usersFileContent = getFile(filename)
    
    users_dict = {}
    user_info = {}
    for line in usersFileContent.split('\n'):
        line = line.strip()
        if line == '===':
            if user_info:
                users_dict[user_info['username']] = user(user_info['username'], user_info['passHash'], user_info['salt'], user_info['groups'])
                user_info = {}
        else:
            key, value = line.split(': ')
            if key == 'groups':
                user_info[key] = value[1:-1].split(', ')
            else:
                user_info[key] = value
    
    return users_dict

def modify_user(user: user):
    """Take the given user and modify its entry in the .user file."""
    filename = '.user'
    users_dict = getUsers()
    try:
        users_dict[user.get_username()] = user
        usersFileContent = '\n'.join([str(user) for user in users_dict.values()])
        storeFile('', filename, usersFileContent, False)
    except Exception as e:
        print(f'Error modifying user: {e}')
        
def getRandomSalt() -> bytes:
    ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    chars = [random.choice(ALPHABET) for _ in range(16)]
    return ''.join(chars).encode()