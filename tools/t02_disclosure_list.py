"""
② 공시목록 조회
질문 예시: "최근에 낸 공시 뭐 있어?"
기반 API: list.json (DS001 / apiId 2019001)
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 2
NAME = "disclosure_list"
TITLE = "공시검색"
KIND = "period"          # none | period | year | multi_year


def get_disclosure_list(
    corp_code: str,
    bgn_de: str,
    end_de: str,
    page_count: int = 20,
) -> list[dict]:
    """
    corp_code: DART 고유번호(8자리)
    bgn_de, end_de: 조회 기간 YYYYMMDD
    """
    data = call_api(
        "list.json",
        {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_count": str(page_count),
        },
    )

    items = data.get("list", [])
    return [
        {
            "rcept_no": item.get("rcept_no"),
            "report_nm": item.get("report_nm"),
            "rcept_dt": item.get("rcept_dt"),
            "flr_nm": item.get("flr_nm"),
            "_source": {"corp_code": corp_code, "rcept_no": item.get("rcept_no")},
        }
        for item in items
    ]


RUN = get_disclosure_list


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
