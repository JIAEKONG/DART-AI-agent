"""
① 기업개황 조회
질문 예시: "삼성전자 뭐 하는 회사야?"
기반 API: company.json (DS001 / apiId 2019002)
"""
from dart_client import call_api

# ── 도구 정보 (tools/__init__.py, run_all.py가 읽음) ──
NUMBER = 1
NAME = "company_overview"
TITLE = "기업개황"
KIND = "none"            # none | period | year | multi_year


def get_company_overview(corp_code: str) -> dict:
    """
    corp_code: DART 고유번호(8자리)
    반환: 회사 기본정보 + 출처(corp_code)
    """
    data = call_api("company.json", {"corp_code": corp_code})

    return {
        "corp_name": data.get("corp_name"),
        "corp_name_eng": data.get("corp_name_eng"),
        "stock_name": data.get("stock_name"),
        "stock_code": data.get("stock_code"),
        "ceo_nm": data.get("ceo_nm"),
        "corp_cls": data.get("corp_cls"),
        "adres": data.get("adres"),
        "induty_code": data.get("induty_code"),
        "est_dt": data.get("est_dt"),
        "acc_mt": data.get("acc_mt"),
        "_source": {
            "corp_code": corp_code,
        },
    }


RUN = get_company_overview


if __name__ == "__main__":
    import sys
    from runner import cli
    cli(sys.modules[__name__])
