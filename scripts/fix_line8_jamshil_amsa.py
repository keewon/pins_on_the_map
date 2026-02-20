#!/usr/bin/env python3
"""8호선 잠실-암사 구간 실제 노선 좌표 추출"""

import json
import urllib.request
import urllib.parse
import os

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

# 8호선 way만 직접 가져오기
query = '''
[out:json][timeout:30];
way["railway"="subway"]["name"~"8호선"](37.50,127.09,37.56,127.14);
out body;
>;
out skel qt;
'''

print('🚇 8호선 way 데이터 가져오는 중...')
try:
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(OVERPASS_URL, data=data)
    
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    elements = result.get('elements', [])
    nodes = {e['id']: e for e in elements if e.get('type') == 'node'}
    ways = [e for e in elements if e.get('type') == 'way']
    
    print(f'   {len(ways)}개 way 발견')
    
    # 잠실-암사 구간의 way들 찾기
    jamshil_amsa_ways = []
    for way in ways:
        coords = []
        for node_id in way.get('nodes', []):
            node = nodes.get(node_id)
            if node and 'lat' in node and 'lon' in node:
                coords.append([node['lon'], node['lat']])
        
        if len(coords) < 2:
            continue
        
        # 잠실-암사 구간인지 확인
        in_range = any(127.09 <= c[0] <= 127.14 and 37.50 <= c[1] <= 37.56 for c in coords)
        if in_range:
            jamshil_amsa_ways.append({
                'way_id': way['id'],
                'coords': coords
            })
            print(f'   Way {way["id"]}: {len(coords)}개 좌표')
    
    if jamshil_amsa_ways:
        # way들을 연결 (끝점과 시작점이 가까우면 연결)
        connected_segments = []
        used_ways = set()
        
        # 첫 way 찾기 (잠실 근처에서 시작)
        start_way = None
        for way_data in jamshil_amsa_ways:
            first_coord = way_data['coords'][0]
            last_coord = way_data['coords'][-1]
            # 잠실 근처에서 시작하거나 끝나는 way
            if (127.09 <= first_coord[0] <= 127.11 and 37.51 <= first_coord[1] <= 37.52) or \
               (127.09 <= last_coord[0] <= 127.11 and 37.51 <= last_coord[1] <= 37.52):
                start_way = way_data
                break
        
        if start_way:
            # 잠실에서 시작하는 방향으로 정렬
            first_coord = start_way['coords'][0]
            if not (127.09 <= first_coord[0] <= 127.11 and 37.51 <= first_coord[1] <= 37.52):
                start_way['coords'] = start_way['coords'][::-1]
            
            connected_segments.append(start_way['coords'])
            used_ways.add(start_way['way_id'])
            print(f'   시작 way: {start_way["way_id"]}')
        
        # 나머지 way들을 연결
        max_iterations = len(jamshil_amsa_ways)
        iteration = 0
        while len(used_ways) < len(jamshil_amsa_ways) and iteration < max_iterations:
            iteration += 1
            last_coord = connected_segments[-1][-1]
            best_match = None
            best_dist = float('inf')
            reverse = False
            
            for way_data in jamshil_amsa_ways:
                if way_data['way_id'] in used_ways:
                    continue
                
                first_coord = way_data['coords'][0]
                last_coord_way = way_data['coords'][-1]
                
                # 거리 계산
                dist1 = ((last_coord[0] - first_coord[0])**2 + (last_coord[1] - first_coord[1])**2)**0.5
                dist2 = ((last_coord[0] - last_coord_way[0])**2 + (last_coord[1] - last_coord_way[1])**2)**0.5
                
                if dist1 < best_dist:
                    best_dist = dist1
                    best_match = way_data
                    reverse = False
                if dist2 < best_dist:
                    best_dist = dist2
                    best_match = way_data
                    reverse = True
            
            if best_match and best_dist < 0.01:  # 0.01도 이내면 연결
                coords = best_match['coords']
                if reverse:
                    coords = coords[::-1]
                connected_segments.append(coords[1:])  # 첫 좌표 제외
                used_ways.add(best_match['way_id'])
                print(f'   연결 way: {best_match["way_id"]} (거리: {best_dist:.6f})')
            else:
                break
        
        # 모든 좌표 합치기
        final_coords = []
        for segment in connected_segments:
            final_coords.extend(segment)
        
        # 잠실-암사 구간만 필터링
        final_coords = [c for c in final_coords if 127.09 <= c[0] <= 127.14 and 37.50 <= c[1] <= 37.56]
        
        print(f'\n연결된 좌표: {len(final_coords)}개')
        if final_coords:
            print(f'첫 좌표: {final_coords[0]}')
            print(f'마지막 좌표: {final_coords[-1]}')
            
            # subway_lines.json에 업데이트
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            lines_path = os.path.join(project_dir, 'data', 'subway_lines.json')
            
            with open(lines_path, 'r', encoding='utf-8') as f:
                lines_data = json.load(f)
            
            line8_index = None
            for i, feature in enumerate(lines_data['features']):
                if '8호선' in feature['properties']['name']:
                    line8_index = i
                    break
            
            if line8_index is not None:
                coords_list = lines_data['features'][line8_index]['geometry']['coordinates']
                # 마지막 구간이 잠실-암사 구간인지 확인하고 제거
                if len(coords_list) > 0:
                    last_seg = coords_list[-1]
                    if any(127.09 <= c[0] <= 127.14 and 37.50 <= c[1] <= 37.56 for c in last_seg):
                        coords_list.pop()
                        print('기존 잠실-암사 구간 제거')
                
                # 실제 노선 좌표 추가
                coords_list.append(final_coords)
                print(f'구간 추가 완료 (총 {len(coords_list)}개 구간)')
                
                with open(lines_path, 'w', encoding='utf-8') as f:
                    json.dump(lines_data, f, ensure_ascii=False, indent=2)
                print('✅ 저장 완료')
    
except Exception as e:
    print(f'오류: {e}')
    import traceback
    traceback.print_exc()

