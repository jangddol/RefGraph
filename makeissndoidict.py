import os
import json
from collections import defaultdict

def extract_common_prefix(dois):
    """Extract the common prefix from a list of DOIs."""
    if not dois:
        return ""
    prefix = dois[0]
    for doi in dois[1:]:
        while not doi.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix

def create_issn_doi_dict(data_dir):
    """Create a dictionary mapping ISSNs to DOI common prefixes."""
    issn_doi_dict = defaultdict(list)
    issn_files = defaultdict(list)

    # Group files by ISSN
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            issn = filename.split("_")[0]
            issn_files[issn].append(os.path.join(data_dir, filename))

    # Process each ISSN group
    for issn, files in issn_files.items():
        all_dois = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_dois.extend(item for item in data)

        if all_dois:
            common_prefix = extract_common_prefix(all_dois)
            if common_prefix:
                issn_doi_dict[issn] = common_prefix

    # Save the dictionary to a JSON file
    with open("issn_doi_dict.json", "w", encoding="utf-8") as f:
        json.dump(issn_doi_dict, f, ensure_ascii=False, indent=4)

def load_issn_doi_dict(filepath):
    """Load the ISSN-DOI dictionary from a JSON file with memoization."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

ISSN_DOI_DICT = load_issn_doi_dict('issn_doi_dict.json')


# Example usage
if __name__ == "__main__":
    data_directory = "./journal_data"  # Adjust this path as needed
    create_issn_doi_dict(data_directory)
    issn_doi_dict = load_issn_doi_dict("issn_doi_dict.json")
    print(issn_doi_dict)