import socket as skt

address = 'localhost'
serverPort = 5001
clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

clientSocket.connect((address, serverPort))

toSend = input('Mensaje: ')
clientSocket.send(toSend.encode())

response = clientSocket.recv(1024).decode()
print("respuesta del servidor", response)

clientSocket.close() 