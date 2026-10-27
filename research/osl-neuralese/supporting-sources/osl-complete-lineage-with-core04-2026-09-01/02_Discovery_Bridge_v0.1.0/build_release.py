"""Create the checksum manifest and deterministic ZIP release."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
ZIP_PATH = ROOT.parent / f"{ROOT.name}.zip"
EXCLUDED_FILES = {"SHA256SUMS.txt"}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}


def release_files() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and path.name not in EXCLUDED_FILES
        and path.suffix != ".pyc"
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    ]


def main() -> int:
    files = release_files()
    lines = [
        f"{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}"
        for path in files
    ]
    manifest = ROOT / "SHA256SUMS.txt"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    files = release_files() + [manifest]
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            relative = Path(ROOT.name) / path.relative_to(ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(2026, 9, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f"{ZIP_PATH} {sha256(ZIP_PATH.read_bytes()).hexdigest()} {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
