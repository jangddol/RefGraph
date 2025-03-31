import json
import plotly.graph_objects as go
import networkx as nx
import random
from issnjournalnamedict import ISSN_JOURNAME_NAME_DICT
from makeissndoidict import ISSN_DOI_DICT
from timemeasure import timeit

from refgraphmaker import get_journal_data_files

@timeit
def flatten_graph_to_edges(graph: dict, graph_object: nx.DiGraph) -> None:
    def add_edges(parent_node, subgraph):
        for child_node, child_subgraph in subgraph.items():
            graph_object.add_edge(parent_node, child_node)
            add_edges(child_node, child_subgraph)

    for root_node, subgraph in graph.items():
        graph_object.add_node(root_node)
        add_edges(root_node, subgraph)

@timeit
def remove_invalid_nodes_and_extract_doi_data(graph_object: nx.DiGraph) -> None:
    """
    Remove nodes with invalid or missing DOI data from the graph and extract DOI-related information.
    This function processes a directed graph by:
    1. Identifying valid DOI nodes by checking against journal data files
    2. Removing nodes that don't have corresponding journal data
    3. Extracting metadata (info, year, journal name) for valid DOI nodes
    
    Args:
        graph_object (nx.DiGraph): The directed graph object containing DOI nodes to process
    Returns:
        dict: A dictionary containing metadata for valid DOI nodes, where:
            - Keys are DOI strings
            - Values are dictionaries containing:
                - 'info': Paper information from journal data
                - 'year': Publication year
                - 'journal': Journal name
    """

    nodes = set(graph_object.nodes())
    nodes_no_need_to_remove = set()
    journal_data_files = get_journal_data_files()
    doi_data = {}

    for filename in journal_data_files:
        issn = filename.split('/')[-1].split('_')[0]
        prefix = ISSN_DOI_DICT.get(issn)
        if not prefix:
            continue

        with open(filename, "r", encoding="utf-8") as f:
            journal_data = json.load(f)
            for doi in nodes:
                if doi.startswith(prefix) and doi in journal_data:
                    nodes_no_need_to_remove.add(doi)
                    doi_data[doi] = {}
                    doi_data[doi]["info"] = journal_data[doi]["info"]
                    doi_data[doi]["year"] = int(filename.split('_')[-1].split('.')[0])
                    doi_data[doi]["journal"] = ISSN_JOURNAME_NAME_DICT.get(issn, "Unknown Journal")

    nodes_to_remove = nodes - nodes_no_need_to_remove
    graph_object.remove_nodes_from(nodes_to_remove)
    return doi_data

@timeit
def assign_node_positions_new(graph_object: nx.DiGraph, doi_data: dict) -> tuple[dict, dict, dict]:
    """
    Assign positions to nodes and collect metadata (years and labels).

    Args:
        graph_object (nx.DiGraph): The graph object.
        doi_data (dict): The DOI data dictionary containing metadata for each node.

    Returns:
        tuple: A tuple containing positions, years, and labels for nodes.
    """
    positions = {}
    years = {}
    labels = {}
    for node in graph_object.nodes():
        paper_info = doi_data[node]["info"]
        year = doi_data[node]["year"]
        journal = doi_data[node]["journal"]
        title = paper_info.get("title", "Unknown Title")
        years[node] = year
        labels[node] = f"{title}<br>{journal}<br>Year: {year}"
        positions[node] = (
            year,  # x-axis is the year
            random.uniform(-100, 100),  # Random y-axis position
            random.uniform(-100, 100)  # Random z-axis position
        )
    return positions, years, labels

@timeit
def create_edge_trace(graph_object: nx.DiGraph, positions: dict) -> go.Scatter3d:
    edge_x, edge_y, edge_z = [], [], []
    for source, target in graph_object.edges():
        x0, y0, z0 = positions[source]
        x1, y1, z1 = positions[target]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    return go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='black', width=1),
        hoverinfo='none'
    )

@timeit
def create_node_trace(graph_object: nx.DiGraph, positions: dict, years: dict, labels: dict) -> go.Scatter3d:
    """
    Create a 3D scatter plot for nodes.

    Args:
        graph_object (nx.DiGraph): The graph object.
        positions (dict): Node positions.
        years (dict): Node years.
        labels (dict): Node labels.

    Returns:
        go.Scatter3d: A 3D scatter plot for nodes.
    """
    node_x, node_y, node_z, node_text = [], [], [], []
    for node in graph_object.nodes():
        x, y, z = positions[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(labels[node])  # Use the label for hover text

    return go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        marker=dict(
            size=10,
            color=[years[node] for node in graph_object.nodes()],  # Color by year
            colorscale='Viridis',
            opacity=0.8
        ),
        text=node_text,  # Hover text
        hoverinfo='text'
    )

@timeit
def save_3d_graph(edge_trace: go.Scatter3d, node_trace: go.Scatter3d, output_file: str) -> None:
    figure = go.Figure(data=[edge_trace, node_trace])
    figure.update_layout(
        title="3D Reference Graph",
        showlegend=False,
        scene=dict(
            xaxis_title="Year",
            yaxis_title="Y",
            zaxis_title="Z",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            zaxis=dict(showgrid=True)
        )
    )
    figure.write_html(output_file)
    print(f"3D Reference graph saved to {output_file}")

@timeit
def visualize_reference_graph_3d(graph: dict, output_file: str = "reference_graph.html") -> None:
    """
    Visualize the reference graph in 3D using plotly.

    Args:
        graph (dict): The reference graph to visualize.
        output_file (str): The name of the output HTML file.
    """
    
    graph_object = nx.DiGraph()
    flatten_graph_to_edges(graph, graph_object)
    doi_data = remove_invalid_nodes_and_extract_doi_data(graph_object)
    node_positions, node_years, node_labels = assign_node_positions_new(graph_object, doi_data)
    edge_trace: go.Scatter3d = create_edge_trace(graph_object, node_positions)
    node_trace: go.Scatter3d = create_node_trace(graph_object, node_positions, node_years, node_labels)
    save_3d_graph(edge_trace, node_trace, output_file)

if __name__ == "__main__":
    from refgraphmaker import load_reference_graph_from_json
    import atexit
    from timemeasure import print_execution_times
    
    # Register the function to be called at program exit
    atexit.register(print_execution_times)
    
    input_file = "reference_graph_10.1038_s42005-020-0317-3.json"
    loaded_graph = load_reference_graph_from_json(input_file)
    output_file = "reference_graph_3d.html"
    visualize_reference_graph_3d(loaded_graph, output_file)
