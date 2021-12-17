from collections import defaultdict
from helper_functions import *

def dijkstra(board, source, destination):
    """
    Implement Dijkstra algorithm to find the shortest path.

    :param free_nodes: A list of all unoccupied nodes.
    :param source: The starting node.
    :param destination: The destination node.
    :returns: A list of nodes that represent a path from the source node to the end.
    """
    if source.id == destination.id:
        return [source]

    # Map of node.coordinates -> distance
    distance = defaultdict(int)
    # Map of node.coordinates -> nodes
    predecessor = {}
    # Priority queue containing ALL the nodes
    pq = set()
    pq.add(source)
    pq.add(destination)

    for row in board:
        for node in row:
            distance[node] = float("inf")
            predecessor[node] = None
            pq.add(node)

    distance[source] = 0
    predecessor[source] = source
    distance[destination] = float("inf")
    predecessor[destination] = None

    while pq:
        current_node = min(pq, key=lambda node: distance[node])
        pq.remove(current_node)

        if current_node.coordinates == destination.coordinates:
            break

        for neighbour in current_node.neighbours:
            if destination.coordinates == neighbour and (current_node.colour == source.colour or current_node.is_free()):
                distance[destination] = distance[current_node] + 1
                predecessor[destination] = current_node

            if is_position_valid(neighbour, len(board)) and (current_node.colour == source.colour or current_node.is_free()):
                x, y = neighbour
                node_of_neighbour = board[x][y]
                if node_of_neighbour in pq:
                    if (
                        node_of_neighbour.colour == source.colour
                        or not node_of_neighbour.colour
                    ):
                        alternative_route = distance[current_node] + 1
                        if alternative_route < distance[node_of_neighbour]:
                            distance[node_of_neighbour] = alternative_route
                            predecessor[node_of_neighbour] = current_node

    path, current_node = [], predecessor[destination]
    try:
        while predecessor[current_node] != source:
            path.append(current_node)
            current_node = predecessor[current_node]
    except KeyError:
        return []

    path.append(current_node)
    
    return path
