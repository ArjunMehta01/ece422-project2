import socket
from encryption import rsaSocket
from auth import login, init_auth, create_user
import dotenv
from pathlib import Path
import os
from clientConnection import clientConnection

dotenv_path = Path('/home/ubuntu/ECE422_PROJ2/master/ece422-project2-master/server/.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

def main():
	print(os.getenv('SECRETS_PATH'))
	print(os.getenv('FILESYSTEM_PATH'))
	server_socket = startServer('0.0.0.0', 12347)
	init_auth()

	while True:
		connection, client_address = server_socket.accept()
		try:
			print("Connection from", client_address)
			handleClient(connection) # if we have time for multiconnection we just need to run this function in a thread
   
		except Exception as e:
			print(e)	
		finally:
			# Clean up the connection
			connection.close()

def startServer(ip, port):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind((ip, port)) # env var
	server_socket.listen(5)

	print(f"Server is listening on port {port}")
	return server_socket

def handleClient(connection):
	rsaConnection = rsaSocket(connection)

	(authenticated, server_pub_key, username) = login(rsaConnection.recv())
	conn = clientConnection(server_pub_key, username)

	if conn.getPubKey() is not None:
		rsaConnection.setClientPubKey(conn.getPubKey())
	else:
		connection.sendall("INVALID PUBKEY") # unencrypted
		return

	if not authenticated:
		rsaConnection.sendall("LOGIN FAILED") # switch to rsa socket
		return
	
	bad_files = conn.verifyIntegrity()
	if bad_files:
		result_str = 'The following files may be corrupted: ' + ', '.join(bad_files)
	else:
		result_str = 'No corrupted files found'
 
	rsaConnection.send("LOGIN SUCCESS: " + result_str)
 
	while True:
		data = rsaConnection.recv()
		tokens = data.split(' ')
		cmd = tokens[0]
		if cmd == 'pwd':
			rsaConnection.send('~/' + conn.current_folder.unencryptedPath)
		elif cmd == 'ls':
			rsaConnection.send(str(conn.current_folder.list_files_in_folder()))
		elif cmd == 'cd':
			dir = tokens[1]

			if dir == '..':
				conn.stepOutOfDirectory()
				continue

			conn.stepIntoDirectory(dir)
			pass
		elif cmd == 'mkdir':
			conn.current_folder.make_directory(tokens[1])
		elif cmd == 'touch':
			conn.current_folder.make_empty_file(tokens[1])
		elif cmd == 'cat':
			filename = tokens[1]
			rsaConnection.send(conn.current_folder.get_file_content(filename))
		elif cmd == 'echo':
			filename = tokens[1]
			content = tokens[2]
			conn.current_folder.modify_file_content(filename, content)
		elif cmd == 'mv':
			conn.current_folder.rename_file(tokens[1], tokens[2])
		elif cmd == 'chmod':
			conn.current_folder.modify_file_permissions(tokens[1], tokens[2])
		elif cmd == 'create_user':
			username = tokens[1]
			password = tokens[2]
			group = tokens[3]
			create_user(username, password, group)
		elif cmd == 'logout':
			break
		
if __name__ == "__main__":
    main()