import socket

BUFFER = 1024
INIT= "!INIT"
AVAILABLE = "!AVAILABLE"
NOT_AVAILABLE = "!NOT_AVAILABLE"
REQUEST_STATE = "!REQUEST_STATE"
REQUEST_MOVE = "!REQUEST_MOVE"
REQUEST_TABLE = "!REQUEST_TABLE"
DISCONNECT = "!DISCONNECT"
FORMAT = "UTF-8"
X = "X"
O = "O"
E = "E"
EMPTY = None

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for i in range(0, len(board)):
        if board[i][0] is not EMPTY:
            j = 1
            while j < len(board[0]):
                if board[i][j] is not board[i][0]:
                    break
                j += 1
            if j == len(board[0]):
                return board[i][0]
    # Check columns
    for j in range(0, len(board[0])):
        if board[0][j] is not EMPTY:
            i = 1
            while i < len(board):
                if board[i][j] is not board[0][j]:
                    break
                i += 1
            if i == len(board):
                return board[0][j]
    # Assuming square board, check diagonal
    diagonal = 0
    anti_diagonal = 0
    for i in range(0, len(board)):
        if (board[i][i] is not EMPTY) and (board[i][i] is board[0][0]):
            diagonal += 1
        if (board[i][len(board) - i - 1] is not EMPTY) and (board[i][len(board) - i - 1] is board[0][len(board) - 1]):
            anti_diagonal += 1
    if diagonal == len(board):
        return board[0][0]
    if anti_diagonal == len(board):
        return board[0][len(board) - 1]
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for row in board:
        for row_element in row:
            if row_element is EMPTY:
                return False
    return True

def empty_entries(board):
    entries = []
    for i in range(0, len(board)):
        for j in range(0, len(board)):
            if board[i][j] is EMPTY:
                entries.append((i, j))
    return entries

address = "localhost"
clientport = 5001
serverport = 5000

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.bind((address, clientport))
clientsocket.listen(1)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
querysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

playersocket, playeraddr = clientsocket.accept()
print(f"[NEW CONNECTION] {playeraddr} connected")


while True:
    msg = playersocket.recv(BUFFER).decode(FORMAT)
    if msg:
        print(f"[CLIENT MESSAGE] {msg} sent by {playeraddr}")
        if msg == INIT:
            table = [[EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY]]
            serversocket.sendto(msg.encode(FORMAT), (address, serverport))
            msg, addr = serversocket.recvfrom(BUFFER)
            msg = msg.decode(FORMAT)
            print(f"[SERVER MESSAGE] {msg} sent by {addr}")
            playersocket.send(msg.encode(FORMAT))
        elif msg == REQUEST_STATE:
            if terminal(table):
                win = winner(table)
                if win == None:
                    win = E
                playersocket.send(win.encode(FORMAT))
            else:
                playersocket.send(str(table).encode(FORMAT))
                msg = playersocket.recv(BUFFER).decode(FORMAT)
                print(f"[CLIENT MESSAGE] {msg} sent by {playeraddr}")
                indices = tuple(map(int, msg.strip().split(",")))
                table[indices[0]][indices[1]] = X
                if not terminal(table):
                    serversocket.sendto(REQUEST_MOVE.encode(FORMAT), (address, serverport))
                    msg, addr = serversocket.recvfrom(BUFFER)
                    msg = msg.decode(FORMAT)
                    print(f"[SERVER MESSAGE] {msg} sent by {addr}")
                    empty_cells = empty_entries(table)
                    querysocket.sendto(str(len(empty_cells)).encode(FORMAT), (address, int(msg)))
                    msg, addr = querysocket.recvfrom(BUFFER)
                    msg = msg.decode(FORMAT)
                    print(f"[QUERY MESSAGE] {msg} sent by {addr}")
                    cell = empty_cells[int(msg)]
                    table[cell[0]][cell[1]] = O
        elif msg == REQUEST_TABLE:
            print(table)
            playersocket.send(str(table).encode(FORMAT))
        else:
            serversocket.sendto(DISCONNECT.encode(FORMAT), (address, serverport))
            break
        

