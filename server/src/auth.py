# provide functions for authenticating login requests
# creating users
# creating groups
# modifying users and adding them to groups

from fileEncryptor import storeFile, getFile
from argon2 import PasswordHasher
from encryption import getRSAKey

class user:
    def __init__(self, username, passHash, group):
        self.username = username
        self.passHash = passHash
        self.group = group
    
    def __repr__(self) -> str:
        return f'username: {self.username}\npassHash: {self.passHash}\ngroup: {self.group}\n===\n'
    
    def get_username(self):
        return self.username
    
    def get_passHash(self):
        return self.passHash
    
    def get_group(self):
        return self.group
    
    def set_group(self, group):
        self.group = group

def login(login_string):
	username, password, pub_key_str = login_string.split('][')

	user_dict = getUsers()
	if username not in user_dict:
		return (False, None, None)
	else:
		user = user_dict[username]
		acc_pass_hash = user.get_passHash()
		test_pass_hash = PasswordHasher().verify(acc_pass_hash, password)

		if test_pass_hash:
			return (True, getRSAKey(pub_key_str), username)
		else:
			return (False, None, None)

def create_user(username, password, groups):
    passHash = PasswordHasher().hash(password)
    new_user = user(username, passHash, groups)
    modify_user(new_user)
    return new_user

def init_auth():
    ADMIN_USERNAME = "admin"
    ADMIN_PASS = "admin"
    ADMIN_GROUP = "admin"
    
    create_user(ADMIN_USERNAME, ADMIN_PASS, ADMIN_GROUP)
     
def getUsers() -> dict[str, user]:
    filename = '.user'
    usersFileContent = getFile(filename)
    
    users_dict = {}
    user_info = {}
    if not usersFileContent:
        return users_dict
    for line in usersFileContent.split('\n'):
        if not line:
            continue
        line = line.strip()
        if line == '===':
            if user_info:
                users_dict[user_info['username']] = user(user_info['username'], user_info['passHash'], user_info['group'])
                user_info = {}
        else:
            key, value = line.split(': ')
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
