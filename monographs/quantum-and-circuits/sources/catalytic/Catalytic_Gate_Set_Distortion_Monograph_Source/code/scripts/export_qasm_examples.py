#!/usr/bin/env python3
"""Export the exact small Clifford witness words as OpenQASM 3 examples."""
from __future__ import annotations

from pathlib import Path

from catalytic_gate_atlas import gate_word_to_openqasm


EXAMPLES = {
    "clifford_2q_restricted.qasm": (
        2,
        ["CX01", "S1", "CX10", "CX01"],
        "Two-qubit restricted witness; symplectic quotient model",
    ),
    "clifford_2q_ambient.qasm": (
        2,
        ["H1", "CX10", "CX01", "H0", "S1", "S0"],
        "Two-qubit ambient witness; entangling cost two in the declared metric",
    ),
    "clifford_3q_restricted.qasm": (
        3,
        ["CX02", "CZ12", "CX20", "CX02", "CX01", "CX10", "CX01"],
        "Three-qubit restricted witness; swap-free primitive-count metric",
    ),
    "clifford_3q_ambient.qasm": (
        3,
        ["H1", "CX12", "CX21", "CX20", "CX02", "H0"],
        "Three-qubit ambient witness; swap-free primitive-count metric",
    ),
}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out = root / "examples"
    out.mkdir(parents=True, exist_ok=True)
    for name, (qubits, word, title) in EXAMPLES.items():
        (out / name).write_text(gate_word_to_openqasm(word, qubits, title=title))
    print(out)


if __name__ == "__main__":
    main()
