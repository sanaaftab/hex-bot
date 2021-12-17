import socket

from copy import deepcopy

from Node import ExternalNodes, Node
from helper_functions import *
from dijkstra import *
from minimax import *

from time import time_ns
from random import choice, shuffle

class Agent14:
    """Represents the agent for Group14."""

    HOST = "127.0.0.1"
    PORT = 1234

    EXTERNAL_NODES = None
    TIME_BUDGET = 295 * 1000 * 1000 * 1000
    MINIMAX_TIMEOUT = 10 * 1000 * 1000 * 1000
    SWITCH_TO_DIJKSTRA = 15 * 1000 * 1000 * 1000

    STARTING_MOVES = [
        (5, 5),
        (3, 6),
        (4, 4),
        (4, 7),
        (6, 3),
        (6, 6),
        (7, 4),
    ]
    PREDETERMINED_MOVES = []
    MOVES_MADE = []

    def __init__(self, board_size=11):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.board = []
        self.colour = ""
        self.turn_count = 0

    def run(self):
        """Reads data until it receives an END message or the socket closes."""
        while True:
            data = self.s.recv(1024)
            if not data or self.interpret_data(data):
                break

    def interpret_data(self, data):
        """
        Checks the type of message and responds accordingly.

        :param data: The binary data string received from the game engine.
        :returns: True if the game ended, False otherwise.
        """
        message = data.decode("utf-8").strip().split("\n")[0].split(";")

        if message[0] == "START":
            if int(message[1]) <= 0:
                print(f"Invalid board size provided: {message[1]}")
                return True
            self.board_size = int(message[1])
            if message[2] not in ["R", "B"]:
                print(f"Invalid player colour provided: {message[2]}")
                return True
            self.colour = message[2]

            self.board = self.initialise_board()
            if self.colour == "R":
                self.make_move(self.board)

        elif message[0] == "END":
            return True

        elif message[0] == "CHANGE":
            if message[3] == "END":
                return True

            elif message[1] == "SWAP":
                self.colour = get_opposing_colour(self.colour)
                if message[3] == self.colour:
                    self.make_move(self.board)

            elif message[3] == self.colour:
                opp_move = [int(x) for x in message[1].split(",")]
                self.board[opp_move[0]][opp_move[1]].occupy(
                    get_opposing_colour(self.colour)
                )
                self.MOVES_MADE.append(opp_move)
                self.make_move(self.board, opp_move)

        return False

    def make_move(self, board, opp_move=None):
        """
        Gets all available moves from the current state of the board and randomly
        chooses the next move to make from the available pool.

        If it can swap, chooses to do so.

        :param board: The board to update.
        :param opp_move: The move made by the opponent. Currently is only used on
            the first turn as the Blue player, to determine if the player should
            swap or not.
        :returns: The updated board.
        """
        current_time = time_ns()
        if self.colour == "B" and self.turn_count == 0 and opp_move in self.STARTING_MOVES:
            self.TIME_BUDGET -= time_ns() - current_time
            self.turn_count += 1
            self.s.sendall(bytes("SWAP\n", "utf-8"))
            return

        if self.turn_count < 5:
            print("Predetermined move -- ", end="")
            # If no predetermined moves have been generated, then get a random starting
            # move.
            if self.PREDETERMINED_MOVES == []:
                possible_move = None
                while self.STARTING_MOVES and not possible_move:
                    possible_move = choice(self.STARTING_MOVES)
                    if is_position_available(possible_move, board):
                        # If the predetermined move is the center, get all 6 neighbours
                        # otherwise get the two bridges according to ./nodes.jpg
                        if possible_move == (5, 5):
                            neighbours = [(3, 6),(4, 4),(4, 7),(6, 3),(6, 6),(7, 4)]
                        elif possible_move in [(6,3), (4,7)]:
                            neighbours = [
                                (possible_move[0] + 1, possible_move[1] - 2),
                                (possible_move[0] - 1, possible_move[1] + 2),
                            ]
                        elif possible_move in [(4,4), (6,6)]:
                            neighbours = [
                                (possible_move[0] - 1, possible_move[1] - 1),
                                (possible_move[0] + 1, possible_move[1] + 1),
                            ]
                        elif possible_move in [(3,6), (7,4)]:
                            neighbours = [
                                (possible_move[0] - 2, possible_move[1] + 1),
                                (possible_move[0] + 2, possible_move[1] - 1),
                            ]
                        else:
                            raise Exception(f"Uncaught possible move returned {possible_move}")

                        # Append the neighbours into the predetermined moves
                        for position in neighbours:
                            self.PREDETERMINED_MOVES.append(position)

                        x, y = possible_move
                        self.STARTING_MOVES.remove(possible_move)
                    else:
                        self.STARTING_MOVES.remove(possible_move)
                        possible_move = None
                # If for some reason a move could not be made from the predetermined
                # set, choose a random free move
                if not possible_move:
                    x, y = choice(get_free_nodes(board)).coordinates
            else:
                possible_move = None
                while self.PREDETERMINED_MOVES and not possible_move:
                    possible_move = choice(self.PREDETERMINED_MOVES)
                    if is_position_available(possible_move, board):
                        x, y = possible_move
                        self.PREDETERMINED_MOVES.remove(possible_move)
                    else:
                        self.PREDETERMINED_MOVES.remove(possible_move)
                        possible_move = None
                # If for some reason a move could not be made from the predetermined
                # set, choose a random free move
                if not possible_move:
                    x, y = choice(get_free_nodes(board)).coordinates
        elif self.turn_count < 20:
            if self.colour == "R":
                self.MOVES_MADE.pop()
                # Bridge above
                if is_position_available((opp_move[0] - 2, opp_move[1] + 1), board):
                    x, y = (opp_move[0] - 2, opp_move[1] + 1)
                # Bridge below
                elif is_position_available((opp_move[0] + 2, opp_move[1] - 1), board):
                    x, y = (opp_move[0] + 2, opp_move[1] - 1)
                elif self.MOVES_MADE:
                    while self.MOVES_MADE:
                        move = self.MOVES_MADE.pop()
                        # Bridge above
                        if is_position_available((move[0] - 2, move[1] + 1), board):
                            x, y = (move[0] - 2, move[1] + 1)
                            break
                        # Bridge below
                        elif is_position_available((move[0] + 2, move[1] - 1), board):
                            x, y = (move[0] + 2, move[1] - 1)
                            break
                else:
                    path = dijkstra(board, self.EXTERNAL_NODES.external_up, self.EXTERNAL_NODES.external_down)
                    path = [node for node in path if not is_coordinate_external(node, len(board)) and not node.colour]
                    x, y = choice(path).coordinates
            else:
                self.MOVES_MADE.pop()
                # Bridge above
                if is_position_available((opp_move[0] + 1, opp_move[1] - 2), board):
                    x, y = (opp_move[0] + 1, opp_move[1] - 2)
                # Bridge below
                elif is_position_available((opp_move[0] - 1, opp_move[1] + 2), board):
                    x, y = (opp_move[0] - 1, opp_move[1] + 2)
                elif self.MOVES_MADE:
                    while self.MOVES_MADE:
                        move = self.MOVES_MADE.pop()
                        # Bridge above
                        if is_position_available((move[0] + 1, move[1] - 2), board):
                            x, y = (move[0] + 1, move[1] - 2)
                            break
                        # Bridge below
                        elif is_position_available((move[0] - 1, move[1] + 2), board):
                            x, y = (move[0] - 1, move[1] + 2)
                            break
                else:
                    path = dijkstra(board, self.EXTERNAL_NODES.external_left, self.EXTERNAL_NODES.external_right)
                    path = [node for node in path if not is_coordinate_external(node, len(board)) and not node.colour]
                    x, y = choice(path).coordinates
        # -~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-
        # | TODO: Implement bridge connection |
        # -~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-
        else:
            # Minimax
            if self.TIME_BUDGET > self.SWITCH_TO_DIJKSTRA:
                print("Minimax move -- ", end="")
                move = self.minimax_wrap(board)
            else:
                print("Dijkstra move -- ", end="")
            # Dijkstra
                if self.colour == "R":
                    path = dijkstra(board, self.EXTERNAL_NODES.external_up, self.EXTERNAL_NODES.external_down)
                else:
                    path = dijkstra(board, self.EXTERNAL_NODES.external_left, self.EXTERNAL_NODES.external_right)
                
                if not path:
                    raise Exception("No path provided")
                path = [node for node in path if not is_coordinate_external(node, len(board)) and not node.colour]
                move = choice(path)

            x, y = move.coordinates

        self.board[x][y].occupy(self.colour)
        print(f"{x}, {y} -- with time left: {int(self.TIME_BUDGET // (1000 * 1000 * 1000))}")

        self.TIME_BUDGET -= time_ns() - current_time
        self.turn_count += 1
        self.s.sendall(bytes(f"{x},{y}\n", "utf-8"))

    def minimax_wrap(self, board):
        val = float("-inf") if self.colour == "R" else float("inf")
        best_move = None
        current_time = time_ns()
        free_nodes = get_free_nodes(board)
        shuffle(free_nodes)
        for node in free_nodes:
            x, y = node.coordinates
            new_board = deepcopy(board)
            new_board[x][y].occupy(self.colour)
            minimax_value = minimax(
                new_board,
                1,
                float("-inf"),
                float("inf"),
                self.colour == "B",
                self.EXTERNAL_NODES,
            )
            if self.colour == "R":
                if minimax_value > val:
                    val = minimax_value
                    best_move = node
            elif self.colour == "B":
                if minimax_value < val:
                    val = minimax_value
                    best_move = node
            # # Time cap minimax
            if self.MINIMAX_TIMEOUT < time_ns() - current_time:
                return best_move
        return best_move

    def initialise_board(self):
        """
        Create a `board_size`x`board_size` list to represent the hex board.
        Also creates the external nodes.

        :returns: A 2-D list of `board_size`x`board_size` dimensions.
        """
        node_id = 0
        board = []
        for x in range(self.board_size):
            board.append([])
            for y in range(self.board_size):
                board[x].append(
                    Node(
                        id=node_id,
                        coordinates=(x, y),
                        board_size=self.board_size,
                        value=(
                            self.board_size
                            - distance_between_points(
                                (self.board_size // 2, self.board_size // 2),
                                (x, y),
                            )
                        ),
                    )
                )
                node_id += 1
        # Create the external nodes
        self.EXTERNAL_NODES = ExternalNodes(self.board_size)

        return board


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
