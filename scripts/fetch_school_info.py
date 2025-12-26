#!/usr/bin/env python3
"""
학교 상세 정보 수집 (학교알리미 OpenAPI)
- 남/여/공학 구분
- 설립유형 (공립/사립)
- 학생수 (남녀별)
- 학교유형: 인문계/실업계/자사고/특목고/특성화고 등
- 고등학교: 졸업생 진로현황 (성별, 진학률)

출처: 학교알리미 (https://www.schoolinfo.go.kr)
API 문서: https://www.schoolinfo.go.kr/download/OpenAPI_Developer_Guide.pdf
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SCHOOLINFO_API_KEY = os.getenv("SCHOOLINFO_API_KEY")
BASE_URL = "https://www.schoolinfo.go.kr/openApi.do"

# 학교급 코드
SCHOOL_KIND = {
    "중학교": "03",
    "고등학교": "04",
}

# 시도코드 및 시군구코드
SIDO_SGG_CODES = {
    "서울": {
        "code": "11",
        "sgg": {
            "종로구": "11110", "중구": "11140", "용산구": "11170", "성동구": "11200",
            "광진구": "11215", "동대문구": "11230", "중랑구": "11260", "성북구": "11290",
            "강북구": "11305", "도봉구": "11320", "노원구": "11350", "은평구": "11380",
            "서대문구": "11410", "마포구": "11440", "양천구": "11470", "강서구": "11500",
            "구로구": "11530", "금천구": "11545", "영등포구": "11560", "동작구": "11590",
            "관악구": "11620", "서초구": "11650", "강남구": "11680", "송파구": "11710",
            "강동구": "11740",
        }
    },
    "부산": {
        "code": "21",
        "sgg": {
            "중구": "21110", "서구": "21140", "동구": "21170", "영도구": "21200",
            "부산진구": "21230", "동래구": "21260", "남구": "21290", "북구": "21320",
            "해운대구": "21350", "사하구": "21380", "금정구": "21410", "강서구": "21440",
            "연제구": "21470", "수영구": "21500", "사상구": "21530", "기장군": "21710",
        }
    },
    "대구": {
        "code": "22",
        "sgg": {
            "중구": "22110", "동구": "22140", "서구": "22170", "남구": "22200",
            "북구": "22230", "수성구": "22260", "달서구": "22290", "달성군": "22710",
            "군위군": "22720",
        }
    },
    "인천": {
        "code": "23",
        "sgg": {
            "중구": "23110", "동구": "23140", "미추홀구": "23150", "연수구": "23170",
            "남동구": "23200", "부평구": "23230", "계양구": "23260", "서구": "23290",
            "강화군": "23710", "옹진군": "23720",
        }
    },
    "광주": {
        "code": "24",
        "sgg": {
            "동구": "24110", "서구": "24140", "남구": "24170", "북구": "24200", "광산구": "24230",
        }
    },
    "대전": {
        "code": "25",
        "sgg": {
            "동구": "25110", "중구": "25140", "서구": "25170", "유성구": "25200", "대덕구": "25230",
        }
    },
    "울산": {
        "code": "26",
        "sgg": {
            "중구": "26110", "남구": "26140", "동구": "26170", "북구": "26200", "울주군": "26710",
        }
    },
    "세종": {
        "code": "29",
        "sgg": {
            "세종시": "29010",
        }
    },
    "경기": {
        "code": "31",
        "sgg": {
            "수원시": "31010", "성남시": "31020", "의정부시": "31030", "안양시": "31040",
            "부천시": "31050", "광명시": "31060", "평택시": "31070", "동두천시": "31080",
            "안산시": "31090", "고양시": "31100", "과천시": "31110", "구리시": "31120",
            "남양주시": "31130", "오산시": "31140", "시흥시": "31150", "군포시": "31160",
            "의왕시": "31170", "하남시": "31180", "용인시": "31190", "파주시": "31200",
            "이천시": "31210", "안성시": "31220", "김포시": "31230", "화성시": "31240",
            "광주시": "31250", "양주시": "31260", "포천시": "31270", "여주시": "31280",
            "연천군": "31710", "가평군": "31720", "양평군": "31730",
        }
    },
    "강원": {
        "code": "32",
        "sgg": {
            "춘천시": "32010", "원주시": "32020", "강릉시": "32030", "동해시": "32040",
            "태백시": "32050", "속초시": "32060", "삼척시": "32070",
            "홍천군": "32710", "횡성군": "32720", "영월군": "32730", "평창군": "32740",
            "정선군": "32750", "철원군": "32760", "화천군": "32770", "양구군": "32780",
            "인제군": "32790", "고성군": "32800", "양양군": "32810",
        }
    },
    "충북": {
        "code": "33",
        "sgg": {
            "청주시": "33010", "충주시": "33020", "제천시": "33030",
            "보은군": "33710", "옥천군": "33720", "영동군": "33730", "증평군": "33740",
            "진천군": "33750", "괴산군": "33760", "음성군": "33770", "단양군": "33780",
        }
    },
    "충남": {
        "code": "34",
        "sgg": {
            "천안시": "34010", "공주시": "34020", "보령시": "34030", "아산시": "34040",
            "서산시": "34050", "논산시": "34060", "계룡시": "34070", "당진시": "34080",
            "금산군": "34710", "부여군": "34720", "서천군": "34730", "청양군": "34740",
            "홍성군": "34750", "예산군": "34760", "태안군": "34770",
        }
    },
    "전북": {
        "code": "35",
        "sgg": {
            "전주시": "35010", "군산시": "35020", "익산시": "35030", "정읍시": "35040",
            "남원시": "35050", "김제시": "35060",
            "완주군": "35710", "진안군": "35720", "무주군": "35730", "장수군": "35740",
            "임실군": "35750", "순창군": "35760", "고창군": "35770", "부안군": "35780",
        }
    },
    "전남": {
        "code": "36",
        "sgg": {
            "목포시": "36010", "여수시": "36020", "순천시": "36030", "나주시": "36040",
            "광양시": "36050",
            "담양군": "36710", "곡성군": "36720", "구례군": "36730", "고흥군": "36740",
            "보성군": "36750", "화순군": "36760", "장흥군": "36770", "강진군": "36780",
            "해남군": "36790", "영암군": "36800", "무안군": "36810", "함평군": "36820",
            "영광군": "36830", "장성군": "36840", "완도군": "36850", "진도군": "36860",
            "신안군": "36870",
        }
    },
    "경북": {
        "code": "37",
        "sgg": {
            "포항시": "37010", "경주시": "37020", "김천시": "37030", "안동시": "37040",
            "구미시": "37050", "영주시": "37060", "영천시": "37070", "상주시": "37080",
            "문경시": "37090", "경산시": "37100",
            "의성군": "37720", "청송군": "37730", "영양군": "37740",
            "영덕군": "37750", "청도군": "37760", "고령군": "37770", "성주군": "37780",
            "칠곡군": "37790", "예천군": "37800", "봉화군": "37810", "울진군": "37820",
            "울릉군": "37830",
        }
    },
    "경남": {
        "code": "38",
        "sgg": {
            "창원시": "38010", "진주시": "38030", "통영시": "38050", "사천시": "38060",
            "김해시": "38070", "밀양시": "38080", "거제시": "38090", "양산시": "38100",
            "의령군": "38710", "함안군": "38720", "창녕군": "38730", "고성군": "38740",
            "남해군": "38750", "하동군": "38760", "산청군": "38770", "함양군": "38780",
            "거창군": "38790", "합천군": "38800",
        }
    },
    "제주": {
        "code": "39",
        "sgg": {
            "제주시": "39010", "서귀포시": "39020",
        }
    },
}


def fetch_schools_basic(sido_code, sgg_code, school_kind_code):
    """학교 기본정보 조회 (apiType=0)"""
    params = {
        "apiKey": SCHOOLINFO_API_KEY,
        "apiType": "0",
        "sidoCode": sido_code,
        "sggCode": sgg_code,
        "schulKndCode": school_kind_code,
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("list", [])
    except Exception as e:
        return []


def fetch_student_count(school_code, school_kind_code, year="2025"):
    """학생수 조회 (apiType=10) - 남녀별 학생수 포함"""
    params = {
        "apiKey": SCHOOLINFO_API_KEY,
        "apiType": "10",
        "schulCode": school_code,
        "schulKndCode": school_kind_code,
        "pbanYr": year,
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        if "list" in data and len(data["list"]) > 0:
            raw = data["list"][0]
            
            # 학년별 남녀 학생수 계산
            result = {
                "total": raw.get("STDNT_SUM", 0),
            }
            
            if school_kind_code == "03":  # 중학교
                # 남학생: MAN_STDNT_31, MAN_STDNT_32, MAN_STDNT_33
                # 여학생: WOMAN_STDNT_31, WOMAN_STDNT_32, WOMAN_STDNT_33
                male_total = (
                    int(raw.get("MAN_STDNT_31", 0) or 0) +
                    int(raw.get("MAN_STDNT_32", 0) or 0) +
                    int(raw.get("MAN_STDNT_33", 0) or 0)
                )
                female_total = (
                    int(raw.get("WOMAN_STDNT_31", 0) or 0) +
                    int(raw.get("WOMAN_STDNT_32", 0) or 0) +
                    int(raw.get("WOMAN_STDNT_33", 0) or 0)
                )
                result["male"] = male_total
                result["female"] = female_total
                result["g1"] = raw.get("STDNT_SUM_31", 0)
                result["g2"] = raw.get("STDNT_SUM_32", 0)
                result["g3"] = raw.get("STDNT_SUM_33", 0)
            else:  # 고등학교
                male_total = (
                    int(raw.get("MAN_STDNT_41", 0) or 0) +
                    int(raw.get("MAN_STDNT_42", 0) or 0) +
                    int(raw.get("MAN_STDNT_43", 0) or 0)
                )
                female_total = (
                    int(raw.get("WOMAN_STDNT_41", 0) or 0) +
                    int(raw.get("WOMAN_STDNT_42", 0) or 0) +
                    int(raw.get("WOMAN_STDNT_43", 0) or 0)
                )
                result["male"] = male_total
                result["female"] = female_total
                result["g1"] = raw.get("STDNT_SUM_41", 0)
                result["g2"] = raw.get("STDNT_SUM_42", 0)
                result["g3"] = raw.get("STDNT_SUM_43", 0)
            
            return result
        return None
    except:
        return None


def fetch_graduation_info(school_code, year="2024"):
    """졸업생 진로현황 조회 - 고등학교만 (apiType=51)"""
    params = {
        "apiKey": SCHOOLINFO_API_KEY,
        "apiType": "51",
        "schulCode": school_code,
        "schulKndCode": "04",
        "pbanYr": year,
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        if "list" in data and len(data["list"]) > 0:
            return data["list"][0]
        return None
    except:
        return None


def get_coed_type(code):
    """남녀공학 구분 변환"""
    if code == "남":
        return "남학교"
    elif code == "녀" or code == "여":
        return "여학교"
    elif code in ["남녀공학", "공학"]:
        return "공학"
    else:
        return "미분류"


def get_school_type(school):
    """학교 유형 분류 (고등학교)"""
    # HS_KND_SC_NM: 고등학교 종류 (일반고등학교, 특수목적고등학교, 특성화고등학교, 자율고등학교)
    
    hs_kind = school.get("HS_KND_SC_NM", "")
    fond_sc = school.get("FOND_SC_CODE", "")  # 공립/사립
    schul_nm = school.get("SCHUL_NM", "")
    
    # 특수목적고 세분화
    if "특수목적" in hs_kind:
        if "과학고" in schul_nm:
            return "과학고"
        elif "외국어고" in schul_nm or "외고" in schul_nm:
            return "외고"
        elif "국제고" in schul_nm:
            return "국제고"
        elif "예술고" in schul_nm:
            return "예술고"
        elif "체육고" in schul_nm:
            return "체육고"
        elif "마이스터" in schul_nm:
            return "마이스터고"
        return "특목고"
    
    # 자율고 (자사고/자공고)
    if "자율" in hs_kind:
        if fond_sc == "사립":
            return "자사고"
        else:
            return "자공고"
    
    # 특성화고
    if "특성화" in hs_kind:
        return "특성화고"
    
    # 일반고
    return "일반고"


def fetch_all_schools(school_type):
    """전국 학교 정보 수집"""
    school_kind_code = SCHOOL_KIND[school_type]
    all_schools = []
    is_high_school = school_type == "고등학교"
    
    print(f"\n🏫 {school_type} 정보 수집 중...")
    
    total_regions = sum(len(info["sgg"]) for info in SIDO_SGG_CODES.values())
    current = 0
    
    for sido_name, sido_info in SIDO_SGG_CODES.items():
        sido_code = sido_info["code"]
        
        for sgg_name, sgg_code in sido_info["sgg"].items():
            current += 1
            print(f"  [{current}/{total_regions}] {sido_name} {sgg_name}...", end=" ", flush=True)
            
            schools = fetch_schools_basic(sido_code, sgg_code, school_kind_code)
            region_count = 0
            
            for school in schools:
                # 폐교 제외
                if school.get("CLOSE_YN") == "Y":
                    continue
                
                school_code = school.get("SCHUL_CODE", "")
                
                school_info = {
                    "name": school.get("SCHUL_NM", ""),
                    "coed_type": get_coed_type(school.get("COEDU_SC_CODE", "")),
                    "found_type": school.get("FOND_SC_CODE", ""),
                    "sido": sido_name,
                    "school_code": school_code,
                }
                
                # 고등학교는 학교유형 추가 (인문계/실업계/자사고 등)
                if is_high_school:
                    school_info["school_type"] = get_school_type(school)
                
                # 학생수 조회 (남녀별)
                student_data = fetch_student_count(school_code, school_kind_code)
                if student_data:
                    school_info["student_total"] = student_data.get("total", 0)
                    school_info["student_male"] = student_data.get("male", 0)
                    school_info["student_female"] = student_data.get("female", 0)
                    school_info["student_g1"] = student_data.get("g1", 0)
                    school_info["student_g2"] = student_data.get("g2", 0)
                    school_info["student_g3"] = student_data.get("g3", 0)
                
                # 고등학교는 졸업생 진로현황도 조회
                if is_high_school:
                    grad_data = fetch_graduation_info(school_code)
                    if grad_data:
                        school_info["grad_male"] = grad_data.get("MAN_SUM", 0)
                        school_info["grad_female"] = grad_data.get("WOMAN_SUM", 0)
                        school_info["advancement_rate"] = grad_data.get("TOTAL_RATE", "")
                
                all_schools.append(school_info)
                region_count += 1
                time.sleep(0.05)  # API 부하 방지
            
            print(f"→ {region_count}개")
            time.sleep(0.1)
    
    return all_schools


def merge_with_existing_data(school_info_list, existing_data_path, output_path):
    """기존 위치 데이터와 병합"""
    
    with open(existing_data_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # 학교명으로 매칭
    school_info_map = {}
    for info in school_info_list:
        name_key = info["name"].replace(" ", "").strip()
        school_info_map[name_key] = info
    
    matched_count = 0
    for pin in existing_data.get("pins", []):
        title = pin.get("title", "").replace(" ", "").strip()
        
        if title in school_info_map:
            info = school_info_map[title]
            pin["coed_type"] = info.get("coed_type", "")
            pin["found_type"] = info.get("found_type", "")
            pin["student_total"] = info.get("student_total", 0)
            pin["student_male"] = info.get("student_male", 0)
            pin["student_female"] = info.get("student_female", 0)
            pin["student_g1"] = info.get("student_g1", 0)
            pin["student_g2"] = info.get("student_g2", 0)
            pin["student_g3"] = info.get("student_g3", 0)
            
            # 고등학교 추가 정보 (학교유형, 졸업생 진로)
            if "school_type" in info:
                pin["school_type"] = info.get("school_type", "")
            if "grad_male" in info:
                pin["grad_male"] = info.get("grad_male", 0)
                pin["grad_female"] = info.get("grad_female", 0)
                pin["advancement_rate"] = info.get("advancement_rate", "")
            
            matched_count += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 매칭 완료: {matched_count}/{len(existing_data.get('pins', []))}개")
    print(f"💾 저장 완료: {output_path}")
    
    return matched_count


def save_raw_data(schools, filename):
    """원본 데이터 저장"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    print(f"📋 원본 데이터 저장: {filepath}")


if __name__ == "__main__":
    if not SCHOOLINFO_API_KEY:
        print("❌ 오류: SCHOOLINFO_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 SCHOOLINFO_API_KEY=your_key_here 형식으로 추가해주세요.")
        print("   API 키는 https://www.schoolinfo.go.kr 에서 발급받을 수 있습니다.")
        exit(1)
    
    print("=" * 60)
    print("🏫 학교 상세 정보 수집 (학교알리미 API)")
    print("=" * 60)
    print("수집 항목: 남/녀/공학, 설립유형, 학생수")
    print("고등학교 추가: 졸업생 성별, 진학률")
    print("=" * 60)
    
    # 중학교 정보 수집
    middle_schools = fetch_all_schools("중학교")
    print(f"\n📊 중학교 총 {len(middle_schools)}개 수집")
    save_raw_data(middle_schools, "중학교_schoolinfo_raw.json")
    
    # 고등학교 정보 수집
    high_schools = fetch_all_schools("고등학교")
    print(f"\n📊 고등학교 총 {len(high_schools)}개 수집")
    save_raw_data(high_schools, "고등학교_schoolinfo_raw.json")
    
    # 기존 데이터와 병합
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print("\n" + "=" * 60)
    print("📝 기존 데이터와 병합 중...")
    print("=" * 60)
    
    merge_with_existing_data(
        middle_schools,
        os.path.join(data_dir, "1.json"),
        os.path.join(data_dir, "1.json")
    )
    
    merge_with_existing_data(
        high_schools,
        os.path.join(data_dir, "9.json"),
        os.path.join(data_dir, "9.json")
    )
    
    print("\n" + "=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print("\n데이터 출처: 학교알리미 (https://www.schoolinfo.go.kr)")
