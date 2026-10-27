#!/usr/bin/env python3
"""Import declared source files with byte checks and one commit per component.

Local API: select_zip(), omission_reason(), and prepare_component().
Publication requires --publish. No imported program is executed by extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

REPOSITORY = "KomorebiP/Operation-KOMOREBI"
MAX_FILE_BYTES = 100 * 1024 * 1024
COPY_CHUNK = 1024 * 1024
OMIT_DIRS = {".git", ".lake", "__pycache__", "node_modules", ".venv", "venv",
             ".pytest_cache", ".mypy_cache", ".ruff_cache"}
COMPILED_SUFFIXES = (".olean.private", ".olean.server", ".olean", ".ilean",
                     ".pyc", ".pyo", ".o", ".so", ".dll", ".exe", ".a")
ARCHIVE_SUFFIXES = (".tar.gz", ".tar.xz", ".zip", ".tar", ".tgz", ".7z", ".whl")
OBJECT_HOSTS = {"objects.githubusercontent.com", "release-assets.githubusercontent.com"}


class ImportFailure(RuntimeError):
    """A source, path, identity, or publication precondition failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ImportFailure(message)


def safe_relative(value: str, *, allow_empty: bool = False) -> str:
    require(isinstance(value, str), "A relative path must be text")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in value), "Control character in path")
    require("\\" not in value and "\x00" not in value, "Backslash or NUL in path")
    require(not value.startswith("/") and not re.match(r"^[A-Za-z]:", value), "Absolute path rejected")
    while value.startswith("./"):
        value = value[2:]
    value = value.rstrip("/")
    if not value or value == ".":
        require(allow_empty, "Empty path rejected")
        return ""
    parts = value.split("/")
    require(all(p not in ("", ".", "..") for p in parts), "Noncanonical or traversing path rejected")
    return "/".join(parts)


def omission_reason(relative_path: str) -> str | None:
    """The shared source-selection filter. build/ and compiled/ remain eligible."""
    path = safe_relative(relative_path)
    parts = PurePosixPath(path).parts
    for part in parts[:-1]:
        if part in OMIT_DIRS:
            return "dependency-or-cache-directory:" + part
    if parts[0] in OMIT_DIRS:
        return "dependency-or-cache-directory:" + parts[0]
    if "/formal_preservation/objects/sha256/" in "/" + path + "/":
        return "duplicate-formal-object-store"
    name = parts[-1].lower()
    if (name == ".env" or name.startswith(".env.")) and name not in (".env.example", ".env.sample"):
        return "environment-secret-file"
    if name.endswith((".pem", ".key", ".p12")):
        return "private-key-file"
    if name.endswith(COMPILED_SUFFIXES):
        return "compiled-output"
    if name.endswith(ARCHIVE_SUFFIXES) or ".zip." in name:
        return "nested-archive-or-partial-transfer"
    return None


def tree_digest(files: list[dict]) -> str:
    lines = [f"{row['sha256']}  {row['path']}\n" for row in sorted(files, key=lambda x: x["path"])]
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(COPY_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _extras(extras) -> dict[str, str]:
    result = {}
    for item in extras or []:
        if isinstance(item, str):
            member = safe_relative(item)
            target = PurePosixPath(member).name
        else:
            require(isinstance(item, dict) and "member" in item and "path" in item,
                    "Extra files must be member strings or {member,path} mappings")
            member, target = safe_relative(item["member"]), safe_relative(item["path"])
        require(member not in result or result[member] == target, "Conflicting extra-file mapping")
        result[member] = target
    return result


def _select(records: list[dict], prefix: str, extras) -> tuple[list[dict], list[dict]]:
    prefix = safe_relative(prefix, allow_empty=True)
    extra_map = _extras(extras)
    names = {r["archive_member"] for r in records if not r["directory"]}
    require(set(extra_map) <= names, "Requested root extra file is absent from the archive")
    selected, omissions, targets = [], [], {}
    prefix_found = not prefix
    for record in records:
        member = record["archive_member"]
        if member == prefix or member.startswith(prefix + "/"):
            prefix_found = True
        if record["directory"]:
            continue
        if member in extra_map:
            target = extra_map[member]
        elif not prefix:
            target = member
        elif member.startswith(prefix + "/"):
            target = member[len(prefix) + 1:]
        else:
            continue
        target = safe_relative(target)
        reason = omission_reason(member) or omission_reason(target)
        if reason:
            omissions.append({"archive_member": member, "path": target, "reason": reason, "size": record["size"]})
            continue
        require(record["kind"] == "file", f"Nonregular source member rejected: {member}")
        require(record["size"] <= MAX_FILE_BYTES, f"Source file exceeds 100 MiB: {target}")
        require(target not in targets, f"Duplicate output path: {target}")
        targets[target] = member
        selected.append({k: record[k] for k in ("archive_member", "size", "mode")} | {"path": target})
    require(prefix_found, f"Selected archive prefix does not exist: {prefix}")
    require(bool(selected), "Archive selection contains no eligible source files")
    paths = set(targets)
    for path in paths:
        require(not any(str(p) in paths for p in PurePosixPath(path).parents if str(p) != "."),
                f"File/directory collision in selected source: {path}")
    return sorted(selected, key=lambda r: r["path"]), sorted(omissions, key=lambda r: (r["path"], r["archive_member"]))


def select_zip(archive, prefix: str = "", extras=()) -> tuple[list[dict], list[dict]]:
    """Return selected member records and omissions without extracting bytes."""
    records, seen = [], set()
    with zipfile.ZipFile(archive) as handle:
        for info in handle.infolist():
            member = safe_relative(info.filename, allow_empty=info.is_dir())
            if not member:
                continue
            require(member not in seen, f"Duplicate archive member: {member}")
            seen.add(member)
            mode = info.external_attr >> 16
            kind_bits = stat.S_IFMT(mode)
            kind = "file" if kind_bits in (0, stat.S_IFREG) else "nonregular"
            records.append({"archive_member": member, "directory": info.is_dir(), "kind": kind,
                            "size": info.file_size, "mode": "100755" if mode & 0o111 else "100644"})
    return _select(records, prefix, extras)


def select_tar(archive, prefix: str = "", extras=()) -> tuple[list[dict], list[dict]]:
    records, seen = [], set()
    with tarfile.open(archive, "r:*") as handle:
        for info in handle.getmembers():
            member = safe_relative(info.name, allow_empty=info.isdir())
            if not member:
                continue
            require(member not in seen, f"Duplicate archive member: {member}")
            seen.add(member)
            records.append({"archive_member": member, "directory": info.isdir(),
                            "kind": "file" if info.isfile() else "nonregular", "size": info.size,
                            "mode": "100755" if info.mode & 0o111 else "100644"})
    return _select(records, prefix, extras)


def _assert_no_symlink(path: Path, boundary: Path) -> None:
    current = path
    while True:
        require(not current.is_symlink(), f"Symlink in destination path: {current.name}")
        if current == boundary:
            return
        require(current != current.parent, "Destination escaped its boundary")
        current = current.parent


class _GitHubRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        require(parsed.scheme == "https" and parsed.hostname in OBJECT_HOSTS and not parsed.username,
                "Download redirected outside approved GitHub object hosts")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            redirected.remove_header("Authorization")
        return redirected


def _download(url: str, output: Path, *, token: str | None = None,
              api: bool = False, expected_size: int | None = None) -> None:
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == "https" and not parsed.username and not parsed.password,
            "Only approved HTTPS source URLs are accepted")
    if api:
        require(parsed.hostname == "api.github.com" and parsed.path.startswith(f"/repos/{REPOSITORY}/git/blobs/"),
                "Unapproved Git blob source")
    else:
        require(parsed.hostname == "github.com" and parsed.path.startswith(f"/{REPOSITORY}/releases/download/")
                and not parsed.query and not parsed.fragment, "Unapproved release download URL")
    headers = {"User-Agent": "Komorebi-source-import", "Accept": "application/vnd.github.raw+json" if api else "application/octet-stream"}
    if api and token:
        headers["Authorization"] = "Bearer " + token
    opener = urllib.request.build_opener(_GitHubRedirects())
    total = 0
    with opener.open(urllib.request.Request(url, headers=headers), timeout=60) as response, output.open("wb") as stream:
        while chunk := response.read(COPY_CHUNK):
            total += len(chunk)
            if expected_size is not None:
                require(total <= expected_size, "Download exceeded its declared byte count")
            stream.write(chunk)
    if expected_size is not None:
        require(total == expected_size, "Downloaded byte count does not match the source declaration")


def _obtain_source(source: dict, temp: Path, local_archive=None) -> Path:
    kind = source.get("kind")
    require(kind in ("zip-url", "blob-tar"), "Unknown source transport kind")
    expected_hash = source.get("sha256", "")
    require(bool(re.fullmatch(r"[0-9a-f]{64}", expected_hash)), "Source SHA-256 is missing or invalid")
    if local_archive is not None:
        archive = Path(local_archive)
        require(archive.is_file() and not archive.is_symlink(), "Local source archive is not a regular file")
    else:
        archive = temp / ("source.zip" if kind == "zip-url" else "source.tar")
        if kind == "zip-url":
            _download(source["url"], archive, expected_size=source.get("size"))
        else:
            chunks = source.get("chunks")
            require(isinstance(chunks, list) and bool(chunks), "Blob transport contains no chunks")
            with archive.open("wb") as combined:
                for index, chunk in enumerate(chunks):
                    require(bool(re.fullmatch(r"[0-9a-f]{40}", chunk.get("sha", ""))), "Invalid Git blob SHA")
                    require(isinstance(chunk.get("size"), int) and 0 <= chunk["size"] <= MAX_FILE_BYTES,
                            "Invalid blob chunk size")
                    part = temp / f"chunk-{index:05d}"
                    _download(f"https://api.github.com/repos/{REPOSITORY}/git/blobs/{chunk['sha']}", part,
                              api=True, token=os.environ.get("GITHUB_TOKEN"), expected_size=chunk["size"])
                    require(sha256_file(part) == chunk.get("sha256"), f"Blob chunk {index} failed SHA-256 validation")
                    with part.open("rb") as stream:
                        shutil.copyfileobj(stream, combined, COPY_CHUNK)
                    part.unlink()
    if source.get("size") is not None:
        require(archive.stat().st_size == source["size"], "Source archive size mismatch")
    require(sha256_file(archive) == expected_hash, "Source archive SHA-256 mismatch")
    return archive


def _copy_member(stream, output: Path, record: dict) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    git_hash = hashlib.sha1(f"blob {record['size']}\0".encode("ascii"))
    total = 0
    with output.open("xb") as target:
        while chunk := stream.read(COPY_CHUNK):
            total += len(chunk)
            require(total <= min(record["size"], MAX_FILE_BYTES), "Archive member exceeded its declared size")
            h.update(chunk)
            git_hash.update(chunk)
            target.write(chunk)
    require(total == record["size"], "Archive member was truncated")
    output.chmod(0o755 if record["mode"] == "100755" else 0o644)
    return {"path": record["path"], "size": total, "sha256": h.hexdigest(),
            "git_blob_sha1": git_hash.hexdigest(), "mode": record["mode"]}


def prepare_component(component: dict, output, local_archive=None, verify_expected: bool = True) -> dict:
    """Extract only source files into an empty output directory and return a report.

    With verify_expected=False this computes the declaration for local preparation.
    This function performs no Git operations and writes no receipt into the output.
    """
    output = Path(output)
    require(not output.is_symlink(), "Output directory is a symlink")
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())), "Preparation output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    source = component["source"]
    prefix, extras = source.get("prefix", ""), source.get("root_extra_files", [])
    with tempfile.TemporaryDirectory(prefix="komorebi-source-") as temporary:
        archive = _obtain_source(source, Path(temporary), local_archive)
        selector = select_zip if source["kind"] == "zip-url" else select_tar
        selected, omissions = selector(archive, prefix, extras)
        if verify_expected:
            require(len(selected) == component["expected"]["file_count"], "Selected source file count differs from expected")
        files = []
        if source["kind"] == "zip-url":
            with zipfile.ZipFile(archive) as handle:
                actual_names = {safe_relative(i.filename, allow_empty=i.is_dir()): i for i in handle.infolist()}
                for record in selected:
                    with handle.open(actual_names[record["archive_member"]], "r") as stream:
                        files.append(_copy_member(stream, output / record["path"], record))
        else:
            with tarfile.open(archive, "r:*") as handle:
                actual_names = {safe_relative(i.name, allow_empty=i.isdir()): i for i in handle.getmembers()}
                for record in selected:
                    stream = handle.extractfile(actual_names[record["archive_member"]])
                    require(stream is not None, "Tar source member could not be read")
                    with stream:
                        files.append(_copy_member(stream, output / record["path"], record))
    digest = tree_digest(files)
    if verify_expected:
        require(digest == component["expected"]["tree_sha256"], "Selected source tree SHA-256 differs from expected")
    return {"schema": 1, "component": component["id"], "destination": component["destination"],
            "source": source, "file_count": len(files), "tree_sha256": digest,
            "files": files, "omissions": omissions, "notes": component.get("notes", [])}


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", capture_output=True)
    if completed.returncode:
        raise ImportFailure("Git operation failed: " + args[0] + "\n" + completed.stderr.strip())
    return completed.stdout.strip()


def _fingerprint(component: dict) -> str:
    return hashlib.sha256(json.dumps(component, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def receipt_matches(component: dict, root: Path, receipt_path: Path) -> bool:
    if not receipt_path.is_file() or receipt_path.is_symlink():
        return False
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("component_sha256") != _fingerprint(component):
            return False
        destination = root / safe_relative(component["destination"])
        files = receipt["files"]
        if len(files) != component["expected"]["file_count"] or tree_digest(files) != component["expected"]["tree_sha256"]:
            return False
        for row in files:
            path = destination / safe_relative(row["path"])
            _assert_no_symlink(path, root)
            if not path.is_file() or path.stat().st_size != row["size"] or sha256_file(path) != row["sha256"]:
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError, ImportFailure):
        return False


def _install_owned(component: dict, prepared: Path, report: dict, root: Path) -> None:
    destination = root / safe_relative(component["destination"])
    _assert_no_symlink(destination, root)
    replacements = component.get("replace_expected_sha256", {})
    for row in report["files"]:
        target = destination / row["path"]
        _assert_no_symlink(target, root)
        if target.exists():
            require(target.is_file(), f"Destination is not a file: {row['path']}")
            existing = sha256_file(target)
            require(existing == row["sha256"] or replacements.get(row["path"]) == existing,
                    f"Conflicting destination bytes: {component['destination']}/{row['path']}")
    for row in report["files"]:
        target = destination / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or sha256_file(target) != row["sha256"]:
            shutil.copyfile(prepared / row["path"], target)
        target.chmod(0o755 if row["mode"] == "100755" else 0o644)


def _verify_staged(root: Path, destination: str, files: list[dict]) -> None:
    raw = subprocess.run(["git", "ls-files", "--stage", "-z", "--", destination], cwd=root,
                         check=True, capture_output=True).stdout
    index = {}
    for entry in raw.split(b"\0"):
        if entry:
            metadata, path = entry.split(b"\t", 1)
            mode, sha, stage = metadata.decode("ascii").split()
            require(stage == "0", "Unmerged path in Git index")
            index[path.decode("utf-8")] = (mode, sha)
    for row in files:
        path = destination + "/" + row["path"]
        require(index.get(path) == (row["mode"], row["git_blob_sha1"]),
                f"Staged bytes or mode differ from verified source: {path}")


def _preserve_source_bytes(config: dict, root: Path) -> None:
    """Keep archived bytes exact despite inherited Git clean transformations.

    These overrides belong only to the importer checkout's Git metadata. They
    preserve the original tracked .gitattributes files and every source byte.
    """
    attribute_path = Path(_git(root, "rev-parse", "--git-path", "info/attributes"))
    if not attribute_path.is_absolute():
        attribute_path = root / attribute_path
    rules = []
    for component in config["components"]:
        destination = safe_relative(component["destination"])
        require(not any(c in destination for c in "*?[]"), "Glob characters in source destination")
        pattern = json.dumps(destination + "/**", ensure_ascii=False)
        rules.append(pattern + " -text -filter -ident -working-tree-encoding")
    attribute_path.parent.mkdir(parents=True, exist_ok=True)
    with attribute_path.open("a", encoding="utf-8") as stream:
        stream.write("\n# Preserve exact archived bytes during the Komorebi source import.\n")
        stream.write("\n".join(sorted(set(rules))) + "\n")


def publish_batch(config: dict, batch: str, expected_base: str, root: Path) -> None:
    require(_git(root, "rev-parse", "HEAD") == expected_base, "Checkout does not match expected_base")
    _preserve_source_bytes(config, root)
    require(not _git(root, "status", "--porcelain"), "Git working tree is not clean")
    require(_git(root, "ls-remote", "origin", "refs/heads/main").split()[0] == expected_base,
            "Remote main does not match expected_base")
    _git(root, "config", "user.name", "Komorebi P.")
    _git(root, "config", "user.email", "52508850+KomorebiP@users.noreply.github.com")
    _git(root, "config", "core.autocrlf", "false")
    components = {row["id"]: row for row in config["components"]}
    require(batch in config["batches"], "Unknown configured batch")
    current_base = expected_base
    for identifier in config["batches"][batch]:
        require(identifier in components, "Batch names an unknown component")
        component = components[identifier]
        require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", identifier)), "Unsafe component identifier")
        destination = safe_relative(component["destination"])
        require(".git" not in PurePosixPath(destination).parts, "Git metadata destination rejected")
        receipt_relative = "manifests/source-imports/" + identifier + ".json"
        receipt_path = root / receipt_relative
        require(not _git(root, "status", "--porcelain"), "Git tree changed between component imports")
        if receipt_matches(component, root, receipt_path):
            print(json.dumps({"component": identifier, "status": "already-matches"}), flush=True)
            continue
        print(json.dumps({"component": identifier, "status": "preparing"}), flush=True)
        with tempfile.TemporaryDirectory(prefix="komorebi-prepared-") as temporary:
            prepared = Path(temporary) / "files"
            report = prepare_component(component, prepared)
            _install_owned(component, prepared, report, root)
        report["component_sha256"] = _fingerprint(component)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        paths = [destination + "/" + row["path"] for row in report["files"]] + [receipt_relative]
        for start in range(0, len(paths), 200):
            _git(root, "add", "--force", "--", *paths[start:start + 200])
        _verify_staged(root, destination, report["files"])
        subprocess.run([sys.executable, "-B", "tools/check_repository.py"], cwd=root, check=True)
        if not _git(root, "diff", "--cached", "--name-only"):
            print(json.dumps({"component": identifier, "status": "unchanged"}), flush=True)
            continue
        require(_git(root, "rev-parse", "HEAD") == current_base, "Local HEAD changed during import")
        _git(root, "commit", "--quiet", "-m", f"Import {identifier} as browsable source files")
        new_head = _git(root, "rev-parse", "HEAD")
        remote_head = _git(root, "ls-remote", "origin", "refs/heads/main").split()[0]
        require(remote_head == current_base, "Remote main changed before push. No force push attempted")
        _git(root, "push", "origin", "HEAD:refs/heads/main")
        require(_git(root, "ls-remote", "origin", "refs/heads/main").split()[0] == new_head,
                "Remote readback did not match the published commit")
        current_base = new_head
        print(json.dumps({"component": identifier, "status": "published", "commit": new_head,
                          "file_count": report["file_count"], "tree_sha256": report["tree_sha256"]}), flush=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("manifests/source-collection.json"))
    parser.add_argument("--batch")
    parser.add_argument("--expected-base")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--prepare-component")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--local-archive", type=Path)
    parser.add_argument("--compute-expected", action="store_true")
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config.get("schema") == 1, "Unsupported source collection schema")
    ids = [row["id"] for row in config["components"]]
    require(len(ids) == len(set(ids)), "Duplicate component identifiers")
    components = {row["id"]: row for row in config["components"]}
    if args.prepare_component:
        require(not args.publish and args.output is not None, "Local preparation requires --output and excludes --publish")
        require(args.prepare_component in components, "Unknown component")
        report = prepare_component(components[args.prepare_component], args.output, args.local_archive,
                                   verify_expected=not args.compute_expected)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    require(args.batch in config["batches"], "A configured --batch is required")
    if args.publish:
        require(bool(re.fullmatch(r"[0-9a-f]{40}", args.expected_base or "")), "A complete --expected-base SHA is required")
        root = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
        publish_batch(config, args.batch, args.expected_base, root)
    else:
        for identifier in config["batches"][args.batch]:
            with tempfile.TemporaryDirectory(prefix="komorebi-preview-") as temporary:
                report = prepare_component(components[identifier], Path(temporary) / "files")
                print(json.dumps({"component": identifier, "status": "verified-without-publishing",
                                  "file_count": report["file_count"], "tree_sha256": report["tree_sha256"]}), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ImportFailure, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print("Source import failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
