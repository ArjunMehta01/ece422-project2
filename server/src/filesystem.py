# store and get files
# should manage permissions for files

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
