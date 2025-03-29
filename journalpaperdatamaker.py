import requests
import json
from typing import List, Dict, Tuple, Optional
import os

def fetch_journal_articles(journal: str, start_year: int, end_year: int) -> List[Dict]:
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
        url: str = f"https://api.crossref.org/journals/{journal}/works"
        params = {
            'filter': f'from-pub-date:{year}-01-01,until-pub-date:{year}-12-31',
            'rows': 100,  # 한 번의 요청에서 가져올 최대 항목 수
            'cursor': '*',  # 초기 cursor 값
        }
        while True:
            try:
                response: requests.Response = requests.get(url, params=params)
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

def fetch_paper_info(doi: str) -> Optional[Dict]:
    """
    주어진 DOI(Digital Object Identifier)를 사용하여 논문의 정보를 가져옵니다.
    Args:
        doi (str): 논문의 DOI 값.
    Returns:
        dict: 논문의 정보를 포함하는 딕셔너리. 요청이 실패한 경우 None을 반환합니다.
    """
    url: str = f"https://api.crossref.org/works/{doi}"
    try:
        response: requests.Response = requests.get(url)
        if response.status_code != 200:
            print(f"Error retrieving paper info for DOI {doi}: {response.status_code}")
            return None
        return response.json().get('message', {})
    except requests.exceptions.Timeout:
        print(f"Request timed out for DOI {doi}.")
        return None

def fetch_paper_citations(doi: str) -> Tuple[Dict, List[str]]:
    """
    주어진 DOI를 사용하여 논문의 정보를 가져오고, 해당 논문의 참조 목록을 반환합니다.
    Args:
        doi (str): 논문의 DOI(Digital Object Identifier).
    Returns:
        tuple: 
            - 논문 정보(dict): 논문의 제목, 저자, 출판 연도, DOI를 포함하는 딕셔너리.
            - 참조 목록(list): 해당 논문이 참조한 논문의 DOI 목록.
    """
    paper_info = fetch_paper_info(doi)
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

def build_journal_graph(journal: str, year: int) -> Dict[str, Dict]:
    """
    특정 학술지에서 지정된 연도의 논문 데이터를 가져와 논문 간 인용 관계를 그래프로 생성합니다.
    Args:
        journal (str): 학술지 이름.
        year (int): 대상 연도.
    Returns:
        dict: DOI를 키로 하고 논문 정보와 인용 정보를 포함하는 딕셔너리. 
                논문 데이터가 없을 경우 빈 딕셔너리를 반환.
    """
    articles = fetch_journal_articles(journal, year, year)
    if not articles:
        return {}
    print(f"Retrieved {len(articles)} articles for journal {journal} for year {year}.")
    graph: Dict[str, Dict] = {}
    for article in articles:
        doi = article.get('DOI')
        if doi:
            info, references = fetch_paper_citations(doi)
            graph[doi] = {
                "info": info,
                "references": references
            }
    return graph

def save_graph_to_json(graph: Dict, folder: str, filename: str) -> None:
    """
    그래프 데이터를 지정된 폴더에 JSON 파일로 저장합니다.
    Args:
        graph (dict): 저장할 그래프 데이터. 일반적으로 딕셔너리 형태로 표현됩니다.
        folder (str): 저장할 폴더 경로.
        filename (str): 저장할 JSON 파일의 이름.
    """
    os.makedirs(folder, exist_ok=True)  # 폴더가 없으면 생성
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=4)

allowed_ISSN: List[str] = [
    '1936-0851', # ACS Nano (1)
    '1936-086X', # ACS Nano (2)
    '2574-0970', # ACS Applied Nano Materials
    '2399-3650', # Communications Physics
    '0036-8075', # Science (1)
    '1095-9203', # Science (2)
    '0028-0836', # Nature (1)
    '1476-4687', # Nature (2)
    '2041-1723', # Nature Communications (1)
    '1745-2473', # Nature Physics (1)
    '1745-2481', # Nature Physics (2)
    '1476-4636', # Nature Physics (3)
    '1748-3387', # Nature Nanotechnology (1)
    '1748-3395', # Nature Nanotechnology (2)
    '1745-2473', # Nature Nanotechnology (3)
    '1745-2481', # Nature Nanotechnology (4)
    '0034-6748', # Review of Scientific Instruments (1)
    '1089-7623', # Review of Scientific Instruments (2)
    '0031-9007', # Physical Review Letters (1)
    '1079-7114', # Physical Review Letters (2)
    '0003-6951', # Applied Physics Letters (1)
    '1077-3118' # Applied Physics Letters (2)
]

if __name__ == '__main__':
    START_YEAR = 2010
    END_YEAR = 2024
    DATA_PATH = os.path.join(os.getcwd(), "journal_data")

    for journal_issn in allowed_ISSN:
        for year in range(START_YEAR, END_YEAR + 1):
            filename: str = f"{journal_issn}_{year}.json"
            filepath: str = os.path.join(DATA_PATH, filename)
            if os.path.exists(filepath):
                print(f"File {filepath} already exists. Skipping.")
                continue
            print(f"Processing journal {journal_issn} for year {year}")
            journal_graph: Dict[str, Dict] = build_journal_graph(journal_issn, year)
            save_graph_to_json(journal_graph, DATA_PATH, filename)
            print(f"Saved graph to {filepath}")
