# provide functions for authenticating login requests
# creating users
# creating groups
# modifying users and adding them to groups

from filesystem import getUsers
from argon2 import PasswordHasher

class user:
	pass

def login(login_string):
	username, password, pub_key = login_string.split('][')

	user_dict = getUsers()
	if username not in user_dict:
		return (False, None)
	else:
		user = user_dict[username]
		acc_pass_hash = user.getPassHash()
		salt = user.getPassSalt()
		test_pass_hash = PasswordHasher.hash(password, salt)

		if acc_pass_hash == test_pass_hash:
			return (True, user)
		else:
			return (False, None)
