#!/usr/bin/env python3
"""지하철/국철역 위치 수집"""

import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

NAME = "지하철역"
LIST_ID = 6
API_KEY = os.environ.get('KAKAO_API_KEY')

# 검색 쿼리 목록 (지역 + 호선별로 세분화)
SEARCH_QUERIES = [
    # 수도권 호선별
    "서울 1호선", "서울 2호선", "서울 3호선", "서울 4호선",
    "서울 5호선", "서울 6호선", "서울 7호선", "서울 8호선", "서울 9호선",
    "경의중앙선", "분당선", "신분당선", "경춘선", "경강선", "서해선",
    "수인분당선", "공항철도", "신림선", "우이신설선",
    "김포골드라인", "에버라인", "의정부경전철",
    # 인천
    "인천 1호선", "인천 2호선", "인천지하철",
    # 부산
    "부산 1호선", "부산 2호선", "부산 3호선", "부산 4호선", "부산지하철",
    "동해선 전철", "부산김해경전철",
    # 대구
    "대구 1호선", "대구 2호선", "대구 3호선", "대구지하철",
    # 대전/광주
    "대전 1호선", "대전지하철", "광주 1호선", "광주지하철",
    # 일반 검색
    "지하철역", "전철역",
]


def fetch_stations():
    """지하철역 검색"""
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    headers = {'Authorization': f'KakaoAK {API_KEY}'}
    
    all_results = []
    seen_ids = set()
    
    for query in SEARCH_QUERIES:
        page = 1
        
        while page <= 45:  # max 45 pages
            params = {'query': query, 'size': 15, 'page': page}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            for doc in data.get('documents', []):
                if doc['id'] not in seen_ids:
                    seen_ids.add(doc['id'])
                    all_results.append(doc)
            
            if data.get('meta', {}).get('is_end', True):
                break
            page += 1
        
        print(f"  {query}: {len(seen_ids)}개 누적")
    
    return all_results


def extract_lines(name, category):
    """역 이름이나 카테고리에서 호선 정보 추출"""
    lines = []
    
    # 카테고리에서 추출 (예: "교통,수송 > 지하철,전철 > 수도권1호선")
    if '호선' in category:
        match = re.search(r'(\d+호선)', category)
        if match:
            lines.append(match.group(1))
    
    # 노선 이름 매핑
    line_keywords = {
        '1호선': '1호선', '2호선': '2호선', '3호선': '3호선', '4호선': '4호선',
        '5호선': '5호선', '6호선': '6호선', '7호선': '7호선', '8호선': '8호선',
        '9호선': '9호선',
        '경의선': '경의중앙선', '중앙선': '경의중앙선', '경의중앙': '경의중앙선',
        '경춘선': '경춘선', '분당선': '분당선', '신분당선': '신분당선',
        '경강선': '경강선', '수인선': '수인분당선', '수인분당': '수인분당선',
        '공항철도': '공항철도', '인천1호선': '인천1호선', '인천2호선': '인천2호선',
        'GTX': 'GTX-A', '신림선': '신림선', '우이신설': '우이신설선',
        '김포골드': '김포골드라인', '에버라인': '에버라인', '용인경전철': '에버라인',
        '의정부': '의정부경전철', '서해선': '서해선',
        '부산1호선': '부산1호선', '부산2호선': '부산2호선', '부산3호선': '부산3호선', '부산4호선': '부산4호선',
        '대구1호선': '대구1호선', '대구2호선': '대구2호선', '대구3호선': '대구3호선',
        '대전1호선': '대전1호선', '광주1호선': '광주1호선',
        'KTX': 'KTX', 'SRT': 'SRT', '새마을': '일반철도', '무궁화': '일반철도',
    }
    
    text = name + ' ' + category
    for keyword, line_name in line_keywords.items():
        if keyword in text and line_name not in lines:
            lines.append(line_name)
    
    return lines


def filter_station(doc):
    """지하철/전철역만 필터링"""
    name = doc.get('place_name', '')
    category = doc.get('category_name', '')
    
    # 지하철/전철 카테고리인 경우
    if '지하철' in category or '전철' in category:
        # 제외 키워드
        exclude = ['주차장', '화장실', '편의점', '보관함', '출입구', '환승', '대합실', '매표소']
        for ex in exclude:
            if ex in name:
                return False
        return True
    
    # 역 이름으로 끝나는 경우
    if name.endswith('역') and ('교통' in category or '철도' in category):
        return True
    
    return False


def get_region(doc):
    """주소에서 광역단체 추출"""
    addr = doc.get('road_address_name') or doc.get('address_name') or ''
    parts = addr.split()
    return parts[0] if parts else '기타'


def convert_to_pins(docs):
    """카카오 API 결과를 핀 데이터로 변환"""
    pins = []
    
    for doc in docs:
        name = doc.get('place_name', '')
        category = doc.get('category_name', '')
        lines = extract_lines(name, category)
        
        description = ', '.join(lines) if lines else ''
        
        pins.append({
            "title": name,
            "lat": float(doc.get('y')),
            "lng": float(doc.get('x')),
            "address": doc.get('road_address_name') or doc.get('address_name'),
            "description": description,
            "url": doc.get('place_url'),
            "region": get_region(doc)
        })
    
    return pins


def main():
    print(f"🚇 {NAME} 데이터 수집 시작...")
    
    # 1. Fetch
    raw = fetch_stations()
    print(f"📥 검색 결과: {len(raw)}개")
    
    # 2. Save raw
    raw_path = os.path.join(os.path.dirname(__file__), f'{NAME}_raw.json')
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    
    # 3. Filter
    filtered = [doc for doc in raw if filter_station(doc)]
    print(f"🔍 필터링 후: {len(filtered)}개")
    
    # 4. Convert to pins
    pins = convert_to_pins(filtered)
    
    # 5. Remove duplicates by title + address
    seen = set()
    unique_pins = []
    for pin in pins:
        key = (pin['title'], pin['address'])
        if key not in seen:
            seen.add(key)
            unique_pins.append(pin)
    
    print(f"✨ 중복 제거 후: {len(unique_pins)}개")
    
    # 6. Save
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', f'{LIST_ID}.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({"pins": unique_pins}, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {data_path} 저장 완료!")


if __name__ == "__main__":
    main()

