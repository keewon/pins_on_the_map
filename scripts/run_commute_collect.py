#!/usr/bin/env python3
"""
출퇴근 시간 수집 CLI

사용법:
    python scripts/run_commute_collect.py --target pangyo --time 0800
    python scripts/run_commute_collect.py --target pangyo --time all
    python scripts/run_commute_collect.py --target all --time all
    python scripts/run_commute_collect.py --target pangyo --time now
    python scripts/run_commute_collect.py --target pangyo --time 0800 --date 20260225
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.commute.config import TARGETS, ALL_SLOTS, check_api_key
from scripts.commute.collector import collect_for_target, get_next_weekday_date
from scripts.commute.meta import update_meta


def get_current_slot():
    """현재 시간에 가장 가까운 슬롯 반환"""
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    for slot in ALL_SLOTS:
        slot_minutes = int(slot[:2]) * 60 + int(slot[2:])
        if abs(current_minutes - slot_minutes) <= 15:
            return slot
    # 가장 가까운 슬롯 찾기
    best = min(ALL_SLOTS, key=lambda s: abs(current_minutes - (int(s[:2]) * 60 + int(s[2:]))))
    return best


def main():
    parser = argparse.ArgumentParser(description="출퇴근 시간 데이터 수집")
    parser.add_argument("--target", required=True, help="타겟 ID (예: pangyo) 또는 'all'")
    parser.add_argument("--time", required=True, help="시간 슬롯 (예: 0800), 'all', 또는 'now'")
    parser.add_argument("--date", default=None, help="날짜 (YYYYMMDD), 기본: 다음 평일")
    args = parser.parse_args()

    if not check_api_key():
        sys.exit(1)

    # 타겟 리스트
    if args.target == "all":
        targets = [t["id"] for t in TARGETS]
    else:
        targets = [args.target]

    # 시간 슬롯 리스트
    if args.time == "all":
        slots = ALL_SLOTS
    elif args.time == "now":
        slots = [get_current_slot()]
        print(f"현재 시간 기준 슬롯: {slots[0]}")
    else:
        slots = [args.time]

    date = args.date

    total = len(targets) * len(slots)
    done = 0

    print(f"=== 출퇴근 시간 데이터 수집 ===")
    print(f"타겟: {', '.join(targets)}")
    print(f"시간: {', '.join(slots)}")
    if date:
        print(f"날짜: {date}")
    else:
        print(f"날짜: 다음 평일 ({get_next_weekday_date(slots[0])})")
    print(f"총 {total}건 수집 예정")
    print()

    for target_id in targets:
        for slot in slots:
            done += 1
            print(f"--- [{done}/{total}] {target_id} / {slot} ---")
            result = collect_for_target(target_id, slot, date)
            if result:
                print(f"  저장: {result}")
            else:
                print(f"  실패!")
            print()

    # 메타데이터 업데이트
    update_meta()
    print("=== 완료 ===")


if __name__ == "__main__":
    main()
