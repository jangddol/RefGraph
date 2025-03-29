import plotly.graph_objects as go
import networkx as nx
import random

from refgraphmaker import get_doi_data_from_json

def flatten_graph_to_edges(graph: dict, graph_object: nx.DiGraph) -> None:
    def add_edges(parent_node, subgraph):
        for child_node, child_subgraph in subgraph.items():
            graph_object.add_edge(parent_node, child_node)
            add_edges(child_node, child_subgraph)

    for root_node, subgraph in graph.items():
        graph_object.add_node(root_node)
        add_edges(root_node, subgraph)

def assign_node_positions(graph_object: nx.DiGraph) -> tuple[dict, dict, dict]:
    """
    Assign positions to nodes and collect metadata (years and labels).

    Args:
        graph_object (nx.DiGraph): The graph object.

    Returns:
        tuple: A tuple containing positions, years, and labels for nodes.
    """
    positions = {}
    years = {}
    labels = {}
    for node in graph_object.nodes():
        # Get metadata for the node
        paper_data, year = get_doi_data_from_json(node)
        title = paper_data.get("title", "Unknown Title")
        journal = paper_data.get("journal", "Unknown Journal")
        if year is None:
            year = random.randint(2000, 2025)  # Assign a random year if missing
        years[node] = year
        labels[node] = f"{title}<br>{journal}<br>Year: {year}"
        positions[node] = (
            year,  # x-axis is the year
            random.uniform(-100, 100),  # Random y-axis position
            random.uniform(-100, 100)  # Random z-axis position
        )
    return positions, years, labels

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

def visualize_reference_graph_3d(graph: dict, output_file: str = "reference_graph.html") -> None:
    """
    Visualize the reference graph in 3D using plotly.

    Args:
        graph (dict): The reference graph to visualize.
        output_file (str): The name of the output HTML file.
    """
    graph_object = nx.DiGraph()
    flatten_graph_to_edges(graph, graph_object)
    node_positions, node_years, node_labels = assign_node_positions(graph_object)
    edge_trace: go.Scatter3d = create_edge_trace(graph_object, node_positions)
    node_trace: go.Scatter3d = create_node_trace(graph_object, node_positions, node_years, node_labels)
    save_3d_graph(edge_trace, node_trace, output_file)

if __name__ == "__main__":
    from refgraphmaker import load_reference_graph_from_json
    
    input_file = "reference_graph.json"
    loaded_graph = load_reference_graph_from_json(input_file)
    output_file = "reference_graph_3d.html"
    visualize_reference_graph_3d(loaded_graph, output_file)
