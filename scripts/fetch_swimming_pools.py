#!/usr/bin/env python3
"""공공수영장 위치 수집"""

from common import fetch_all

# 설정
NAME = "공공수영장"
LIST_ID = 5
KEYWORDS = [
    "공공수영장",
    "시민수영장",
    "구민수영장",
    "군민수영장",
    "국민체육센터 수영장",
    "종합체육관 수영장",
]


def filter_pool(doc):
    """공공수영장만 필터링"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    # 수영 관련 키워드 포함
    if "수영" not in name and "수영" not in category:
        return False
    
    # 제외 키워드 (사설 수영장, 호텔 등)
    exclude = ["호텔", "리조트", "콘도", "아파트", "빌라", "학원", "레슨"]
    for ex in exclude:
        if ex in name:
            return False
    
    return True


if __name__ == "__main__":
    fetch_all(
        name=NAME,
        keywords=KEYWORDS,
        list_id=LIST_ID,
        filter_func=filter_pool,
    )
