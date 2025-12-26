#!/usr/bin/env python3
"""유명 브랜드 아파트 단지 수집"""

import json
import os
import sys
import time
sys.path.append(os.path.dirname(__file__))

from common import check_api_key, fetch_places_in_region, remove_duplicates, convert_to_pins, save_pins, save_raw_data, DETAILED_REGIONS
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 브랜드별 설정
APARTMENT_BRANDS = [
    {
        'name': '래미안',
        'keywords': ['래미안'],
        'list_id': 15,
        'color': '#1428A0',  # 삼성 파란색
    },
    {
        'name': '아이파크',
        'keywords': ['아이파크'],
        'list_id': 16,
        'color': '#E31837',  # 현대 빨간색
    },
    {
        'name': '자이',
        'keywords': ['자이 아파트', 'GS자이'],  # 더 구체적인 키워드
        'list_id': 17,
        'color': '#FF6600',  # GS 주황색
    },
    {
        'name': '푸르지오',
        'keywords': ['푸르지오'],
        'list_id': 18,
        'color': '#00A651',  # 대우 녹색
    },
    {
        'name': '이편한세상',
        'keywords': ['이편한세상', 'e편한세상'],
        'list_id': 19,
        'color': '#0072BC',  # DL이앤씨 파란색
    },
    {
        'name': '힐스테이트',
        'keywords': ['힐스테이트'],
        'list_id': 20,
        'color': '#003366',  # 현대건설 네이비
    },
    {
        'name': '롯데캐슬',
        'keywords': ['롯데캐슬'],
        'list_id': 21,
        'color': '#C8102E',  # 롯데 빨간색
    },
    {
        'name': '위브',
        'keywords': ['위브 아파트', '위브아파트'],
        'list_id': 22,
        'color': '#7B2D8E',  # 두산 보라색
    },
    {
        'name': '더샵',
        'keywords': ['더샵'],
        'list_id': 23,
        'color': '#005BAC',  # 포스코 파란색
    },
]


def create_apartment_filter(brand_name):
    """브랜드별 아파트 필터 함수 생성"""
    # 이편한세상은 e편한세상도 허용
    if brand_name == '이편한세상':
        brand_variants = ['이편한세상', 'e편한세상']
    else:
        brand_variants = [brand_name]
    
    def filter_func(doc):
        name = doc.get('place_name', '')
        category = doc.get('category_name', '')
        
        # 카테고리에 '아파트'가 포함되어야 함
        if '아파트' not in category:
            return False
        
        # 브랜드 이름이 포함되어야 함
        if not any(variant in name for variant in brand_variants):
            return False
        
        # 상가동 제외
        if '상가동' in name:
            return False
        
        return True
    
    return filter_func


def fetch_brand(brand):
    """단일 브랜드 아파트 수집"""
    brand_name = brand['name']
    keywords = brand['keywords']
    list_id = brand['list_id']
    
    print(f"\n🏢 {brand_name} 아파트 수집 시작...")
    print(f"   검색 키워드: {', '.join(keywords)}")
    print(f"   검색 지역 수: {len(DETAILED_REGIONS)}개")
    print()
    
    filter_func = create_apartment_filter(brand_name)
    all_places = []
    
    for i, region in enumerate(DETAILED_REGIONS, 1):
        print(f"[{i}/{len(DETAILED_REGIONS)}] {region} 검색 중...", end=" ")
        places = fetch_places_in_region(region, keywords, filter_func)
        print(f"→ {len(places)}개")
        all_places.extend(places)
        time.sleep(0.1)  # Rate limit
    
    # 중복 제거
    unique_places = remove_duplicates(all_places)
    print()
    print(f"✅ 총 {len(unique_places)}개 {brand_name} 아파트 수집 완료")
    
    # 핀 형식으로 변환 및 저장
    pins = convert_to_pins(unique_places)
    save_pins(pins, list_id)
    
    # 원본 데이터 백업
    save_raw_data(unique_places, f"{brand_name}_raw.json")
    
    return len(unique_places)


def main():
    if not check_api_key():
        return
    
    results = {}
    
    for brand in APARTMENT_BRANDS:
        count = fetch_brand(brand)
        results[brand['name']] = count
    
    print("\n" + "=" * 50)
    print("📊 수집 결과 요약:")
    for name, count in results.items():
        print(f"   {name}: {count}개")
    
    print("\n📋 lists.json 업데이트가 필요합니다!")
    print("다음 항목을 추가해주세요:")
    for brand in APARTMENT_BRANDS:
        print(f'  - {brand["list_id"]}: {brand["name"]} (색상: {brand["color"]})')


if __name__ == "__main__":
    main()
