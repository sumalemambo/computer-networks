import socket
import threading

class Server:
    def __init__(self, header=64, format="utf-8", init_msg = "!INIT", 
                    disconnect_msg="!DISCONECT"):
        # create an INET, STREAMing socket
        # socket.SOCK_STREAM specifies TCP protocol
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        self.serversocket.bind(("localhost", 5050))
        # number of bits that we will be receiving in each message after the header
        self.connectsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connectsocket.connect(("localhost", 5051))
        self.header = header
        # format of the msg
        self.format = format
        # server disconnect msg
        self.disconnect_msg = disconnect_msg
    
    def send_msg(self, sock, msg):
        msg = msg.encode(self.format)
        msg_length = len(msg)
        send_lenght = str(msg_length).encode(self.format)
        send_lenght += b' ' * (64 - len(send_lenght))
        sock.send(send_lenght)
        sock.send(msg)


    def request_play(self):
        pass

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")

        connected = True
        while connected:
            msg_length = conn.recv(self.header).decode(self.format)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.format)
                if msg == self.disconnect_msg:
                    connected = False
                print(f"[{addr}] {msg}")
                
        conn.close()
    
    def start(self):
        print("hola")
        # locks if there are more than 5 concurrent clients
        self.serversocket.listen(5)
        while True:
            (clientsocket, address) = self.serversocket.accept()
            thread = threading.Thread(target=self.handle_client, args=(clientsocket, address))
            thread.start()


a = Server()
a.start()