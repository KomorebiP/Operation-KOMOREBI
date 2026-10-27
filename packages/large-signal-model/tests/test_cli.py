from __future__ import annotations

from komorebi_arc3_offline.cli import main


def test_smoke_cli(tmp_path) -> None:
    code = main([
        "smoke",
        "--output",
        str(tmp_path),
        "--max-actions",
        "20",
        "--initial-probes",
        "8",
    ])
    assert code == 0
