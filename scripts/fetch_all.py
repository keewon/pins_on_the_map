#!/usr/bin/env python3
"""
모든 리스트 데이터 일괄 수집
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    ("fetch_middle_schools.py", "중학교"),
    ("fetch_mcdonalds.py", "맥도날드"),
    ("fetch_subway.py", "서브웨이"),
    ("fetch_libraries.py", "공공도서관"),
    ("fetch_swimming_pools.py", "공공수영장"),
]


def main():
    script_dir = Path(__file__).parent
    
    print("=" * 50)
    print("📍 전체 데이터 수집 시작")
    print("=" * 50)
    print()
    
    for script_name, label in SCRIPTS:
        print(f"\n{'='*50}")
        print(f"▶ {label} 수집 중...")
        print("=" * 50)
        
        script_path = script_dir / script_name
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_dir,
        )
        
        if result.returncode != 0:
            print(f"⚠️ {label} 수집 중 오류 발생")
        
        print()
    
    print("=" * 50)
    print("✅ 전체 데이터 수집 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()

