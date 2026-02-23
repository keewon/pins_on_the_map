"""
출퇴근 시간 등고선 맵 - 카카오 자동차 경로 API 래퍼
엔드포인트: https://apis-navi.kakaomobility.com/v1/future/directions
"""

import time
import requests

from .config import KAKAO_API_KEY

API_URL = "https://apis-navi.kakaomobility.com/v1/future/directions"


def get_car_duration(origin_lat, origin_lng, dest_lat, dest_lng, departure_time):
    """
    자동차 경로 소요시간 조회 (future/directions)

    Args:
        origin_lat, origin_lng: 출발지 좌표
        dest_lat, dest_lng: 도착지 좌표
        departure_time: 출발시간 (YYYYMMDDHHMM 형식, 예: "202602240800")

    Returns:
        소요시간(분) 또는 None (경로 없음/에러)
    """
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "Content-Type": "application/json",
    }

    # 카카오 API는 lng,lat 순서
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        "departure_time": departure_time,
        "priority": "RECOMMEND",
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 404:
            # 경로를 찾을 수 없음
            return None

        response.raise_for_status()
        data = response.json()

        # routes 배열에서 결과 확인
        routes = data.get("routes", [])
        if not routes:
            return None

        # result_code는 routes[0] 안에 있음
        result_code = routes[0].get("result_code", -1)
        if result_code != 0:
            return None

        summary = routes[0].get("summary", {})
        duration_sec = summary.get("duration", 0)

        if duration_sec <= 0:
            return None

        return round(duration_sec / 60)

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            print(f"  API 호출 한도 초과, 1초 대기 후 재시도...")
            time.sleep(1)
            return get_car_duration(origin_lat, origin_lng, dest_lat, dest_lng, departure_time)
        print(f"  HTTP 오류: {e}")
        return None
    except Exception as e:
        print(f"  API 오류: {e}")
        return None
