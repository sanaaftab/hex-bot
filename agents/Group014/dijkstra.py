from collections import defaultdict, deque
from helper_functions import *

def dijkstra(board, free_nodes, source, destination):
    """
    Implement Dijkstra algorithm to find the shortest path.

    :param free_nodes: A list of all unoccupied nodes.
    :param source: The starting node.
    :param destination: The destination node.
    :returns: A list of nodes that create a path from the source node to the end.
    """
    if source.id == destination.id:
        return [source]

    # Map of node.coordinates -> weight
    weights = defaultdict(int)

    # Map of node.coordinates -> set of visited nodes? (pre-decessor map)
    predecessor = defaultdict(set)

    for node in free_nodes:
        weights[node] = float("inf")
        predecessor[node] = None

    weights[source] = 0
    predecessor[source] = source

    # predecessor[source.coordinates].append(source)

    while free_nodes:
        u = min(free_nodes, key=lambda node: weights[node.value])
        free_nodes.remove(u)

        if u == destination:
            break

        print(u.neighbours)

        for nb in u.neighbours:
            print(nb, nb[0], nb[1])
            v = board[nb[0]][nb[1]]
            print(v)
            w = v.value
            alt = weights[u] + w
            if alt < weights[v]:
                weights[v] = alt
                predecessor[v] = u

        # # If minimum infinite then break
        # if weights[current_node.coordinates] == float("inf"):
        #     break

        # IMPLEMENT 'IS_SPECIAL' HERE
        # for neighbour in current_node.neighbours:
        #     alternative_route = weights[current_node.coordinates] + 1
        #     if alternative_route < weights[neighbour]:
        #         weights[neighbour] = alternative_route
        #         predecessor[neighbour] = current_node

    path, current_node = [], destination
    while predecessor[current_node]:
        path.append(current_node)
        current_node = predecessor[current_node]
    if path:
        path.append(current_node)

    path.reverse()
    return path
