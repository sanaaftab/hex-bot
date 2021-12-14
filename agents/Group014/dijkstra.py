from collections import defaultdict
from helper_functions import *

def dijkstra(board, source, destination):
    """
    Implement Dijkstra algorithm to find the shortest path.

    :param board: The game board.
    :param source: The starting node.
    :param destination: The destination node.
    :returns: A list of nodes that create a path from the source node to the end.
    """
    if source.id == destination.id:
        return [source]

    # Map of node.coordinates -> weight
    weights = defaultdict(int)
    # Map of node.coordinates -> set of visited nodes?
    previous_nodes = defaultdict(set)

    free_nodes = []
    for row in  board:
        for node in row:
            if node.is_free() or node.colour == source.colour:
                free_nodes.append(node)

                weights[node.coordinates] = float("inf")
                previous_nodes[node.coordinates] = []

    weights[source.coordinates] = 0

    while free_nodes:
        current_node = min(free_nodes, key=lambda node: weights[node.coordinates])
        free_nodes.remove(current_node)
        if weights[current_node.coordinates] == float("inf"):
            break

        for neighbour in current_node.neighbours:
            alternative_route = weights[current_node.coordinates] + 1
            if alternative_route < weights[neighbour]:
                weights[neighbour] = alternative_route
                previous_nodes[neighbour] = current_node

    path, current_node = [], destination
    while previous_nodes[current_node.coordinates]:
        path.append(current_node)
        current_node = previous_nodes[current_node.coordinates]
    if path:
        path.append(current_node)

    path.reverse()
    return path
