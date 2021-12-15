from copy import deepcopy
from random import randint
from dijkstra import *
from helper_functions import *

def minimax(board, depth, alpha, beta, maximising, external_nodes):
    """
    Applies that minimax algorithm with alpha-beta pruning to the current state of
    the board and returns the static value of the move.

    :param board: The game board.
    :param depth: How deep to traverse the tree, or how many moves to look ahead.
    :param alpha: The alpha (max) value for alpha-beta pruning.
    :param beta: The beta (min) value for alpha-beta pruning.
    :param maximising: True to represent maximising players turn, or False to
        represent the minimising players turn.
    :param external_nodes: TBD.

    :returns: The static value of the best move to make based on the current state
        of the board.
    """
    if depth == 0:
        return get_static_evaluation(board, external_nodes)

    legal_moves = get_free_nodes(board)
    if len(legal_moves) == 0:
        return 0

    if maximising:
        current_max = float("-inf")
        for node in legal_moves:
            x, y = node.coordinates
            new_board = deepcopy(board)
            new_board[x][y].occupy("R")
            current_evaluation = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                False,
                external_nodes,
            )
            current_max = max(current_max, current_evaluation)
            alpha = max(alpha, current_evaluation)
            if beta <= alpha:
                break
        return current_max
    else:
        current_min = float("inf")
        for node in legal_moves:
            x, y = node.coordinates
            new_board = deepcopy(board)
            new_board[x][y].occupy("B")
            current_evaluation = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                True,
                external_nodes,
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
    if perc >= 65:
        return 3
    elif perc >= 30:
        return 2
    else:
        return 1

def get_static_evaluation(board, external_nodes):
    # blue_nodes = get_free_occupied_nodes(board, "B")
    # red_nodes = get_free_occupied_nodes(board, "R")


    # board[0][0].occupy("R")
    # board[2][0].occupy("R")
    # board[3][0].occupy("R")
    # board[4][0].occupy("R")
    red_eval = dijkstra(board, external_nodes.external_up, external_nodes.external_down)
    red_length = 0
    for node in red_eval:
        if not is_coordinate_external(node.coordinates, len(board)) and not node.colour:
            red_length += 1

    print("DIJKSTRA EVAL FOR RED", [node.coordinates for node in red_eval])
    from sys import exit
    exit(0)

    blue_eval = dijkstra(board, external_nodes.external_left, external_nodes.external_right)
    blue_length = 0
    for node in blue_eval:
        if not is_coordinate_external(node.coordinates, len(board)) and not node.colour:
            blue_length += 1

    print("BLUE EVALUATIONL", blue_length)
    print("RED EVALUATIONL", red_length)
    # red_eval = len([node_coordinates for node_coordinates in red_eval if board[node_coordinates].is_free])
    return blue_length - red_length
