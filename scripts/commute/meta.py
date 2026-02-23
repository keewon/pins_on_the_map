"""
출퇴근 시간 등고선 맵 - 메타데이터 관리
"""

import json
from datetime import datetime
from pathlib import Path

from .config import TARGETS, MORNING_SLOTS, EVENING_SLOTS, GRID_STEP_KM, DATA_DIR


def update_meta():
    """메타데이터 JSON 업데이트 (수집된 파일 기반)"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 수집된 파일 스캔
    collected = {}
    for f in DATA_DIR.glob("*_car_*.json"):
        if f.name == "meta.json":
            continue
        # 파일명: {target_id}_car_{slot}.json
        parts = f.stem.split("_car_")
        if len(parts) == 2:
            target_id, slot = parts
            if target_id not in collected:
                collected[target_id] = []
            collected[target_id].append(slot)

    # 정렬
    for target_id in collected:
        collected[target_id].sort()

    meta = {
        "targets": TARGETS,
        "modes": ["car"],
        "morning_slots": MORNING_SLOTS,
        "evening_slots": EVENING_SLOTS,
        "grid_step_km": GRID_STEP_KM,
        "collected": collected,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }

    meta_path = DATA_DIR / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"메타데이터 업데이트: {meta_path}")
    return meta_path
