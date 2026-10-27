from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLError, OSLRuntime, run_program  # noqa: E402


def test_all_packaged_examples_match_expected_status() -> None:
    for path in sorted((ROOT / "examples").glob("*.osl")):
        expected = None
        for line in path.read_text(encoding="utf-8").splitlines()[:5]:
            if line.startswith("# EXPECT-ERROR:"):
                expected = line.split(":", 1)[1].strip()
                break
        result = run_program(path)
        if expected is None:
            assert result["ok"], (path.name, result["error"])
        else:
            assert not result["ok"], path.name
            assert expected.lower() in result["error"].lower()


def test_communication_preserves_content_but_not_observation_token() -> None:
    runtime = OSLRuntime()
    runtime.run_text(
        """
        module comm
        lineage LA
        lineage LB
        agent A lineage LA
        agent B lineage LB
        observe e by A content "event" confidence 0.9
        communicate e from A to B as eB
        """
    )
    source = runtime.state.packets["e"]
    target = runtime.state.packets["eB"]
    assert source.content == target.content
    assert "A" in source.observation_tokens
    assert target.observation_tokens == set()
    assert target.provenance == "communicated"
    assert target.source_agent == "A"


def test_injected_content_is_accessible_but_quarantined() -> None:
    runtime = OSLRuntime()
    runtime.run_text(
        """
        module injection
        lineage LA
        agent A lineage LA
        inject x to A content "same-content" confidence 0.99
        """
    )
    packet = runtime.state.packets["x"]
    assert "A" in packet.accessible_to
    assert "A" in packet.quarantined_by
    assert "A" not in packet.bound_to


def test_transported_projector_is_idempotent() -> None:
    runtime = OSLRuntime()
    runtime.run_text(
        """
        module transport
        space H dim 2
        operator P : H -> H kind projector matrix [[1,0],[0,0]]
        operator T : H -> H kind linear matrix [[1,1],[0,1]]
        transport P via T as P2
        check_projector P2 tolerance 1e-9
        """
    )
    p2 = runtime.state.operators["P2"].matrix
    assert np.allclose(p2 @ p2, p2)


def test_snapshot_is_deterministic_for_same_program() -> None:
    source = """
    module deterministic
    lineage LA
    agent A lineage LA
    observe e by A content "event" confidence 0.9
    write_memory e by A as observed
    """
    first = OSLRuntime().run_text(source).snapshot()
    second = OSLRuntime().run_text(source).snapshot()
    assert first == second


def test_effect_capability_is_required_at_execute_time() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="lacks capability"):
        runtime.run_text(
            """
            module cap
            lineage LA
            agent A lineage LA
            observe e by A content "event" confidence 0.9
            endorse e by A threshold 0.8
            authorize e by A for planning
            plan act by A using e effect externalAct
            execute act by A
            """
        )
