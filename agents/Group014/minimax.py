from copy import deepcopy
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


def get_static_evaluation(board, external_nodes):
    red_eval = dijkstra(board, external_nodes.external_up, external_nodes.external_down)
    red_length = 0
    for node in red_eval:
        if not is_coordinate_external(node, len(board)) and not node.colour:
            red_length += 1

    blue_eval = dijkstra(
        board, external_nodes.external_left, external_nodes.external_right
    )
    blue_length = 0
    for node in blue_eval:
        if not is_coordinate_external(node, len(board)) and not node.colour:
            blue_length += 1

    return blue_length - red_length
