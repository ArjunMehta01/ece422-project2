import socket

MESSAGE_SIZE = 1024

def main():
	server_socket = startServer('localhost', 12345)

	while True:
		connection, client_address = server_socket.accept()

		try:
			print("Connection from", client_address)

			handleClient(connection, client_address) # if we have time for multiconnection we just need to run this function in a thread
				
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
	# Start with login

	# get rsa connection

	(authenticated, pubKey) = login(connection) # switch to rsa connection

	if pubKey:
		# set rsa socket pubkey
		pass
	else:
		connection.sendall("INVALID PUBKEY") # unencrypted
		return

	if not authenticated:
		message = "LOGIN FAILED"
		connection.sendall(message) # switch to rsa socket
		return
	
	# start accepting and processing commands
	while True:
		command = connection.recv(1024) # switch to rsa socket
		processCommand(command)

def login(connection):
	username, password, pubkey = connection.read().split(' ')
	

