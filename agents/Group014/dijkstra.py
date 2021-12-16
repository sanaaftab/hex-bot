from collections import defaultdict, deque
from helper_functions import *
import heapq

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
                # alternative_route = distance[current_node] + 1
                # if alternative_route < distance[destination]:
                #     print("here too")
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

    # print("THIS IS THE BOARD!!!")
    # for row in board:
    #     for node in row:
    #         print(f"{node.coordinates} -- {node.colour}")
    
    # print("\n\nPREDECESSORS MAP!!!!!!")
    # for key, value in predecessor.items():
    #     if value:
    #         print(f"Predecessor of {key.coordinates} is {value.coordinates}")
    #     else:
    #         print(f"{key.coordinates} has no predecessor")

    path, current_node = [], predecessor[destination]
    while predecessor[current_node] != source:
        path.append(current_node)
        current_node = predecessor[current_node]


    path.append(current_node)
    
    return path
