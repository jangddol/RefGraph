from refgraphmaker import load_reference_graph_from_json
from journalpaperdatamaker import fetch_paper_info
from collections import Counter
import os

def find_leaf_nodes(reference_graph: dict) -> list[str]:
    """
    Find all leaf nodes (DOIs with no children) in the reference graph.

    Args:
        reference_graph (dict): The reference graph.

    Returns:
        list[str]: A list of DOIs that are leaf nodes.
    """
    leaf_nodes = []

    def traverse_graph(graph):
        for doi, children in graph.items():
            if not children:  # No children means it's a leaf node
                leaf_nodes.append(doi)
            else:
                traverse_graph(children)

    traverse_graph(reference_graph)
    return leaf_nodes

def get_journal_name_from_doi(doi: str) -> str:
    """
    Fetch the journal name for a given DOI using CrossRef API.

    Args:
        doi (str): The DOI of the paper.

    Returns:
        str: The journal name, or "Unknown" if not found.
    """
    paper_info = fetch_paper_info(doi)
    if paper_info:
        container_title = paper_info.get("container-title", [])
        if container_title:
            return container_title[0]
    return "Unknown"

def find_popular_journals(reference_graph: dict) -> None:
    """
    Find the most popular journals among the leaf nodes of the reference graph.

    Args:
        reference_graph (dict): The reference graph.
    """
    # Step 1: Find all leaf nodes
    leaf_nodes = find_leaf_nodes(reference_graph)
    print(f"Found {len(leaf_nodes)} leaf nodes.")

    # Step 2: Fetch journal names for each leaf node
    journal_names = []
    for doi in leaf_nodes:
        journal_name = get_journal_name_from_doi(doi)
        journal_names.append(journal_name)

    # Step 3: Count the frequency of each journal name
    journal_counter = Counter(journal_names)

    # Step 4: Print the most popular journals
    print("\nMost Popular Journals:")
    for journal, count in journal_counter.most_common():
        print(f"{journal}: {count}")

if __name__ == "__main__":
    # Load the reference graph
    json_name = "reference_graph_10.1038_s42005-020-0317-3.json"
    reference_graph = load_reference_graph_from_json(json_name)

    # Find and print the most popular journals
    find_popular_journals(reference_graph)