import socket

from time import time
from copy import deepcopy
from random import choice

from ExternalNodes import ExternalNodes
from Node import Node
from helper_functions import *
from dijkstra import *
from minimax import *


class Agent14:
    """Represents the agent for Group14."""

    HOST = "127.0.0.1"
    PORT = 1234

    TIME_LEFT = 300  # seconds
    thinking_time = 1
    EXTERNAL_NODES = None

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
        current_time = time()
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
                self.board[opp_move[0]][opp_move[1]].colour = get_opposing_colour(self.colour)
                self.board[opp_move[0]][opp_move[1]].value = float("-inf")
                self.board[opp_move[0]][opp_move[1]].occupy(get_opposing_colour(self.colour))
                self.make_move(self.board)

        self.TIME_LEFT -= int((time() - current_time))
        return False

    def make_move(self, board):
        """
        Gets all available moves from the current state of the board and randomly
        chooses the next move to make from the available pool.

        If it can swap, chooses to do so.

        :param board: The board to update.
        :returns: The updated board.
        """
        # for x in range(len(board)):
        #     for y in range(len(board[0])):
        #         print(board[x][y].value)

        if self.colour == "B" and self.turn_count == 0:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
            self.turn_count += 1
            return board

        move = self.minimax_wrap(board)
        x, y = move.coordinates
        # board = self.update_heatmap(board, move)
        move.occupy(self.colour)

        self.turn_count += 1
        self.s.sendall(bytes(f"{x},{y}\n", "utf-8"))

    def minimax_wrap(self, board):
        val = float("-inf") if self.colour == "R" else float("inf")
        best_move = None
        free_nodes = get_free_nodes(board)
        for node in free_nodes:
            x, y = node.coordinates
            new_board = deepcopy(board)
            new_board[x][y].occupy(self.colour)

            minimax_value = minimax(
                new_board,
                1,
                float("-inf"),
                float("inf"),
                self.colour == "R",
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
        return best_move

    def initialise_board(self):
        """
        Create a `board_size` x `board_size` matrix to represent the hex board.

        :returns: A 2-D array of `board_size` x `board_size` dimensions.
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
                        board_size = self.board_size,
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
        neighbours = self.EXTERNAL_NODES.external_up.neighbours[2]

        print("NEIGHBOUR COORDINATES", neighbours, board[neighbours[0]][neighbours[1]].neighbours)
        # print("COORDINATES", [node.neighbours for node in [self.EXTERNAL_NODES.external_up, self.EXTERNAL_NODES.external_down, self.EXTERNAL_NODES.external_left, self.EXTERNAL_NODES.external_right]])
        return board


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
