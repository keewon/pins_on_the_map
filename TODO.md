# TODO: 대중교통 출퇴근 시간 데이터

## 현재 상태
- 자동차(카카오 Mobility API)는 구현 완료
- 대중교통 API 조사 완료, 구현 미착수

## 대중교통 API 후보

### TMAP Transit API (추천)
- 출발시간 지정 가능 (`searchDttm` 파라미터)
- Summary API: 0.55원/콜, 전체 수집 약 4,000원
- 원본 데이터 24시간 보관 제한 (소요시간만 추출 저장하면 파생 데이터로 볼 수 있음)
- 무료: 10콜/일 (테스트용)
- 가입: https://openapi.sk.com → appKey 발급
- 엔드포인트: `POST https://apis.openapi.sk.com/transit/routes/sub`

### ODsay API
- 출발시간 지정 불가
- 무료 1,000콜/일 (6개월), 이후 유료 (가격 비공개)
- 약관에 "데이터 분석 용도 별도 문의 필요" → 우리 용도는 해당될 가능성 높음

### 서울시 경로검색 API (data.go.kr)
- 서울만 지원 (전국 X)
- 출발시간 지정 불확실, 서버 불안정

### Google Routes API
- 출발시간 지정 가능
- $10/1,000콜 → 전체 수집 약 $72
- 결과 저장 30일 제한
