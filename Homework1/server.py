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


# Function to find the (i, j) positions that are empty in the table
def empty_entries(board):
    entries = ""
    for i in range(0, len(board)):
        for j in range(0, len(board)):
            if board[i][j] is EMPTY:
                entries = entries + "(" + str(i) + "," + str(j) + "), "
    return (entries[:len(entries) - 2])


# Connection variables
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
        # If msg is not empty

        print(f"[CLIENT MESSAGE] {msg} sent by {playeraddr}")

        # Handle the different message types
        if msg == INIT:
            table = [[EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY]]

            serversocket.sendto(msg.encode(FORMAT), (address, serverport))
            msg, addr = serversocket.recvfrom(BUFFER)
            msg = msg.decode(FORMAT)
            print(f"[SERVER MESSAGE] {msg} sent by {addr}")
            # send message back to client
            playersocket.send(msg.encode(FORMAT))
        elif msg == REQUEST_STATE:
            # Check if table is in terminal state i.e the game has ended
            if terminal(table):
                win = winner(table)
                if win == None:
                    win = E
                playersocket.send(win.encode(FORMAT))
            else:
                # If the game is not in terminal state send the table back to the client
                playersocket.send(str(table).encode(FORMAT))
                msg = playersocket.recv(BUFFER).decode(FORMAT)

                # Apply the client move to the table
                print(f"[CLIENT MESSAGE] {msg} sent by {playeraddr}")
                indices = tuple(map(int, msg.strip().split(",")))
                table[indices[0]][indices[1]] = X

                # If the game is not in terminal state ask the gato_server for a play
                if not terminal(table):
                    # Request move to the gato_server
                    serversocket.sendto(REQUEST_MOVE.encode(FORMAT), (address, serverport))
                    # Msg contains the port on which the gato_server will open a UDP connection to
                    # send the move
                    msg, addr = serversocket.recvfrom(BUFFER)
                    msg = msg.decode(FORMAT)
                    print(f"[SERVER MESSAGE] {msg} sent by {addr}")
                    # empty_cells will contain the (i, j) positions in the table that are empty
                    empty_cells = empty_entries(table)
                    # Send the length of the array containing the empty entries of the table to
                    # the query port of the gato_server
                    querysocket.sendto(empty_cells.encode(FORMAT), (address, int(msg)))
                    # The gato_server will return an index asociated with a (i, j) position in the
                    # empty_cells array
                    msg, addr = querysocket.recvfrom(BUFFER)
                    msg = msg.decode(FORMAT)
                    # QUERY MESSAGE identifies the messages sent by the randomly open port in the gato_server
                    print(f"[QUERY MESSAGE] {msg} sent by {addr}")
                    # Apply the play empty_cells[msg] on the table where msg is the index sent by gato_server
                    cell = (msg[1], msg[3])
                    table[int(cell[0])][int(cell[1])] = O
        elif msg == REQUEST_TABLE:
            playersocket.send(str(table).encode(FORMAT))
        else:
            serversocket.sendto(DISCONNECT.encode(FORMAT), (address, serverport))
            break
        

