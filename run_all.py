"""
OpenDART 데이터 수집기 (도구 1~14번, 도구별 파일은 tools/ 폴더)

사용법:
  python run_all.py          # 14개 전부
  python run_all.py 6 7      # 6번, 7번 도구만

결과:
  ./dart_data/<도구이름>.json   도구별, 기업별로 묶음
  ./dart_data/all.json          dart_data 안의 도구별 결과를 합친 파일

설정(연도, 보고서 종류, 조회 기간)은 dart_client.py 맨 위에서 바꿔요.
"""
import json
import sys

from dart_client import OUT_DIR, DartLimitError
from corp_codes import load_corp_codes, resolve
from runner import run_tool
from tools import TOOLS

# 수집할 기업 (필요하면 수정하세요)
COMPANIES = [
    "AK홀딩스",
    "BGF",
    "BGF리테일",
    "BNK금융지주",
    "BYC",
    "CJ",
    "CJ CGV",
    "CJ대한통운",
    "CJ씨푸드",
]


def main():
    numbers = [int(a) for a in sys.argv[1:]] or sorted(TOOLS)
    unknown = [n for n in numbers if n not in TOOLS]
    if unknown:
        raise SystemExit(f"없는 도구 번호: {unknown} (1~{max(TOOLS)})")

    corps = load_corp_codes()
    targets = []
    for q in COMPANIES:
        found = resolve(corps, q)
        if not found:
            print(f"[못찾음] {q}")
            continue
        if len(found) > 1:
            print(f"[여러개] {q} → {[c['corp_name'] for c in found]} (첫 번째 사용)")
        targets.append(found[0])
    targets = list({c["corp_code"]: c for c in targets}.values())  # 중복 제거
    print("대상:", [f"{c['corp_name']}({c['stock_code']})" for c in targets])

    OUT_DIR.mkdir(exist_ok=True)
    for n in numbers:
        mod = TOOLS[n]
        print(f"\n[{n}] {mod.TITLE}")
        try:
            result = run_tool(mod, targets)
        except DartLimitError as e:
            print(f"\n호출 한도 초과로 중단했어요: {e}")
            print("완료된 도구 결과는 저장돼 있어요. 내일 남은 번호만 다시 실행하세요.")
            break
        for name, rows in result.items():
            print(f"  {name:<14} {len(rows)}건")
        (OUT_DIR / f"{mod.NAME}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # all.json: 저장된 도구별 파일을 전부 합침 (일부만 실행해도 기존 결과가 유지됨)
    data = {}
    for n in sorted(TOOLS):
        f = OUT_DIR / f"{TOOLS[n].NAME}.json"
        if f.exists():
            data[TOOLS[n].NAME] = json.loads(f.read_text(encoding="utf-8"))
    (OUT_DIR / "all.json").write_text(
        json.dumps({"companies": targets, "data": data}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n저장 완료 → {OUT_DIR}")


if __name__ == "__main__":
    main()
