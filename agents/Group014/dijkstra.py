from collections import defaultdict, deque
from helper_functions import *

# between a node and a free node = 1
# between a node and one of the same colour is 0
# between a node and one of the opposite colour is INFINITY
def get_weight(node_1, node_2):
    if node_1.is_external():
        if node_1.colour == node_2.colour or node_2.colour == None:
            return 0
        else:
            return float("inf")
    elif node_2.is_external():
        if node_2.colour == node_1.colour or node_1.colour == None:
            return 0
        else:
            return float("inf")
    elif node_1.colour == 0 or node_2.colour == None:
        return 1
    else:
        return 0 if node_1.colour == node_2.colour else float("inf")


def dijkstra(free_nodes, source, destination):
    """
    Implement Dijkstra algorithm to find the shortest path.

    :param free_nodes: A list of all unoccupied nodes.
    :param source: The starting node.
    :param destination: The destination node.
    :returns: A list of nodes that create a path from the source node to the end.
    """
    if source.id == destination.id:
        return [source]

    # Map of node.coordinates -> distance
    distance = defaultdict(int)
    # Map of node.coordinates -> nodes
    previous_nodes = {}

    # for node in free_nodes:
    #     distance[node.coordinates] = float("inf")
    #     previous_nodes[node.coordinates] = None

    distance[source.coordinates] = 0
    previous_nodes[source.coordinates] = source
    # previous_nodes[source.coordinates] = source.coordinates

    # Note that `free_nodes` contains both the free and the nodes occupied by the current player
    while free_nodes:
        current_node = min(free_nodes, key=lambda node: distance[node.coordinates])
        free_nodes.remove(current_node)

        if current_node == destination:
            break

        for neighbour in current_node.neighbours:
            # x, y = neighbour
            # alternative_route = get_weight(current_node, neighbour_node, board)
            # if distance[current_node.coordinates] != float("inf"):
            alternative_route = distance[current_node.coordinates] + 1
            if alternative_route < distance[neighbour]:
                distance[neighbour] = alternative_route
                previous_nodes[neighbour] = current_node
            if neighbour == destination.coordinates:
                previous_nodes[destination.coordinates] = current_node

    path = []
    current_node = destination
    while previous_nodes[current_node.coordinates]:
        path.append(current_node)
        current_node = previous_nodes[current_node.coordinates]
    if path:
        path.append(current_node)

    path.reverse()
    print(f"Predescessors: {[node for node in previous_nodes]}\nWeights: {[node for node in distance]}\nPath: {[node for node in path]}")
    return path
