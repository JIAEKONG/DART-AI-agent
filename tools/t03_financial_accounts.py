"""
③ 다중회사 주요계정 조회 (1개~N개 회사 — 단일/비교 질문 모두 이걸로 처리)
질문 예시: "매출/영업이익/순이익/부채 얼마야?", "삼성전자랑 SK하이닉스 매출 비교해줘"
기반 API: fnlttMultiAcnt.json (DS003 / apiId 2019017)
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 3
NAME = "financial_accounts"
TITLE = "다중회사 주요계정"
KIND = "multi_year"      # none | period | year | multi_year
REPORT_CODES = None      # None이면 dart_client.REPORT_CODES(사업/반기/1분기/3분기) 사용. 예: ["11011"]

MAX_COMPANIES_PER_CALL = 100


def get_financial_accounts(
    corp_codes: list[str],
    bsns_year: str,
    reprt_code: str = "11011",
) -> list[dict]:
    """
    corp_codes: DART 고유번호 리스트 (1개~최대 100개)
    bsns_year: 사업연도 (예: "2023")
    reprt_code: 11011(사업보고서, 기본값) / 11012(반기) / 11013(1분기) / 11014(3분기)
    반환: 회사 x 계정명 조합의 리스트. corp_code로 회사를 구분해서 묶어야 함
    """
    if not corp_codes:
        raise ValueError("corp_codes는 최소 1개 이상 필요합니다.")
    if len(corp_codes) > MAX_COMPANIES_PER_CALL:
        raise ValueError(f"한 번에 최대 {MAX_COMPANIES_PER_CALL}개 회사까지만 조회 가능합니다.")

    data = call_api(
        "fnlttMultiAcnt.json",
        {
            "corp_code": ",".join(corp_codes),
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        },
    )

    items = data.get("list", [])
    return [
        {
            "corp_code": item.get("corp_code"),
            "stock_code": item.get("stock_code"),
            "fs_div": item.get("fs_div"),  # CFS(연결)/OFS(별도)
            "fs_nm": item.get("fs_nm"),
            "sj_div": item.get("sj_div"),  # BS(재무상태표)/IS(손익계산서)
            "account_nm": item.get("account_nm"),
            "thstrm_amount": item.get("thstrm_amount"),
            "frmtrm_amount": item.get("frmtrm_amount"),
            "bfefrmtrm_amount": item.get("bfefrmtrm_amount"),
            "currency": item.get("currency"),
            "_source": {
                "corp_code": item.get("corp_code"),
                "bsns_year": bsns_year,
                "reprt_code": reprt_code,
                "rcept_no": item.get("rcept_no"),
            },
        }
        for item in items
    ]


RUN = get_financial_accounts


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
