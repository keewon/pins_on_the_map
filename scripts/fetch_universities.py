#!/usr/bin/env python3
"""대학교 위치 수집"""

from common import fetch_all, DETAILED_REGIONS

NAME = "대학교"
LIST_ID = 24
KEYWORDS = ["대학교", "대학"]


def filter_university(doc):
    """대학교만 필터링 (본부/캠퍼스만)"""
    name = doc.get("place_name", "")
    category = doc.get("category_name", "")
    
    # 폐교 제외
    if "폐교" in name or "(폐교)" in name:
        return False
    
    # 와플대학 제외
    if "와플대학" in name:
        return False
    
    # 카테고리에 대학/학교가 포함되어야 함
    if "교육" not in category and "학교" not in category and "대학" not in category:
        return False
    
    # 이름에 대학교/대학이 포함되거나, 특수 케이스 (KAIST, POSTECH 등)
    has_university_keyword = "대학교" in name or "대학" in name
    is_special_case = any(keyword in name for keyword in ["KAIST", "POSTECH", "GIST", "UNIST", "DGIST", "예정"])
    
    if not (has_university_keyword or is_special_case):
        return False
    
    # 제외 키워드 (건물명, 병원, 기관 등)
    exclude_keywords = [
        "별관", "체육관", "학생체육관", "도서관", "기숙사", "연구소",
        "병원", "의원", "센터", "타워", "관", "호관", "건물",
        "교육원", "연수원", "학원", "SLP", "비전", "글로벌센터",
        "지역대학", "지점", "분원", "수련원", "수위실", "어린이집", "구장", "노인대학",
        "강당", "연구동", "공학동", "교습소", "교류원", "산학협력단", "총학생회", "교육장",
        "보건실", "강의동", "여행대학", "입시컨설팅", "분수대", "매점", "아트홀", "장학재단",
        "연습장", "게임장", "실습동"
    ]
    if any(ex in name for ex in exclude_keywords):
        return False
    
    # 사범대학 부속/부설 학교 제외
    if ("부속" in name or "부설" in name) and "학교" in name:
        return False
    
    # "캠퍼스"로 끝나는 것은 포함 (본부 캠퍼스)
    # 단, 건물명이 포함된 것은 제외
    if "캠퍼스" in name:
        # 캠퍼스 이름만 있는 것은 OK (예: "경기대학교 수원캠퍼스")
        # 하지만 건물명이 있으면 제외
        building_keywords = ["관", "타워", "센터", "건물", "호관"]
        if any(bk in name for bk in building_keywords):
            return False
    
    return True


if __name__ == "__main__":
    fetch_all(NAME, KEYWORDS, LIST_ID, filter_university, DETAILED_REGIONS)

