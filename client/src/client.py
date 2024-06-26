import socket
from encryption import rsaSocket, load_server_pub_key
import dotenv
from pathlib import Path
import os

dotenv_path = Path('/home/ubuntu/ECE422_PROJ2/master/ece422-project2-master/client/.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

def main():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logged_in = False
    
    # get ip and port from .env file
    ip = os.getenv('SERVER_IP')
    port = int(os.getenv('SERVER_PORT'))
    
    try:
        server_socket = rsaSocket(ip, port)
        
        while True:
            logged_in = login(server_socket, server_socket.get_pub_key_string())
            if logged_in:
                while True:
                    message = input("Enter your message:")
                    
                    if message.lower()== "logout":
                        logged_in = False
                        server_socket.send(message.lower())
                        break
                    
                    process_command(server_socket, message)
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
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    message = username + "][" + password + "][" + public_key
    socket.send(message)
    
    response = socket.recv()
    print("Received:", response)
    
    if response.lower() == 'login failed' or response.lower() == 'invalid pubkey':
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
            
            result = socket.recv()
            print(result)
            
            return True
    elif tokenized_command[0] == "ls":
        if len(tokenized_command) != 1:
            print("ls: too few/many arguments")
            return False
        else:
            socket.send(message)
            
            result = socket.recv()
            print(result)
            
            return True
    elif tokenized_command[0] == 'cd':
        if len(tokenized_command) != 2:
            print("cd: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True  
    elif tokenized_command[0] == 'mkdir':
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

            result = socket.recv()
            print(result)

            return True  
          
    elif tokenized_command[0] == 'echo':
        if len(tokenized_command) != 3:
            print("echo: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
  
    elif tokenized_command[0] == 'mv':
        if len(tokenized_command) != 3:
            print("mv: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True  
    
    elif tokenized_command[0] == 'chmod':
        if len(tokenized_command) != 3:
            print("chmod: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
    
    elif tokenized_command[0] == 'create_user':
        if len(tokenized_command) != 4:
            print("create_user: too few/many arguments")
            return False
        else:
            socket.send(message)
            return True
    else:
        print("invalid command")
        return False
      
        
if __name__ == "__main__" :
    main()