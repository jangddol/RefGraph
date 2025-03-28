import os
import json

def extract_journal_doi(doi: str) -> str:
    """
    Extract the journal DOI from the full DOI.

    Args:
        doi (str): The full DOI.

    Returns:
        str: The journal DOI.
    """
    return doi.split('/')[0]

def get_journal_data_files(journal_doi: str) -> list[str]:
    """
    Get the list of journal data files for a specific journal DOI.

    Args:
        journal_doi (str): The journal DOI.

    Returns:
        list[str]: A list of filenames containing the journal data.
    """
    journal_data_path = 'journal_data/'
    journal_data_fullpath = os.listdir(journal_data_path)
    return [file for file in journal_data_fullpath if file.startswith(journal_doi)]

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
    Retrieve the data of a paper using its DOI from JSON files.

    Args:
        doi (str): The DOI of the paper.

    Returns:
        tuple[dict, int]: A tuple containing the paper's data and the year of the data.
    """
    journal_doi = extract_journal_doi(doi)
    journal_data_files = get_journal_data_files(journal_doi)
    
    for filename in journal_data_files:
        doi_data, doi_year = find_doi_in_file(filename, doi)
        if doi_data:
            return doi_data, doi_year
    return None, None

def get_references(doi: str) -> list[str]:
    """
    Retrieve the list of references for a given DOI.

    Args:
        doi (str): The Digital Object Identifier (DOI) of the document.

    Returns:
        list[str]: A list of DOIs that are referenced by the given document.
    """
    paper_data = get_doi_data_from_json(doi)[0]
    if paper_data:
        return paper_data.get('references', [])
    return []


def find_before_doi(doi_container: list[str], remain_depth:int, already_done: list[str]=None) -> list[str]:
    if remain_depth == 0:
        return doi_container

    if already_done is None:
        already_done = []

    new_doi_container = []
    for doi in doi_container:
        if doi in already_done:
            continue
        already_done.append(doi)
        new_doi_container.extend(get_references(doi))

    return find_before_doi(new_doi_container, remain_depth-1, already_done)

# 예제 사용
if __name__ == '__main__':
    start_doi = '10.1038/s42005-020-0317-3'
    search_distance = 2
    dois = find_before_doi([start_doi], search_distance)
    print(f"Found {len(dois)} DOIs before {start_doi} within {search_distance} steps.")
    print(dois)

# TODO : journal_data의 파일명의 형식이 {doi}_{year}.json이 아닌 {ISSN}_{year}.json으로 되어있어서 수정이 필요함
# TODO : doi로부터 journal의 ISSN을 추출하는 함수가 필요함