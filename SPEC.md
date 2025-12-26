# Pins in the map

이 서비스는 요약하자면 지도에 핀을 꽂는 서비스로 데스크탑 및 모바일을 지원한다.
Multiple pins can be included in each pin list.
Users can check/uncheck each list.
Users can specify color for each list.
Adding pins to the list is manual at this moment. It's static json list.

Each pin has following fields
 - latitude
 - longitude
 - title
 - description

Each list has following fields
 - title
 - description

list 로는 다음과 같은 것을 생각하고 있다.
 - 전국 중학교 리스트
 - 전국 맥도날드 리스트
 - 전국 써브웨이 리스트
 - 전국 공공도서관 리스트
 - 전국 공공수영장 리스트

각 리스트의 체크 여부는 쿠키에 저장해줘. 그리고 uncheck 됐을 땐 title 과 체크박스만 보이게 해줘

## 리스트 관리
list 별로 하나의 파일로 관리해주고, 리스트 목록을 갖고 있는 파일을 만들어줘. 각 리스트는 integer id 를 가지도록 해주고, 그걸 list 의 파일 이름으로 해줘 

색상은 사용자가 커스터마이즈 할 수 있어야 해. 기본 색상이 data 에 있는 것은 맞아. 커스터마이즈 한 색은 쿠키에 저장해줘 

## 리스트 가져오기
