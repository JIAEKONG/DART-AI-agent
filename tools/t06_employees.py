"""
⑥ 직원 현황 조회
질문 예시: "직원 몇 명이야? 평균 연봉은?"
기반 API: empSttus.json (정기보고서 주요정보)
주의: 사업부문·성별 등 여러 줄로 올 수 있어서 합산 규칙이 필요할 수 있음 (테스트로 확인)
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 6
NAME = "employees"
TITLE = "직원 현황"
KIND = "year"            # none | period | year | multi_year
REPORT_CODES = None      # None이면 dart_client.REPORT_CODES(사업/반기/1분기/3분기) 사용. 예: ["11011"]

# ── 가져올 필드 (실제 응답과 다르면 test_all_tools.py 결과를 보고 수정) ──
FIELDS = [
    "rgllbr_co",                         # 팀 표 핵심 값
    "jan_salary_am",                     # 팀 표 핵심 값
    "fo_bbm",                            # 추가 후보 (내 기억 기준, 테스트로 확인)
    "sexdstn",                           # 추가 후보 (내 기억 기준, 테스트로 확인)
    "sm",                                # 추가 후보 (내 기억 기준, 테스트로 확인)
    "fyer_salary_totamt",                # 추가 후보 (내 기억 기준, 테스트로 확인)
]


def get_employees(corp_code: str, bsns_year: str, reprt_code: str = "11011", raw: bool = False) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    bsns_year: 사업연도 (예: "2025")
    reprt_code: 11011(사업보고서, 기본값) / 11012(반기) / 11013(1분기) / 11014(3분기)
    raw: True면 필드를 추리지 않고 응답 원본을 그대로 돌려줌 (필드명 확인용)
    """
    data = call_api("empSttus.json", {"corp_code": corp_code, "bsns_year": bsns_year, "reprt_code": reprt_code})

    items = data.get("list", [])
    if raw:
        return items
    return [
        {
            **{k: item.get(k) for k in FIELDS},
            "_source": {
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": reprt_code,
                "rcept_no": item.get("rcept_no"),
            },
        }
        for item in items
    ]


RUN = get_employees


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
