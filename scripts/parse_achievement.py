#!/usr/bin/env python3
"""
송파구 중학교 학업성취도 XLS(HTML) 파일을 파싱하여 data/1.json에 achievement 필드를 추가하는 스크립트.

Usage:
    python3 scripts/parse_achievement.py
"""

import json
import glob
import os
import unicodedata
from bs4 import BeautifulSoup

# XLS 파일명 축약 → 1.json title 매핑
NAME_MAP = {
    "잠실여중": "잠실여자중학교",
    "정신여중": "정신여자중학교",
    "영파여중": "영파여자중학교",
    "성남여중": "성남여자중학교",
}

# 파일명 지역 prefix → 1.json description 매칭 키워드
REGION_MAP = {
    "서울-송파": "송파구",
    "서울-강남": "강남구",
    "서울-강동": "강동구",
    "성남-분당": "분당구",
    "성남-수정": "수정구",
    "경기-광주": "광주시",
    "경기-남양주": "남양주시",
    "경기-양평": "양평군",
    "경기-하남": "하남시",
    "서울-광진": "광진구",
    "서울-양천": "양천구",
    "전남-고흥": "고흥군",
}

def parse_filename(filename):
    """XLS 파일명에서 (학교명, 지역키워드) 추출.
    패턴1: '가락중-2025-3-1.xls' → ('가락중학교', None)
    패턴2: '강동-한산중학교-2025-3-1.xls' → ('한산중학교', '강동구')
    """
    name = unicodedata.normalize('NFC', filename.replace('-2025-3-1.xls', ''))
    parts = name.split('-')
    school = parts[-1]
    if school in NAME_MAP:
        school = NAME_MAP[school]
    elif '중학교' not in school:
        school = school.replace("중", "중학교")

    # 지역 prefix 추출
    region = None
    if len(parts) >= 2:
        prefix = '-'.join(parts[:-1])
        region = REGION_MAP.get(prefix)

    return school, region


def parse_xls(filepath):
    """HTML 형태의 XLS 파일에서 3학년 1학기 학업성취도 데이터를 파싱"""
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    tables = soup.find_all('table')
    if len(tables) < 3:
        print(f"  WARNING: {filepath} has only {len(tables)} tables, expected 3")
        return None

    # Table index 2 = 3학년
    table = tables[2]
    rows = table.find_all('tr')

    subjects = {}
    for row in rows[5:]:  # Skip header rows (0-4)
        cells = row.find_all(['td', 'th'])
        texts = [c.get_text(strip=True) for c in cells]

        if len(texts) < 2 or texts[0] == '검색된 결과가 없습니다.':
            continue

        subject_name = texts[0]
        avg = float(texts[1]) if texts[1] else 0

        grades = {}
        for i, grade in enumerate(['A', 'B', 'C', 'D', 'E']):
            val = texts[2 + i] if (2 + i) < len(texts) and texts[2 + i] else '0'
            grades[grade] = float(val) if val else 0

        subjects[subject_name] = {
            "avg": avg,
            **grades
        }

    return subjects


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    raw_dir = os.path.join(project_dir, 'raw_data')
    json_path = os.path.join(project_dir, 'data', '1.json')

    # Load 1.json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build title → list of (index, description) for duplicate handling
    from collections import defaultdict
    title_to_pins = defaultdict(list)
    for i, pin in enumerate(data['pins']):
        title_to_pins[pin['title']].append((i, pin.get('description', '')))

    # Parse all XLS files
    xls_files = glob.glob(os.path.join(raw_dir, '*-2025-3-1.xls'))
    print(f"Found {len(xls_files)} XLS files")

    matched = 0
    for xls_path in sorted(xls_files):
        filename = os.path.basename(xls_path)
        full_name, region_keyword = parse_filename(filename)

        print(f"  {filename} → {full_name}", end="")

        candidates = title_to_pins.get(full_name)
        if not candidates:
            print(f" [NOT FOUND in 1.json]")
            continue

        # 동명 학교가 여러 개면 지역으로 필터
        if len(candidates) > 1:
            keyword = region_keyword
            filtered = [(i, d) for i, d in candidates if keyword in d]
            if filtered:
                candidates = filtered

        if len(candidates) > 1:
            print(f" [AMBIGUOUS: {len(candidates)} matches]")
            continue

        idx = candidates[0][0]

        subjects = parse_xls(xls_path)
        if not subjects:
            print(f" [NO DATA]")
            continue

        data['pins'][idx]['achievement'] = {
            "year": "2025-1",
            "subjects": subjects
        }
        matched += 1
        desc = candidates[0][1]
        print(f" [OK] {len(subjects)} subjects ({desc})")

    # Save updated 1.json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {matched}/{len(xls_files)} schools matched and updated")


if __name__ == '__main__':
    main()
