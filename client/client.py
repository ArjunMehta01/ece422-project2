import socket

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('localhost', 12345) # make this an envvar so we can change it on the actual server
client_socket.connect(server_address)

try:
    # Send data
    message = "Hello, server!"
    print("Sending:", message)
    client_socket.sendall(message.encode())

    # Receive data
    data = client_socket.recv(1024)
    print("Received:", data.decode())

finally:
    # Clean up the connection
    client_socket.close()
