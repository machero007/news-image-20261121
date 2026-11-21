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
# PNG layout: 8-byte signature, then the IHDR chunk (length 4B, type 4B,
# width 4B big-endian, height 4B big-endian). The bounty image is 1024x1024.
IHDR_OFFSET = 16
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1 << 20  # 1 MiB


def _check_png(payload: bytes) -> None:
    """Fail loudly if the bundled image is not the expected 1024x1024 PNG."""
    if not payload.startswith(PNG_MAGIC):
        raise SystemExit("entry.png does not start with the PNG magic bytes")
    if len(payload) < IHDR_OFFSET + 8:
        raise SystemExit("entry.png is too short to contain an IHDR chunk")
    if payload[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk after the signature")
    width = int.from_bytes(payload[IHDR_OFFSET:IHDR_OFFSET + 4], "big")
    height = int.from_bytes(payload[IHDR_OFFSET + 4:IHDR_OFFSET + 8], "big")
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(
            f"entry.png is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    if len(payload) > MAX_BYTES:
        raise SystemExit(
            f"entry.png is {len(payload)} bytes, over the 1 MiB limit"
        )


def main() -> int:
    payload = SOURCE.read_bytes()
    _check_png(payload)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(payload)
    print(f"wrote {DEST} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
