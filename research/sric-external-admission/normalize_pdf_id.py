from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ID_PATTERN = re.compile(rb"/ID\[<([0-9A-Fa-f]{32})><([0-9A-Fa-f]{32})>\]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace the nondeterministic PDF trailer ID with a source-derived fixed ID."
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()

    pdf_bytes = args.pdf.read_bytes()
    matches = list(ID_PATTERN.finditer(pdf_bytes))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one PDF trailer ID, found {len(matches)}")
    fixed = hashlib.sha256(args.source.read_bytes()).hexdigest()[:32].encode("ascii")
    replacement = b"/ID[<" + fixed + b"><" + fixed + b">]"
    normalized = ID_PATTERN.sub(replacement, pdf_bytes, count=1)
    if len(normalized) != len(pdf_bytes):
        raise SystemExit("PDF ID normalization changed byte length")
    args.pdf.write_bytes(normalized)
    print(f"PDF_FIXED_ID={fixed.decode('ascii')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
