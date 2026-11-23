"""
④ 다중회사 주요 재무지표 조회 (1개~N개 회사)
질문 예시: "ROE/부채비율 얼마야?", "두 회사 중 부채비율 누가 더 낮아?"
기반 API: fnlttCmpnyIndx.json (DS003 / apiId 2022002)
주의: 2023년 3분기 이후 사업연도부터만 데이터 제공됨
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 4
NAME = "financial_indicators"
TITLE = "다중회사 주요 재무지표"
KIND = "multi_year"      # none | period | year | multi_year
REPORT_CODES = None      # None이면 dart_client.REPORT_CODES(사업/반기/1분기/3분기) 사용. 예: ["11011"]

IDX_CL_CODES = {
    "수익성지표": "M210000",
    "안정성지표": "M220000",
    "성장성지표": "M230000",
    "활동성지표": "M240000",
}

MAX_COMPANIES_PER_CALL = 100


def get_financial_indicators(
    corp_codes: list[str],
    bsns_year: str,
    idx_cl_code: str = "M220000",
    reprt_code: str = "11011",
) -> list[dict]:
    """
    corp_codes: DART 고유번호 리스트 (1개~최대 100개)
    idx_cl_code: IDX_CL_CODES 값 중 하나. 기본값 안정성지표(부채비율 등 포함)
    """
    if not corp_codes:
        raise ValueError("corp_codes는 최소 1개 이상 필요합니다.")
    if len(corp_codes) > MAX_COMPANIES_PER_CALL:
        raise ValueError(f"한 번에 최대 {MAX_COMPANIES_PER_CALL}개 회사까지만 조회 가능합니다.")
    if idx_cl_code not in IDX_CL_CODES.values():
        raise ValueError(f"idx_cl_code는 {list(IDX_CL_CODES.values())} 중 하나여야 합니다.")

    data = call_api(
        "fnlttCmpnyIndx.json",
        {
            "corp_code": ",".join(corp_codes),
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "idx_cl_code": idx_cl_code,
        },
    )

    items = data.get("list", [])
    return [
        {
            "corp_code": item.get("corp_code"),
            "stock_code": item.get("stock_code"),
            "idx_cl_nm": item.get("idx_cl_nm"),
            "idx_nm": item.get("idx_nm"),
            "idx_val": item.get("idx_val"),
            "_source": {
                "corp_code": item.get("corp_code"),
                "bsns_year": bsns_year,
                "reprt_code": reprt_code,
                "stlm_dt": item.get("stlm_dt"),
            },
        }
        for item in items
    ]


def get_financial_indicators_all(
    corp_codes: list[str],
    bsns_year: str,
    reprt_code: str = "11011",
) -> list[dict]:
    """지표 분류 4종(수익성·안정성·성장성·활동성)을 모두 조회해서 합친다. (일괄 수집용)"""
    rows = []
    for code in IDX_CL_CODES.values():
        rows += get_financial_indicators(corp_codes, bsns_year, code, reprt_code)
    return rows


RUN = get_financial_indicators_all


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
