# 이 파일에서는 논문의 doi가 주어졌을 때, 그 논문이 인용한 논문의 doi와 그 논문을 인용한 논문의 doi를 불러오는 것을 목표로 합니다.
# 이를 위해 GraphNode라는 클래스를 정의하고, 이 클래스는 논문의 doi를 인자로 받아, 그 논문이 인용한 논문의 doi와 그 논문을 인용한 논문의 doi를 불러옵니다.
# 이를 위해 GraphNode 클래스는 다음과 같은 메소드를 가집니다.
# 1. __init__(self, doi): 논문의 doi를 인자로 받아 객체를 초기화합니다.
# 2. update(self): 이 메소드가 핵심입니다.
    # 이 메소드는 doi에 해당하는 url을 만든 후 request를 보내고, 그 결과를 파싱하여 인용한 논문의 doi와 그 논문을 인용한 논문의 doi를 불러옵니다.
    # 그렇게 불러진 doi는 self.cited_dois와 self.citing_dois에 저장됩니다.
# 3. get_cited_dois(self): 인용한 논문의 doi를 반환합니다.
# 4. get_citing_dois(self): 인용한 논문의 doi를 반환합니다.
# 5. get_doi(self): 논문의 doi를 반환합니다.
# 6. get_cited_num(self): 인용한 논문의 수를 반환합니다.
# 7. get_citing_num(self): 인용한 논문의 수를 반환합니다.

import requests


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

def get_citing_papers(doi):
    url = f"https://opencitations.net/index/coci/api/v1/citations/{doi}"
    response = requests.get(url)
    citing_papers_list = []
    if response.status_code == 200:
        citations = response.json()
        for citation in citations:
            citing_doi = citation.get("citing")
            if citing_doi:
                citing_papers_list.append(citing_doi)
    else:
        print(f"Failed to retrieve citing papers for DOI {doi}: {response.status_code}")
    return citing_papers_list

def get_paper_citations(doi):
    paper_info = get_paper_info(doi)
    if paper_info:
        title = paper_info.get('title', [''])[0]
        authors = ', '.join([author['given'] + ' ' + author['family'] for author in paper_info.get('author', [])])
        year = paper_info.get('published-print', {}).get('date-parts', [[None]])[0][0]
        info = {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi
        }
    else:
        print(f"Failed to retrieve paper information for DOI {doi}.")
        return {}, [], []

    references = get_references(doi)
    citing_papers = get_citing_papers(doi)
    return info, references, citing_papers


class GraphNode:
    def __init__(self, doi):
        self.doi = doi
        self.info = {}
        self.references = []
        self.citing_dois = []
        self.update()
        
    def update(self):
        info, references, citing_papers = get_paper_citations(self.doi)
        self.info = info
        self.references = references
        self.citing_dois = citing_papers
    
    def get_references(self):
        return self.references
    
    def get_citing_dois(self):
        return self.citing_dois
    
    def get_doi(self):
        return self.doi
    
    def get_cited_num(self):
        return len(self.references)
    
    def get_citing_num(self):
        return len(self.citing_dois)

if __name__ == '__main__':
    doi  = '10.1038/s42005-020-0317-3'
    info, references, citing_papers = get_paper_citations(doi)
    print("Paper Info:", info)
    print("References:", references)
    print("Citing Papers:", citing_papers)