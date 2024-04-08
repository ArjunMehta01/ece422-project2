import socket
from encryption import rsaSocket
from auth import login, init_auth
import dotenv
from pathlib import Path
import os

dotenv_path = Path('../.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

def main():
	print(os.getenv('SECRETS_PATH'))
	print(os.getenv('FILESYSTEM_PATH'))
	server_socket = startServer('localhost', 12345)
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

	(authenticated, conn) = login(rsaConnection.recv())

	if conn.getPubKey() is not None:
		rsaConnection.setClientPubKey(conn.getPubKey())
	else:
		connection.sendall("INVALID PUBKEY") # unencrypted
		return

	if not authenticated:
		rsaConnection.sendall("LOGIN FAILED") # switch to rsa socket
		return
	
	rsaConnection.send("LOGIN SUCCESS")