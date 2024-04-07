# provide functions for authenticating login requests
# creating users
# creating groups
# modifying users and adding them to groups

from fileEncryptor import storeFile, getFile
from argon2 import PasswordHasher
from clientConnection import clientConnection
from encryption import getRSAKey

class user:
    def __init__(self, username, passHash, groups):
        self.username = username
        self.passHash = passHash
        self.groups = groups
    
    def __repr__(self) -> str:
        return f'username: {self.username}\npassHash: {self.passHash}\ngroups: {self.groups}\n===\n'
    
    def get_username(self):
        return self.username
    
    def get_passHash(self):
        return self.passHash
    
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
		test_pass_hash = PasswordHasher().verify(acc_pass_hash, password)

		if test_pass_hash:
			clientConn = clientConnection(getRSAKey(pub_key_str), username)
			return (True, clientConn)
		else:
			return (False, None)

def create_user(username, password, groups):
    passHash = PasswordHasher().hash(password)
    return user(username, passHash, groups)

def init_auth():
    filename = '.user'
    ADMIN_USERNAME = "admin"
    ADMIN_PASS = "admin"
    ADMIN_GROUPS = ["admin"]
    
    admin_user = create_user(ADMIN_USERNAME, ADMIN_PASS, ADMIN_GROUPS)
    
    # if the file already exists, don't overwrite it
    if getFile(filename):
        return
    
    try:
        storeFile('', filename, '', False)
        modify_user(admin_user)
    except Exception as e:
        print(f'Error initializing file: {e}')
     
def getUsers() -> dict[str, user]:
    filename = '.user'
    usersFileContent = getFile(filename)
    
    users_dict = {}
    user_info = {}
    for line in usersFileContent.split('\n'):
        if not line:
            continue
        line = line.strip()
        if line == '===':
            if user_info:
                users_dict[user_info['username']] = user(user_info['username'], user_info['passHash'], user_info['groups'])
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
