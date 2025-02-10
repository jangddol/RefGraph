import requests
import json
import os

def get_journal_articles(journal, start_year, end_year):
    articles = []
    for year in range(start_year, end_year + 1):
        url = f"https://api.crossref.org/journals/{journal}/works"
        params = {
            'filter': f'from-pub-date:{year}-01-01,until-pub-date:{year}-12-31',
            'rows': 1000  # Adjust the number of rows as needed
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            items = response.json().get('message', {}).get('items', [])
            articles.extend(items)
        else:
            print(f"Error retrieving articles for journal {journal} for year {year}: {response.status_code}")
    return articles

def get_paper_info(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('message', {})
    else:
        print(f"Error retrieving paper info for DOI {doi}: {response.status_code}")
        return None

def get_references(doi):
    paper_info = get_paper_info(doi)
    references_list = []
    if paper_info:
        references = paper_info.get('reference', [])
        for ref in references:
            ref_doi = ref.get('DOI')
            if ref_doi:
                references_list.append(ref_doi)
    else:
        print(f"Failed to retrieve references for DOI {doi}.")
    return references_list

def get_paper_citations(doi):
    paper_info = get_paper_info(doi)
    if paper_info:
        title = paper_info.get('title', ['unknown'])[0] if paper_info.get('title') else 'unknown'
        authors = ', '.join([author.get('given', 'unknown') + ' ' + author.get('family', 'unknown') for author in paper_info.get('author', [])]) if paper_info.get('author') else 'unknown'
        year = paper_info.get('published-print', {}).get('date-parts', [[None]])[0][0] if paper_info.get('published-print') else 'unknown'
        info = {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi
        }
    else:
        print(f"Failed to retrieve paper information for DOI {doi}.")
        return {}, []

    references = get_references(doi)
    return info, references

def get_journal_graph(journal, start_year, end_year):
    articles = get_journal_articles(journal, start_year, end_year)
    print(f"Retrieved {len(articles)} articles for journal {journal} from {start_year} to {end_year}.")
    graph = {}
    for article in articles:
        doi = article.get('DOI')
        if doi:
            info, references = get_paper_citations(doi)
            graph[doi] = {
                "info": info,
                "references": references
            }
    return graph

def save_graph_to_json(graph, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=4)

allowed_ISSN = [
    '1936-0851', # ACS Nano (1)
    '1936-086X', # ACS Nano (2)
    '2574-0970' # ACS Applied Nano Materials
]

if __name__ == '__main__':
    start_year = 2010
    end_year = 2024

    for journal in allowed_ISSN:
        for year in range(start_year, end_year + 1):
            print(f"Processing journal {journal} for year {year}")
            journal_graph = get_journal_graph(journal, year, year)
            filename = f"{journal}_{year}.json"
            save_graph_to_json(journal_graph, filename)
            print(f"Saved graph to {filename}")