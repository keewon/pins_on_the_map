"""
출퇴근 시간 등고선 맵 - 데이터 수집 오케스트레이터
"""

import json
import time
from datetime import datetime, timedelta

from .config import (
    TARGETS, GRID_RADIUS_KM, GRID_STEP_KM, MAX_DURATION_MIN,
    DATA_DIR, get_target, slot_to_direction, check_api_key,
)
from .grid import generate_grid
from .api_kakao_car import get_car_duration


def get_next_weekday_date(slot):
    """
    다음 평일 날짜를 YYYYMMDD 형식으로 반환.
    future/directions API는 미래 시간만 허용하므로 적절한 날짜를 계산.
    """
    now = datetime.now()
    # 다음 평일 찾기 (월~금)
    target_date = now + timedelta(days=1)
    while target_date.weekday() >= 5:  # 5=토, 6=일
        target_date += timedelta(days=1)
    return target_date.strftime("%Y%m%d")


def collect_for_target(target_id, time_slot, date=None):
    """
    특정 타겟, 시간대에 대해 수집

    Args:
        target_id: 타겟 ID (예: "pangyo")
        time_slot: 시간 슬롯 (예: "0800")
        date: 날짜 (YYYYMMDD), None이면 다음 평일

    Returns:
        저장된 파일 경로 또는 None
    """
    target = get_target(target_id)
    if not target:
        print(f"오류: 타겟 '{target_id}'을 찾을 수 없습니다.")
        return None

    if not check_api_key():
        return None

    direction = slot_to_direction(time_slot)
    if date is None:
        date = get_next_weekday_date(time_slot)

    departure_time = f"{date}{time_slot}"

    print(f"수집 시작: {target['name']} ({target_id})")
    print(f"  시간: {time_slot} ({departure_time})")
    print(f"  방향: {'출근 (그리드→타겟)' if direction == 'to_target' else '퇴근 (타겟→그리드)'}")

    # 그리드 생성
    grid = generate_grid(target["lat"], target["lng"], GRID_RADIUS_KM, GRID_STEP_KM)
    points = grid["points"]
    print(f"  그리드: {grid['rows']}x{grid['cols']}, {len(points)}개 포인트")

    # 결과 2D 배열 초기화 (null)
    data = [[None for _ in range(grid["cols"])] for _ in range(grid["rows"])]

    # API 호출
    for i, (row, col, lat, lng) in enumerate(points, 1):
        if i % 50 == 0 or i == 1:
            print(f"  [{i}/{len(points)}] 처리 중...")

        if direction == "to_target":
            # 출근: 그리드포인트 → 타겟
            duration = get_car_duration(lat, lng, target["lat"], target["lng"], departure_time)
        else:
            # 퇴근: 타겟 → 그리드포인트
            duration = get_car_duration(target["lat"], target["lng"], lat, lng, departure_time)

        # MAX_DURATION_MIN 초과 시 None 처리
        if duration is not None and duration > MAX_DURATION_MIN:
            duration = None

        data[row][col] = duration
        time.sleep(0.1)  # rate limit

    # 저장
    result = {
        "target": target_id,
        "mode": "car",
        "time_slot": time_slot,
        "direction": direction,
        "departure_time": departure_time,
        "collected_at": datetime.now().isoformat(),
        "grid": {
            "center_lat": target["lat"],
            "center_lng": target["lng"],
            "origin_lat": grid["origin_lat"],
            "origin_lng": grid["origin_lng"],
            "step_lat": grid["step_lat"],
            "step_lng": grid["step_lng"],
            "rows": grid["rows"],
            "cols": grid["cols"],
        },
        "data": data,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / f"{target_id}_car_{time_slot}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    # 통계
    filled = sum(1 for row in data for val in row if val is not None)
    print(f"  완료: {filled}/{len(points)} 포인트에 데이터 ({output_path.name})")

    return output_path
