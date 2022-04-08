import socket
import threading

class Server():
    def __init__(self, BUFFER=1024, INIT="!INIT", AVAILABLE="!AVAILABLE",
                    NOT_AVAILABLE="!NOT_AVAILABLE", REQUEST="!REQUEST_MOVE",
                    FORMAT="UTF-8", SOURCE_PORT=5050, DEST_ADDRESS=("localhost", 5000)):
        # TCP server socket
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(("localhost", SOURCE_PORT))
        # UDP client socket
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_adress = DEST_ADDRESS
        # Fixed message length of size equals BUFFER
        self.buffer = BUFFER
        # Message format
        self.format = FORMAT
        # Message types
        self.init_msg = INIT
        self.available_msg = AVAILABLE

    def handle_server(self, msg):
        # Handling of connection to the gato server
        self.clientsocket.sendto(msg, self.dest_adress)
        msg, addr = self.clientsocket.recv(self.buffer)
        msg = msg.decode(self.format)
        print(f"[MESSAGE] New message: {msg} from {addr}")
        return msg


    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")

        connected = True
        while connected:
            msg, addr = conn.recv(self.buffer)
            # Check if msg exist
            if msg:
                msg = msg.decode(self.format)
                print(f"[MESSAGE] New message: {msg} from {addr}")
                if msg == self.init_msg:
                    # Send init msg to gato server
                    response = self.handle_server(msg.encode(self.format))
                    conn.send(response)
                    
        conn.close()


    def start(self):
        # Locks if 5 concurrent clients
        self.serversocket.listen(5)
        # Connect to UDP gato server
        self.clientsocket.connect(self.dest_adress)

        while True:
            (clientsocket, address) = self.serversocket.accept()
            thread = threading.Thread(target=self.handle_client, args=(clientsocket, address))
            thread.start()

BUFFER = 1024

connectsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = "!REQUEST_MOVE"
msg = str(msg)
msg = msg.encode("UTF-8")
connectsocket.sendto(msg, ("localhost", 5000))

msg, addr = connectsocket.recvfrom(1024)

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("mensaje del servidor", msg.decode())
msg = [(1,2), (3,4), (5,6)]
msg = ','.join([str(f) for f in msg])
print(msg)

