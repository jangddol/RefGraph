import requests

def search_journal_by_name(journal_name):
    url = "https://api.crossref.org/journals"
    params = {
        'query': journal_name,
        'rows': 10  # Adjust the number of rows as needed
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json().get('message', {}).get('items', [])
        for item in items:
            print(f"Journal Name: {item.get('title')}, ISSN: {item.get('ISSN')}")
        return items
    else:
        print(f"Error searching for journal {journal_name}: {response.status_code}")
        return []

# if __name__ == '__main__':
#     journal_name = 'acs nano'  # Example journal name
#     search_journal_by_name(journal_name)