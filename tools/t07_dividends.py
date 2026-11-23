"""
⑦ 배당에 관한 사항 조회
질문 예시: "배당금 얼마야?"
기반 API: alotMatter.json (정기보고서 주요정보)
참고: thstrm / frmtrm = 당기 / 전기 값
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 7
NAME = "dividends"
TITLE = "배당에 관한 사항"
KIND = "year"            # none | period | year | multi_year
REPORT_CODES = None      # None이면 dart_client.REPORT_CODES(사업/반기/1분기/3분기) 사용. 예: ["11011"]

# ── 가져올 필드 (실제 응답과 다르면 test_all_tools.py 결과를 보고 수정) ──
FIELDS = [
    "se",                                # 팀 표 핵심 값
    "thstrm",                            # 팀 표 핵심 값
    "frmtrm",                            # 팀 표 핵심 값
    "stock_knd",                         # 추가 후보 (내 기억 기준, 테스트로 확인)
]


def get_dividends(corp_code: str, bsns_year: str, reprt_code: str = "11011", raw: bool = False) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    bsns_year: 사업연도 (예: "2025")
    reprt_code: 11011(사업보고서, 기본값) / 11012(반기) / 11013(1분기) / 11014(3분기)
    raw: True면 필드를 추리지 않고 응답 원본을 그대로 돌려줌 (필드명 확인용)
    """
    data = call_api("alotMatter.json", {"corp_code": corp_code, "bsns_year": bsns_year, "reprt_code": reprt_code})

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


RUN = get_dividends


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
