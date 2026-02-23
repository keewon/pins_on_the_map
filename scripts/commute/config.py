"""
출퇴근 시간 등고선 맵 - 설정
"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

KAKAO_API_KEY = os.environ.get("KAKAO_API_KEY", "")

TARGETS = [
    {"id": "yeoksam", "name": "역삼역", "lat": 37.500622, "lng": 127.036456},
    {"id": "pangyo", "name": "판교역", "lat": 37.394894, "lng": 127.111304},
    {"id": "euljiro", "name": "을지로입구역", "lat": 37.566014, "lng": 126.982160},
    {"id": "yeouido", "name": "여의도역", "lat": 37.521624, "lng": 126.924191},
    {"id": "gasan", "name": "가산디지털단지", "lat": 37.481426, "lng": 126.882882},
    {"id": "pangyo2", "name": "제2판교테크노밸리", "lat": 37.381300, "lng": 127.115202},
    {"id": "jamsil", "name": "잠실역", "lat": 37.513280, "lng": 127.100070},
    {"id": "seongsu", "name": "성수역", "lat": 37.544580, "lng": 127.055990},
]

GRID_RADIUS_KM = 20
GRID_STEP_KM = 2
MAX_DURATION_MIN = 90

MORNING_SLOTS = ["0600", "0630", "0700", "0730", "0800", "0830", "0900", "0930", "1000"]
EVENING_SLOTS = ["1700", "1730", "1800", "1830", "1900", "1930", "2000"]
ALL_SLOTS = MORNING_SLOTS + EVENING_SLOTS

DATA_DIR = PROJECT_ROOT / "data" / "commute"


def get_target(target_id):
    """타겟 ID로 타겟 정보 반환"""
    for t in TARGETS:
        if t["id"] == target_id:
            return t
    return None


def check_api_key():
    """API 키 확인"""
    if not KAKAO_API_KEY:
        print("오류: KAKAO_API_KEY가 설정되지 않았습니다.")
        print("  .env 파일에 KAKAO_API_KEY=발급받은키 를 추가하세요.")
        return False
    return True


def slot_to_direction(slot):
    """시간 슬롯으로 방향 결정: 오전=출근(to_target), 오후=퇴근(from_target)"""
    hour = int(slot[:2])
    if hour < 12:
        return "to_target"
    else:
        return "from_target"
