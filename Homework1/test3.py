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

a = [['X', 'O', 'O'], ['X', 'X', None], ['X', None, 'O']]
print(terminal(a))

[[None, 'X', 'X'],
 ['O', 'X', 'O'],
 1 ['X', None, 'O']]