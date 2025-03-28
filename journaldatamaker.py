import requests
import json
from typing import List, Dict, Tuple, Optional
import os

def get_journal_articles(journal: str, start_year: int, end_year: int) -> List[Dict]:
    """
    주어진 저널과 연도 범위에 따라 CrossRef API를 사용하여 저널 기사 목록을 가져옵니다.
    Args:
        journal (str): 저널의 ISSN 또는 식별자.
        start_year (int): 검색을 시작할 연도 (YYYY 형식).
        end_year (int): 검색을 종료할 연도 (YYYY 형식).
    Returns:
        list: 검색된 저널 기사들의 목록. 각 항목은 CrossRef API에서 반환된 JSON 데이터의 'items'에 해당합니다.
    """
    articles: List[Dict] = []
    for year in range(start_year, end_year + 1):
        url = f"https://api.crossref.org/journals/{journal}/works"
        params = {
            'filter': f'from-pub-date:{year}-01-01,until-pub-date:{year}-12-31',
            'rows': 100,  # 한 번의 요청에서 가져올 최대 항목 수
            'cursor': '*',  # 초기 cursor 값
        }
        while True:
            try:
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print(f"Error retrieving articles for journal {journal} for year {year}: {response.status_code}")
                    break

                data = response.json()
                items = data.get('message', {}).get('items', [])
                if not items:
                    print(f"No articles found for journal {journal} for year {year}.")
                    break  # 0개 받은 경우 멈춤
                articles.extend(items)

                # 다음 페이지로 이동하기 위한 cursor 값 업데이트
                next_cursor = data.get('message', {}).get('next-cursor')
                if not next_cursor:
                    break  # 더 이상 가져올 데이터가 없으면 종료
                params['cursor'] = next_cursor
                print(f"Retrieved {len(items)} articles for journal {journal} for year {year}.")
            except requests.exceptions.Timeout:
                print(f"Request timed out for journal {journal} for year {year}.")
                break
    return articles

def get_paper_info(doi: str) -> Optional[Dict]:
    """
    주어진 DOI(Digital Object Identifier)를 사용하여 논문의 정보를 가져옵니다.
    Args:
        doi (str): 논문의 DOI 값.
    Returns:
        dict: 논문의 정보를 포함하는 딕셔너리. 요청이 실패한 경우 None을 반환합니다.
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error retrieving paper info for DOI {doi}: {response.status_code}")
            return None
        return response.json().get('message', {})
    except requests.exceptions.Timeout:
        print(f"Request timed out for DOI {doi}.")
        return None

def get_paper_citations(doi: str) -> Tuple[Dict, List[str]]:
    """
    주어진 DOI를 사용하여 논문의 정보를 가져오고, 해당 논문의 참조 목록을 반환합니다.
    Args:
        doi (str): 논문의 DOI(Digital Object Identifier).
    Returns:
        tuple: 
            - 논문 정보(dict): 논문의 제목, 저자, 출판 연도, DOI를 포함하는 딕셔너리.
            - 참조 목록(list): 해당 논문이 참조한 논문의 DOI 목록.
    """
    paper_info = get_paper_info(doi)
    if not paper_info:
        print(f"Failed to retrieve paper information for DOI {doi}.")
        return {}, []

    title = paper_info.get('title', ['unknown'])[0] if paper_info.get('title') else 'unknown'
    authors = ', '.join([author.get('given', 'unknown') + ' ' + author.get('family', 'unknown') for author in paper_info.get('author', [])]) if paper_info.get('author') else 'unknown'
    year = paper_info.get('published-print', {}).get('date-parts', [[None]])[0][0] if paper_info.get('published-print') else 'unknown'
    info: Dict = {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi
    }

    references_list: List[str] = []
    references = paper_info.get('reference', [])
    for ref in references:
        ref_doi = ref.get('DOI')
        if ref_doi:
            references_list.append(ref_doi)
    return info, references_list

def get_journal_graph(journal: str, start_year: int, end_year: int) -> Dict[str, Dict]:
    """
    특정 학술지에서 지정된 연도 범위의 논문 데이터를 가져와 논문 간 인용 관계를 그래프로 생성합니다.
    Args:
        journal (str): 학술지 이름.
        start_year (int): 시작 연도.
        end_year (int): 종료 연도.
    Returns:
        dict: DOI를 키로 하고 논문 정보와 인용 정보를 포함하는 딕셔너리. 
              논문 데이터가 없을 경우 빈 딕셔너리를 반환.
    """
    articles = get_journal_articles(journal, start_year, end_year)
    if not articles:
        return {}
    print(f"Retrieved {len(articles)} articles for journal {journal} from {start_year} to {end_year}.")
    graph: Dict[str, Dict] = {}
    for article in articles:
        doi = article.get('DOI')
        if doi:
            info, references = get_paper_citations(doi)
            graph[doi] = {
                "info": info,
                "references": references
            }
    return graph

def save_graph_to_json(graph: Dict, filename: str) -> None:
    """
    그래프 데이터를 JSON 파일로 저장합니다.
    Args:
        graph (dict): 저장할 그래프 데이터. 일반적으로 딕셔너리 형태로 표현됩니다.
        filename (str): 저장할 JSON 파일의 경로와 이름.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=4)

allowed_ISSN = [
    '1936-0851', # ACS Nano (1)
    '1936-086X', # ACS Nano (2)
    '2574-0970', # ACS Applied Nano Materials
    '2399-3650' # Communications Physics
]

if __name__ == '__main__':
    START_YEAR = 2010
    END_YEAR = 2024

    for journal_issn in allowed_ISSN:
        for year in range(START_YEAR, END_YEAR + 1):
            filename = f"{journal_issn}_{year}.json"
            if os.path.exists(filename):
                print(f"File {filename} already exists. Skipping.")
                continue
            print(f"Processing journal {journal_issn} for year {year}")
            journal_graph = get_journal_graph(journal_issn, year, year)
            save_graph_to_json(journal_graph, filename)
            print(f"Saved graph to {filename}")
