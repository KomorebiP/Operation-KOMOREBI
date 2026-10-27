#!/usr/bin/env python3
"""Assemble the unchanged 1.7.0 core and focused extension; no Lean is executed.

The archive hash and every copied source byte are checked against the archive.
Existing destinations are refused. Run this from a copy without project/ to
reproduce the union. This program does not reinterpret prior evidence as fresh.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from zipfile import ZipFile

from common import EXPECTED_ARCHIVE, ROOT_MODULE, graph, sha, write_json

HOME = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--archive", type=Path, required=True)
    args = ap.parse_args()
    source, archive = args.source.resolve(), args.archive.resolve()
    project = HOME / "project"
    if project.exists() or (HOME / "inventory.json").exists():
        ap.error("Refusing to overwrite an assembled project or inventory")
    actual = sha(archive)
    if actual != EXPECTED_ARCHIVE:
        ap.error(f"Wrong archive hash: {actual}")
    inherited, duplicates, entries = [], [], {}
    with ZipFile(archive) as z:
        roots = {n.split("/")[0] for n in z.namelist() if n.endswith("/formal/KomorebiSpace.lean")}
        if len(roots) != 1:
            ap.error("Archive has no unique canonical source root")
        archive_root = next(iter(roots))
        files = []
        for scope, root in (("formal", "KomorebiSpace.lean"),
                            ("extension", "KomorebiSpaceRegularization.lean")):
            files.extend((scope, p, p.relative_to(source / scope))
                         for p in sorted((source / scope / "KomorebiSpace").rglob("*.lean")))
            files.append((scope, source / scope / root, Path(root)))
        for scope, path, rel in files:
            data = path.read_bytes()
            archive_name = f"{archive_root}/{scope}/{rel.as_posix()}"
            if data != z.read(archive_name):
                raise ValueError(f"Extracted source differs from archive: {path}")
            key = rel.as_posix()
            if key in entries:
                if entries[key][1] != data:
                    raise ValueError(f"Nonidentical module collision: {key}")
                duplicates.append({"destination": key, "scopes": [entries[key][0], scope]})
            else:
                entries[key] = (scope, data)
            inherited.append({"scope": scope, "source": f"{scope}/{key}",
                              "destination": key, "sha256": sha(path),
                              "archive_member": archive_name, "archive_bytes_match": True})
        project.mkdir()
        for rel, (_, data) in sorted(entries.items()):
            dest = project / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        # Separate scope directories avoid the two Placeholder and CustomAxiom names colliding.
        ancillary = []
        for scope in ("formal", "extension"):
            for path in sorted((source / scope / "tests").rglob("*.lean")):
                rel = path.relative_to(source)
                if path.read_bytes() != z.read(f"{archive_root}/{rel.as_posix()}"):
                    raise ValueError(f"Control differs from archive: {path}")
                dest = project / "tests" / scope / path.relative_to(source / scope / "tests")
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
                ancillary.append({"source": rel.as_posix(), "destination": str(dest.relative_to(project)),
                                  "sha256": sha(path), "archive_bytes_match": True})
        for rel in ("formal/pinned-dependencies.json", "formal/lean-toolchain", "formal/scripts/type_names.txt"):
            path = source / rel
            if path.read_bytes() != z.read(f"{archive_root}/{rel}"):
                raise ValueError(f"Auxiliary differs from archive: {rel}")
            dest = project / path.name
            shutil.copyfile(path, dest)
            ancillary.append({"source": rel, "destination": dest.name, "sha256": sha(path),
                              "archive_bytes_match": True})
    (project / f"{ROOT_MODULE}.lean").write_text(
        "-- Combined entrypoint; inherited module bytes are unchanged.\n"
        "import KomorebiSpace\nimport KomorebiSpaceRegularization\n")
    (project / "lakefile.toml").write_text(
        'name = "KomorebiSpaceCombined"\nversion = "1.7.1"\n'
        'defaultTargets = ["KomorebiSpaceCombined"]\n\n'
        '[[require]]\nname = "mathlib"\ngit = "https://github.com/leanprover-community/mathlib4.git"\n'
        'rev = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"\n\n'
        '[[lean_lib]]\nname = "KomorebiSpace"\n\n'
        '[[lean_lib]]\nname = "KomorebiSpaceRegularization"\n\n'
        '[[lean_lib]]\nname = "KomorebiSpaceCombined"\n')
    info = graph(project)
    (project / "wanted_modules.txt").write_text("\n".join(info["compile_order"]) + "\n")
    info.update({"schema": "komorebi-space-cumulative-static-inventory-v1",
                 "status": "STATIC_CHECKS_PASS_NOT_LEAN_VERIFIED", "lean_executed": False,
                 "source_archive_sha256": actual, "source_archive_name": archive.name,
                 "inherited_files": inherited, "inherited_auxiliary": ancillary,
                 "byte_identical_module_collisions": duplicates,
                 "forbidden_tokens_checked": ["sorry", "admit", "axiom", "native_decide", "unsafe"],
                 "control_counts": {scope: {kind: len(list((project / "tests" / scope / kind).glob("*.lean")))
                                             for kind in ("positive", "negative", "policy")}
                                    for scope in ("formal", "extension")}})
    if info["production_modules"] != 141 or info["compile_targets"] != 144:
        raise ValueError("Unexpected frozen release module inventory")
    info["project_file_sha256"] = {str(p.relative_to(project)): sha(p)
                                    for p in sorted(project.rglob("*")) if p.is_file()}
    write_json(HOME / "inventory.json", info)
    print(f"STATIC ONLY: {info['production_modules']} production modules, "
          f"{info['compile_targets']} targets, all copied sources archive-matched. Lean not run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
