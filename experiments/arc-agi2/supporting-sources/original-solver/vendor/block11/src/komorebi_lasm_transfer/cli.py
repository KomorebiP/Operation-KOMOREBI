"""Command-line entry point for the Block 11 retrospective audit.

The label-blind prediction freeze remains a separate explicit module:
``python -m komorebi_lasm_transfer.freeze``.

Author: Komorebi P.
"""
from __future__ import annotations

from .audit import main


if __name__ == "__main__":
    raise SystemExit(main())

