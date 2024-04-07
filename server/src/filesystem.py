# store and get files
# should manage permissions for files
from argon2 import PasswordHasher


class file:
    def __init__(self, name, content, owner, groups, users):
        self.name = name
        self.content = content
        self.owner = owner
        self.groups = groups
        self.users = users
    
    def get_name(self):
        return self.name
    
    def get_content(self):
        return self.content
    
    def get_owner(self):
        return self.owner
    
    def get_group(self):
        return self.group
    
    def get_permissions(self):
        return self.users

    def add_user(self, user):
        self.users.append(user)
        
    def remove_user(self, user):
        self.users.remove(user)
    
    def add_group(self, group):
        self.groups.append(group)
    
    def remove_group(self, group):
        self.groups.remove(group)

class folder:
	pass


def init(username, password, salt, groups):
    filename = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\server\\filesystem\\.user'
    pass_hash = PasswordHasher.hash(password, salt)
    
    
    
    try:
        with open(filename, 'w') as file:
            file.write('===\n')
            file.write(f'username: {username}\npassword: {pass_hash}\nsalt: {salt}\n')
            file.write(salt)
            file.write(f'groups: [{", ".join(groups)}]\n')
        print(f'File "{filename}" created successfully.')
    except Exception as e:
    	print(f'Error creating file: {e}')
     
def getUsers():
    filename = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\server\\filesystem\\.user'
    users_dict = {}
    try:
        with open(filename, 'r') as file:
            user_info = {}
            for line in file:
                line = line.strip()
                if line == '===':
                    if user_info:
                        users_dict[user_info['username']] = user_info
                        user_info = {}
                else:
                    key, value = line.split(': ')
                    if key == 'groups':
                        user_info[key] = value[1:-1].split(',')
                    else:
                        user_info[key] = value
            if user_info:
                users_dict[user_info['username']] = user_info
    except Exception as e:
        print(f'Error reading file: {e}')
    return users_dict

# def modify(username, new_info):
#     filename = '.user'
#     try:
#         with open(filename, 'r') as file:
#             lines = file.readlines()

#         with open(filename, 'w') as file:
#             found_user = False
#             for line in lines:
#                 if line.strip().startswith('username:'):
#                     if line.strip().split(': ')[1] == username:
#                         found_user = True
#                         for key, value in new_info.items():
#                             if key == 'groups':
#                                 file.write(f'{key}: {", ".join(value)}\n')
#                             else:
#                                 file.write(f'{key}: {value}\n')
#                         file.write('===\n')
#                     else:
#                         found_user = False
#                 elif line.strip() == '===' and found_user:
#                     continue
#                 else:
#                     file.write(line)

#         if found_user:
#             print(f'Information for user "{username}" updated successfully.')
#         else:
#             print(f'User "{username}" not found.')
#     except Exception as e:
#         print(f'Error modifying file: {e}')

# # Example usage:
# modify('admin', {'password': 'newpassword', 'groups': ['x', 'y', 'z']})


# print(getUsers())
def add_user(username, password, groups):
    filename = 'C:\\Users\\svirk\\Documents\\SehbazzPersonal\\ECE422\\ece422-project2\\server\\filesystem\\.user'
    try:
        with open(filename, 'a') as file:
            file.write('===\n')
            file.write(f'username: {username}\n')
            file.write(f'password: {password}\n')
            file.write(f'groups: [{", ".join(groups)}]\n')
            print(f'User "{username}" added successfully.')
    except Exception as e:
        print(f'Error adding user: {e}')

# Example usage:
# createUserFile("admin", "passwardo", ["a", "balls"])
# add_user('peepeepoopoo', 'balls', ['a', 'b', 'c'])

# print(getUsers())
