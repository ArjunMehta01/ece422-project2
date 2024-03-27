import socket
from encryption import rsaSocket
from auth import login
import filesystem


MESSAGE_SIZE = 1024

def main():
	server_socket = startServer('localhost', 12345)
	filesystem.init('admin', 'currently_unhashed', [])

	while True:
		connection, client_address = server_socket.accept()

		try:
			print("Connection from", client_address)

			handleClient(connection, client_address) # if we have time for multiconnection we just need to run this function in a thread
   
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

	(authenticated, user) = login(rsaConnection.read())

	if user.get_pub_key() is not None:
		rsaConnection.setPubKey(user.get_pub_key())
	else:
		connection.sendall("INVALID PUBKEY") # unencrypted
		return

	if not authenticated:
		rsaConnection.sendall("LOGIN FAILED") # switch to rsa socket
		return
	
	# start accepting and processing commands
	while True:
		command = rsaConnection.recv() # switch to rsa socket
		
		rsaConnection.send(result)
  
  
if __name__ == "__main__" :
    main()