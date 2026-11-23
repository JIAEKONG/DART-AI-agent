"""
⑪ 영업정지 조회
질문 예시: "영업정지 당한 적 있어?"
기반 API: bsnSp.json (주요사항보고서)
주의: 결과가 비어 있으면 '조회된 영업정지 공시가 없음'이지, 영업정지 사실이 없다는 단정이 아님
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 11
NAME = "business_stop"
TITLE = "영업정지"
KIND = "period"            # none | period | year | multi_year

# ── 가져올 필드 (실제 응답과 다르면 test_all_tools.py 결과를 보고 수정) ──
FIELDS = [
    "bsnsp_rs",                          # 팀 표 핵심 값
    "bsnsp_amt",                         # 팀 표 핵심 값
    "sl_vs",                             # 팀 표 핵심 값
]


def get_business_stop(corp_code: str, bgn_de: str, end_de: str, raw: bool = False) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    bgn_de, end_de: 조회 기간 YYYYMMDD
    raw: True면 필드를 추리지 않고 응답 원본을 그대로 돌려줌 (필드명 확인용)
    """
    data = call_api("bsnSp.json", {"corp_code": corp_code, "bgn_de": bgn_de, "end_de": end_de})

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


RUN = get_business_stop


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
