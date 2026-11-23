"""
14개 도구 스모크 테스트: 회사 1곳, 2025 사업보고서 1건씩만 호출 (약 20번)

사용법:
  python test_all_tools.py            # 삼성전자
  python test_all_tools.py 카카오      # 회사 지정
"""
import inspect
import sys

from corp_codes import load_corp_codes, resolve
from dart_client import BGN_DE, END_DE, DartApiError
from runner import call_tool
from tools import TOOLS

YEAR, REPORT = "2025", "11011"

company = sys.argv[1] if len(sys.argv) > 1 else "삼성전자"
found = resolve(load_corp_codes(), company)
if not found:
    raise SystemExit(f"[못찾음] {company}")
corp = found[0]
print(f"대상: {corp['corp_name']} ({corp['corp_code']}), {YEAR}년 {REPORT}\n")

results = []   # (번호, 제목, 결과, 상세, 실제 필드 목록)
for n in sorted(TOOLS):
    mod = TOOLS[n]
    try:
        rows = call_tool(mod, [corp], YEAR, REPORT)
    except DartApiError as e:
        results.append((n, mod.TITLE, "오류", str(e), None))
        continue
    except Exception as e:
        results.append((n, mod.TITLE, "코드오류", f"{type(e).__name__}: {e}", None))
        continue
    if not rows:
        results.append((n, mod.TITLE, "비어있음", "0건", None))
        continue

    keys = [k for k in rows[0] if k != "_source"]
    none_fields = [k for k in keys if all(r.get(k) is None for r in rows)]
    if len(none_fields) == len(keys):
        status = "필드불일치"
    elif none_fields:
        status = "일부필드없음"
    else:
        status = "OK"

    raw_keys = None
    if status != "OK" and "raw" in inspect.signature(mod.RUN).parameters:
        code = corp["corp_code"]
        if mod.KIND == "year":
            raw_rows = mod.RUN(code, YEAR, REPORT, raw=True)
        elif mod.KIND == "period":
            raw_rows = mod.RUN(code, BGN_DE, END_DE, raw=True)
        else:
            raw_rows = mod.RUN(code, raw=True)
        if raw_rows:
            raw_keys = list(raw_rows[0].keys())
    results.append((n, mod.TITLE, status, f"{len(rows)}건, 비어있는 필드: {none_fields or '없음'}", raw_keys))

print(f"{'번호':<4}{'도구':<26}{'결과':<12}상세")
for n, title, status, detail, _ in results:
    print(f"{n:<4}{title:<26}{status:<12}{detail}")

print("\n--- 확인이 필요한 도구 ---")
for n, title, status, detail, raw_keys in results:
    if status == "오류":
        print(f"[{n}] {title}: {detail}  → 엔드포인트/인자를 개발가이드와 대조 (020이면 호출 한도 초과)")
    elif status == "코드오류":
        print(f"[{n}] {title}: {detail}  → 도구 파일 코드 확인")
    elif status in ("필드불일치", "일부필드없음"):
        extra = f"\n     실제 응답 필드: {raw_keys}" if raw_keys else ""
        print(f"[{n}] {title}: {detail}  → FIELDS 수정{extra}")
    elif status == "비어있음":
        print(f"[{n}] {title}: 데이터 없음  (영업정지·분할·대량보유 등 이벤트는 없는 게 정상일 수 있음)")
