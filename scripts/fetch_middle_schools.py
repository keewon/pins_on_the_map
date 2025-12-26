#!/usr/bin/env python3
"""중학교 위치 수집"""

from common import fetch_all

# 설정
NAME = "중학교"
LIST_ID = 1
KEYWORDS = ["중학교"]


def filter_school(doc):
    """중학교만 필터링"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    # 중학교가 포함되어야 함
    if "중학교" not in name:
        return False
    
    # 교육 카테고리인지 확인
    if "교육" not in category and "학교" not in category:
        return False
    
    return True


if __name__ == "__main__":
    fetch_all(
        name=NAME,
        keywords=KEYWORDS,
        list_id=LIST_ID,
        filter_func=filter_school,
    )

