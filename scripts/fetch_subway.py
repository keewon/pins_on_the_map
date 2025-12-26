#!/usr/bin/env python3
"""써브웨이 매장 위치 수집"""

from common import fetch_all

# 설정
NAME = "써브웨이"
LIST_ID = 3
KEYWORDS = ["써브웨이"]  # 카카오맵에서는 "써브웨이"로 표기됨


def filter_subway(doc):
    """써브웨이 매장만 필터링"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    # 써브웨이/서브웨이가 이름에 포함되어야 함
    if "써브웨이" not in name and "서브웨이" not in name and "SUBWAY" not in name.upper():
        return False
    
    # 지하철역 제외
    if "지하철" in category:
        return False
    
    return True


if __name__ == "__main__":
    fetch_all(
        name=NAME,
        keywords=KEYWORDS,
        list_id=LIST_ID,
        filter_func=filter_subway,
    )

