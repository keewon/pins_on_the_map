#!/usr/bin/env python3
"""
기차 노선 데이터 수집 (OpenStreetMap Overpass API)

사용법:
    python scripts/fetch_train_lines.py

출력:
    data/train_lines.json - 기차 노선 GeoJSON
"""

import json
import os
import urllib.request
import urllib.parse
from collections import defaultdict

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass QL 쿼리 - 대한민국 기차 노선
QUERY = """
[out:json][timeout:180];
area["name"="대한민국"]->.korea;
(
  relation["route"="train"](area.korea);
);
out body;
>;
out skel qt;
"""

# 기차 노선 색상 정의
TRAIN_COLORS = {
    'KTX': '#003DA5',  # KTX 파란색
    'SRT': '#8B0029',  # SRT 자주색
    '경부': '#0054A6',
    '호남': '#00A651',
    '경전': '#F7941D',
    '중앙': '#EF4123',
    '영동': '#0072BC',
    '태백': '#00A99D',
    '충북': '#8DC63F',
    '경북': '#F15A29',
    '전라': '#009444',
    '장항': '#00AEEF',
}


def get_line_color(name):
    """노선 이름에서 색상 결정"""
    for key, color in TRAIN_COLORS.items():
        if key in name:
            return color
    return '#666666'


def fetch_from_overpass():
    """Overpass API에서 데이터 가져오기"""
    print("🚂 Overpass API에서 기차 노선 데이터 가져오는 중...")
    
    data = urllib.parse.urlencode({'data': QUERY}).encode('utf-8')
    req = urllib.request.Request(OVERPASS_URL, data=data)
    
    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    print(f"   {len(result.get('elements', []))}개 elements 수신")
    return result


def process_osm_data(data):
    """OSM 데이터를 GeoJSON으로 변환"""
    elements = data.get('elements', [])
    
    # 인덱스 생성
    nodes_by_id = {}
    ways_by_id = {}
    
    for e in elements:
        if e.get('type') == 'node':
            nodes_by_id[e['id']] = e
        elif e.get('type') == 'way':
            ways_by_id[e['id']] = e
    
    relations = [e for e in elements if e.get('type') == 'relation']
    print(f"   {len(relations)}개 노선 relation 발견")
    
    # 노선별로 구간 모으기
    lines = defaultdict(lambda: {'colour': '#666666', 'coordinates': []})
    
    for rel in relations:
        tags = rel.get('tags', {})
        name = tags.get('name', '')
        
        if not name:
            continue
        
        # 이름에서 기본 노선명 추출
        base_name = name.split(':')[0].strip()
        
        # 색상 결정
        colour = tags.get('colour') or get_line_color(base_name)
        lines[base_name]['colour'] = colour
        
        # way 멤버들의 좌표 추출
        way_ids = [m['ref'] for m in rel.get('members', []) if m['type'] == 'way']
        
        for way_id in way_ids:
            way = ways_by_id.get(way_id)
            if not way:
                continue
            
            coords = []
            for node_id in way.get('nodes', []):
                node = nodes_by_id.get(node_id)
                if node and 'lat' in node and 'lon' in node:
                    coords.append([node['lon'], node['lat']])
            
            if len(coords) >= 2:
                lines[base_name]['coordinates'].append(coords)
    
    # GeoJSON 생성
    features = []
    for name, line_data in lines.items():
        if line_data['coordinates']:
            feature = {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "colour": line_data['colour']
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": line_data['coordinates']
                }
            }
            features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def main():
    # 스크립트 위치 기준으로 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(project_dir, 'data', 'train_lines.json')
    
    # Overpass API에서 데이터 가져오기
    raw_data = fetch_from_overpass()
    
    # GeoJSON으로 변환
    print("🔄 GeoJSON으로 변환 중...")
    geojson = process_osm_data(raw_data)
    
    # 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    
    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"✅ {len(geojson['features'])}개 노선 저장 완료")
    print(f"   파일: {output_path} ({file_size:.1f}MB)")
    
    # 노선 목록 출력
    print("\n📋 노선 목록:")
    for feat in sorted(geojson['features'], key=lambda x: x['properties']['name'])[:15]:
        props = feat['properties']
        print(f"   {props['name']} ({props['colour']})")
    
    if len(geojson['features']) > 15:
        print(f"   ... 외 {len(geojson['features']) - 15}개")


if __name__ == "__main__":
    main()

