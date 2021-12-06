#!/home/muffin/.pyenv/shims/python
import numpy as np
import socket

from copy import deepcopy
from random import choice
from time import sleep, time


class Agent14:
    """Represents the agent for Group14."""

    HOST = "127.0.0.1"
    PORT = 1234
    colour_dict = {
        "None": 0,
        "R": 1,
        "B": -1,
    }
    last_move_made_by = "R"

    # time left (%) -> depth level map
    # 100% - 65% of time left --> 3 levels
    # 64% - 30% of time left --> 2 levels
    # 29% - 0% of time left --> 1 level
    TIME_LEFT = 300  # seconds
    thinking_time = 3

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

            self.board = np.zeros((self.board_size, self.board_size), dtype="int32")
            # self.board = [[0] * self.board_size for _ in range(self.board_size)]
            if self.colour == "R":
                self.make_move()
            self.last_move_made_by = message[2]

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
                self.board[action[0]][action[1]] = self.colour_dict[self.opp_colour()]
                self.make_move()
            self.last_move_made_by = message[3]

        self.TIME_LEFT -= int((time() - current_time))
        # Percentage = (time_left / 300) * 100
        self.thinking_time = self.get_minimax_depth_level(int(self.TIME_LEFT / 3))
        return False

    def make_move(self):
        """
        Gets all available moves from the current state of the board and randomly
        chooses the next move to make from the available pool.

        If it can swap, chooses to do so.
        """
        if self.colour == "B" and self.turn_count == 0:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
            self.turn_count += 1
            return

        # Could possibly filter out with NumPy and avoid recreating everything.
        # Filter and return the (x, y) indices of all elements that are equal to 0.
        choices_x, choices_y = np.where(self.board == 0)
        
        move = self.minimax_wrap(self.board)
        
        #move = choice(np.array((choices_x, choices_y)).T)
        # Needs to sleep for now as it replies too fast and the socket might skip the message
        sleep(1 * 10 ** -3)
        self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
        self.board[move[0]][move[1]] = self.colour_dict[self.colour]
        self.turn_count += 1
        self.last_move_made_by = self.colour

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

    def minimax_wrap(board)
        max_val = float("-inf")
        best_move = None
        prev_colour = self.opp_colour()
        for x,y in board:
            if board[x][y] == 0:
                value = minimax(board, self.thinking_time, float("-inf"), float("inf"), True, prev_colour)
                if value > max_value:
                    max_value = value
                    best_move = (x,y)
        return best_move
                
    def minimax(
        self, board, depth, alpha, beta, maximising, last_move
    ):
        """
        Applies that minimax algorithm with alpha-beta pruning to the current state of,
        the board and returns the static value of the move.

        NOTE: This method does not take weights into account. All moves are considered
            equal.

        :param board: The current state of the board.
        :param depth: How deep to traverse the tree, or how many moves to look ahead.
        :param alpha: The alpha (max) value for alpha-beta pruning.
        :param beta: The beta (min) value for alpha-beta pruning.
        :param maximising: True to represent maximising players turn, or False to
            represent the minimising players turn.
        :param available_choices: A list with all the available moves, represented
            as a list of (x: int, y: int) tuples.
        :param last_move: The color of the player who has made the last move. This is
            used for the heuristic.
        :returns: The static value of the best move to make based on the current state
            of the board.
        """
        
        if depth == 0:
            return self.get_position_value()

        next_move = "B" if last_move == "R" else "R"
        #INDEX = 0

        if maximising:
            current_max = float("-inf")
            for x, y in board:
                if self.board[x][y] == 0:
                    board = deepcopy(self.board)
                    board[x][y] = self.colour_dict[next_move] #colour_dict is the player making the next move
                    
                    current_evaluation = self.minimax(
                        board,
                        depth - 1,
                        alpha,
                        beta,
                        False,
                        next_move
                    )
                    #board[x][y] = 0
                    current_max = max(current_max, current_evaluation)
                    alpha = max(alpha, current_evaluation)
                    if beta <= alpha:
                        break
            return current_max
        else:
            current_min = float("inf")
            for x, y in self.board:
                if self.board[x][y] == 0:
                    board = deepcopy(self.board)
                    board[x][y] = self.colour_dict[next_move]
                    current_evaluation = self.minimax(
                        board,
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        next_move
                    )
                    #board[x][y] = 0
                    current_min = min(current_min, current_evaluation)
                    beta = min(beta, current_evaluation)
                    if beta <= alpha:
                        break
            return current_min

    def get_position_value(self):
        """
        Get the value of the current position based on the state of the board.
        This is basically the heuristic of the current position.

        :returns: The static value of the current position.
        """
        # Heuristic can be, if Red made last move (won) 1, else -1
        return self.colour_dict[self.last_move_made_by]

    def get_minimax_depth_level(self, perc):
        """
        Return the depth level to use in minimax based on the percentage of time used.

        :param perc: The percentage of time used.
        :returns: 3 for a percentage level [65, 100], 2 for [30, 64], 1 otherwise.
        """
        if perc >= 65:
            return 3
        elif perc >= 30 and perc < 65:
            return 2
        else:
            return 1


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
