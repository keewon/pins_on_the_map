#!/usr/bin/env python3
"""
브랜드 매장 위치 수집 (카카오 API 사용)
"""

import sys
from common import fetch_all

# 브랜드별 설정
BRANDS = {
    'lotteria': {
        'id': 10,
        'name': '롯데리아',
        'keywords': ['롯데리아'],
    },
    'burgerking': {
        'id': 11,
        'name': '버거킹',
        'keywords': ['버거킹'],
    },
    'paris': {
        'id': 12,
        'name': '파리바게뜨',
        'keywords': ['파리바게뜨'],
    },
    'starbucks': {
        'id': 13,
        'name': '스타벅스',
        'keywords': ['스타벅스'],
    },
    'tous': {
        'id': 14,
        'name': '뚜레쥬르',
        'keywords': ['뚜레쥬르'],
    },
}


def make_filter(keywords):
    """브랜드 필터 함수 생성"""
    def filter_func(doc):
        name = doc.get("place_name", "")
        for keyword in keywords:
            if keyword in name:
                return True
        return False
    return filter_func


def fetch_brand(brand_key):
    """특정 브랜드 데이터 수집"""
    if brand_key not in BRANDS:
        print(f"❌ 알 수 없는 브랜드: {brand_key}")
        print(f"   사용 가능: {', '.join(BRANDS.keys())}")
        return
    
    brand = BRANDS[brand_key]
    fetch_all(
        name=brand['name'],
        keywords=brand['keywords'],
        list_id=brand['id'],
        filter_func=make_filter(brand['keywords'])
    )


def fetch_all_brands():
    """모든 브랜드 데이터 수집"""
    for brand_key in BRANDS:
        print(f"\n{'='*60}")
        fetch_brand(brand_key)
    print(f"\n{'='*60}")
    print("✅ 모든 브랜드 수집 완료!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        brand_key = sys.argv[1].lower()
        if brand_key == 'all':
            fetch_all_brands()
        else:
            fetch_brand(brand_key)
    else:
        print("사용법: python fetch_brand.py <brand>")
        print("  브랜드: lotteria, burgerking, paris, starbucks, tous, all")
        print("\n예시:")
        print("  python fetch_brand.py starbucks")
        print("  python fetch_brand.py all")
