import rsa
import socket
from encryption import rsaSocket

SERVER_PUB_KEY = ""

def loadPubKey(path):
    with open(path, 'rb') as pub_key_file:  # Assuming the public key is stored in a file named 'public_key.pem'
        public_key_string = pub_key_file.read()
        public_key_string = public_key_string.replace(b'\\n', b'\n').decode('ascii')
        # pub_innit = rsa.PublicKey.load_pkcs1(public_key_string)
        return public_key_string

def main():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 12345) # make this an envvar so we can change it on the actual server
    logged_in = False
    
    try:
        client_socket.connect(server_address)  
        rsa_socket = rsaSocket(client_socket)
        rsa_socket.setPubKey(loadPubKey("../.secrets/public_key_server.pem"))
        
        while True:
            logged_in = login(rsa_socket, loadPubKey("../.secrets/public_key.pem"))
            if logged_in:
                while True:
                    message = input("Enter your message:")
                    rsa_socket.send(message)
                    print("Sending:", message)
                

                    # Receive data
                    response = rsa_socket.recv()
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
    socket.send(message)
    
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