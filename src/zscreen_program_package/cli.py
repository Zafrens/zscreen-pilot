"""Console entry point: python -m zscreen_program_package.verify equivalent."""

from __future__ import annotations

import argparse
from pathlib import Path

from .verify import verification_passed, verify_package


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="zscreen-program-package",
        description="Verify the Z-Screen Program Package")
    parser.add_argument("--root", default=".",
                        help="package root (default: current directory)")
    parser.add_argument("--full", action="store_true",
                        help="recalculate every manifested SHA-256 digest")
    arguments = parser.parse_args()
    results = verify_package(Path(arguments.root), full=arguments.full)
    for result in results:
        print(f"{result.status:4}  {result.check}: {result.detail}")
    print("RESULT:", "PASS" if verification_passed(results) else "FAIL")
    return 0 if verification_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
