import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

server_socket.bind(('localhost', 12345)) # env var
server_socket.listen(5)

print("Server is listening on port 12345")

while True:
	connection, client_address = server_socket.accept()

	try:
		print("Connection from", client_address)

		# Receive the data in small chunks and retransmit it
		while True:
			data = connection.recv(1024)
			if data:
				print("Received:", data.decode())
				connection.sendall(data)
			else:
				print("No more data from:", client_address)
				break
			
	finally:
		# Clean up the connection
		connection.close()
