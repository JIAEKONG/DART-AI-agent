"""
⑫ 대량보유 상황보고 조회
질문 예시: "누가 주식 많이 샀대?"
기반 API: majorstock.json (지분공시)
주의: 보고가 있었던 경우에만 데이터가 있음 (비어 있으면 '조회된 보고 없음')
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 12
NAME = "major_holdings"
TITLE = "대량보유 상황보고"
KIND = "none"            # none | period | year | multi_year

# ── 가져올 필드 (실제 응답과 다르면 test_all_tools.py 결과를 보고 수정) ──
FIELDS = [
    "repror",                            # 팀 표 핵심 값
    "stkqy",                             # 팀 표 핵심 값
    "stkrt",                             # 팀 표 핵심 값
    "rcept_dt",                          # 추가 후보 (내 기억 기준, 테스트로 확인)
]


def get_major_holdings(corp_code: str, raw: bool = False) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    raw: True면 필드를 추리지 않고 응답 원본을 그대로 돌려줌 (필드명 확인용)
    """
    data = call_api("majorstock.json", {"corp_code": corp_code})

    items = data.get("list", [])
    if raw:
        return items
    return [
        {
            **{k: item.get(k) for k in FIELDS},
            "_source": {"corp_code": corp_code, "rcept_no": item.get("rcept_no")},
        }
        for item in items
    ]


RUN = get_major_holdings


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
