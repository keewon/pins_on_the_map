#!/usr/bin/env python3
"""중학교 위치 수집"""

from common import fetch_all, DETAILED_REGIONS

NAME = "중학교"
LIST_ID = 1
KEYWORDS = ["중학교"]


def filter_school(doc):
    """중학교만 필터링 ('학교'로 끝나는 것만)"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    if "중학교" not in name:
        return False
    if "교육" not in category and "학교" not in category:
        return False
    # '학교'로 끝나지 않으면 제외 (건물명, 휴교/폐교/예정 등)
    if not name.endswith("학교"):
        return False
    return True


if __name__ == "__main__":
    fetch_all(NAME, KEYWORDS, LIST_ID, filter_school, DETAILED_REGIONS)

