"""
이 모듈은 CrossRef API를 사용하여 저널 이름으로 검색하는 기능을 제공합니다.
함수:
    - search_journal_by_name: 저널 이름으로 검색하여 제목 및 ISSN과 같은 정보를 가져옵니다.
사용 예시:
    모듈을 직접 실행하여 특정 저널 이름으로 검색하고 결과를 표시할 수 있습니다.
    예시:
        python journalsearcher.py
의존성:
    - requests: CrossRef API에 HTTP 요청을 보내는 데 사용됩니다.
참고:
    CrossRef API를 사용하려면 인터넷 연결이 필요합니다.

"""
import requests

def search_journal_by_name(_journal_name, _rows=10):
    """
    CrossRef API를 사용하여 저널 이름으로 검색합니다.

    매개변수:
        journal_name (str): 검색할 저널의 이름.
        rows (int, 선택적): 검색 결과의 개수. 기본값은 10.

    반환값:
        list: 저널 정보(예: 제목, ISSN)를 포함하는 딕셔너리의 리스트.
    """
    url = "https://api.crossref.org/journals"
    params = {
        'query': _journal_name,
        'rows': _rows
    }
    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"저널 {_journal_name} 검색 중 오류 발생: {response.status_code}")
        return []

    items = response.json().get('message', {}).get('items', [])
    for item in items:
        print(f"저널 이름: {item.get('title')}, ISSN: {item.get('ISSN')}")
    return items

# Nature Nanotechnology: 7
# Applied Physics Letters: 3
# Physical Review Letters: 2
# Review of Scientific Instruments: 2

if __name__ == '__main__':
    JOURNAL_NAME = 'Nature Nanotechnology'  # 예시 저널 이름
    ROWS = 20  # 예시 검색 결과 개수
    search_journal_by_name(JOURNAL_NAME, ROWS)
