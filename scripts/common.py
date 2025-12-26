"""
공통 유틸리티 모듈
카카오맵 API를 사용한 장소 데이터 수집을 위한 공통 기능
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# .env 파일 로드
load_dotenv(PROJECT_ROOT / ".env")

# 카카오 REST API 키
API_KEY = os.environ.get("KAKAO_API_KEY", "")

# 광역자치단체 목록 (기본)
REGIONS = [
    "서울특별시",
    "부산광역시",
    "대구광역시",
    "인천광역시",
    "광주광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "경기도",
    "강원특별자치도",
    "충청북도",
    "충청남도",
    "전북특별자치도",
    "전라남도",
    "경상북도",
    "경상남도",
    "제주특별자치도",
]

# 광역단체 매핑 (주소에서 추출용)
REGION_MAP = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "세종특별자치시": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "강원특별자치도": "강원특별자치도",
    "충북": "충청북도",
    "충청북도": "충청북도",
    "충남": "충청남도",
    "충청남도": "충청남도",
    "전북": "전북특별자치도",
    "전북특별자치도": "전북특별자치도",
    "전남": "전라남도",
    "전라남도": "전라남도",
    "경북": "경상북도",
    "경상북도": "경상북도",
    "경남": "경상남도",
    "경상남도": "경상남도",
    "제주": "제주특별자치도",
    "제주특별자치도": "제주특별자치도",
}

# 세분화된 지역 목록 (API 45개 제한 우회용)
DETAILED_REGIONS = [
    # 서울 25개 구
    "서울 강남구", "서울 강동구", "서울 강북구", "서울 강서구", "서울 관악구",
    "서울 광진구", "서울 구로구", "서울 금천구", "서울 노원구", "서울 도봉구",
    "서울 동대문구", "서울 동작구", "서울 마포구", "서울 서대문구", "서울 서초구",
    "서울 성동구", "서울 성북구", "서울 송파구", "서울 양천구", "서울 영등포구",
    "서울 용산구", "서울 은평구", "서울 종로구", "서울 중구", "서울 중랑구",
    # 경기도 시/군 (31개)
    "경기 수원시", "경기 성남시", "경기 고양시", "경기 용인시", "경기 부천시",
    "경기 안산시", "경기 안양시", "경기 남양주시", "경기 화성시", "경기 평택시",
    "경기 의정부시", "경기 시흥시", "경기 파주시", "경기 광명시", "경기 김포시",
    "경기 군포시", "경기 광주시", "경기 이천시", "경기 양주시", "경기 오산시",
    "경기 구리시", "경기 안성시", "경기 포천시", "경기 의왕시", "경기 하남시",
    "경기 여주시", "경기 동두천시", "경기 과천시",
    "경기 양평군", "경기 가평군", "경기 연천군",  # 군 추가
    # 인천 구/군 (10개)
    "인천 중구", "인천 동구", "인천 미추홀구", "인천 연수구",
    "인천 남동구", "인천 부평구", "인천 계양구", "인천 서구",
    "인천 강화군", "인천 옹진군",  # 군 추가
    # 부산 구/군 (16개)
    "부산 중구", "부산 서구", "부산 동구", "부산 영도구", "부산 부산진구",
    "부산 동래구", "부산 남구", "부산 북구", "부산 해운대구", "부산 사하구",
    "부산 금정구", "부산 강서구", "부산 연제구", "부산 수영구", "부산 사상구",
    "부산 기장군",  # 군 추가
    # 나머지 광역시/도
    "대구광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시",
    "강원특별자치도", "충청북도", "충청남도",
    "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도",
]


def check_api_key():
    """API 키 확인"""
    if not API_KEY:
        print("❌ 오류: KAKAO_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 KAKAO_API_KEY=발급받은키 를 추가하세요.")
        return False
    return True


def search_keyword(query: str, page: int = 1) -> dict:
    """카카오 키워드 검색 API 호출"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {API_KEY}"}
    params = {
        "query": query,
        "page": page,
        "size": 15,
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def fetch_places_in_region(region: str, keywords: list, filter_func=None) -> list:
    """
    특정 지역에서 장소 검색
    
    Args:
        region: 검색할 지역
        keywords: 검색 키워드 리스트
        filter_func: 결과 필터링 함수 (doc -> bool)
    
    Returns:
        검색된 장소 리스트
    """
    results = []
    
    for keyword in keywords:
        query = f"{region} {keyword}"
        
        for page in range(1, 4):  # 최대 3페이지 (45개)
            try:
                data = search_keyword(query, page)
                documents = data.get("documents", [])
                
                if not documents:
                    break
                
                for doc in documents:
                    # 필터 함수가 있으면 적용
                    if filter_func and not filter_func(doc):
                        continue
                    
                    results.append({
                        "id": doc.get("id"),
                        "name": doc.get("place_name", ""),
                        "address": doc.get("address_name", ""),
                        "road_address": doc.get("road_address_name", ""),
                        "lat": float(doc.get("y", 0)),
                        "lng": float(doc.get("x", 0)),
                        "phone": doc.get("phone", ""),
                        "url": doc.get("place_url", ""),
                        "category": doc.get("category_name", ""),
                    })
                
                if data.get("meta", {}).get("is_end", True):
                    break
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  오류 발생 ({query}, page {page}): {e}")
                break
        
        time.sleep(0.1)
    
    return results


def remove_duplicates(places: list) -> list:
    """중복 제거 (카카오 place id 기준)"""
    seen = set()
    unique = []
    
    for place in places:
        place_id = place.get("id")
        if place_id and place_id not in seen:
            seen.add(place_id)
            unique.append(place)
    
    return unique


def extract_region(address: str) -> str:
    """주소에서 광역단체 추출"""
    if not address:
        return "기타"
    
    # 주소의 첫 부분 추출
    parts = address.split()
    if not parts:
        return "기타"
    
    first_part = parts[0]
    
    # REGION_MAP에서 매핑 찾기
    for key, value in REGION_MAP.items():
        if first_part.startswith(key):
            return value
    
    return "기타"


def convert_to_pins(places: list) -> list:
    """핀 데이터 형식으로 변환"""
    return [
        {
            "lat": place["lat"],
            "lng": place["lng"],
            "title": place["name"],
            "description": place["road_address"] or place["address"],
            "url": place.get("url", ""),  # 카카오맵 URL
            "region": extract_region(place["road_address"] or place["address"])
        }
        for place in places
    ]


def save_pins(pins: list, list_id: int):
    """핀 데이터를 JSON 파일로 저장"""
    output_path = PROJECT_ROOT / "data" / f"{list_id}.json"
    output_data = {"pins": pins}
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 저장 완료: {output_path}")
    return output_path


def save_raw_data(places: list, filename: str):
    """원본 데이터 백업"""
    backup_path = Path(__file__).parent / filename
    
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    print(f"📋 원본 데이터 백업: {backup_path}")
    return backup_path


def fetch_all(name: str, keywords: list, list_id: int, filter_func=None, regions=None):
    """
    장소 데이터 수집 메인 함수
    
    Args:
        name: 수집 대상 이름 (출력용)
        keywords: 검색 키워드 리스트
        list_id: 저장할 리스트 ID (data/{list_id}.json)
        filter_func: 결과 필터링 함수
        regions: 검색할 지역 리스트 (기본: 전국)
    """
    if not check_api_key():
        return
    
    search_regions = regions or REGIONS
    
    print(f"🔍 {name} 위치 수집 시작...")
    print(f"   검색할 지역 수: {len(search_regions)}개")
    print(f"   검색 키워드: {', '.join(keywords)}")
    print()
    
    all_places = []
    
    for i, region in enumerate(search_regions, 1):
        print(f"[{i}/{len(search_regions)}] {region} 검색 중...")
        places = fetch_places_in_region(region, keywords, filter_func)
        print(f"         → {len(places)}개 발견")
        all_places.extend(places)
        time.sleep(0.2)
    
    # 중복 제거
    unique_places = remove_duplicates(all_places)
    print()
    print(f"✅ 총 {len(unique_places)}개 {name} 수집 완료 (중복 제거 후)")
    
    # 핀 형식으로 변환 및 저장
    pins = convert_to_pins(unique_places)
    save_pins(pins, list_id)
    
    # 원본 데이터 백업
    raw_filename = f"{name.lower().replace(' ', '_')}_raw.json"
    save_raw_data(unique_places, raw_filename)
    
    return unique_places

