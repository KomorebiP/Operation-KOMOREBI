from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def scrub_pdf(path: Path, *, title: str, subject: str, author: str = "Komorebi P.") -> None:
    reader = PdfReader(str(path))
    writer = PdfWriter()
    # Clone pages, annotations, outlines, named destinations, and document structure.
    writer.clone_document_from_reader(reader)
    writer.metadata = {
        "/Title": title,
        "/Subject": subject,
        "/Author": author,
    }
    writer.xmp_metadata = None

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        writer.write(handle)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rewrite a PDF with author-only production metadata.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--author", default="Komorebi P.")
    args = parser.parse_args()
    scrub_pdf(args.pdf, title=args.title, subject=args.subject, author=args.author)


if __name__ == "__main__":
    main()
