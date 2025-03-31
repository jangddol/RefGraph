# 개요

이 프로젝트는 논문간의 reference 관계를 graph3d로 보여주는 것을 목표로 하는 프로젝트입니다.
나중에는 문장과 reference의 제목을 embedding해서 분야까지 잘 갈라내는 것을 목표로 할 것입니다.

이 프로젝트는 다음과 같은 일을 하는 것을 목표로 합니다.

1. start_doi와 search_depth를 정합니다. start_doi는 내가 reference 찾기를 시작할 가장 최신 논문, search_depth는 iteration을 돌릴 횟수입니다.
2. 위의 정보를 가지고 reference tree를 만듭니다.
3. reference tree를 만들고 나면, 기존에 저장해놓은 journal data로부터 제목, journal, 출판연도를 가지고 옵니다.
4. 이를 바탕으로 DiGraph 객체를 만들고, 보여줍니다.


# 사용법

1. start_doi가 있는 journal의 이름을 가지고 "journalsearcher.py"로 가서, 대응되는 issn을 찾습니다.
2. "journalpaperdatamaker.py"로 가서 해당 저널의 논문 정보들을 받습니다. 저널 한개당 1.4초가 걸립니다.
3. journal을 받고 나면 "makeissndoidict.py"를 돌려서 issn_doi_dict.json를 업데이트 해주고, "issnjournalnamedict.py"를 업데이트 해줍니다.
3. 미리 받아진 journal 정보를 바탕으로 "refgraphmaker.py"로 가서 reference tree가 담긴 json을 만듭니다.
4. 해당 json을 "findpopularjournalfromgraph.py"에 넣고, 다음에 논문 정보를 받을 journal을 선정합니다. 다시 2번으로 갑니다.
5. 어느정도 만족할만큼 journal 정보를 받았다면 "graphvisualizer.py"로 가서 visualizing을 합니다.
