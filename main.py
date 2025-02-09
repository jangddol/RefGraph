from GraphNode import GraphNode
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math

def build_graph(start_doi, search_distance):
    total_graphnodes = {}
    visited_dois = set()

    def add_node(doi, distance):
        if doi in visited_dois or distance > search_distance:
            return
        visited_dois.add(doi)
        node = GraphNode(doi)
        total_graphnodes[doi] = node
        for ref_doi in node.get_references():
            add_node(ref_doi, distance + 1)
        for citing_doi in node.get_citing_dois():
            add_node(citing_doi, distance + 1)

    add_node(start_doi, 0)
    return total_graphnodes

def visualize_graph(total_graphnodes):
    G = nx.DiGraph()
    pos = {}
    sizes = []
    labels = {}
    
    for doi, node in total_graphnodes.items():
        year = node.info.get('year', 0)
        x = year
        y = np.random.rand() * 100
        z = np.random.rand() * 100
        pos[doi] = (x, y, z)
        size = math.log(node.get_citing_num() + 1) * 100
        sizes.append(size)
        labels[doi] = node.info.get('title', '')

        G.add_node(doi, size=size, label=node.info.get('title', ''))

    for doi, node in total_graphnodes.items():
        for ref_doi in node.get_references():
            if ref_doi in total_graphnodes:
                G.add_edge(doi, ref_doi)
        for citing_doi in node.get_citing_dois():
            if citing_doi in total_graphnodes:
                G.add_edge(citing_doi, doi)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for edge in G.edges():
        x = [pos[edge[0]][0], pos[edge[1]][0]]
        y = [pos[edge[0]][1], pos[edge[1]][1]]
        z = [pos[edge[0]][2], pos[edge[1]][2]]
        ax.plot(x, y, z, color='black')

    for node in G.nodes():
        ax.scatter(pos[node][0], pos[node][1], pos[node][2], s=G.nodes[node]['size'], label=G.nodes[node]['label'])

    ax.set_xlabel('Year')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

# 예제 사용
if __name__ == '__main__':
    start_doi = '10.1038/s42005-020-0317-3'
    search_distance = 3
    total_graphnodes = build_graph(start_doi, search_distance)
    visualize_graph(total_graphnodes)