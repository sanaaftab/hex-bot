from helper_functions import *

class Node():
    """Represents a slot on the board"""
    # The uniqe id of the node
    id = None
    # A list of neighbouring nodes
    neighbours = None
    # A list of possible bridges
    bridges = None
    # The coordinates of the node on the board as a tuple
    coordinates = None
    # The dimension of the board
    board_size = 11
    # The colour of the player that is occupying the node, None otherwise
    colour = None

    def __init__(self, id, coordinates, board_size=11, colour=None):
        self.id = id
        self.coordinates = coordinates
        self.neighbours = self._get_neighbours()
        self.bridges = self._get_bridges()
        self.board_size = board_size
        self.colour = colour

    def _get_neighbours(self):
        """
        Get the coordinates of the current nodes neighbouring nodes.

        :returns: A list of neighbouring node coordinates.
        """
        (x, y) = self.coordinates
        neighbours_list = []
        for position in [(x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y)]:
            if (is_position_valid(position, self.board_size)):
                neighbours_list.append(position)
        return neighbours_list

    def _get_bridges(self):
        """
        Get the current nodes bridging nodes.

        :returns: A list of bridging nodes.
        """
        (x, y) = self.coordinates
        bridge_list = []
        for position in [(x+2, y-1), (x+1, y-2), (x+1, y+1), (x-1, y-1), (x-1, y+2), (x-2, y+1)]:
            if (is_position_valid(position, self.board_size)):
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
        self.colour = colour

    def is_free(self):
        """
        Checks if the current node is not occupied.

        :returns: True if unoccupied, False otherwise.
        """
        return self.colour is None