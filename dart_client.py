"""
DART API 공통 클라이언트 + 공통 설정

모든 도구 파일(tools/tNN_*.py)은 `from dart_client import call_api`로 이 파일을 씁니다.
키는 .env 파일의 DART_API_KEY에서만 읽어요. (코드에 직접 적지 않기 / .env는 깃에 올리지 않기)

call_api 규칙 (팀 저장소에 이미 dart_client.py가 있다면 이 규칙만 맞추면 돼요)
  - call_api("company.json", {"corp_code": "..."}) 처럼 endpoint에 .json을 붙여 부른다
  - 000(정상) -> 응답 dict 그대로
  - 013(데이터 없음) -> {"status": "013", "message": ..., "list": []}
  - 그 외 오류 -> DartApiError (020 = 호출 한도 초과 -> DartLimitError)
"""
import hashlib
import json
import os
import time
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("DART_API_KEY")
BASE = "https://opendart.fss.or.kr/api"

# ───────────── 수집 설정 (run_all.py, test_all_tools.py가 읽음) ─────────────
YEARS = [2023, 2024, 2025]                              # 사업연도
REPORT_CODES = ["11011", "11012", "11013", "11014"]     # 사업 / 반기 / 1분기 / 3분기 (회의 결정: 전부 포함)
BGN_DE = "20230101"                                     # 공시검색, 영업정지, 회사분할 조회 시작일
END_DE = date.today().strftime("%Y%m%d")

# ───────────── 동작 설정 ─────────────
USE_CACHE = True      # 같은 호출은 .cache에 저장해서 재사용 (최신값이 필요하면 .cache 폴더를 지우세요)
SLEEP = 0.15          # 실제 호출 뒤 대기(초)
RETRIES = 3

ROOT = Path(__file__).parent
CACHE_DIR = ROOT / ".cache"
OUT_DIR = ROOT / "dart_data"


class DartApiError(RuntimeError):
    pass


class DartLimitError(DartApiError):
    """status 020: 요청 한도 초과"""


def call_api(endpoint: str, params: dict | None = None) -> dict:
    if not API_KEY:
        raise DartApiError("DART_API_KEY가 없어요. .env 파일에 DART_API_KEY=본인키 를 적어주세요.")
    params = dict(params or {})

    cache_file = None
    if USE_CACHE:
        CACHE_DIR.mkdir(exist_ok=True)
        key = hashlib.md5(json.dumps([endpoint, params], sort_keys=True).encode()).hexdigest()
        cache_file = CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))

    last_error = "unknown"
    for i in range(RETRIES):
        try:
            r = requests.get(f"{BASE}/{endpoint}", params={"crtfc_key": API_KEY, **params}, timeout=30)
            r.raise_for_status()
            data = r.json()
            break
        except (requests.RequestException, ValueError) as e:
            last_error = type(e).__name__   # 오류 메시지에 URL(=키)이 찍히지 않도록 종류만 남김
            time.sleep(2 ** i)
    else:
        raise DartApiError(f"{endpoint} 호출 실패: {last_error}")
    time.sleep(SLEEP)

    status = data.get("status")
    if status == "013":
        data = {"status": "013", "message": data.get("message"), "list": []}
    elif status != "000":
        error_class = DartLimitError if status == "020" else DartApiError
        raise error_class(f"{endpoint} 오류 {status}: {data.get('message')}")

    if cache_file is not None:
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data
