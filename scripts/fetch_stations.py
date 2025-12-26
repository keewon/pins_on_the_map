#!/usr/bin/env python3
"""지하철/국철역 위치 수집"""

import json
import os
import re
import math
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
    text = name + ' ' + category
    
    # 지역 호선 먼저 확인 (부산4호선, 대구3호선 등)
    regional_patterns = [
        (r'부산(\d)호선', '부산{}호선'),
        (r'대구(\d)호선', '대구{}호선'),
        (r'대전(\d)호선', '대전{}호선'),
        (r'광주(\d)호선', '광주{}호선'),
        (r'인천(\d)호선', '인천{}호선'),
    ]
    
    regional_line_nums = set()  # 지역 호선에서 사용된 번호 기록
    
    for pattern, format_str in regional_patterns:
        matches = re.findall(pattern, text)
        for num in matches:
            line_name = format_str.format(num)
            if line_name not in lines:
                lines.append(line_name)
                regional_line_nums.add(num)
    
    # 수도권 호선 (지역 호선에서 사용된 번호는 제외)
    for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        if f'{num}호선' in text and num not in regional_line_nums:
            line_name = f'{num}호선'
            if line_name not in lines:
                lines.append(line_name)
    
    # 기타 노선
    other_keywords = {
        '경의선': '경의중앙선', '중앙선': '경의중앙선', '경의중앙': '경의중앙선',
        '경춘선': '경춘선', '분당선': '분당선', '신분당선': '신분당선',
        '경강선': '경강선', '수인선': '수인분당선', '수인분당': '수인분당선',
        '공항철도': '공항철도', 'GTX': 'GTX-A', '신림선': '신림선', '우이신설': '우이신설선',
        '김포골드': '김포골드라인', '에버라인': '에버라인', '용인경전철': '에버라인',
        '의정부': '의정부경전철', '서해선': '서해선', '동해선': '동해선',
        '부산김해경전철': '부산김해경전철', '부산김해': '부산김해경전철',
    }
    
    for keyword, line_name in other_keywords.items():
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
        exclude = ['주차장', '화장실', '편의점', '보관함', '출입구', '환승', '대합실', '매표소', '출구']
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


def haversine_distance(lat1, lng1, lat2, lng2):
    """두 좌표 간 거리 계산 (km)"""
    R = 6371  # 지구 반경 (km)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def normalize_station_name(name):
    """역 이름에서 호선 정보 제거하여 정규화"""
    # "고촌역 김포골드라인" -> "고촌역"
    # "서울역 1호선" -> "서울역"
    patterns = [
        r'\s+(김포골드라인|에버라인|의정부경전철|신분당선|경의중앙선|공항철도|신림선|우이신설선|서해선|경춘선|경강선|분당선|수인분당선)',
        r'\s+(부산\d호선|대구\d호선|대전\d호선|광주\d호선|인천\d호선)',
        r'\s+\d호선',
        r'\s+GTX-?[A-Z]?',
        r'\s+동해선',
        r'\s+부산김해경전철',
    ]
    
    result = name
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    
    return result.strip()


def merge_transfer_stations(pins):
    """가까운 거리에 있는 같은 이름의 역을 환승역으로 병합"""
    MERGE_DISTANCE_KM = 0.5  # 500m 이내만 병합
    
    # 정규화된 이름으로 그룹화
    name_groups = {}
    for pin in pins:
        normalized = normalize_station_name(pin['title'])
        if normalized not in name_groups:
            name_groups[normalized] = []
        name_groups[normalized].append(pin)
    
    merged_pins = []
    
    for name, group in name_groups.items():
        if len(group) == 1:
            # 단일 역
            pin = group[0]
            pin['title'] = name  # 정규화된 이름 사용
            merged_pins.append(pin)
        else:
            # 여러 개의 같은 이름 역 - 거리 기반 클러스터링
            clusters = []
            
            for pin in group:
                added_to_cluster = False
                
                for cluster in clusters:
                    # 클러스터의 첫 번째 역과 거리 비교
                    dist = haversine_distance(
                        cluster[0]['lat'], cluster[0]['lng'],
                        pin['lat'], pin['lng']
                    )
                    
                    if dist < MERGE_DISTANCE_KM:
                        cluster.append(pin)
                        added_to_cluster = True
                        break
                
                if not added_to_cluster:
                    clusters.append([pin])
            
            # 각 클러스터를 하나의 역으로 병합
            for cluster in clusters:
                if len(cluster) == 1:
                    pin = cluster[0]
                    pin['title'] = name
                    merged_pins.append(pin)
                else:
                    # 환승역 - 노선 정보 합치기
                    all_lines = []
                    for pin in cluster:
                        if pin['description']:
                            for line in pin['description'].split(', '):
                                if line and line not in all_lines:
                                    all_lines.append(line)
                    
                    # 첫 번째 역 정보를 기준으로 병합
                    merged = cluster[0].copy()
                    merged['title'] = name
                    merged['description'] = ', '.join(all_lines)
                    merged_pins.append(merged)
    
    return merged_pins


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
    
    # 6. Merge transfer stations (within 500m)
    merged_pins = merge_transfer_stations(unique_pins)
    print(f"🔄 환승역 병합 후: {len(merged_pins)}개")
    
    # 7. Save
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', f'{LIST_ID}.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({"pins": merged_pins}, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {data_path} 저장 완료!")


if __name__ == "__main__":
    main()

