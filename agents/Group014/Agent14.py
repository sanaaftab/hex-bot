#!/f/Python/Python39/python
import socket
from random import choice
from time import sleep


class Agent14:
    """
    
    ~~~~~ TBD ~~~~~

    """
    HOST = "127.0.0.1"
    PORT = 1234

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
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if not data or self.interpret_data(data):
                break
        # print(f"Naive agent {self.colour} terminated")

    def interpret_data(self, data):
        """
        Checks the type of message and responds accordingly.

        :returns: True if the game ended, False otherwise.
        """
        # data = 'START;2;R\n' -- strip \n --> 'START;2;R'
        messages = data.decode("utf-8").strip().split("\n")
        # messages = [['START', 2, 'R'], ['']] ... why?
        messages = [x.split(";") for x in messages]

        for s in messages:
            if s[0] == "START":
                if int(s[1]) <= 0:
                    print(f"Invalid board size provided: {s[1]}")
                    return True
                self.board_size = int(s[1])
                if s[2] not in ["R", "B"]:
                    print(f"Invalid player colour provided: {s[2]}")
                    return True
                self.colour = s[2]

                self.board = [[0] * self.board_size for _ in range(self.board_size)]
                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    # s[1] = 2,3 -- split(',') --> [2, 3]
                    action = [int(x) for x in s[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_colour()
                    self.make_move()

        return False

    def make_move(self):
        """
        ~~~~~ TBD ~~~~~
        
        If it can swap, chooses to do so 50% of the time.
        """
        if self.colour == "B" and self.turn_count == 0:
            if choice([0, 1]) == 1:
                self.s.sendall(bytes("SWAP\n", "utf-8"))
                self.turn_count += 1
                return

        # Could possibly filter out with NumPy and avoid recreating everything
        choices = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    choices.append((i, j))
        move = choice(choices)

        self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
        self.board[move[0]][move[1]] = self.colour
        self.turn_count += 1

    def opp_colour(self):
        """
        Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"


if __name__ == "__main__":
    agent = Agent14()
    agent.run()
