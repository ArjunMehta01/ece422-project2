import socket
from encryption import rsaSocket

SERVER_PUB_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDixmkplIjjGnD4v4ZDYbzlhsKw0ENNGajdBkySyYSMbLQ9eV9yKtpU4CZY9iOHJ6eA+FiZDb3fAyYSOth65A4LV5gcq/uyGnRddGDKpm9ZW76EDbp5IBBmMlKVzQYtNB/rs4v1tTMfrdW3sOtpz9th6RM9l1AR23Z6MkSQjchc71P/botpaUSFwP7nUl4yj+x812evJUPynQikIBrRNG4ooyb6IXY6odTCogn71UhBb678hhFnSLB5pfY6VDI+QdpzpYnzu5DriH0erkHdQSdYQh5yvVPLZlyGOk4vstisHc/w+WuV1DL7mozW5m9T8pH+RsjWf0dWW1VpnXULjD2wV2bWx2P0jhfquA2fzEQ6kO0gTv/ewf9Ec0nwcCAOhl/qMYRYIMvM1/bxxBn4k0NSWXTEsr3QSUfnNXFE18zxF0latavyUz1/sZP5rzKUHTjuMtBYVYPAs4RzplGL81fA3aNYeYPrGqKMck83AZV/ElpogPh139haJNtJXs9on3M= intelliwavetech\svirk@LAPTOP-HUS0S65J"

def main():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 12345) # make this an envvar so we can change it on the actual server
    logged_in = False
    
    try:
        original_client = client_socket.connect(server_address)  
        client_socket = rsaSocket(client_socket)
        client_socket.setPubKey(SERVER_PUB_KEY)
        
        while True:
            logged_in = login(socket)
            if logged_in:
                while True:
                    message = input("Enter your message:")
                    client_socket.send(message)
                    print("Sending:", message)
                

                    # Receive data
                    response = client_socket.recv()
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
        original_client.close()
    

def login(socket, public_key):
    print("LOGIN PLZ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    message = username + " " + password + " " + public_key
    socket.send(message.encode())
    
    response = socket.recv()
    print("Received:", response)
    
    if response.lower() == 'login failed':
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
        return False
    
    if tokenized_command[0] == "pwd":
        if len(tokenized_command) != 1:
            print("pwd: too many arguments")
            return False
        else:
            socket.send(message)
            return True
    elif tokenized_command[0] == "ls":
        if len(tokenized_command) != 1:
            print("ls: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
    elif tokenized_command[0] == 'cd':
        if len(tokenized_command) != 2:
            print("cd: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True  
    elif tokenized_command[0] == 'mkdir':
        print("mkdir: too few/many arguments")
        if len(tokenized_command) != 2:
            print("mkdir: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
    elif tokenized_command[0] == 'touch':
        if len(tokenized_command) != 2:
            print("touch: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True            
    elif tokenized_command[0] == 'cat':
        if len(tokenized_command) != 2:
            print("cat: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True  
          
    elif tokenized_command[0] == 'echo':
        if len(tokenized_command) != 2:
            print("echo: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
  
    elif tokenized_command[0] == 'mv':
        if len(tokenized_command) != 2:
            print("mv: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True  
    else:
        print("invalid command")
        return False
      
        
if __name__ == "__main__" :
    main()