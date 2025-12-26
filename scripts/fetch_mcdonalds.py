#!/usr/bin/env python3
"""맥도날드 매장 위치 수집"""

from common import fetch_all

# 설정
NAME = "맥도날드"
LIST_ID = 2
KEYWORDS = ["맥도날드"]


def filter_mcdonalds(doc):
    """맥도날드 매장만 필터링"""
    name = doc.get("place_name", "")
    return "맥도날드" in name or "McDonald" in name


if __name__ == "__main__":
    fetch_all(
        name=NAME,
        keywords=KEYWORDS,
        list_id=LIST_ID,
        filter_func=filter_mcdonalds,
    )
