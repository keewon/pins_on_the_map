# 📍 Pins on the Map

지도에 핀을 꽂아 다양한 장소를 관리하는 웹 서비스입니다.

![Desktop & Mobile Support](https://img.shields.io/badge/Platform-Desktop%20%7C%20Mobile-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 기능

- 🗺️ **인터랙티브 지도**: Leaflet 기반의 부드러운 지도 인터랙션 (한글 지명 지원)
- 📋 **다중 핀 리스트**: 여러 개의 핀 리스트를 동시에 관리
- ✅ **체크박스 토글**: 각 리스트를 표시/숨김 가능
- 🎨 **색상 커스터마이징**: 각 리스트별 색상 및 아이콘 지정 가능
- 📱 **반응형 디자인**: 데스크탑 및 모바일 완벽 지원
- 🌙 **다크 테마**: 눈이 편한 다크 테마 기본 적용
- 🚇 **노선도 표시**: 지하철 및 기차 노선도 오버레이
- 🏫 **학교 정보**: 남/녀/공학, 학생수, 학교유형 표시
- 📍 **스마트 클러스터링**: 2개까지는 개별 마커로 표시, 3개 이상부터 클러스터링
- 💬 **스마트 팝업**: 화면 가장자리에서도 팝업이 항상 보이도록 위치 자동 조정

## 📍 포함된 데이터

| 카테고리 | 리스트 |
|----------|--------|
| 🏫 교육 | 중학교, 고등학교 (일반고/특목고/자사고/특성화고 등), 대학교 |
| 📚 문화 | 도서관, 수영장 |
| 🍔 음식점 | 맥도날드, 써브웨이 |
| 🚇 교통 | 지하철역, 기차역 (노선도 포함) |
| 🏢 아파트 | 래미안, 자이, 푸르지오, 아이파크, 이편한세상, 힐스테이트, 롯데캐슬, 위브, 더샵 |

## 🚀 시작하기

### 방법 1: 간단한 로컬 서버 (권장)

#### Python 사용 시
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

#### Node.js 사용 시
```bash
# npx 사용 (Node.js 설치 필요)
npx serve

# 또는 http-server 설치 후
npm install -g http-server
http-server
```

### 방법 2: VS Code Live Server

1. VS Code에서 "Live Server" 확장 프로그램 설치
2. `index.html` 파일 우클릭 → "Open with Live Server"

### 접속

브라우저에서 `http://localhost:8000` (또는 해당 포트) 접속

## 📁 프로젝트 구조

```
pins_on_the_map/
├── index.html          # 메인 HTML 파일
├── styles.css          # 스타일시트
├── app.js              # 애플리케이션 로직
├── data/
│   ├── lists.json      # 리스트 메타데이터 (제목, 색상, 아이콘)
│   ├── 1.json          # 중학교 데이터
│   ├── 2.json          # 도서관 데이터
│   ├── 6.json          # 지하철역 데이터
│   ├── 9.json          # 고등학교 데이터
│   ├── 24.json         # 대학교 데이터
│   ├── ...             # 기타 데이터 파일
│   ├── subway_lines.json   # 지하철 노선도
│   └── train_lines.json    # 기차 노선도
├── scripts/            # 데이터 수집 스크립트
│   ├── fetch_apartments.py
│   ├── fetch_middle_schools.py
│   ├── fetch_high_schools.py
│   ├── fetch_universities.py
│   ├── fetch_school_info.py
│   ├── fetch_stations.py
│   └── ...
├── SPEC.md             # 기획 문서
└── README.md           # 이 문서
```

## 📝 데이터 구조

### 리스트 메타데이터 (lists.json)
```json
{
  "lists": [
    {
      "id": 1,
      "title": "중학교",
      "description": "전국 중학교 위치",
      "color": "#06b6d4",
      "icons": ["color", "🏫", "중", "中"]
    }
  ]
}
```

### 핀 데이터 ({id}.json)
```json
{
  "list_id": 1,
  "pins": [
    {
      "lat": 37.5665,
      "lng": 126.9780,
      "title": "서울중학교",
      "description": "서울특별시 종로구"
    }
  ]
}
```

### 학교 데이터 추가 필드
```json
{
  "lat": 37.5665,
  "lng": 126.9780,
  "title": "서울고등학교",
  "description": "서울특별시 서초구",
  "coed_type": "공학",
  "school_type": "일반고"
}
```

## 🎨 새로운 핀 리스트 추가하기

### 1. lists.json에 리스트 메타데이터 추가
```json
{
  "id": 99,
  "title": "나만의 리스트",
  "description": "나만의 장소 모음",
  "color": "#ff6b6b",
  "icons": ["color", "📍", "M", "M"]
}
```

### 2. data/99.json 파일 생성
```json
{
  "list_id": 99,
  "pins": [
    {
      "lat": 37.5665,
      "lng": 126.9780,
      "title": "서울역",
      "description": "서울특별시 용산구"
    }
  ]
}
```

## 🎨 사용 가능한 기본 색상

| 색상명 | HEX 코드 |
|--------|----------|
| Gold | `#d4a853` |
| Copper | `#c47d4e` |
| Teal | `#4a9d8e` |
| Coral | `#e07a5f` |
| Indigo | `#5c6bc0` |
| Rose | `#d4648a` |
| Emerald | `#4caf50` |
| Amber | `#ffa726` |

## 📱 반응형 브레이크포인트

- **Desktop**: 768px 이상
- **Tablet**: 768px 이하
- **Mobile**: 400px 이하

## 🛠️ 기술 스택

- **HTML5** / **CSS3** / **JavaScript (ES6+)**
- **[Leaflet](https://leafletjs.com/)** - 오픈소스 지도 라이브러리
- **[Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster)** - 마커 클러스터링
- **[OpenStreetMap](https://www.openstreetmap.org/)** - 맵 타일 (한글 지명 지원)
- **Google Fonts** - Noto Sans KR, Playfair Display
- **Python** - 데이터 수집 스크립트

## 📊 데이터 출처

| 데이터 | 출처 | 라이선스 |
|--------|------|----------|
| 맥도날드, 써브웨이, 도서관, 수영장 위치 | [카카오맵 API](https://developers.kakao.com/) | 카카오 API 이용약관 |
| 중학교, 고등학교, 대학교 위치 | [카카오맵 API](https://developers.kakao.com/) | 카카오 API 이용약관 |
| 중학교, 고등학교 상세정보 (남/녀/공학, 학생수, 학교유형) | [학교알리미](https://www.schoolinfo.go.kr/) | 공공누리 |
| 지하철역, 기차역 위치 | [카카오맵 API](https://developers.kakao.com/) | 카카오 API 이용약관 |
| 지하철 노선도 | [OpenStreetMap](https://www.openstreetmap.org/) via Overpass API | ODbL |
| 기차 노선도 | [OpenStreetMap](https://www.openstreetmap.org/) via Overpass API | ODbL |
| 아파트 위치 (래미안, 자이, 푸르지오, 아이파크, 이편한세상, 힐스테이트, 롯데캐슬, 위브, 더샵) | [카카오맵 API](https://developers.kakao.com/) | 카카오 API 이용약관 |

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포하실 수 있습니다.

### 데이터 라이선스
- 카카오맵 API 데이터: [카카오 API 이용약관](https://developers.kakao.com/terms/latest/ko/site-policy) 준수
- OpenStreetMap 데이터: [ODbL (Open Database License)](https://opendatacommons.org/licenses/odbl/) - © OpenStreetMap contributors

---

Made with ❤️ for exploring places on the map

