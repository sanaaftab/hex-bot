from helper_functions import *


class Node:
    """Represents a slot on the board"""

    # The uniqe id of the node
    # A list of neighbouring nodes
    # A list of possible bridges
    # The coordinates of the node on the board as a tuple
    # The dimension of the board
    # The static value/weight of the node
    # The colour of the player that is occupying the node, None otherwise

    def __init__(self, id, coordinates, board_size, value=1, colour=None):
        self.id = id
        self.coordinates = coordinates
        self.board_size = board_size
        self.value = value
        self.colour = colour
        self.neighbours = self._get_neighbours()
        self.bridges = self._get_bridges()

    def __lt__(self, node_2):
        return distance_between_points(
            (0, 0), node_2.coordinates
        ) < distance_between_points((0, 0), self.coordinates)

    def __eq__(self, node_2):
        if not node_2:
            return False
        return self.coordinates == node_2.coordinates

    def __hash__(self):
        if self.colour == "R":
            return 0
        elif self.colour == "B":
            return -1
        else:
            return self.coordinates[0] ** 5 + 7 + self.coordinates[1] ** 3

    def _get_neighbours(self):
        """
        Get the coordinates current nodes neighbouring nodes.

        :returns: A list of neighbouring node coordinates.
        """
        (x, y) = self.coordinates
        neighbours_list = []
        for position in [
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
        ]:
            if is_position_valid(position, self.board_size) or self.is_external():
                neighbours_list.append(position)

        # Add the external nodes as neighbours to each edge node
        if y == 0:
            neighbours_list.append((0, -1))
        if y == self.board_size - 1:
            neighbours_list.append((0, self.board_size))
        if x == 0:
            neighbours_list.append((-1, 0))
        if x == self.board_size - 1:
            neighbours_list.append((self.board_size, 0))

        return neighbours_list

    def _get_bridges(self):
        """
        Get the current nodes bridging nodes.

        :returns: A list of bridging nodes.
        """
        (x, y) = self.coordinates
        bridge_list = []
        for position in [
            (x + 2, y - 1),
            (x + 1, y - 2),
            (x + 1, y + 1),
            (x - 1, y - 1),
            (x - 1, y + 2),
            (x - 2, y + 1),
        ]:
            if is_position_valid(position, self.board_size):
                bridge_list.append(position)
        return bridge_list

    def is_neighbour(self, position):
        """
        Checks if the given point is a neighbour to the current node (can connect).

        :param position: The position to check against.
        :returns: True if they are neighbouring nodes, False otherwise.
        """
        return position in self.neighbours

    def occupy(self, colour):
        """
        Sets the colour of the current node and updates its `is_free` and `value` attributes.

        :param colour: The colour that occupied this node.
        """
        self.value = float("inf") if colour == "R" else float("-inf")
        self.colour = colour

    def is_external(self):
        """
        Determine whether the node is an external node.

        :returns: True if the node is an external node, False otherwise.
        """
        x, y = self.coordinates
        return x == -1 or x == self.board_size or y == -1 or y == self.board_size

    def is_free(self):
        """
        Determine whether the node is unoccupied.

        :returns: True if the node is unoccupied, False otherwise.
        """
        return self.colour is None


class ExternalNodes:
    """Represents the external nodes."""

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
        """Create the four external nodes."""
        self.board_size = board_size
        self._setup_up()
        self._setup_right()
        self._setup_down()
        self._setup_left()

    def _setup_up(self):
        self.external_up = Node(self.UP, (-1, 0), self.board_size, 0, "R")
        self.external_up.neighbours = self._get_neighbours(self.UP)

    def _setup_right(self):
        self.external_right = Node(
            self.RIGHT, (0, self.board_size), self.board_size, 0, "B"
        )
        self.external_right.neighbours = self._get_neighbours(self.RIGHT)

    def _setup_down(self):
        self.external_down = Node(
            self.DOWN, (self.board_size, 0), self.board_size, 0, "R"
        )
        self.external_down.neighbours = self._get_neighbours(self.DOWN)

    def _setup_left(self):
        self.external_left = Node(self.LEFT, (0, -1), self.board_size, 0, "B")
        self.external_left.neighbours = self._get_neighbours(self.LEFT)

    def _get_neighbours(self, direction):
        neighbours = []
        if direction == self.UP:
            for x in range(self.board_size):
                neighbours.append((0, x))
        elif direction == self.RIGHT:
            for x in range(self.board_size):
                neighbours.append((x, self.board_size - 1))
        elif direction == self.DOWN:
            for x in range(self.board_size):
                neighbours.append((self.board_size - 1, x))
        elif direction == self.LEFT:
            for x in range(self.board_size):
                neighbours.append((x, 0))
        return neighbours
