from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "admission-1.0"
MAX_BYTES = 300 * 1024
SAMPLES = {"cutover": "订单编码切换", "single": "单源演练"}
