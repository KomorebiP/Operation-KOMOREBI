#!/usr/bin/env python3
"""Read-only integrity checks for the Paper XI release (Python 3.10+, PyMuPDF).

    python tools/verify_release.py --output /outside/release/integrity.json
    python tools/verify_release.py --root /unpacked/release \
        --zip /outside/release.zip --output /outside/archive-integrity.json

--output is a JSON FILE outside the release. No release files are written, no
archive is extracted, and no compiler or network access is invoked. Exit status
is zero only when every required check passes. A missing final manifest, build
record, or required visual signoff is a failure, including during preflight.

The Lean check is a source-token scan, not a kernel check or an axiom audit.
Catalogue totals are retained lexical counts, not a new declaration census.
PDF link checks establish local destinations and bounds, not visual usability.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any
from urllib.parse import unquote, urlsplit
import zipfile

sys.dont_write_bytecode = True
try:
    import fitz
except ImportError:
    fitz = None

KINDS = ("traditional", "visual_guide", "lean_guide")
GUIDE = "publication/source/lean_guide"
EVIDENCE = "evidence/release_1_1"
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fingerprint(root: Path) -> str:
    """The exact sorted-path/NUL/binary-hash algorithm in build_readers.py."""
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            h.update(str(path.relative_to(root)).encode() + b"\0"
                     + bytes.fromhex(sha256(path)))
    return h.hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object)


def safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ValueError(f"Invalid relative path: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ValueError(f"Unsafe or noncanonical relative path: {value!r}")
    if PurePosixPath(value).is_absolute():
        raise ValueError(f"Absolute path: {value!r}")
    return value


def positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def lean_comment_mask(source: str) -> tuple[str, list[str]]:
    """Mask nested Lean comments while preserving line/column offsets.

    Strings and quoted identifiers are preserved, so this conservative scan
    also flags the requested words inside them for manual interpretation. This
    avoids hiding code interpolated into strings. It is not a Lean parser.
    """
    out = list(source)
    i, depth = 0, 0
    quote: str | None = None
    issues: list[str] = []
    while i < len(source):
        if depth:
            if source.startswith("/-", i):
                depth += 1
                out[i:i + 2] = "  "
                i += 2
            elif source.startswith("-/", i):
                depth -= 1
                out[i:i + 2] = "  "
                i += 2
            else:
                if source[i] not in "\r\n":
                    out[i] = " "
                i += 1
        elif quote is not None:
            if source.startswith(quote, i):
                i += len(quote)
                quote = None
            elif quote == '"' and source[i] == "\\":
                i += 2
            else:
                i += 1
        elif source.startswith("--", i):
            end = source.find("\n", i)
            if end < 0:
                end = len(source)
            out[i:end] = " " * (end - i)
            i = end
        elif source.startswith("/-", i):
            depth = 1
            out[i:i + 2] = "  "
            i += 2
        elif source[i] == "«":
            quote = "»"
            i += 1
        elif source[i] == '"':
            quote = '"'
            i += 1
        elif source[i] == "r" and (i == 0 or not source[i - 1].isalnum()):
            raw = re.match(r'r(#+)"', source[i:])
            if raw:
                quote = '"' + raw.group(1)
                i += len(raw.group())
            else:
                i += 1
        else:
            i += 1
    if depth:
        issues.append("Unterminated block comment")
    if quote:
        issues.append("Unterminated string or quoted identifier")
    return "".join(out), issues


@dataclass(frozen=True)
class PDFRef:
    number: int
    generation: int


class PDFName(str):
    pass


def pdf_bytes_text(data: bytes) -> str:
    if data.startswith((b"\xfe\xff", b"\xff\xfe")):
        return data.decode("utf-16")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


class PDFObjectParser:
    """Parse MuPDF's normalized object text, without reading PDF streams.

    Used to inspect inline, indirect, outline, and open-action dictionaries;
    high-level page-link APIs alone can omit malformed or non-page actions.
    """
    def __init__(self, text: str):
        self.text, self.i = text, 0

    def whitespace(self) -> None:
        while self.i < len(self.text):
            if self.text[self.i].isspace() or self.text[self.i] == "\0":
                self.i += 1
            elif self.text[self.i] == "%":
                end = self.text.find("\n", self.i)
                self.i = len(self.text) if end < 0 else end + 1
            else:
                return

    def value(self, depth: int = 0) -> Any:
        if depth > 100:
            raise ValueError("PDF object nesting exceeds 100")
        self.whitespace()
        s, i = self.text, self.i
        if i >= len(s):
            raise ValueError("Unexpected end of PDF object")
        if s.startswith("<<", i):
            self.i += 2
            result = {}
            while True:
                self.whitespace()
                if s.startswith(">>", self.i):
                    self.i += 2
                    return result
                key = self.value(depth + 1)
                if not isinstance(key, PDFName) or key in result:
                    raise ValueError("Invalid or duplicate PDF dictionary key")
                result[key] = self.value(depth + 1)
        if s[i] == "[":
            self.i += 1
            result = []
            while True:
                self.whitespace()
                if self.i < len(s) and s[self.i] == "]":
                    self.i += 1
                    return result
                result.append(self.value(depth + 1))
        if s[i] == "/":
            self.i += 1
            start = self.i
            while self.i < len(s) and not s[self.i].isspace() and s[self.i] not in "()<>[]{}/%":
                self.i += 1
            name = s[start:self.i]
            decoded = re.sub(r"#([0-9A-Fa-f]{2})", lambda m: chr(int(m[1], 16)), name)
            return PDFName(decoded)
        if s[i] == "(":
            self.i += 1
            data = bytearray()
            nesting = 1
            escapes = {"n": 10, "r": 13, "t": 9, "b": 8, "f": 12}
            while self.i < len(s):
                char = s[self.i]
                self.i += 1
                if char == "\\":
                    if self.i >= len(s):
                        break
                    char = s[self.i]
                    self.i += 1
                    if char in "\r\n":
                        if char == "\r" and self.i < len(s) and s[self.i] == "\n":
                            self.i += 1
                        continue
                    if char in "01234567":
                        digits = char
                        while len(digits) < 3 and self.i < len(s) and s[self.i] in "01234567":
                            digits += s[self.i]
                            self.i += 1
                        data.append(int(digits, 8) & 255)
                    elif char in escapes:
                        data.append(escapes[char])
                    else:
                        data.extend(char.encode("utf-8"))
                elif char == "(":
                    nesting += 1
                    data.append(40)
                elif char == ")":
                    nesting -= 1
                    if not nesting:
                        return pdf_bytes_text(bytes(data))
                    data.append(41)
                else:
                    data.extend(char.encode("utf-8"))
            raise ValueError("Unterminated PDF string")
        if s[i] == "<":
            end = s.find(">", i + 1)
            if end < 0:
                raise ValueError("Unterminated PDF hex string")
            value = re.sub(r"\s", "", s[i + 1:end])
            if len(value) % 2:
                value += "0"
            self.i = end + 1
            return pdf_bytes_text(bytes.fromhex(value))
        token = re.match(r"[^\s\x00()<>\[\]{}/%]+", s[i:])
        if token is None:
            raise ValueError(f"Unexpected PDF token at {i}")
        word = token.group()
        self.i += len(word)
        if re.fullmatch(r"[+-]?\d+", word):
            number = int(word)
            end = self.i
            self.whitespace()
            ref = re.match(r"(\d+)\s+R\b", s[self.i:])
            if ref:
                self.i += len(ref.group())
                return PDFRef(number, int(ref[1]))
            self.i = end
            return number
        if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)", word):
            return float(word)
        return {"null": None, "true": True, "false": False}.get(word, word)


class Verifier:
    def __init__(self, root: Path):
        self.root = root
        self.report: dict[str, Any] = {
            "schema_version": 1,
            "tool": "tools/verify_release.py",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "scope": "Release integrity, retained source/excerpt correspondence, local PDF navigation, and build-record consistency",
            "lean_scope": "Conservative token scan excluding comments; no Lean compilation or kernel/axiom audit",
            "checks": {}, "errors": [], "warnings": [],
        }
        self.manifest: dict[str, dict[str, Any]] = {}
        self.pdfs: dict[Path, dict[str, Any]] = {}
        self.visual: dict[str, dict[str, Any]] = {}

    def error(self, check: str, message: str, **details: Any) -> None:
        self.report["errors"].append({"check": check, "message": message, **details})

    def require(self, condition: bool, check: str, message: str, **details: Any) -> bool:
        if not condition:
            self.error(check, message, **details)
        return condition

    def local(self, relative: str, base: Path | None = None) -> Path:
        path = (base or self.root) / safe_relative(relative)
        if not path.resolve().is_relative_to(self.root):
            raise ValueError(f"Path escapes the release: {relative}")
        return path

    def run(self, name: str, function: Any) -> None:
        before = len(self.report["errors"])
        try:
            result = function() or {}
        except Exception as exc:
            self.error(name, f"{type(exc).__name__}: {exc}")
            result = {}
        result["status"] = "passed" if len(self.report["errors"]) == before else "failed"
        self.report["checks"][name] = result

    def check_manifest(self) -> dict[str, Any]:
        record = read_json(self.root / "MANIFEST.json")
        if record.get("schema_version") != 1 or not isinstance(record.get("files"), list):
            raise ValueError("MANIFEST.json must have schema_version 1 and a files list")
        entries = record["files"]
        for entry in entries:
            relative = safe_relative(entry["path"])
            if relative == "MANIFEST.json" or relative in self.manifest:
                self.error("manifest", "Excluded or duplicate manifest entry", path=relative)
                continue
            if not isinstance(entry.get("bytes"), int) or isinstance(entry["bytes"], bool) or entry["bytes"] < 0:
                raise ValueError(f"Invalid byte count for {relative}")
            if not isinstance(entry.get("sha256"), str) or not SHA_RE.fullmatch(entry["sha256"]):
                raise ValueError(f"Invalid SHA-256 for {relative}")
            self.manifest[relative] = entry
        actual: set[str] = set()
        for directory, directories, files in os.walk(self.root, followlinks=False):
            base = Path(directory)
            for name in list(directories):
                path = base / name
                if path.is_symlink():
                    self.error("manifest", "Symlink directory is not a portable release member", path=str(path.relative_to(self.root)))
                    directories.remove(name)
            for name in files:
                path = base / name
                relative = path.relative_to(self.root).as_posix()
                safe_relative(relative)
                actual.add(relative)
                if path.is_symlink() or not stat.S_ISREG(path.lstat().st_mode):
                    self.error("manifest", "Nonregular release member", path=relative)
        expected = set(self.manifest) | {"MANIFEST.json"}
        self.require(actual == expected, "manifest", "Release file set differs from manifest",
                     missing=sorted(expected - actual), extra=sorted(actual - expected))
        folded = Counter(x.casefold() for x in actual)
        self.require(all(n == 1 for n in folded.values()), "manifest", "Case-insensitive path collision")
        verified = 0
        for relative, entry in self.manifest.items():
            path = self.local(relative)
            if not path.is_file() or path.is_symlink():
                continue
            size_ok = self.require(path.stat().st_size == entry["bytes"], "manifest", "File byte count mismatch", path=relative)
            hash_ok = self.require(sha256(path) == entry["sha256"], "manifest", "File SHA-256 mismatch", path=relative)
            verified += int(size_ok and hash_ok)
        return {"manifest_sha256": sha256(self.root / "MANIFEST.json"),
                "listed_files": len(entries), "actual_files_including_manifest": len(actual),
                "files_verified": verified}

    def check_sources(self) -> dict[str, Any]:
        base = self.root / GUIDE
        catalog = read_json(base / "SOURCE_CATALOG.json")
        modules = catalog["modules"]
        if not isinstance(modules, dict):
            raise ValueError("SOURCE_CATALOG.modules is not an object")
        self.require(len(modules) == 423, "sources", "Expected 423 selected modules", found=len(modules))
        source_paths: set[Path] = set()
        all_declarations = []
        token_hits = []
        verified = 0
        for name, item in modules.items():
            self.require(item["module"] == name, "sources", "Module key/name mismatch", module=name)
            path = self.local(item["local_source_path"], base)
            self.require(path not in source_paths, "sources", "Duplicate local source path", module=name)
            source_paths.add(path)
            if self.require(path.is_file(), "sources", "Selected source is missing", module=name):
                verified += int(self.require(sha256(path) == item["sha256"], "sources", "Catalog source SHA-256 mismatch", module=name))
                source = path.read_text(encoding="utf-8")
                masked, issues = lean_comment_mask(source)
                for issue in issues:
                    self.error("sources", issue, module=name)
                for match in re.finditer(r"(?<![\w'])\b(sorry|admit|axiom)\b(?![\w'])", masked):
                    line = masked.count("\n", 0, match.start()) + 1
                    hit = {"module": name, "line": line, "token": match[1]}
                    token_hits.append(hit)
                    self.error("sources", "Requested proof-token scan found a non-comment occurrence", **hit)
            all_declarations.extend(dict(decl, module=name) for decl in item["declarations"])
        actual_sources = set((base / "sources").rglob("*.lean"))
        self.require(actual_sources == source_paths, "sources", "Production Lean file set differs from selected catalog",
                     extra=sorted(str(p.relative_to(base)) for p in actual_sources - source_paths),
                     missing=sorted(str(p.relative_to(base)) for p in source_paths - actual_sources))
        declarations = read_json(base / "DECLARATION_CATALOG.json")
        self.require(isinstance(declarations, list) and len(declarations) == 4342,
                     "sources", "Expected 4342 retained lexical declaration names", found=len(declarations))
        names = [decl["name"] for decl in declarations]
        duplicates = sorted(name for name, count in Counter(names).items() if count != 1)
        self.require(not duplicates, "sources", "Declaration names are not unique", duplicates=duplicates)
        canonical = lambda items: sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in items)
        self.require(canonical(declarations) == canonical(all_declarations), "sources", "Flat declaration catalog differs from module catalog")
        return {"selected_modules": len(modules), "source_hashes_verified": verified,
                "retained_lexical_declarations": len(declarations), "unique_names": len(set(names)),
                "placeholder_scan": {"tokens": ["sorry", "admit", "axiom"], "hits": token_hits,
                    "nested_comments_excluded": True, "strings_conservatively_retained": True,
                    "replaces_axiom_audit": False, "lean_compilation_performed": False}}

    def check_excerpts(self) -> dict[str, Any]:
        base = self.root / GUIDE
        excerpts = read_json(base / "EXCERPTS.json")
        modules = read_json(base / "SOURCE_CATALOG.json")["modules"]
        self.require(isinstance(excerpts, list) and len(excerpts) == 40, "excerpts", "Expected 40 excerpts", found=len(excerpts))
        ids = [entry["id"] for entry in excerpts]
        self.require(len(set(ids)) == len(ids), "excerpts", "Duplicate excerpt identifier")
        verified = 0
        for entry in excerpts:
            before = len(self.report["errors"])
            identifier = entry["id"]
            safe_relative(identifier)
            path = self.local(entry["source_path"], base)
            module = modules[entry["module"]]
            self.require(path == self.local(module["local_source_path"], base), "excerpts", "Excerpt source path differs from selected module", excerpt=identifier)
            self.require(sha256(path) == entry["source_sha256"] == module["sha256"], "excerpts", "Excerpt source hash mismatch", excerpt=identifier)
            raw = (base / "excerpts" / f"{identifier}.raw.txt").read_bytes()
            rendered = (base / "excerpts" / f"{identifier}.render.txt").read_bytes()
            for label, value in (("raw", raw), ("render", rendered)):
                self.require(hashlib.sha256(value).hexdigest() == entry[f"{label}_sha256"], "excerpts", f"Excerpt {label} hash mismatch", excerpt=identifier)
            raw_text, rendered_text = raw.decode("utf-8"), rendered.decode("utf-8")
            display_map = entry["display_escape_map"]
            forward, reverse = raw_text, rendered_text
            for token, character in display_map.items():
                self.require(len(character) == 1 and token == f"[U+{ord(character):04X}]", "excerpts", "Invalid display escape mapping", excerpt=identifier, token=token)
                forward = forward.replace(character, token)
                reverse = reverse.replace(token, character)
            self.require(forward == rendered_text and reverse == raw_text, "excerpts", "Display escape map does not round-trip exactly", excerpt=identifier)
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            first, last = entry["first_line"], entry["last_line"]
            if not (positive_int(first) and positive_int(last) and first <= last <= len(lines)):
                self.error("excerpts", "Invalid source line range", excerpt=identifier)
                continue
            rest, source_slice = "".join(lines[first - 1:]), "".join(lines[first - 1:last])
            content = raw_text.rstrip("\r\n")
            self.require(rest.startswith(raw_text), "excerpts", "Raw excerpt is not an exact source prefix at its declared first line", excerpt=identifier)
            self.require(first + len(content.splitlines()) - 1 == last, "excerpts", "Excerpt last content line differs from recorded line", excerpt=identifier)
            mode = entry["mode"]
            if mode == "contiguous proof excerpt":
                valid = source_slice.rstrip("\r\n") == content
            elif mode == "literal declaration excerpt; body omitted after a top-level assignment":
                valid = source_slice.startswith(content)
            else:
                valid = False
            self.require(valid, "excerpts", "Excerpt mode/source-slice mismatch", excerpt=identifier, mode=mode)
            for setup in entry.get("ambient_setup", []):
                line = setup["line"]
                self.require(positive_int(line) and line <= len(lines) and lines[line - 1].rstrip("\r\n") == setup["text"], "excerpts", "Ambient setup line differs from source", excerpt=identifier, line=line)
            verified += int(len(self.report["errors"]) == before)
        return {"excerpts": len(excerpts), "fully_verified": verified,
                "slice_policy": "Exact byte-derived text prefix at first_line; last nonempty line checked; proof slices complete, declaration slices may end within the final line"}

    def pdf(self, path: Path) -> dict[str, Any]:
        path = path.resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"PDF target is outside the release: {path}")
        if path not in self.pdfs:
            if fitz is None:
                raise RuntimeError("PyMuPDF is required: install pymupdf")
            doc = fitz.open(path)
            if not doc.is_pdf or doc.needs_pass or len(doc) == 0:
                doc.close()
                raise ValueError(f"Unreadable, encrypted, or empty PDF: {path.name}")
            self.pdfs[path] = {"doc": doc, "names": doc.resolve_names(),
                               "page_refs": {doc.page_xref(i): i for i in range(len(doc))},
                               "objects": {}, "path": path}
        return self.pdfs[path]

    def pdf_object(self, info: dict[str, Any], number: int) -> Any:
        if number not in info["objects"]:
            if not 0 < number < info["doc"].xref_length():
                raise ValueError(f"Invalid PDF object reference {number}")
            info["objects"][number] = PDFObjectParser(info["doc"].xref_object(number, compressed=True)).value()
        return info["objects"][number]

    def dereference(self, info: dict[str, Any], value: Any) -> Any:
        seen = set()
        while isinstance(value, PDFRef):
            if value.number in seen:
                raise ValueError("Cyclic PDF object reference")
            seen.add(value.number)
            value = self.pdf_object(info, value.number)
        return value

    def page_bound(self, info: dict[str, Any], page: Any, where: str) -> None:
        self.require(isinstance(page, int) and not isinstance(page, bool) and 0 <= page < len(info["doc"]),
                     "pdfs", "PDF destination page is out of bounds", file=info["path"].name, location=where, page=page, pages=len(info["doc"]))

    def named_destination(self, info: dict[str, Any], name: str, where: str) -> None:
        target = info["names"].get(name)
        if target is None:
            self.error("pdfs", "Unresolved named PDF destination", file=info["path"].name, location=where, name=name)
        else:
            self.page_bound(info, target.get("page"), where + " named=" + name)

    def destination(self, owner: dict[str, Any], target: dict[str, Any], value: Any, where: str) -> None:
        value = self.dereference(owner, value)
        if isinstance(value, dict) and "D" in value:
            value = self.dereference(owner, value["D"])
        if isinstance(value, str):
            self.named_destination(target, value, where)
        elif isinstance(value, list) and value:
            page = value[0]
            if isinstance(page, PDFRef):
                if owner is not target:
                    self.error("pdfs", "Remote destination uses a local page-object reference", file=owner["path"].name, location=where)
                    return
                page = target["page_refs"].get(page.number)
            self.page_bound(target, page, where)
        else:
            self.error("pdfs", "Unsupported or missing PDF destination", file=owner["path"].name, location=where, value=repr(value)[:250])

    def remote(self, owner: dict[str, Any], value: Any) -> dict[str, Any]:
        value = self.dereference(owner, value)
        if isinstance(value, dict):
            value = self.dereference(owner, value.get("UF", value.get("F")))
        if not isinstance(value, str) or not value:
            raise ValueError("Missing remote PDF file specification")
        if urlsplit(value).scheme or "\\" in value or Path(value).is_absolute():
            raise ValueError(f"Remote PDF target is not a portable local file: {value}")
        return self.pdf(owner["path"].parent / unquote(value))

    def uri(self, value: Any, info: dict[str, Any], where: str) -> None:
        self.require(isinstance(value, str), "pdfs", "Invalid URI action", file=info["path"].name, location=where)
        self.require("komorebi.invalid" not in unquote(str(value)).casefold(), "pdfs", "Unresolved placeholder URI", file=info["path"].name, location=where, uri=str(value))

    def named_action(self, value: Any, info: dict[str, Any], where: str) -> None:
        self.require(value in {"FirstPage", "LastPage", "NextPage", "PrevPage", "GoBack", "GoForward"},
                     "pdfs", "Unrecognized named viewer action", file=info["path"].name, location=where, action=str(value))

    def walk_pdf_actions(self, info: dict[str, Any], value: Any, where: str, counts: Counter) -> None:
        if isinstance(value, list):
            for i, child in enumerate(value):
                self.walk_pdf_actions(info, child, f"{where}[{i}]", counts)
        elif isinstance(value, dict):
            action = value.get("S")
            if action == "GoTo":
                counts["GoTo"] += 1
                self.destination(info, info, value.get("D"), where)
            elif action == "GoToR":
                counts["GoToR"] += 1
                self.destination(info, self.remote(info, value.get("F")), value.get("D"), where)
            elif action == "Named":
                counts["Named"] += 1
                self.named_action(value.get("N"), info, where)
            elif action == "URI":
                counts["URI"] += 1
                self.uri(self.dereference(info, value.get("URI")), info, where)
            if "Dest" in value:
                counts["direct_Dest"] += 1
                self.destination(info, info, value["Dest"], where + "/Dest")
            if "OpenAction" in value:
                opened = self.dereference(info, value["OpenAction"])
                if not isinstance(opened, dict):
                    counts["open_destination"] += 1
                    self.destination(info, info, opened, where + "/OpenAction")
            for key, child in value.items():
                self.walk_pdf_actions(info, child, where + "/" + str(key), counts)

    def check_pdfs(self) -> dict[str, Any]:
        paths = sorted((self.root / "publication/pdfs").glob("*.pdf"))
        self.require(len(paths) == 5, "pdfs", "Expected five publication PDFs", found=len(paths))
        summaries = []
        for path in paths:
            info = self.pdf(path)
            doc = info["doc"]
            before = len(self.report["errors"])
            counts: Counter = Counter()
            for name, target in info["names"].items():
                self.page_bound(info, target.get("page"), "destination-table:" + name)
            for page in doc:
                for link in page.get_links():
                    counts["annotation_links"] += 1
                    where = f"page:{page.number + 1},xref:{link.get('xref')}"
                    kind = link.get("kind")
                    if kind == fitz.LINK_GOTO:
                        self.page_bound(info, link.get("page"), where)
                    elif kind == fitz.LINK_GOTOR:
                        target = self.remote(info, link.get("file"))
                        if isinstance(link.get("page"), int) and link["page"] >= 0:
                            self.page_bound(target, link["page"], where)
                        else:
                            self.named_destination(target, link.get("nameddest", link.get("to", "")), where)
                    elif kind == fitz.LINK_NAMED:
                        if link.get("nameddest"):
                            self.named_destination(info, link["nameddest"], where)
                        else:
                            self.named_action(link.get("name"), info, where)
                    elif kind == fitz.LINK_URI:
                        self.uri(link.get("uri"), info, where)
            toc = doc.get_toc(simple=False)
            for i, entry in enumerate(toc):
                if entry[2] > 0:
                    self.page_bound(info, entry[2] - 1, f"outline:{i}")
            interesting = re.compile(r"/(?:S\s*/(?:GoToR?|Named|URI)\b|Dest\b|OpenAction\b)")
            for number in range(1, doc.xref_length()):
                text = doc.xref_object(number, compressed=True)
                if interesting.search(text):
                    try:
                        self.walk_pdf_actions(info, self.pdf_object(info, number), f"xref:{number}", counts)
                    except Exception as exc:
                        self.error("pdfs", f"PDF action inspection failed: {exc}", file=path.name, xref=number)
            summaries.append({"file": path.name, "pages": len(doc), "sha256": sha256(path),
                              "named_destinations": len(info["names"]), "outline_items": len(toc),
                              "action_counts": dict(counts), "status": "passed" if len(self.report["errors"]) == before else "failed"})
        return {"files": summaries, "page_counts_observed_not_prescribed": True,
                "external_URIs_preserved_without_network_validation": True,
                "navigation_scope": "All named destinations, page links, outline page targets, and raw GoTo/GoToR/Named/URI/direct-Dest/open actions"}

    def check_visual(self) -> dict[str, Any]:
        path = self.root / EVIDENCE / "VISUAL_REVIEW.json"
        if not path.exists():
            return {"present": False, "required_when_underfull_hboxes_exist": True}
        record = read_json(path)
        self.require(record.get("status") == "passed", "visual_review", "Visual review is not marked passed")
        for entry in record["reviews"]:
            name = safe_relative(entry["file"])
            if "/" in name or name in self.visual:
                raise ValueError(f"Invalid or duplicate visual-review filename: {name}")
            info = self.pdf(self.root / "publication/pdfs" / name)
            before = len(self.report["errors"])
            self.require(sha256(info["path"]) == entry["pdf_sha256"], "visual_review", "Visual review refers to different PDF bytes", file=name)
            for field in ("contact_pages", "detailed_pages"):
                pages = entry.get(field, [])
                self.require(isinstance(pages, list), "visual_review", "Visual page list must be a list", file=name, field=field)
                for page in pages:
                    self.require(positive_int(page) and page <= len(info["doc"]), "visual_review", "Visual review page is out of bounds", file=name, field=field, page=page)
            self.require(isinstance(entry.get("findings"), list), "visual_review", "Visual findings must be recorded as a list", file=name)
            self.require(bool(entry.get("contact_pages") or entry.get("detailed_pages") or entry.get("findings")), "visual_review", "Visual review has no recorded scope", file=name)
            if record.get("status") == "passed" and len(self.report["errors"]) == before:
                self.visual[name] = entry
        return {"present": True, "valid_current_PDF_reviews": sorted(self.visual),
                "scope": "Recorded human/visual signoff and current PDF hashes checked; no new visual judgement made"}

    def check_build(self) -> dict[str, Any]:
        record = read_json(self.root / EVIDENCE / "BUILD_RECORD.json")
        routes = read_json(self.root / EVIDENCE / "READING_ROUTES.json")
        self.require(record.get("status") == "passed", "build", "Final build is not marked passed")
        self.require(set(record["records"]) == set(KINDS), "build", "Build record must contain the three rebuilt readers")
        result = {}
        fatal = re.compile(r"(?i)(?:reference|citation).*undefined|undefined.*(?:reference|citation)|missing character|overfull|(?:^|\s)(?:LaTeX|Package \S+) Error|emergency stop|fatal error")
        for kind in KINDS:
            item = record["records"][kind]
            source = self.root / "publication/source" / kind
            current = fingerprint(source)
            self.require(current == item["source_fingerprint"], "build", "Source fingerprint differs from compilation", kind=kind)
            name = safe_relative(routes["pdfs"][kind])
            info = self.pdf(self.root / "publication/pdfs" / name)
            self.require(sha256(info["path"]) == item["sha256"], "build", "Final PDF hash differs from build record", kind=kind, file=name)
            self.require(len(info["doc"]) == item["pages"], "build", "PDF page count differs from build record", kind=kind)
            self.require(item.get("status") == "compiled", "build", "Reader compilation not marked completed", kind=kind)
            commands = item["commands"]
            self.require(bool(commands) and all(command.get("returncode") == 0 for command in commands), "build", "A recorded build command failed or command evidence is empty", kind=kind)
            diagnostics = item["diagnostics"]
            if not isinstance(diagnostics, list) or not all(isinstance(x, str) for x in diagnostics):
                raise ValueError(f"Invalid final diagnostics for {kind}")
            underfull = []
            for diagnostic in diagnostics:
                if fatal.search(diagnostic) or diagnostic.lstrip().startswith("!"):
                    self.error("build", "Disallowed final compile diagnostic", kind=kind, diagnostic=diagnostic)
                elif "underfull" in diagnostic.casefold():
                    underfull.append(diagnostic)
                    self.require("hbox" in diagnostic.casefold() and name in self.visual,
                                 "build", "Underfull diagnostic requires an hbox and matching passed visual review", kind=kind, diagnostic=diagnostic)
            result[kind] = {"source_fingerprint": current, "pdf": name, "pages": len(info["doc"]),
                            "final_diagnostics": diagnostics, "underfull_hboxes_with_visual_signoff": len(underfull)}
        for key, expected in record.get("source_fingerprints", {}).items():
            source = self.root / "publication/source" / key if key in KINDS else self.local(key)
            self.require(source.is_dir() and fingerprint(source) == expected, "build", "Additional source fingerprint mismatch", source=key)
        return {"readers": result, "builder_sha256": sha256(self.root / "tools/build_readers.py"),
                "fingerprint_algorithm": "build_readers.fingerprint: sorted relative path, NUL, binary SHA-256 per file",
                "raw_intermediate_PDFs_rechecked": False,
                "preserved_companion_PDFs": "Checked by the release manifest, PDF inspection, and any supplied visual record"}

    def check_zip(self, path: Path) -> dict[str, Any]:
        if not self.manifest:
            raise ValueError("A valid release manifest is required before checking the archive")
        expected = dict(self.manifest)
        manifest_path = self.root / "MANIFEST.json"
        expected["MANIFEST.json"] = {"bytes": manifest_path.stat().st_size, "sha256": sha256(manifest_path)}
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            self.require(len(names) == len(set(names)), "zip", "Duplicate ZIP member names")
            files = {}
            directories = set()
            for info in infos:
                name = info.filename[:-1] if info.is_dir() else info.filename
                safe_relative(name)
                mode = (info.external_attr >> 16) & 0o170000
                self.require(mode != stat.S_IFLNK, "zip", "ZIP contains a symbolic link", member=info.filename)
                self.require(mode in (0, stat.S_IFREG, stat.S_IFDIR), "zip", "ZIP contains a nonregular filesystem member", member=info.filename)
                self.require(not (info.flag_bits & 1), "zip", "ZIP contains an encrypted member", member=info.filename)
                if info.is_dir():
                    self.require(info.file_size == 0 and info.CRC == 0, "zip", "ZIP directory member contains data", member=info.filename)
                    directories.add(name)
                else:
                    files[name] = info
            candidates = []
            for name, info in files.items():
                if name.split("/")[-1] != "MANIFEST.json" or info.file_size != expected["MANIFEST.json"]["bytes"]:
                    continue
                if hashlib.sha256(archive.read(info)).hexdigest() == expected["MANIFEST.json"]["sha256"]:
                    candidates.append(name[:-len("MANIFEST.json")])
            if len(candidates) != 1:
                raise ValueError(f"Expected one archive root manifest matching the release, found {len(candidates)}")
            prefix = candidates[0]
            members = {prefix + name: entry for name, entry in expected.items()}
            self.require(set(files) == set(members), "zip", "Archive file member set differs from release manifest",
                         missing=sorted(set(members) - set(files)), extra=sorted(set(files) - set(members)))
            allowed_directories = {str(parent) for name in members for parent in PurePosixPath(name).parents if str(parent) != "."}
            self.require(directories <= allowed_directories, "zip", "Archive contains extraneous directory members", extra=sorted(directories - allowed_directories))
            folded = Counter(name.casefold() for name in files)
            self.require(all(count == 1 for count in folded.values()), "zip", "Case-insensitive ZIP path collision")
            verified = 0
            for name, expected_entry in members.items():
                if name not in files:
                    continue
                info = files[name]
                if not self.require(info.file_size == expected_entry["bytes"], "zip", "Archive byte count mismatch", member=name):
                    continue
                h = hashlib.sha256()
                with archive.open(info) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        h.update(block)
                verified += int(self.require(h.hexdigest() == expected_entry["sha256"], "zip", "Archive member hash mismatch", member=name))
            return {"archive": str(path), "sha256": sha256(path), "root_prefix": prefix,
                    "file_members": len(files), "verified_file_members": verified,
                    "CRC_checked_by_complete_ZipExtFile_reads": verified == len(members) == len(files),
                    "extraction_performed": False}

    def close(self) -> None:
        for info in self.pdfs.values():
            info["doc"].close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Release root (default: this tool's parent directory)")
    parser.add_argument("--output", required=True, type=Path, help="JSON report file outside the release")
    parser.add_argument("--zip", type=Path, help="Optional ZIP archive to check against this release without extracting")
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if not root.is_dir():
        parser.error("--root must be an existing release directory")
    if output.is_relative_to(root):
        parser.error("--output must be outside the release; the verifier never writes into it")
    if args.zip and output == args.zip.resolve():
        parser.error("--output must not overwrite the archive being checked")
    verifier = Verifier(root)
    try:
        verifier.run("manifest", verifier.check_manifest)
        verifier.run("sources", verifier.check_sources)
        verifier.run("excerpts", verifier.check_excerpts)
        verifier.run("pdfs", verifier.check_pdfs)
        verifier.run("visual_review", verifier.check_visual)
        verifier.run("build", verifier.check_build)
        if args.zip:
            verifier.run("zip", lambda: verifier.check_zip(args.zip.resolve()))
    finally:
        verifier.close()
    report = verifier.report
    report["status"] = "failed" if report["errors"] else "passed"
    report["release_files_modified"] = False
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(output),
                      "errors": len(report["errors"]),
                      "checks": {key: value["status"] for key, value in report["checks"].items()}}))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
