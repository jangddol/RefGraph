import os
import json

def get_journal_data_files() -> list[str]:
    """
    Get the list of all journal data files.

    Returns:
        list[str]: A list of filenames containing the journal data.
    """
    journal_data_path = 'journal_data/'
    return [os.path.join(journal_data_path, file) for file in os.listdir(journal_data_path)]

def find_doi_in_file(filename: str, doi: str) -> tuple[dict, int]:
    """
    Find the DOI in a specific JSON file.

    Args:
        filename (str): The name of the JSON file.
        doi (str): The DOI to search for.

    Returns:
        tuple[dict, int]: A tuple containing the paper's data and the year of the data.
    """
    with open(filename, 'r', encoding='UTF-8') as f:
        journal_data = json.load(f)
        if doi in journal_data:
            doi_data = journal_data[doi]
            doi_year = int(filename.split('_')[-1].split('.')[0])
            return doi_data, doi_year
    return None, None

def get_doi_data_from_json(doi: str) -> tuple[dict, int]:
    """
    Retrieve the data of a paper using its DOI from all JSON files.

    Args:
        doi (str): The DOI of the paper.

    Returns:
        tuple[dict, int]: A tuple containing the paper's data and the year of the data.
    """
    journal_data_files = get_journal_data_files()
    
    for filename in journal_data_files:
        doi_data, doi_year = find_doi_in_file(filename, doi)
        if doi_data:
            return doi_data, doi_year
    return None, None

def build_reference_graph(start_doi: str, search_depth: int) -> dict:
    """
    Build a reference graph starting from a given DOI.

    Args:
        start_doi (str): The starting DOI.
        search_depth (int): The depth of the search.

    Returns:
        dict: A nested dictionary representing the reference graph.
    """
    def recursive_search(doi: str, depth: int) -> dict:
        if depth == 0:
            return {}
        
        doi_data, _ = get_doi_data_from_json(doi)
        if not doi_data or 'references' not in doi_data:
            return {}
        
        references = doi_data['references']
        graph = {}
        for ref_doi in references:
            graph[ref_doi] = recursive_search(ref_doi, depth - 1)
        return graph

    return {start_doi: recursive_search(start_doi, search_depth)}

def save_reference_graph_to_json(reference_graph: dict, output_file: str) -> None:
    """
    Save the reference graph to a JSON file.

    Args:
        reference_graph (dict): The reference graph to save.
        output_file (str): The path to the output JSON file.
    """
    with open(output_file, 'w', encoding='UTF-8') as f:
        json.dump(reference_graph, f, indent=4)

def load_reference_graph_from_json(input_file: str) -> dict:
    """
    Load the reference graph from a JSON file.

    Args:
        input_file (str): The path to the input JSON file.

    Returns:
        dict: The loaded reference graph.
    """
    with open(input_file, 'r', encoding='UTF-8') as f:
        return json.load(f)

if __name__ == "__main__":
    START_DOI = "10.1038/s42005-020-0317-3"
    SEARCH_DEPTH = 2
    REFERENCE_GRAPH = build_reference_graph(START_DOI, SEARCH_DEPTH)
    GRAPH_NAME = f"reference_graph_{START_DOI.replace('/', '_')}.json"
    save_reference_graph_to_json(REFERENCE_GRAPH, GRAPH_NAME)
