import socket

from time import time
from copy import deepcopy

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
                self.board = self.make_move(self.board)

        elif message[0] == "END":
            return True

        elif message[0] == "CHANGE":
            if message[3] == "END":
                return True

            elif message[1] == "SWAP":
                self.colour = self.opp_colour()
                if message[3] == self.colour:
                    self.board = self.make_move(self.board)

            elif message[3] == self.colour:
                opp_move = [int(x) for x in message[1].split(",")]
                self.board[opp_move[0]][opp_move[1]][0] = self.colour_dict[self.opp_colour()]
                self.board[opp_move[0]][opp_move[1]][1] = float("-inf")
                self.board = self.update_heatmap(self.board, opp_move)
                self.board = self.make_move(self.board)

        self.TIME_LEFT -= int((time() - current_time))
        # Percentage = (time_left / 300) * 100
        self.thinking_time = self.get_minimax_depth_level(int(self.TIME_LEFT / 3))
        return False

    def make_move(self, board):
        """
        Gets all available moves from the current state of the board and randomly
        chooses the next move to make from the available pool.

        If it can swap, chooses to do so.
        
        :param board: The board to update.
        :returns: The updated board.
        """
        if self.colour == "B" and self.turn_count == 0:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
            self.turn_count += 1
            return board

        move = self.minimax_wrap(board)

        board[move[0]][move[1]][1] = float("inf")
        board = self.update_heatmap(board, move)

        self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
        board[move[0]][move[1]][0] = self.colour_dict[self.colour]
        self.turn_count += 1

        return board

    def opp_colour(self):
        """
        Returns the char representation of the colour opposite to the current one.

        :returns: 'R' for red, 'B' for blue, 'None' otherwise.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"

    def update_heatmap(self, board, move, colour=None):
        """
        Updates the board weights and returns the updated board.

        :param board: The board to update.
        :param move: The move that has been made.
        :param colour: The player that has made the move.
        :returns: The updated board.
        """
        colour = colour if colour else self.colour

        for move_x, move_y in self.neighbours(move):
            board[move_x][move_y][1] = board[move_x][move_y][1] + 4 if colour == "R" else board[move_x][move_y][1] - 4
        for move_x, move_y in self.bridges(move):
            board[move_x][move_y][1] = board[move_x][move_y][1] + 5 if colour == "B" else board[move_x][move_y][1] - 5

        if self.turn_count > 1:
            longest_current_chain = self.get_longest_chain(board, colour)
            if longest_current_chain:
                self.update_chain_neighbours(longest_current_chain[0], longest_current_chain[len(longest_current_chain) - 1], colour)
        return board

    def minimax_wrap(self, board):
        val = float("-inf") if self.colour == "R" else float("inf")
        best_move = None
        # for i in self.board:
        #     print([x[1] for x in i])
        # print("------------------------------------------")
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y][0] == 0:
                    board = self.dijkstra((x, y), board)
                    value = self.minimax(self.board, self.thinking_time, float("-inf"), float("inf"), self.colour == "R", self.opp_colour(), x, y)
                    if self.colour == "R":
                        if value > val:
                            val = value
                            best_move = (x, y)
                    elif self.colour == "B":
                        if value < val:
                            val = value
                            best_move = (x, y)
        return best_move

    def minimax(
        self, board, depth, alpha, beta, maximising, last_move, x_coor, y_coor
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
        if depth == 0 or self.is_board_full(board):
            return self.get_position_value(x_coor, y_coor)

        next_move = "B" if last_move == "R" else "R"
        if maximising:
            current_max = float("-inf")
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if board[x][y][0] == 0:
                        new_board = deepcopy(board)
                        new_board[x][y][0] = self.colour_dict[next_move]
                        new_board = self.update_heatmap(board, (x, y), next_move)
                        current_evaluation = self.minimax(
                            new_board,
                            depth - 1,
                            alpha,
                            beta,
                            False,
                            next_move,
                            x,
                            y,
                        )
                        current_max = max(current_max, current_evaluation)
                        alpha = max(alpha, current_evaluation)
                        if beta <= alpha:
                            break
            return current_max
        else:
            current_min = float("inf")
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if board[x][y][0] == 0:
                        new_board = deepcopy(board)
                        new_board[x][y][0] = self.colour_dict[next_move]
                        new_board = self.update_heatmap(board, (x, y), next_move)
                        current_evaluation = self.minimax(
                            new_board,
                            depth - 1,
                            alpha,
                            beta,
                            True,
                            next_move,
                            x,
                            y,
                        )
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
        """
        Checks if the given position exists on the board and is free.

        :param position: The position to check.
        :returns: True if it's a valid slot, and is not occupied. False otherwise.
        """
        return self.is_position_valid(position) and self.board[position[0]][position[1]][0] not in ["B", "R"]

    def neighbours(self, position):
        """
        TBD
        """
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

    def update_chain_neighbours(self, first, last, colour=None):
        """
        Updates the weights of the first and last position in a chain.
        Gets the top and bottom neighbours for the red player, left and right for blue.

        :param first: The first position to evaluate (Top for red, left for blue).
        :param last: The last position to evaluate (Bottom for red, right for blue).
        :param colour: The colour of the player who made the move.
        """
        x_first, y_first = first
        x_last, y_last = last
        colour = colour if colour else self.colour

        if colour == "R":
            neighbours = [(x_first - 1, y_first), (x_first - 1, y_first + 1), (x_last + 1, y_last), (x_last + 1, y_last - 1)]
        else:
            neighbours = [(x_first, y_first - 1), (x_first + 1, y_first - 1), (x_last - 1, y_last + 1), (x_last, y_last + 1)]

        for x, y in neighbours:
            if self.is_position_available((x, y)):
                self.board[x][y][1] = self.board[x][y][1] + 50 if colour == "R" else self.board[x][y][1] - 50


    def is_neighbour(self, position1, position2):
        """
        Checks if the given points are neighbours (can connect).

        :param position1: The first position to check.
        :param position2: The second position to check.
        :returns: True if they are neighbouring slots, False otherwise.
        """
        (x, y) = position1
        possible_positions = [position for position in [(x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y)] if self.is_position_available(position)]
        return position2 in possible_positions

    def bridges(self, position):
        """
        TBD
        """
        (x, y) = position
        bridge_list = []
        possible_bridge_list = [(x+2, y-1), (x+1, y-2), (x+1, y+1), (x-1, y-1), (x-1, y+2), (x-2, y+1)]
        for possition in possible_bridge_list:
            if (self.is_position_valid(possition)):
                bridge_list.append(possition)
        return bridge_list

    def distance_between_points(self, p1, p2):
        """
        Gets the distance between two points on a hex board.

        :param p1: The first point to check for.
        :param p2: The second point to check for.
        :returns: The absolute distance between the two points.
        """
        y1, x1 = p1
        y2, x2 = p2
        du = x2 - x1
        dv = (y2 + x2 // 2) - (y1 + x1 // 2)
        return max(abs(du), abs(dv)) if ((du >= 0 and dv >= 0) or (du < 0 and dv < 0)) else abs(du) + abs(dv)

    def get_longest_chain(self, board, colour=None):
        """
        Scans the board for any slots occupied by the players colour, which are
        connecting, and marks them as a chain.

        :param board: The board to scan.
        :param colour: The colour of the player to check for.
        :returns: A list of coordinates of the slots that make the longest chain.
        """
        colour = colour if colour else self.colour
        our_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y][0] == self.colour_dict[colour]:
                    our_moves.append((x, y))

        possible_chains = []
        for move in our_moves:
            chain = []
            for move_2 in our_moves:
                if move == move_2:
                    continue
                if self.is_neighbour(move, move_2):
                    if move not in chain:
                        chain.append(move)
                    if move_2 not in chain:
                        chain.append(move_2)
            possible_chains.append(chain)

        max = 0
        index = 0
        for i in range(len(possible_chains)):
            length = len(possible_chains[i])
            if length > max:
                max = length
                index = i
        return possible_chains[index]

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

    def is_board_full(self, board):
        """
        Checks if the board is full.

        :param board: The board to evaluate.
        :returns: True if there are no more free slots, False otherwise.
        """
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == 0:
                    return False
        return True

    def dijkstra(self, source, board):
        """
        Runs the dijkstra algorithm to get the shortest path from the given slot.

        :param source: The slot to search from.
        :param board: The current state of the board.
        :returns: The updated board.
        """
        nodes = [[float("inf")] * self.board_size for _ in range(self.board_size)]
        nodes[source[0]][source[1]] = 0
        spt_set = [[False] * self.board_size for _ in range(self.board_size)]

        # TODO: Run `self.board_size` times to ensure we get a patch across from one
        # end to the next.
        for _ in range(self.board_size):
            x, y = self.minimum_distance(spt_set, board)
            spt_set[x][y] = True

            """
            Update the weight of the adjacent slots of the calculated slot only if the
            current weight is greater than the new weight and the slot is not in the
            shortest path tree
            """
            possible_positions = [(x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y)]
            for position_x, position_y in possible_positions:
                if self.is_position_valid((position_x, position_y)) and board[position_x][position_y][1] > 0 and spt_set[position_x][position_y] == False and nodes[position_x][position_y] > nodes[position_x][position_y] + board[position_x][position_y][1]:
                    board[position_x][position_y][1] += nodes[position_x][position_y]
        
        return board

    def minimum_distance(self, spt_set, board):
        """
        Gets the slot with the minimum weight, from the slots that have not been
        included in the shortest path tree yet.

        :param spt_set: The 2-D boolean list containing the visited slots.
        :param board: The current state of the board.
        :returns: The coordinates of the slot with the lowest weight.
        """
        min = float("inf") 
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y][1] < min and spt_set[x][y] == False:
                    min = board[x][y][1]
                    minimum_slot = (x, y)
        return minimum_slot

if __name__ == "__main__":
    agent = Agent14()
    agent.run()
