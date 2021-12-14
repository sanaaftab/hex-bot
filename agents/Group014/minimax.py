from copy import deepcopy
from dijkstra import *
from helper_functions import *
from random import choice

def minimax(board, depth, alpha, beta, maximising, last_move):
    """
    Applies that minimax algorithm with alpha-beta pruning to the current state of
    the board and returns the static value of the move.

    :param board: The game board.
    :param depth: How deep to traverse the tree, or how many moves to look ahead.
    :param alpha: The alpha (max) value for alpha-beta pruning.
    :param beta: The beta (min) value for alpha-beta pruning.
    :param maximising: True to represent maximising players turn, or False to
        represent the minimising players turn.
    :param last_move: The color of the player who has made the last move. This is
        used for the heuristic.

    :returns: The static value of the best move to make based on the current state
        of the board.
    """
    if len(get_free_nodes(board)) == 0:
        return 0

    if depth == 0:
        return get_static_evaluation(board)

    next_move = "B" if last_move == "R" else "R"
    if maximising:
        current_max = float("-inf")
        for row in board:
            for node in row:
                x, y = node.coordinates
                new_board = deepcopy(board)
                new_board[x][y].occupy(next_move)
                current_evaluation = minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    next_move,
                )
                current_max = max(current_max, current_evaluation)
                alpha = max(alpha, current_evaluation)
                if beta <= alpha:
                    break
        return current_max
    else:
        current_min = float("inf")
        for row in board:
            for node in row:
                x, y = node.coordinates
                new_board = deepcopy(board)
                new_board[x][y].occupy(next_move)
                current_evaluation = minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    next_move,
                )
                current_min = min(current_min, current_evaluation)
                beta = min(beta, current_evaluation)
                if beta <= alpha:
                    break
        return current_min


def get_minimax_depth_level(perc):
    """
    Return the depth level to use in minimax based on the percentage of time used.

    :param perc: The percentage of time used.
    :returns: 3 for a percentage level [65, 100], 2 for [30, 64], 1 otherwise.
    """
    if perc >= 50:
        return 2
    else:
        return 1


def get_static_evaluation(board):
    """
    Calculates and returns the heuristic (the difference between the length of the
    Dijkstra path of the blue player with the length of the Dijkstra path of the red
    player).

    The path for red is chosen at random based on the free or red occupied nodes on the
    top and bottom row, while blue uses the same logic for left and right.

    :param board: The current game board.
    :returns: The difference between the two paths.
    """
    last_node_index = len(board[0]) - 1

    src_red = []
    for node in board[0]:
        if node.colour == "R":
            src_red = [node]
            break
        if node.is_free():
            src_red.append(node)
    if len(src_red) == 0:
        return 0
    src_red = choice(src_red)

    dest_red = []
    # If the node directly downwards from the source is free, choose it.
    if board[last_node_index][src_red.coordinates[1]].is_free():
        dest_red.append(board[last_node_index][src_red.coordinates[1]])
    else:
        for node in board[last_node_index]:
            if node.colour == "R":
                dest_red = [node]
                break
            if node.is_free():
                dest_red.append(node)
    if len(dest_red) == 0:
        return 0
    dest_red = choice(dest_red)

    src_blue = []
    for row in board:
        if row[0].colour == "B":
            src_blue = [row[0]]
            break
        if row[0].is_free():
            src_blue.append(row[0])
    if len(src_blue) == 0:
        return 0
    src_blue = choice(src_blue)

    dest_blue = []
    # If the node directly across from the source is free, choose it.
    if board[src_blue.coordinates[0]][last_node_index].is_free():
        dest_blue.append(board[src_blue.coordinates[0]][last_node_index])
    else:
        for row in board:
            if row[last_node_index].colour == "B":
                dest_blue = [row[last_node_index]]
                break
            if row[last_node_index].is_free():
                dest_blue.append(row[last_node_index])
    if len(dest_blue) == 0:
        return 0
    dest_blue = choice(dest_blue)

    red_path = dijkstra(board, src_red, dest_red)
    blue_path = dijkstra(board, src_blue, dest_blue)
    return len(blue_path) - len(red_path)
