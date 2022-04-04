import socket as skt

address = 'localhost'

serverPort = 5000
serverSocket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)

clientPort = 5001
clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM) #skt.AF_INET indica la direccion ipv4 y skt.SOCK_STREAM para el tipo de conexion tcp
clientSocket.bind(('', clientPort))
clientSocket.listen(1)


print('Esperando mensaje del cliente')
playerSocket, playerAddr = clientSocket.accept()
msg = playerSocket.recv(1024).decode()
print('Mensaje del cliente', msg)


serverSocket.sendto(msg.encode(), (address, serverPort))

print("esperando mensaje del servidor")
msg, addr = serverSocket.recvfrom(1024)

print("mensaje del servidor", msg.decode())
playerSocket.send(msg)