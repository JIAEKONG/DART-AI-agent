"""tools 폴더의 tNN_*.py 파일을 자동으로 모아서 TOOLS[번호]로 꺼내 쓸 수 있게 한다.

도구 파일마다 꼭 있어야 하는 것: NUMBER, NAME, TITLE, KIND, RUN
"""
import importlib
import pkgutil

TOOLS = {}
_REQUIRED = ("NUMBER", "NAME", "TITLE", "KIND", "RUN")

for _m in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
    if not (_m.name.startswith("t") and _m.name[1:3].isdigit()):
        continue
    _mod = importlib.import_module(f"{__name__}.{_m.name}")
    _missing = [a for a in _REQUIRED if not hasattr(_mod, a)]
    if _missing:
        raise ImportError(f"{_m.name}.py에 {_missing} 가 없어요.")
    if _mod.NUMBER in TOOLS:
        raise ImportError(
            f"도구 번호 {_mod.NUMBER}가 중복이에요: {TOOLS[_mod.NUMBER].__name__}, {_mod.__name__} "
            "(예전 파일이 남아 있다면 지워주세요)"
        )
    TOOLS[_mod.NUMBER] = _mod
