import socket

from time import time


class Agent14:
    """Represents the agent for Group14."""

    HOST = "127.0.0.1"
    PORT = 1234
    colour_dict = {
        "None": 0,
        "R": 1,
        "B": -1,
    }

    # time left (%) -> depth level map
    # 100% - 65% of time left --> 2 levels
    # 64% - 0% of time left --> 1 level
    TIME_LEFT = 300  # seconds
    thinking_time = 2

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

            # Create a n*n (value, weight) board
            self.board = []
            for x in range(self.board_size):
                self.board.append([])
                for y in range(self.board_size):
                    self.board[x].append([0, 9 - self.distance_between_points((self.board_size // 2, self.board_size // 2), (x, y))])
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
                opp_move = [int(x) for x in message[1].split(",")]
                self.board[opp_move[0]][opp_move[1]][0] = self.colour_dict[self.opp_colour()]
                self.board[opp_move[0]][opp_move[1]][1] = float("-inf")
                # Update the heatmap
                for move_x, move_y in self.neighbours(opp_move):
                    self.board[move_x][move_y][1] -= 2
                for move_x, move_y in self.bridges(opp_move):
                    self.board[move_x][move_y][1] -= 3
                self.make_move()

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

        move = self.minimax_wrap()
        self.board[move[0]][move[1]][1] = float("inf")
        # Update the heatmap
        for move_x, move_y in self.neighbours(move):
            self.board[move_x][move_y][1] += 4
        for move_x, move_y in self.bridges(move):
            self.board[move_x][move_y][1] += 5

        self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
        self.board[move[0]][move[1]][0] = self.colour_dict[self.colour]
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

    def minimax_wrap(self):
        max_val = float("-inf")
        best_move = None
        # prev_colour = self.opp_colour()
        # for x in range(self.board_size):
        #     for y in range(self.board_size):
        #         if self.is_position_valid_and_available((x, y), self.board_size) and self.board[x][y][0] == 0:
        #             value = self.minimax(self.thinking_time, float("-inf"), float("inf"), True, prev_colour, x, y)
        #             if value > max_val:
        #                 max_val = value
        #                 best_move = (x, y)
        for i in self.board:
            print()
            for j in i:
                print(j[1], ", ", end="")
        print()
        print("------------------------------------------")
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y][0] == 0:
                    value = self.board[x][y][1]
                    if value > max_val:
                        max_val = value
                        best_move = (x, y)
        return best_move

    def minimax(
        self, depth, alpha, beta, maximising, last_move, x_coor, y_coor
    ):
        """
        Applies that minimax algorithm with alpha-beta pruning to the current state of
        the board and returns the static value of the move.

        :param depth: How deep to traverse the tree, or how many moves to look ahead.
        :param alpha: The alpha (max) value for alpha-beta pruning.
        :param beta: The beta (min) value for alpha-beta pruning.
        :param maximising: True to represent maximising players turn, or False to
            represent the minimising players turn.
        :param last_move: The color of the player who has made the last move. This is
            used for the heuristic.
        :param x_coor: The x coordinate of the position currently under investigation.
        :param y_coor: The y coordinate of the position currently under investigation.

        :returns: The static value of the best move to make based on the current state
            of the board.
        """
        if depth == 0:
            return self.get_position_value(x_coor, y_coor)

        next_move = "B" if last_move == "R" else "R"
        if maximising:
            current_max = float("-inf")
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.board[x][y][0] == 0:
                        self.board[x][y][0] = self.colour_dict[next_move]
                        current_evaluation = self.minimax(
                            depth - 1,
                            alpha,
                            beta,
                            False,
                            next_move,
                            x,
                            y,
                        )
                        self.board[x][y][0] = 0
                        current_max = max(current_max, current_evaluation)
                        alpha = max(alpha, current_evaluation)
                        if beta <= alpha:
                            break
            return current_max
        else:
            current_min = float("inf")
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.board[x][y][0] == 0:
                        self.board[x][y][0] = self.colour_dict[next_move]
                        current_evaluation = self.minimax(
                            depth - 1,
                            alpha,
                            beta,
                            True,
                            next_move,
                            x,
                            y,
                        )
                        self.board[x][y][0] = 0
                        current_min = min(current_min, current_evaluation)
                        beta = min(beta, current_evaluation)
                        if beta <= alpha:
                            break
            return current_min

    def get_position_value(self, x, y):
        """
        Get the value of the current position based on the state of the board.
        This is basically the heuristic of the current position.

        :returns: The static value of the current position.
        """
        return self.board[x][y][1]

    def is_position_valid(self, position):
        """
        Checks if the given (x, y) position given is valid and not occupied.

        :param position: A tuple of the format (x: int, y: int), that represents the
            position on the board under evaluation.

        :returns: True if the position exists on the board, False otherwise.
        """
        try:
            x = position[0]
            y = position[1]
            if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
                return False
            return True
        except Exception:
            return False

    def is_position_available(self, position):
        return self.is_position_valid(position) and self.board[position[0]][position[1]][0] not in ["B", "R"]

    def neighbours(self, position):
        (x, y) = position
        count = 0
        neighbours_list = []
        possible_positions = [(x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y)]
        for position in possible_positions:
            if self.is_position_valid(position):
                if self.is_position_available(position):
                    neighbours_list.append(position)
                elif self.board[position[0]][position[1]][0] == self.colour:
                    count += 1
                elif self.board[position[0]][position[1]][0] == self.opp_colour():
                    count -= 1
                # Avoid stone clusters (blobs)
                if count >= 3:
                    self.board[position[0]][position[1]][1] -= 10
                elif count <= -3:
                    self.board[position[0]][position[1]][1] += 10
        return neighbours_list

    def bridges(self, position):
        (x, y) = position
        bridge_list = []
        possible_bridge_list = [(x+2, y-1), (x+1, y-2), (x+1, y+1), (x-1, y-1), (x-1, y+2), (x-2, y+1)]
        for possition in possible_bridge_list:
            if (self.is_position_valid(possition)):
                bridge_list.append(possition)
        return bridge_list

    def distance_between_points(self, p1, p2):
        y1, x1 = p1
        y2, x2 = p2
        du = x2 - x1
        dv = (y2 + x2 // 2) - (y1 + x1 // 2)
        return max(abs(du), abs(dv)) if ((du >= 0 and dv >= 0) or (du < 0 and dv < 0)) else abs(du) + abs(dv)

    # def centerness(self, size, x, y):
    #     score = 0
    #     center = (size // 2, size // 2)
    #     center_val = self.board[size // 2][size // 2]
    #     if center_val != 0:
    #         score += 50 * center_val
    #         center_neighbours = self.neighbours(center, size)
    #         # Number of red - number of blue
    #         count = 0
    #         for (x, y) in center_neighbours:
    #             value = self.board[x][y][1]
    #             score += 3 * value
    #             if (value == self.colour):
    #                 count += 1
    #             elif (value == self.opp_colour()):
    #                 count -= 1

    #         # Don't want to continue clusters (blobs)
    #         if count >= 4:
    #             score -= 20
    #         elif count <= -4:
    #             score += 20
    #     return score

    def get_minimax_depth_level(self, perc):
        """
        Return the depth level to use in minimax based on the percentage of time used.

        :param perc: The percentage of time used.
        :returns: 3 for a percentage level [65, 100], 2 for [30, 64], 1 otherwise.
        """
        if perc >= 65:
            return 2
        else:
            return 1


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
