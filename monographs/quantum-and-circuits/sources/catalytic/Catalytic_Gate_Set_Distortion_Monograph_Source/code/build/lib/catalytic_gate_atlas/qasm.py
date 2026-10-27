"""Minimal OpenQASM 3 export for exact witness words.

The exporter is intentionally small.  It supports the named gates used by the
finite Clifford atlas and emits a circuit whose Clifford action can be checked
against the binary symplectic witness.  The finite census works modulo global
phase and Pauli translations, so equality of exported witness words is meant at
that declared quotient level unless a separate unitary check is supplied.
"""
from __future__ import annotations

import re
from collections.abc import Sequence

_SINGLE = re.compile(r"^(H|S|X)(\d+)$", re.IGNORECASE)
_PAIR_COMMA = re.compile(r"^(CX|CZ|SWAP)(\d+)\s*,\s*(\d+)$", re.IGNORECASE)
_PAIR_COMPACT = re.compile(r"^(CX|CZ|SWAP)(\d)(\d)$", re.IGNORECASE)


def _parse_gate(label: str) -> tuple[str, tuple[int, ...]]:
    token = label.strip().upper()
    single = _SINGLE.fullmatch(token)
    if single:
        return single.group(1), (int(single.group(2)),)
    pair = _PAIR_COMMA.fullmatch(token) or _PAIR_COMPACT.fullmatch(token)
    if pair:
        return pair.group(1), (int(pair.group(2)), int(pair.group(3)))
    raise ValueError(
        f"unsupported gate label {label!r}; use H0, S1, X2, CX1,0, CZ0,2, or SWAP0,1"
    )


def gate_word_to_openqasm(
    word: Sequence[str],
    qubits: int,
    *,
    title: str | None = None,
) -> str:
    """Return an OpenQASM 3 program for a named Clifford/reversible word.

    Parameters
    ----------
    word:
        Labels such as ``H1``, ``S0``, ``CX1,0``, ``CZ0,2``, and ``SWAP0,1``.
        The compact two-index labels used by the atlas (for example ``CX10``)
        are also accepted for single-digit indices.
    qubits:
        Number of qubits in the emitted register.
    title:
        Optional human-readable comment.
    """
    if qubits <= 0:
        raise ValueError("qubits must be positive")
    lines = ["OPENQASM 3.0;", 'include "stdgates.inc";']
    if title:
        clean = " ".join(title.splitlines()).strip()
        lines.append(f"// {clean}")
    lines.append(f"qubit[{qubits}] q;")
    names = {"H": "h", "S": "s", "X": "x", "CX": "cx", "CZ": "cz", "SWAP": "swap"}
    for label in word:
        gate, indices = _parse_gate(label)
        if any(index < 0 or index >= qubits for index in indices):
            raise ValueError(f"gate {label!r} addresses a qubit outside 0..{qubits - 1}")
        if len(indices) == 2 and indices[0] == indices[1]:
            raise ValueError(f"two-qubit gate {label!r} repeats its qubit index")
        operands = ", ".join(f"q[{index}]" for index in indices)
        lines.append(f"{names[gate]} {operands};")
    return "\n".join(lines) + "\n"
