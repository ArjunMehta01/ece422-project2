import socket
from encryption import rsaSocket
from auth import login, init_auth
import dotenv
from pathlib import Path

dotenv_path = Path('../.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

def main():
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
		rsaConnection.setPubKey(conn.getPubKey())
	else:
		connection.sendall("INVALID PUBKEY") # unencrypted
		return

	if not authenticated:
		rsaConnection.sendall("LOGIN FAILED") # switch to rsa socket
		return
	
	# start accepting and processing commands
	while True:
		command = rsaConnection.recv() # switch to rsa socket
		print(command)
  
  
if __name__ == "__main__" :
    main()