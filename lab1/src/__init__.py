from pathlib import Path
import sys

_COMMON_PATH = Path(__file__).resolve().parents[2] / "common"
_common_str = str(_COMMON_PATH)
if _common_str not in sys.path:
    sys.path.insert(0, _common_str)
