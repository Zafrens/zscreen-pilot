"""Run package verification without requiring an installed console script."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Keep verification side-effect free: importing the package must not write
# bytecode caches (absolute local paths would leak into .pyc files).
sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from zscreen_program_package.verify import verification_passed, verify_package  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the Z-Screen Program Package")
    parser.add_argument("--full", action="store_true",
                        help="recalculate every manifested SHA-256 digest")
    arguments = parser.parse_args()
    results = verify_package(ROOT, full=arguments.full)
    for result in results:
        print(f"{result.status:4}  {result.check}: {result.detail}")
    print("RESULT:", "PASS" if verification_passed(results) else "FAIL")
    return 0 if verification_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
