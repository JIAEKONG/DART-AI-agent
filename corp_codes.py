"""회사 이름 -> 고유번호(corp_code) 변환 (상장사만)"""
import io
import json
import zipfile
import xml.etree.ElementTree as ET

import requests

from dart_client import API_KEY, BASE, OUT_DIR


def load_corp_codes() -> list[dict]:
    """corpCode.xml(전체 기업 목록)을 받아 dart_data/corp_codes.json에 캐시한다."""
    OUT_DIR.mkdir(exist_ok=True)
    cache = OUT_DIR / "corp_codes.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))

    if not API_KEY:
        raise RuntimeError("DART_API_KEY가 없어요. .env 파일에 DART_API_KEY=본인키 를 적어주세요.")
    try:
        r = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"corpCode.xml 호출 실패: {type(e).__name__}") from None
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        root = ET.fromstring(z.read(z.namelist()[0]))
    corps = [
        {
            "corp_code": n.findtext("corp_code", "").strip(),
            "corp_name": n.findtext("corp_name", "").strip(),
            "stock_code": n.findtext("stock_code", "").strip(),
        }
        for n in root.iter("list")
    ]
    cache.write_text(json.dumps(corps, ensure_ascii=False), encoding="utf-8")
    return corps


def normalize(name: str) -> str:
    return name.replace("(주)", "").replace("㈜", "").replace(" ", "").strip().upper()


def resolve(corps: list[dict], query: str) -> list[dict]:
    """상장사(stock_code 있음) 중 정규화한 이름이 정확히 일치하는 기업. 없으면 접두어 일치."""
    listed = [c for c in corps if c["stock_code"]]
    q = normalize(query)
    exact = [c for c in listed if normalize(c["corp_name"]) == q]
    return exact or [c for c in listed if normalize(c["corp_name"]).startswith(q)][:5]
