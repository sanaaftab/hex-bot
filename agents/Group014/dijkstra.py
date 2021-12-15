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
    :returns: A list of nodes that create a path from the source node to the end.
    """
    if source.id == destination.id:
        return [source]

    # Map of node.coordinates -> distance
    distance = defaultdict(int)
    # Map of node.coordinates -> nodes
    predecessor = {}

    for row in board:
        for node in row:
            distance[node] = float("inf")
            predecessor[node] = None

    distance[source] = 0
    predecessor[source] = source
    distance[destination] = float("inf")
    predecessor[destination] = None
    # predecessor[source.coordinates] = source.coordinates

    # pq = [cell for cells in board for cell in cells]
    pq = []
    pq.append(source)
    pq.append(destination)
    heapq.heapify(pq)

    # Note that `free_nodes` contains both the free and the nodes occupied by the current player
    while pq != []:
        current_node = heapq.heappop(pq)
        if current_node == destination:
            break

        # make sure neighbor is either free or same color as us
        for neighbour in current_node.neighbours:
            if (is_position_available(neighbour, board) or is_coordinate_external(neighbour, board)):
                print(f"Hello neighbour {neighbour} -- {current_node.coordinates}")
                x, y = neighbour
                node_of_neighbour = board[x][y]
                if node_of_neighbour.colour == source.colour or not node_of_neighbour.colour:
                    pq.append(node_of_neighbour)
                    # x, y = neighbour
                    # alternative_route = get_weight(current_node, neighbour_node, board)
                    # if distance[current_node.coordinates] != float("inf"):
                    alternative_route = distance[current_node] + 1

                    print(f"General Kenoby, {node_of_neighbour.coordinates} -- {current_node.coordinates}")
                    if alternative_route < distance[node_of_neighbour]:
                        distance[node_of_neighbour] = alternative_route
                        predecessor[node_of_neighbour] = current_node
                    if node_of_neighbour.coordinates == destination.coordinates:
                        predecessor[destination] = current_node
                        heapq.heapify(pq)

    path = []
    # i = 1
    # print("LEN OF PREV NODES", len(predecessor))
    # import pdb;pdb.set_trace()
    for node in predecessor.keys():
        if predecessor[node] and node not in [source, destination]:   # I AM TESTING ON 4X4
            # print(node.coordinates, predecessor[node].coordinates)
            path.append(node)
    #
    # while predecessor[current_node.coordinates]:
    #     print(f"predecessor of {current_node.coordinates} is {predecessor[current_node.coordinates]}")
    #     path.append(current_node)
    #     current_node = predecessor[current_node.coordinates]
    # path.reverse()
    # print(f"Predescessors: {[node for node in predecessor]}\nPath: {[node for node in path]}")
    return path
