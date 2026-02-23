"""
출퇴근 시간 등고선 맵 - 그리드 생성
"""

import math


# 지구 반경 (km)
EARTH_RADIUS_KM = 6371.0


def haversine(lat1, lng1, lat2, lng2):
    """두 좌표 간 거리 (km)"""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def km_to_lat(km):
    """km를 위도 차이로 변환"""
    return km / (EARTH_RADIUS_KM * math.pi / 180)


def km_to_lng(km, lat):
    """km를 경도 차이로 변환 (위도에 따라 다름)"""
    return km / (EARTH_RADIUS_KM * math.cos(math.radians(lat)) * math.pi / 180)


def generate_grid(center_lat, center_lng, radius_km, step_km):
    """
    중심점 기준 원형 범위 내 그리드 포인트 생성

    Returns:
        dict with:
            - origin_lat: 그리드 좌하단 위도
            - origin_lng: 그리드 좌하단 경도
            - step_lat: 위도 간격
            - step_lng: 경도 간격
            - rows: 행 수
            - cols: 열 수
            - points: list of (row, col, lat, lng) - 원형 범위 내 포인트만
    """
    step_lat = km_to_lat(step_km)
    step_lng = km_to_lng(step_km, center_lat)

    # 반경을 그리드 스텝 수로 변환
    n_steps = int(math.ceil(radius_km / step_km))

    # 그리드 원점 (좌하단)
    origin_lat = center_lat - n_steps * step_lat
    origin_lng = center_lng - n_steps * step_lng

    rows = 2 * n_steps + 1
    cols = 2 * n_steps + 1

    points = []
    for r in range(rows):
        for c in range(cols):
            lat = origin_lat + r * step_lat
            lng = origin_lng + c * step_lng

            # 원형 범위 체크
            dist = haversine(center_lat, center_lng, lat, lng)
            if dist <= radius_km:
                points.append((r, c, lat, lng))

    return {
        "origin_lat": origin_lat,
        "origin_lng": origin_lng,
        "step_lat": step_lat,
        "step_lng": step_lng,
        "rows": rows,
        "cols": cols,
        "points": points,
    }


if __name__ == "__main__":
    # 테스트: 판교역 기준 그리드 생성
    grid = generate_grid(37.394894, 127.111304, 20, 2)
    print(f"그리드: {grid['rows']}x{grid['cols']}")
    print(f"포인트 수: {len(grid['points'])}")
    print(f"원점: ({grid['origin_lat']:.5f}, {grid['origin_lng']:.5f})")
    print(f"스텝: lat={grid['step_lat']:.5f}, lng={grid['step_lng']:.5f}")
