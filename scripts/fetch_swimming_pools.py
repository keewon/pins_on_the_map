#!/usr/bin/env python3
"""공공수영장 위치 수집"""

from common import fetch_all, DETAILED_REGIONS

NAME = "공공수영장"
LIST_ID = 5
KEYWORDS = [
    "공공수영장",
    "시민수영장",
    "구민수영장",
    "군민수영장",
    "국민체육센터 수영장",
    "종합체육관 수영장",
    "올림픽수영장",
    "곰두리체육센터",
    "곰두리스포츠센터",
    "장애인체육관 수영장",
]

# 수영장이 있는 것으로 알려진 체육센터 (이름에 "수영"이 없어도 포함)
KNOWN_POOL_CENTERS = [
    "곰두리체육센터",
    "곰두리스포츠센터",
    "곰두리국민체육센터",
]


def filter_pool(doc):
    """공공수영장만 필터링"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    # 알려진 수영장 보유 체육센터는 무조건 포함
    for center in KNOWN_POOL_CENTERS:
        if center in name:
            return True
    
    if "수영" not in name and "수영" not in category:
        return False
    
    # 제외 키워드 (사설 수영장, 호텔, 부대시설 등)
    exclude = ["호텔", "리조트", "콘도", "아파트", "빌라", "학원", "레슨", "주차장", "화장실"]
    for ex in exclude:
        if ex in name:
            return False
    return True


if __name__ == "__main__":
    fetch_all(NAME, KEYWORDS, LIST_ID, filter_pool, DETAILED_REGIONS)
