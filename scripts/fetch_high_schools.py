#!/usr/bin/env python3
"""고등학교 위치 수집"""

from common import fetch_all, DETAILED_REGIONS

NAME = "고등학교"
LIST_ID = 9
KEYWORDS = ["고등학교"]


def filter_school(doc):
    """고등학교만 필터링 (교무실, 행정실 제외)"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    if "고등학교" not in name:
        return False
    if "교육" not in category and "학교" not in category:
        return False
    # 교무실, 행정실, 교장실, 별관, 체육관, 학생체육관 제외
    exclude = ["교무실", "행정실", "교장실", "별관", "체육관", "학생체육관"]
    if any(ex in name for ex in exclude):
        return False
    return True


if __name__ == "__main__":
    fetch_all(NAME, KEYWORDS, LIST_ID, filter_school, DETAILED_REGIONS)

