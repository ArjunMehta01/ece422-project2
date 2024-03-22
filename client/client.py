import socket



def main():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 12345) # make this an envvar so we can change it on the actual server
    logged_in = False
    public_key = ''
    
    try:
        client_socket.connect(server_address)  
        
        while True:
            logged_in = login(socket)
            if logged_in:
                while True:
                    message = input("Enter your message:")
                    client_socket.sendall(message.encode())
                    print("Sending:", message)
                

                    # Receive data
                    response = client_socket.recv(1024).decode()
                    print("Received:", response)
                    
                    if message.lower()== "LOGOUT":
                        logged_in = False
                        break
            if message.lower() == 'exit':
                print("EXITING....")
                break
    except ConnectionRefusedError:
        print("[ERROR] Connection refused. Make sure the server is running.")
    except KeyboardInterrupt:
        print("[INFO] User interrupted. Exiting.")
    finally:
    # Clean up the connection
        client_socket.close()
    

def login(socket, public_key):
    print("LOGIN PLZ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    message = username + " " + password + " " + public_key
    socket.sendall(message.encode())
    
    response = client_socket.recv(1024).decode()
    print("Received:", response)
    
    if reponse.lower() == 'login failed':
        return False
    
    return True

def command_check(command):
    valid_commands = ['pwd', 'ls', 'cd', 'mkdir', 'touch', 'cat', 'echo', 'mv']
    return command in valid_commands


def process_command(socket, message):
    tokenized_command = message.split(" ")
    # logic
    if len(tokenized_command) < 1:
        print("invalid command")
        return
    
    if tokenized_command[0] == "pwd":
        if len(tokenized_command) != 1:
            print("pwd: too many arguments")
            return
        # forward info via socket
        return
    elif tokenized_command[0] == "ls":
        if len(tokenized_command) != 2:
            print("ls: too few/many arguments")
            return
        # forward info via socket
        return
    elif tokenized_command[0] == 'cd':
        if len(tokenized_command) != 2:
            print("cd: too few/many arguments")
            return
        # forward info via socket
        return        
    elif tokenized_command[0] == 'mkdir':
        if len(tokenized_command) != 2:
            print("mkdir: too few/many arguments")
            return
        # forward info via socket
        return     
    elif tokenized_command[0] == 'touch':
        if len(tokenized_command) != 2:
            print("touch: too few/many arguments")
            return
        # forward info via socket
        return
    elif tokenized_command[0] == 'cat':
        if len(tokenized_command) != 2:
            print("cat: too few/many arguments")
            return
        # forward info via socket
        return
    elif tokenized_command[0] == 'echo':
        if len(tokenized_command) != 2:
            print("echo: too few/many arguments")
            return
        # forward info via socket
        return
    elif tokenized_command[0] == 'mv':
        if len(tokenized_command) != 2:
            print("mv: too few/many arguments")
            return
        # forward info via socket
        return
    else:
        print("invalid command")
        return
        
        
if __name__ == "__main__" :
    main()