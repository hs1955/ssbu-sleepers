# scripts/img-ripper.py
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://tiermaker.com/images/chart/chart/super-smash-bros-ultimate-renders-with-echos-combinable-1070092/"
OUT = Path("images")

def main() -> None:
    OUT.mkdir(exist_ok=True)
    chars = json.loads(Path("data/fighters.json").read_text())["fighters"]
    for i, c in enumerate(chars, 1):
        dest = OUT / c["image"]
        if dest.exists():
            continue
        try:
            req = Request(BASE + c["image"], headers={"User-Agent": "Mozilla/5.0"})
            dest.write_bytes(urlopen(req).read())
            print(f"[{i:>2}/{len(chars)}] ✓ {c['image']}")
        except Exception as e:
            print(f"[{i:>2}/{len(chars)}] ✗ {c['image']}: {e}")
        time.sleep(0.1)  # be a good citizen

if __name__ == "__main__":
    main()