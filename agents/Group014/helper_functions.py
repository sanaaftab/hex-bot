def is_position_valid(position, board_size):
    """
    Checks if the given (x, y) position given is valid and not occupied.

    :param position: A tuple of the format (x: int, y: int), that represents the
        position on the board under evaluation.
    :param board_size: The dimension of the board.
    :returns: True if the position exists on the board, False otherwise.
    """
    try:
        x = position[0]
        y = position[1]
        if x < 0 or x >= board_size or y < 0 or y >= board_size:
            return False
        return True
    except Exception:
        return False

def is_position_available(position, board):
    """
    Checks if the given position exists on the board and is free.

    :param position: The position to check.
    :param board: The board that the position is checked against.
    :returns: True if it's a valid slot, and is not occupied. False otherwise.
    """
    return is_position_valid(position) and board[position[0]][position[1]].is_free

def get_opposing_colour(current_colour):
    """
    Returns the char representation of the colour opposite to the current one.

    :param current_colour: The current colour of the player.
    :returns: 'R' for red, 'B' for blue, 'None' otherwise.
    """
    if current_colour == "R":
        return "B"
    elif current_colour == "B":
        return "R"
    else:
        return "None"

def distance_between_points(point_1, point_2):
    """
    Gets the distance between two points on a hex board.

    :param point_1: The first point to check for.
    :param point_2: The second point to check for.
    :returns: The absolute distance between the two points.
    """
    y1, x1 = point_1
    y2, x2 = point_2
    dx = x2 - x1
    dy = (y2 + x2 // 2) - (y1 + x1 // 2)
    return max(abs(dx), abs(dy)) if ((dx >= 0 and dy >= 0) or (dx < 0 and dy < 0)) else abs(dx) + abs(dy)

def is_board_full(board):
    """
    Checks if the board is full.

    :param board: The board to evaluate.
    :returns: True if there are no more free slots, False otherwise.
    """
    for row in board:
        for node in row:
            if node.is_free:
                return False
    return True

def get_free_nodes(board):
    """
    Get all the nodes which are unoccupied from the board as a list.

    :param board: The board to extract the nodes from.
    :returns: A list of all the unoccupied nodes.
    """
    nodes = []
    for row in board:
        for node in row:
            if node.is_free:
                nodes.append(node)
    return nodes