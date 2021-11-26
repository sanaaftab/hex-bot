#!/home/muffin/.pyenv/shims/python
import socket
from random import choice
from time import sleep
import numpy as np


class Agent14:
    """Represents the agent for Group14."""

    HOST = "127.0.0.1"
    PORT = 1234
    color_dict = {
        "None": 0,
        "R": 1,
        "B": -1,
    }

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

            self.board = np.zeros((self.board_size, self.board_size), dtype="int32")
            if self.colour == "R":
                self.make_move()

        elif message[0] == "END":
            return True

        elif message[0] == "CHANGE":
            if message[3] == "END":
                return True

            elif message[1] == "SWAP":
                self.colour = self.opp_colour()
                if message[3] == self.colour:
                    self.make_move()

            elif message[3] == self.colour:
                # If the last part of the message is this agents color
                # this means that the opposing agent made a move, hence
                # ... = self.opp_colour()
                action = [int(x) for x in message[1].split(",")]
                self.board[action[0]][action[1]] = self.color_dict[self.opp_colour()]
                self.make_move()

        return False

    def make_move(self):
        """
        Gets all available moves from the current state of the board and randomly
        chooses the next move to make from the available pool.

        If it can swap, chooses to do so 50% of the time.
        """
        if self.colour == "B" and self.turn_count == 0:
            if choice([0, 1]) == 1:
                self.s.sendall(bytes("SWAP\n", "utf-8"))
                self.turn_count += 1
                return

        # Could possibly filter out with NumPy and avoid recreating everything.
        # Filter and return the (x, y) indices of all elements that are equal to 0.
        choices = np.where(self.board == 0)
        move = choice(np.column_stack((choices[0], choices[1])))

        self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
        self.board[move[0]][move[1]] = self.color_dict[self.colour]
        self.turn_count += 1

    def opp_colour(self):
        """
        Returns the char representation of the colour opposite to the current one.

        :returns: 'R' for red, 'B' for blue, or 'None' otherwise.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"

    def minimax(self, current_position, depth, alpha, beta, max):
        """
        Applies that minimax algorithm with alpha-beta pruning to the current state of,
        the board and returns the static value of the move.

        NOTE: This method does not take weights into account. All moves are considered
            equal.

        :param current_position: The current position on the board.
        :param depth: How deep to traverse the tree, or how many moves to look ahead.
        :param alpha: The alpha (max) value for alpha-beta pruning.
        :param beta: The beta (min) value for alpha-beta pruning.
        :param max: True to represent maximising players turn, or False to represent
            the minimising players turn.
        :returns: The static value of the best move to make based on the current state
            of the current_position.
        """
        if depth == 0:
            return self.get_position_value()

        if max:
            current_max = float("-inf")
            for child in current_position:
                current_evaluation = self.minimax(child, depth - 1, alpha, beta, False)
                current_max = max(current_max, current_evaluation)
                alpha = max(alpha, current_evaluation)
                if beta <= alpha:
                    break
            return current_max
        else:
            current_min = float("inf")
            for child in current_position:
                current_evaluation = self.minimax(child, depth - 1, alpha, beta, True)
                current_min = max(current_min, current_evaluation)
                beta = max(beta, current_evaluation)
                if beta <= alpha:
                    break
            return current_min

    def get_position_value(position):
        """
        Get the value of the current position based on the state of the board.
        This is basically the heuristic of the current position.

        :param position: The position on the board being evaluated.
        :returns: The static value of the current position.
        """
        return 0


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
