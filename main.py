#!/usr/bin/env python3
"""Entry point for news-image-20261121 (make.fun daily news-image bounty).

Stdlib only. Verifies the bundled entry.png is a real PNG, then places a
byte-identical copy at /output/entry.png for the grader to read.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST = Path("/output") / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main() -> int:
    payload = SOURCE.read_bytes()
    if not payload.startswith(PNG_MAGIC):
        raise SystemExit("entry.png does not start with the PNG magic bytes")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(payload)
    print(f"wrote {DEST} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
