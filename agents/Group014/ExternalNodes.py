from Node import Node

class ExternalNodes():
    """TBD"""
    UP = -1
    RIGHT = -2
    DOWN = -3
    LEFT = -4

    board_size = None

    external_up = None
    external_right = None
    external_down = None
    external_left = None

    def __init__(self, board_size):
        """
        Create a special node based on the direction (UP=0, RIGHT=1, DOWN=2, LEFT=3).
        """
        self.board_size = board_size
        self._setup_up()
        self._setup_right()
        self._setup_down()
        self._setup_left()

    def _setup_up(self):
        self.external_up = Node(
            self.UP,
            (-1, 0),
            self.board_size,
            0,
            True,
            "R"
        )
        self.external_up.neighbours = self._get_neighbours(self.UP)

    def _setup_right(self):
        self.external_right = Node(
            self.RIGHT,
            (0, self.board_size),
            self.board_size,
            0,
            True,
            "B"
        )
        self.external_right.neighbours = self._get_neighbours(self.RIGHT)

    def _setup_down(self):
        self.external_down = Node(
            self.DOWN,
            (self.board_size, 0),
            self.board_size,
            0,
            True,
            "R"
        )
        self.external_down.neighbours = self._get_neighbours(self.DOWN)

    def _setup_left(self):
        self.external_left = Node(
            self.LEFT,
            (0, -1),
            self.board_size,
            0,
            True,
            "B"
        )
        self.external_left.neighbours = self._get_neighbours(self.LEFT)

    def _get_neighbours(self, direction):
        self.neighbours = []
        if direction == self.UP:
            for x in range(self.board_size):
                self.neighbours.append((0, x)) 
        elif direction == self.RIGHT:
            for x in range(self.board_size):
                self.neighbours.append((x, self.board_size - 1)) 
        elif direction == self.DOWN:
            for x in range(self.board_size):
                self.neighbours.append((self.board_size - 1, x)) 
        elif direction == self.LEFT:
            for x in range(self.board_size):
                self.neighbours.append((x, 0))
