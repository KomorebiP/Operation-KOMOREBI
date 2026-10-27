import hashlib
import json

import pytest

from validation.aggregate_v029 import _load_parts, _validate_official_parts_parent
from validation.run_v029_one_seed import _validate_official_request
from validation.v029_official_integrity import (
    PermanentSeedJournal,
    verify_freeze_manifest,
    write_pickle_atomic_once,
)


def _canonical_json(payload):
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _manifest_fixture(tmp_path):
    root = tmp_path / "project"
    validation = root / "validation"
    source = root / "src" / "frozen.py"
    validation.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    source.write_bytes(b"frozen\n")
    manifest = validation / "V0_29_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_29_PREOUTCOME_FREEZE.json.sha256"
    payload = {
        "files": {
            "src/frozen.py": {
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        },
        "official_seed_access_before_freeze": "none",
        "official_seeds": [5601, 5607, 5613, 5619, 5621, 5627, 5631, 5639],
        "schema": "rrct.v029.preoutcome_freeze.v1",
        "status": "sealed_before_official_outcomes",
        "version": "0.29.0.dev1",
    }
    raw = _canonical_json(payload)
    manifest.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    checksum.write_text(f"{digest}  {manifest.name}\n", encoding="ascii")
    return root, source, manifest, checksum, digest


def test_official_request_rejects_nonexact_basename_and_unreserved_seed(tmp_path):
    with pytest.raises(ValueError, match="basename must be exactly 17.pkl"):
        _validate_official_request(
            17,
            tmp_path / "wrong.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    with pytest.raises(ValueError, match="not a reserved"):
        _validate_official_request(
            19,
            tmp_path / "19.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    with pytest.raises(ValueError, match="output parent must be exactly"):
        _validate_official_request(
            17,
            tmp_path / "other" / "17.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    _validate_official_request(
        17,
        tmp_path / "17.pkl",
        reserved_seeds=(17,),
        expected_parent=tmp_path,
    )
    with pytest.raises(ValueError, match="parts directory must be exactly"):
        _validate_official_parts_parent(
            tmp_path / "other",
            expected=tmp_path,
        )
    _validate_official_parts_parent(tmp_path, expected=tmp_path)


def test_permanent_seed_journal_exclusively_blocks_a_second_attempt(tmp_path):
    path = tmp_path / "17.lock"
    digest = "a" * 64
    first = PermanentSeedJournal.create(
        path,
        seed=17,
        output_basename="17.pkl",
        freeze_manifest_sha256=digest,
    )
    first.close()
    with pytest.raises(FileExistsError):
        PermanentSeedJournal.create(
            path,
            seed=17,
            output_basename="17.pkl",
            freeze_manifest_sha256=digest,
        )
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [record["event"] for record in records] == ["started"]


def test_freeze_manifest_detects_listed_file_and_companion_tampering(tmp_path):
    root, source, manifest, checksum, digest = _manifest_fixture(tmp_path)
    assert (
        verify_freeze_manifest(
            manifest,
            checksum,
            project_root=root,
        )
        == digest
    )

    source.write_bytes(b"broken\n")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)

    source.write_bytes(b"frozen\n")
    checksum.write_text(f"{'0' * 64}  {manifest.name}\n", encoding="ascii")
    with pytest.raises(ValueError, match="checksum companion mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)


def test_aggregator_rejects_part_with_wrong_freeze_manifest_digest(tmp_path):
    expected_digest = "b" * 64
    parts = tmp_path / "parts"
    parts.mkdir()
    final = parts / "17.pkl"
    temporary = parts / "17.pkl.tmp"
    journal = PermanentSeedJournal.create(
        parts / "17.lock",
        seed=17,
        output_basename=final.name,
        freeze_manifest_sha256=expected_digest,
    )
    size, output_hash = write_pickle_atomic_once(
        {
            "seed": 17,
            "cohort": "official",
            "freeze_manifest_sha256": "c" * 64,
        },
        final,
        temporary,
    )
    journal.append(
        "completed",
        seed=17,
        output=final.name,
        freeze_manifest_sha256=expected_digest,
        output_size=size,
        output_sha256=output_hash,
    )
    journal.close()
    with pytest.raises(ValueError, match="manifest digest mismatch"):
        _load_parts(parts, expected_digest, reserved_seeds=(17,))
