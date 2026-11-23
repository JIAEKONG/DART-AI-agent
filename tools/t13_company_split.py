"""
⑬ 회사분할 결정 조회
질문 예시: "회사 분할했어?"
기반 API: cmpDvDecsn.json (주요사항보고서)
주의: 결과가 비어 있으면 '조회된 분할 결정 공시가 없음'이지, 분할 사실이 없다는 단정이 아님
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 13
NAME = "company_split"
TITLE = "회사분할 결정"
KIND = "period"            # none | period | year | multi_year

# ── 가져올 필드 (실제 응답과 다르면 test_all_tools.py 결과를 보고 수정) ──
FIELDS = [
    "dv_mth",                            # 팀 표 핵심 값
    "dv_rt",                             # 팀 표 핵심 값
    "dvfcmp_cmpnm",                      # 팀 표 핵심 값
    "bddd",                              # 추가 후보 (내 기억 기준, 테스트로 확인)
]


def get_company_split(corp_code: str, bgn_de: str, end_de: str, raw: bool = False) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    bgn_de, end_de: 조회 기간 YYYYMMDD
    raw: True면 필드를 추리지 않고 응답 원본을 그대로 돌려줌 (필드명 확인용)
    """
    data = call_api("cmpDvDecsn.json", {"corp_code": corp_code, "bgn_de": bgn_de, "end_de": end_de})

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


RUN = get_company_split


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
