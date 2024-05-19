import map_graph

def search_from_node(node, depth, path = []):
    """
    Purpose: generate possible paths of length k from current node
    Parameters: node, map graph node, depth, the length of the target paths, path, the path that has been built so far.
    Returns: a nested list, where each list represents a path of MapGraph nodes"""
    path = path + [node]
    depth -= node.text.count(" ")
    if depth == 0:
        return [path]
    if depth < 0:
        return []
    paths = []
    for neighbor in node.neighbors:
        if neighbor not in path:
            new_paths = search_from_node(neighbor, depth - 1, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths

def express_node_sequence_as_phrase(node_sequence):
    return " ".join([node.text for node in node_sequence])

def search_for_text_phrase(nodes_list, phrase, nodes_sequence_found = []):
    current_phrase_found = express_node_sequence_as_phrase(nodes_sequence_found)
    if current_phrase_found == phrase:
        return nodes_sequence_found
    else:
        for node in nodes_list:
            # check if adding the current node's text will add something that is part of the actual phrase
            if (len(nodes_sequence_found) == 0 and node.text in phrase) or current_phrase_found + " " + node.text in phrase:
                print(node.text)
                phrase_found_from_node = search_for_text_phrase(node.neighbors, phrase, nodes_sequence_found + [node])
                if phrase_found_from_node != None:
                    return phrase_found_from_node
        return None

def search_node_sequence_in_graph(nodes_list, node_sequence):
    """
    Purpose: recursively determine whether a given sequence of feature nodes is connected in a given map graph
    Parameters: nodes_list, a list containing feature nodes which have been linked in some way 
        (usually taken from a MapGraph object's .nodes attribute in the initial call)
        node sequence, a list of FeatureNode objects to check if they form a connected path in the map graph
    Returns: True or False whether a connected node sequence matching the desired node sequence exists in the graph
    """
    if len(node_sequence) == 0:
        return True
    else:
        for node in nodes_list:
            if node_sequence[0].equals(node):
                return search_node_sequence_in_graph(node.neighbors, node_sequence[1:])
    return False

def list_all_multiword_paths(map_graph, depth_limit = 1):
    paths = []
    for depth in range(1, depth_limit + 1):
        for node in map_graph.nodes:
            paths += search_from_node(node, depth)
    return paths

if __name__ == "__main__":
    mg = map_graph.MapGraph("0068010_h2_w7.png")
    map_graph.prims_mst(mg.nodes, map_graph.FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty)
    multiword_paths = list_all_multiword_paths(mg)
    print([express_node_sequence_as_phrase(path) for path in multiword_paths])
    print(search_for_text_phrase(mg.nodes, "Griswold Stursbery", []))
    for path in multiword_paths:
        print(search_node_sequence_in_graph(mg.nodes, path))
