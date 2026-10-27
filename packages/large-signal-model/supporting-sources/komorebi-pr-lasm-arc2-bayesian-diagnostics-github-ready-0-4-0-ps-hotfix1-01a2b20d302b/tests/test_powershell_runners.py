from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = ROOT / "powershell"


def test_conda_runtime_helper_is_bundled() -> None:
    helper = (POWERSHELL / "Conda_Runtime.ps1").read_text(encoding="utf-8")
    assert "CONDA_EXE" in helper
    assert "Resolve-KomorebiCondaExecutable" in helper
    assert "Invoke-KomorebiConda" in helper
    assert "CommandType Application" in helper


def test_every_powershell_runner_uses_conda_runtime_helper() -> None:
    runners = sorted(path for path in POWERSHELL.glob("*.ps1") if path.name != "Conda_Runtime.ps1")
    assert runners
    for path in runners:
        text = path.read_text(encoding="utf-8")
        assert "Conda_Runtime.ps1" in text, path.name
        assert "Resolve-KomorebiCondaExecutable" in text, path.name
        assert "Invoke-KomorebiConda" in text, path.name
        assert "conda run" not in text.lower(), path.name
        assert "conda @arguments" not in text.lower(), path.name


def test_diagnostic_runner_fails_if_expected_atlas_is_missing() -> None:
    text = (POWERSHELL / "Run_Diagnostic_Audit.ps1").read_text(encoding="utf-8")
    assert "Diagnostic audit completed without creating" in text
    assert "Test-Path -LiteralPath $Index -PathType Leaf" in text
