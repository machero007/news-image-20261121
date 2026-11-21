#!/usr/bin/env python3
"""make.fun entry: Sum up 21 November's world news in one image.

The simplest allowed program: copy the image this repository holds
(entry.png) to /output/entry.png. Deterministic (same bytes every run),
no network access, no dependencies beyond the standard library.
"""
import os
import shutil


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(src, "/output/entry.png")


if __name__ == "__main__":
    main()
