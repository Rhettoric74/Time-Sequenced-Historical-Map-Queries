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

def list_all_multiword_paths(map_graph, depth_limit = 1):
    paths = []
    for depth in range(1, depth_limit + 1):
        for node in map_graph.nodes:
            paths += search_from_node(node, depth)
    return paths

if __name__ == "__main__":
    mg = map_graph.MapGraph("0068010_h2_w7.png")
    map_graph.prims_mst(mg.nodes, map_graph.FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty)
    print(list_all_multiword_paths(mg))
