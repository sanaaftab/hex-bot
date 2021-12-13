from copy import deepcopy
from dijkstra import *
from helper_functions import *
import random
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
    if depth == 0:
        return get_static_evaluation(board)

    legal_moves = get_free_nodes(board)
    next_move = "B" if last_move == "R" else "R"
    if maximising:
        current_max = float("-inf")
        for node in legal_moves:
            x, y = node.coordinates
            board[x][y].occupy(next_move)
            current_evaluation = minimax(
                deepcopy(board),
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
        for node in legal_moves:
            x, y = node.coordinates
            board[x][y].occupy(next_move)
            current_evaluation = minimax(
                deepcopy(board),
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
    if perc >= 65:
        return 3
    elif perc >= 30:
        return 2
    else:
        return 1

def get_static_evaluation(board):

    best_val = 0
    best_node = None

    free_nodes = get_free_nodes(board)
    last_node_index = len(board[0]) - 1

    # for node in free_nodes:
    #     if node.value > best_val:
    #         best_val = node.value
    #         best_node = node

    # src_red = [node for node in board[0] if node.is_free]
    # dest_red = [node for node in board[last_node_index] if node.is_free]

    src_red = board[0][last_node_index]
    dest_red = board[last_node_index][0]

    src_blue = board[1][0]
    dest_blue = board[1][last_node_index]

    # src_blue = []
    # dest_blue = []
    # for x in board:
    #     if x[0].is_free:
    #         src_blue.append(x[0])
    #     if x[last_node_index].is_free:
    #         dest_blue.append(x[last_node_index])
    #
    # if len(src_red) == 0 or len(dest_red) == 0 or len(src_blue) == 0 or len(dest_blue) == 0:
    #     return 0

    #  DEBUG
    # # coordinates_r = [red_node.coordinates for red_node in dijkstra_result_red]
    # # print("red:", coordinates_r)
    # # coordinates_b = [blue_node.coordinates for blue_node in dijkstra_result_blue]
    # # print("blue:", coordinates_b)
    #
    # dijkstra_result = len(dijkstra_result_blue) - len(dijkstra_result_red)
    # print("final result:", dijkstra_result)

    # dijkstra_result_red = dijkstra(board, free_nodes, src_red, dest_red)
    # dijkstra_result_blue = dijkstra(board, free_nodes, src_blue, dest_blue)
    # dijkstra_result = len(dijkstra(free_nodes, choice(src_blue), choice(dest_blue))) - len(dijkstra(free_nodes, choice(src_red), choice(dest_red)))

    # coordinates = []
    # for x in range(len(board)):
    #     coordinates.append([])
    #     for y in range(len(board[0])):
    #         coordinates[x].append(distance_between_points((len(board) // 2, len(board[0]) // 2), (x,y)))
    #         # coordinates[x].append([0, 9 - distance_between_points((len(board) // 2, len(board[0]) // 2))])
    #         # elf.board[x].append([0, 9 - self.distance_between_points((self.board_size // 2, self.board_size // 2), (x, y))])
    #
    # red_count = 0
    # for i in range(len(board)):
    #     for j in range(len(board)):
    #         if board[i][j].colour == 'R':
    #             red_count += coordinates[i][j]
    return random.randint(1, 100)
