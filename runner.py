"""도구 실행 도우미: 도구 파일의 KIND에 맞춰 호출 방식을 정하고, 단독 실행(cli)을 제공한다.

KIND 4종 (도구 파일에 적혀 있음)
  none        RUN(corp_code)                          기업개황, 대량보유
  period      RUN(corp_code, bgn_de, end_de)          공시목록, 영업정지, 회사분할
  year        RUN(corp_code, bsns_year, reprt_code)   정기보고서 계열
  multi_year  RUN(corp_codes, bsns_year, reprt_code)  다중회사 주요계정/지표 (회사 여러 개를 한 번에)
"""
import json
import sys

from dart_client import BGN_DE, END_DE, REPORT_CODES, YEARS, DartApiError, DartLimitError
from corp_codes import load_corp_codes, resolve


def as_list(x) -> list[dict]:
    return x if isinstance(x, list) else [x]


def call_tool(mod, corps: list[dict], year: str = "2025", report: str = "11011") -> list[dict]:
    """도구 1회 호출. corps는 [{'corp_code':..., 'corp_name':...}, ...]"""
    codes = [c["corp_code"] for c in corps]
    if mod.KIND == "none":
        return as_list(mod.RUN(codes[0]))
    if mod.KIND == "period":
        return as_list(mod.RUN(codes[0], BGN_DE, END_DE))
    if mod.KIND == "year":
        return as_list(mod.RUN(codes[0], year, report))
    if mod.KIND == "multi_year":
        return as_list(mod.RUN(codes, year, report))
    raise ValueError(f"{mod.__name__}: 알 수 없는 KIND '{mod.KIND}'")


def run_tool(mod, corps: list[dict]) -> dict:
    """도구 하나를 회사 목록 전체에 실행해서 {회사이름: 행 리스트}로 돌려준다.
    year / multi_year 도구는 YEARS x REPORT_CODES 조합을 모두 호출한다.
    호출 한도 초과(020)는 DartLimitError로 그대로 올려보낸다."""
    reports = getattr(mod, "REPORT_CODES", None) or REPORT_CODES
    result = {c["corp_name"]: [] for c in corps}

    def safe(label, fn):
        try:
            return fn()
        except DartLimitError:
            raise
        except Exception as e:
            print(f"  ! {label} / {mod.NAME}: {e}")
            return []

    if mod.KIND == "multi_year":
        by_code = {c["corp_code"]: c["corp_name"] for c in corps}
        batch = getattr(mod, "MAX_COMPANIES_PER_CALL", 100)
        for i in range(0, len(corps), batch):
            chunk = corps[i:i + batch]
            for y in YEARS:
                for rc in reports:
                    rows = safe(f"묶음{i // batch + 1} {y}/{rc}", lambda: call_tool(mod, chunk, str(y), rc))
                    for row in rows:
                        name = by_code.get(row.get("corp_code"))
                        if name:
                            result[name].append(row)
                        else:
                            result.setdefault("_unmatched", []).append(row)
    elif mod.KIND == "year":
        for c in corps:
            for y in YEARS:
                for rc in reports:
                    result[c["corp_name"]] += safe(f"{c['corp_name']} {y}/{rc}",
                                                   lambda: call_tool(mod, [c], str(y), rc))
    else:  # none, period
        for c in corps:
            result[c["corp_name"]] = safe(c["corp_name"], lambda: call_tool(mod, [c]))
    return result


def cli(mod):
    """도구 파일 단독 실행: python -m tools.파일이름 회사이름 [연도] [보고서코드]"""
    if len(sys.argv) < 2:
        print("사용법: python -m tools.파일이름 회사이름 [연도] [보고서코드]")
        print("예시:   python -m tools.t06_employees 삼성전자 2025 11011")
        return
    found = resolve(load_corp_codes(), sys.argv[1])
    if not found:
        print(f"[못찾음] {sys.argv[1]}")
        return
    corp = found[0]
    year = sys.argv[2] if len(sys.argv) > 2 else str(YEARS[-1])
    report = sys.argv[3] if len(sys.argv) > 3 else "11011"
    try:
        rows = call_tool(mod, [corp], year, report)
    except DartApiError as e:
        print(f"오류: {e}")
        return
    print(f"[{mod.TITLE}] {corp['corp_name']} {year}/{report}: {len(rows)}건")
    print(json.dumps(rows[:5], ensure_ascii=False, indent=2))
