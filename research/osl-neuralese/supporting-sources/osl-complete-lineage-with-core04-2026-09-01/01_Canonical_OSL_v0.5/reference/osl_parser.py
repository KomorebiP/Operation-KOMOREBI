"""Parser and static checker for OSL-Core 0.3.

The concrete language remains intentionally line-oriented so examples are easy
to audit.  Unlike OSL-Core 0.1, every program is parsed into an explicit AST and
passes a declaration/type-oriented static phase before the runtime is entered.
"""
from __future__ import annotations

import ast
import json
import re
from collections import Counter
from typing import Any, Iterable

try:  # pragma: no cover - package/script dual use
    from .osl_model import (
        CONTRACT_TEMPLATES,
        EFFECTS,
        PROOF_KINDS,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        OSLStaticError,
        Statement,
        StaticReport,
        digest,
    )
except ImportError:  # pragma: no cover
    from osl_model import (  # type: ignore
        CONTRACT_TEMPLATES,
        EFFECTS,
        PROOF_KINDS,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        OSLStaticError,
        Statement,
        StaticReport,
        digest,
    )


IDENT = r"[A-Za-z_][\w-]*"
REAL = r"[-+0-9.eE]+"


def _literal(text: str) -> Any:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return ast.literal_eval(text)


def _name_list(text: str) -> tuple[str, ...]:
    value = _literal(text)
    if not isinstance(value, (list, tuple)):
        raise ValueError("expected a bracketed list")
    result = tuple(str(item) for item in value)
    if len(set(result)) != len(result):
        raise ValueError("list entries must be unique")
    return result


def _stmt(kind: str, line_number: int, raw_source: str, **args: Any) -> Statement:
    return Statement(kind=kind, args=args, line_number=line_number, source=raw_source)


def parse_line(line: str, line_number: int) -> Statement:
    """Parse one nonempty, noncomment source line."""

    if match := re.fullmatch(rf"module\s+({IDENT})", line):
        return _stmt("module", line_number, line, name=match.group(1))

    if match := re.fullmatch(rf"lineage\s+({IDENT})(?:\s+extends\s+({IDENT}))?", line):
        return _stmt("lineage", line_number, line, name=match.group(1), parent=match.group(2))

    if match := re.fullmatch(rf"agent\s+({IDENT})\s+lineage\s+({IDENT})", line):
        return _stmt("agent", line_number, line, name=match.group(1), lineage=match.group(2))

    if match := re.fullmatch(
        rf"grant\s+({IDENT})\s+effect\s+({IDENT})(?:\s+uses\s+(\d+))?(?:\s+until\s+(\d+))?",
        line,
    ):
        agent, effect, uses, until = match.groups()
        return _stmt(
            "grant",
            line_number,
            line,
            agent=agent,
            effect=effect,
            uses=None if uses is None else int(uses),
            until=None if until is None else int(until),
        )

    if match := re.fullmatch(rf"revoke\s+({IDENT})\s+effect\s+({IDENT})", line):
        return _stmt("revoke", line_number, line, agent=match.group(1), effect=match.group(2))

    if match := re.fullmatch(rf"space\s+({IDENT})\s+dim\s+(\d+)", line):
        return _stmt("space", line_number, line, name=match.group(1), dim=int(match.group(2)))

    if match := re.fullmatch(rf"vector\s+({IDENT})\s+in\s+({IDENT})\s+values\s+(.+)", line):
        return _stmt(
            "vector",
            line_number,
            line,
            name=match.group(1),
            space=match.group(2),
            values=_literal(match.group(3)),
        )

    if match := re.fullmatch(
        rf"operator\s+({IDENT})\s*:\s*({IDENT})\s*->\s*({IDENT})\s+kind\s+({IDENT})\s+matrix\s+(.+)",
        line,
    ):
        return _stmt(
            "operator",
            line_number,
            line,
            name=match.group(1),
            source_space=match.group(2),
            target_space=match.group(3),
            operator_kind=match.group(4),
            matrix=_literal(match.group(5)),
        )

    if match := re.fullmatch(rf"apply\s+({IDENT})\s*=\s*({IDENT})\(({IDENT})\)", line):
        return _stmt(
            "apply",
            line_number,
            line,
            target=match.group(1),
            operator=match.group(2),
            vector=match.group(3),
        )

    if match := re.fullmatch(rf"transport\s+({IDENT})\s+via\s+({IDENT})\s+as\s+({IDENT})", line):
        return _stmt(
            "transport",
            line_number,
            line,
            operator=match.group(1),
            transport=match.group(2),
            result=match.group(3),
        )

    if match := re.fullmatch(rf"check_projector\s+({IDENT})(?:\s+tolerance\s+({REAL}))?", line):
        return _stmt(
            "check_projector",
            line_number,
            line,
            operator=match.group(1),
            tolerance=float(match.group(2) or "1e-9"),
        )

    if match := re.fullmatch(
        rf"check_intertwiner\s+({IDENT})\s+between\s+({IDENT})\s+and\s+({IDENT})(?:\s+tolerance\s+({REAL}))?",
        line,
    ):
        return _stmt(
            "check_intertwiner",
            line_number,
            line,
            transport=match.group(1),
            left=match.group(2),
            right=match.group(3),
            tolerance=float(match.group(4) or "1e-9"),
        )

    if match := re.fullmatch(
        rf'observe\s+({IDENT})\s+by\s+({IDENT})\s+content\s+(".*")\s+confidence\s+({REAL})',
        line,
    ):
        return _stmt(
            "observe",
            line_number,
            line,
            name=match.group(1),
            agent=match.group(2),
            content=ast.literal_eval(match.group(3)),
            confidence=float(match.group(4)),
        )

    if match := re.fullmatch(
        rf'infer\s+({IDENT})\s+by\s+({IDENT})\s+from\s+({IDENT})\s+content\s+(".*")\s+confidence\s+({REAL})',
        line,
    ):
        return _stmt(
            "infer",
            line_number,
            line,
            name=match.group(1),
            agent=match.group(2),
            source_packet=match.group(3),
            content=ast.literal_eval(match.group(4)),
            confidence=float(match.group(5)),
        )

    if match := re.fullmatch(
        rf'simulate\s+({IDENT})\s+by\s+({IDENT})\s+content\s+(".*")\s+confidence\s+({REAL})',
        line,
    ):
        return _stmt(
            "simulate",
            line_number,
            line,
            name=match.group(1),
            agent=match.group(2),
            content=ast.literal_eval(match.group(3)),
            confidence=float(match.group(4)),
        )

    if match := re.fullmatch(
        rf'inject\s+({IDENT})\s+to\s+({IDENT})\s+content\s+(".*")\s+confidence\s+({REAL})',
        line,
    ):
        return _stmt(
            "inject",
            line_number,
            line,
            name=match.group(1),
            agent=match.group(2),
            content=ast.literal_eval(match.group(3)),
            confidence=float(match.group(4)),
        )

    if match := re.fullmatch(
        rf'neural_propose\s+({IDENT})\s+to\s+({IDENT})\s+feature\s+({IDENT})\s+content\s+(".*")\s+confidence\s+({REAL})',
        line,
    ):
        return _stmt(
            "neural_propose",
            line_number,
            line,
            name=match.group(1),
            agent=match.group(2),
            feature=match.group(3),
            content=ast.literal_eval(match.group(4)),
            confidence=float(match.group(5)),
        )

    if match := re.fullmatch(
        rf"communicate\s+({IDENT})\s+from\s+({IDENT})\s+to\s+({IDENT})\s+as\s+({IDENT})(?:\s+in\s+({IDENT}))?",
        line,
    ):
        return _stmt(
            "communicate",
            line_number,
            line,
            source_packet=match.group(1),
            source_agent=match.group(2),
            target_agent=match.group(3),
            target_packet=match.group(4),
            session=match.group(5),
        )

    if match := re.fullmatch(rf"bind\s+({IDENT})\s+to\s+({IDENT})", line):
        return _stmt("bind", line_number, line, packet=match.group(1), agent=match.group(2))

    if match := re.fullmatch(rf"quarantine\s+({IDENT})\s+by\s+({IDENT})", line):
        return _stmt("quarantine", line_number, line, packet=match.group(1), agent=match.group(2))

    if match := re.fullmatch(rf"endorse\s+({IDENT})\s+by\s+({IDENT})\s+threshold\s+({REAL})", line):
        return _stmt(
            "endorse",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            threshold=float(match.group(3)),
        )

    if match := re.fullmatch(
        rf"authorize\s+({IDENT})\s+by\s+({IDENT})\s+for\s+({IDENT})(?:\s+requires\s+({IDENT}))?",
        line,
    ):
        return _stmt(
            "authorize",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            scope=match.group(3),
            proof=match.group(4),
        )

    if match := re.fullmatch(
        rf"write_memory\s+({IDENT})\s+by\s+({IDENT})\s+as\s+({IDENT})(?:\s+requires\s+({IDENT}))?",
        line,
    ):
        return _stmt(
            "write_memory",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            memory_class=match.group(3),
            proof=match.group(4),
        )

    if line.startswith("plan "):
        match = re.fullmatch(
            rf"plan\s+({IDENT})\s+by\s+({IDENT})\s+using\s+({IDENT})\s+effect\s+({IDENT})(.*)",
            line,
        )
        if match:
            action, agent, packet, effect, tail = match.groups()
            expected: float | None = None
            proof: str | None = None
            tail = tail.strip()
            while tail:
                if m := re.match(rf"expected\s+({REAL})(?:\s+|$)", tail):
                    if expected is not None:
                        raise OSLStaticError(f"line {line_number}: duplicate expected clause")
                    expected = float(m.group(1))
                    tail = tail[m.end() :].strip()
                    continue
                if m := re.match(rf"requires\s+({IDENT})(?:\s+|$)", tail):
                    if proof is not None:
                        raise OSLStaticError(f"line {line_number}: duplicate requires clause")
                    proof = m.group(1)
                    tail = tail[m.end() :].strip()
                    continue
                raise OSLStaticError(f"line {line_number}: invalid plan clause {tail!r}")
            return _stmt(
                "plan",
                line_number,
                line,
                action=action,
                agent=agent,
                packet=packet,
                effect=effect,
                expected=expected,
                proof=proof,
            )

    if match := re.fullmatch(rf"execute\s+({IDENT})\s+by\s+({IDENT})", line):
        return _stmt("execute", line_number, line, action=match.group(1), agent=match.group(2))

    if match := re.fullmatch(rf"feedback\s+({IDENT})\s+by\s+({IDENT})\s+observed\s+({REAL})", line):
        return _stmt(
            "feedback",
            line_number,
            line,
            action=match.group(1),
            agent=match.group(2),
            observed=float(match.group(3)),
        )

    # First-class proof terms.  Resource modes are parsed as a suffix so the
    # core proof grammar remains readable and backward compatible.
    proof_line = line
    proof_mode = "persistent"
    if line.startswith("proof "):
        mode_match = re.fullmatch(
            r"(.+)\s+mode\s+(persistent|affine|linear)", line
        )
        if mode_match:
            proof_line = mode_match.group(1)
            proof_mode = mode_match.group(2)

    proof_patterns: list[tuple[str, str]] = [
        ("access", rf"proof\s+({IDENT})\s+access\s+({IDENT})\s+by\s+({IDENT})"),
        ("origin", rf"proof\s+({IDENT})\s+origin\s+({IDENT})\s+source\s+({IDENT})\s+lineage\s+({IDENT})"),
        ("clear", rf"proof\s+({IDENT})\s+clear\s+({IDENT})\s+for\s+({IDENT})"),
        ("endorsement", rf"proof\s+({IDENT})\s+endorsement\s+({IDENT})\s+by\s+({IDENT})"),
        ("authorization", rf"proof\s+({IDENT})\s+authorization\s+({IDENT})\s+by\s+({IDENT})\s+for\s+({IDENT})"),
        ("observation", rf"proof\s+({IDENT})\s+observation\s+({IDENT})\s+by\s+({IDENT})"),
        ("capability", rf"proof\s+({IDENT})\s+capability\s+({IDENT})\s+by\s+({IDENT})"),
    ]
    for proof_kind, pattern in proof_patterns:
        if match := re.fullmatch(pattern, proof_line):
            groups = match.groups()
            args: dict[str, Any] = {
                "name": groups[0],
                "proof_kind": proof_kind,
                "resource_mode": proof_mode,
            }
            if proof_kind == "origin":
                args.update(packet=groups[1], source_agent=groups[2], source_lineage=groups[3])
            elif proof_kind == "authorization":
                args.update(packet=groups[1], agent=groups[2], scope=groups[3])
            elif proof_kind == "capability":
                args.update(effect=groups[1], agent=groups[2])
            else:
                args.update(packet=groups[1], agent=groups[2])
            return _stmt("proof", line_number, line, **args)

    if match := re.fullmatch(
        rf"proof\s+({IDENT})\s+use\s+({IDENT})\s+by\s+({IDENT})\s+for\s+({IDENT})\s+from\s+(\[.*\])",
        proof_line,
    ):
        return _stmt(
            "proof",
            line_number,
            line,
            name=match.group(1),
            proof_kind="use",
            packet=match.group(2),
            agent=match.group(3),
            scope=match.group(4),
            premises=_name_list(match.group(5)),
            resource_mode=proof_mode,
        )

    if match := re.fullmatch(
        rf"proof\s+({IDENT})\s+ownership\s+({IDENT})\s+by\s+({IDENT})\s+as\s+({IDENT})\s+from\s+(\[.*\])",
        proof_line,
    ):
        return _stmt(
            "proof",
            line_number,
            line,
            name=match.group(1),
            proof_kind="ownership",
            packet=match.group(2),
            agent=match.group(3),
            memory_class=match.group(4),
            premises=_name_list(match.group(5)),
            resource_mode=proof_mode,
        )

    # Trusted boundary attestations for provisional neural packets.
    if match := re.fullmatch(
        rf"attest\s+origin\s+({IDENT})\s+by\s+({IDENT})\s+lineage\s+({IDENT})\s+as\s+({IDENT})",
        line,
    ):
        return _stmt(
            "attest_origin",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            lineage=match.group(3),
            proof=match.group(4),
        )

    if match := re.fullmatch(
        rf"attest\s+relevance\s+({IDENT})\s+by\s+({IDENT})\s+for\s+({IDENT})\s+as\s+({IDENT})",
        line,
    ):
        return _stmt(
            "attest_relevance",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            scope=match.group(3),
            proof=match.group(4),
        )

    if match := re.fullmatch(rf"admit\s+({IDENT})\s+by\s+({IDENT})\s+using\s+(\[.*\])", line):
        return _stmt(
            "admit",
            line_number,
            line,
            packet=match.group(1),
            agent=match.group(2),
            proofs=_name_list(match.group(3)),
        )

    if match := re.fullmatch(rf"reject_candidate\s+({IDENT})\s+by\s+({IDENT})", line):
        return _stmt(
            "reject_candidate", line_number, line, packet=match.group(1), agent=match.group(2)
        )

    # Temporal contracts.
    if match := re.fullmatch(rf"contract\s+({IDENT})\s+always\s+({IDENT})", line):
        return _stmt(
            "contract",
            line_number,
            line,
            name=match.group(1),
            template=match.group(2),
            within=None,
        )

    if match := re.fullmatch(
        rf"contract\s+({IDENT})\s+after\s+execute\s+require\s+feedback\s+within\s+(\d+)",
        line,
    ):
        return _stmt(
            "contract",
            line_number,
            line,
            name=match.group(1),
            template="feedback_deadline",
            within=int(match.group(2)),
        )

    if line == "check_contracts":
        return _stmt("check_contracts", line_number, line)

    if line == "verify_receipts":
        return _stmt("verify_receipts", line_number, line)

    # Transactions.
    if match := re.fullmatch(rf"begin_transaction\s+({IDENT})", line):
        return _stmt("begin_transaction", line_number, line, name=match.group(1))
    if match := re.fullmatch(rf"commit_transaction\s+({IDENT})", line):
        return _stmt("commit_transaction", line_number, line, name=match.group(1))
    if match := re.fullmatch(rf"rollback_transaction\s+({IDENT})", line):
        return _stmt("rollback_transaction", line_number, line, name=match.group(1))

    # Finite-state shared-workspace/session protocols.
    if match := re.fullmatch(
        rf"session\s+({IDENT})\s+participants\s+(\[.*\])\s+initial\s+({IDENT})",
        line,
    ):
        return _stmt(
            "session",
            line_number,
            line,
            name=match.group(1),
            participants=_name_list(match.group(2)),
            initial=match.group(3),
        )

    if match := re.fullmatch(
        rf"session_transition\s+({IDENT})\s+({IDENT})\s+communicate\s+({IDENT})\s+({IDENT})\s*->\s*({IDENT})",
        line,
    ):
        return _stmt(
            "session_transition",
            line_number,
            line,
            session=match.group(1),
            source_state=match.group(2),
            sender=match.group(3),
            receiver=match.group(4),
            target_state=match.group(5),
        )

    if match := re.fullmatch(rf"start_session\s+({IDENT})", line):
        return _stmt("start_session", line_number, line, session=match.group(1))

    if match := re.fullmatch(
        rf"session_terminal\s+({IDENT})\s+({IDENT})", line
    ):
        return _stmt(
            "session_terminal",
            line_number,
            line,
            session=match.group(1),
            state=match.group(2),
        )

    if match := re.fullmatch(rf"verify_session\s+({IDENT})", line):
        return _stmt("verify_session", line_number, line, session=match.group(1))

    # Hyperproperty audit carriers.
    if match := re.fullmatch(rf"secret\s+({IDENT})\s+value\s+(.+)", line):
        return _stmt("secret", line_number, line, name=match.group(1), value=_literal(match.group(2)))

    if match := re.fullmatch(
        rf"metadata\s+({IDENT})\s+value\s+(.+)\s+source\s+(trusted|agent)", line
    ):
        return _stmt(
            "metadata",
            line_number,
            line,
            name=match.group(1),
            value=_literal(match.group(2)),
            source=match.group(3),
            secret=None,
        )

    if match := re.fullmatch(
        rf"metadata\s+({IDENT})\s+from_secret\s+({IDENT})\s+source\s+(trusted|agent)",
        line,
    ):
        return _stmt(
            "metadata",
            line_number,
            line,
            name=match.group(1),
            value=None,
            source=match.group(3),
            secret=match.group(2),
        )

    if line.startswith("assert "):
        return _stmt("assert", line_number, line, body=line[len("assert ") :])

    if line == "show":
        return _stmt("show", line_number, line)

    raise OSLStaticError(f"line {line_number}: unrecognized statement: {line}")


def parse_program(source: str) -> tuple[Statement, ...]:
    statements: list[Statement] = []
    for line_number, raw in enumerate(source.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        statements.append(parse_line(stripped, line_number))
    return tuple(statements)


class StaticChecker:
    """Finite declaration/type-oriented checker for the concrete language."""

    def check(self, statements: Iterable[Statement]) -> StaticReport:
        statements = tuple(statements)
        module_seen = False
        lineages: set[str] = set()
        agents: set[str] = set()
        spaces: set[str] = set()
        vectors: set[str] = set()
        operators: set[str] = set()
        packets: set[str] = set()
        proofs: set[str] = set()
        actions: set[str] = set()
        contracts: set[str] = set()
        sessions: set[str] = set()
        secrets: set[str] = set()
        transaction: str | None = None
        warnings: list[str] = []
        counts: Counter[str] = Counter()

        def fail(stmt: Statement, message: str) -> None:
            raise OSLStaticError(f"line {stmt.line_number}: {message}")

        def require(stmt: Statement, name: str, table: set[str], kind: str) -> None:
            if name not in table:
                fail(stmt, f"unknown {kind} {name!r}")

        for stmt in statements:
            counts[stmt.kind] += 1
            a = stmt.args
            if stmt.kind == "module":
                if module_seen:
                    fail(stmt, "module already declared")
                module_seen = True
            elif stmt.kind == "lineage":
                if a["name"] in lineages:
                    fail(stmt, f"lineage {a['name']!r} already declared")
                if a["parent"] is not None:
                    require(stmt, a["parent"], lineages, "parent lineage")
                lineages.add(a["name"])
            elif stmt.kind == "agent":
                if a["name"] in agents:
                    fail(stmt, f"agent {a['name']!r} already declared")
                require(stmt, a["lineage"], lineages, "lineage")
                agents.add(a["name"])
            elif stmt.kind in {"grant", "revoke"}:
                require(stmt, a["agent"], agents, "agent")
                if a["effect"] not in EFFECTS:
                    fail(stmt, f"unknown effect {a['effect']!r}")
                if stmt.kind == "grant" and a["uses"] is not None and a["uses"] <= 0:
                    fail(stmt, "capability uses must be positive")
            elif stmt.kind == "space":
                if a["dim"] <= 0:
                    fail(stmt, "space dimension must be positive")
                if a["name"] in spaces:
                    fail(stmt, f"space {a['name']!r} already declared")
                spaces.add(a["name"])
            elif stmt.kind == "vector":
                require(stmt, a["space"], spaces, "space")
                vectors.add(a["name"])
            elif stmt.kind == "operator":
                require(stmt, a["source_space"], spaces, "source space")
                require(stmt, a["target_space"], spaces, "target space")
                operators.add(a["name"])
            elif stmt.kind == "apply":
                require(stmt, a["operator"], operators, "operator")
                require(stmt, a["vector"], vectors, "vector")
                vectors.add(a["target"])
            elif stmt.kind == "transport":
                require(stmt, a["operator"], operators, "operator")
                require(stmt, a["transport"], operators, "transport operator")
                operators.add(a["result"])
            elif stmt.kind == "check_projector":
                require(stmt, a["operator"], operators, "operator")
            elif stmt.kind == "check_intertwiner":
                require(stmt, a["transport"], operators, "transport operator")
                require(stmt, a["left"], operators, "left operator")
                require(stmt, a["right"], operators, "right operator")
            elif stmt.kind in {"observe", "simulate", "inject", "neural_propose"}:
                require(stmt, a["agent"], agents, "agent")
                if a["name"] in packets:
                    fail(stmt, f"packet {a['name']!r} already declared")
                if not 0.0 <= a["confidence"] <= 1.0:
                    fail(stmt, "confidence must lie in [0,1]")
                packets.add(a["name"])
            elif stmt.kind == "infer":
                require(stmt, a["agent"], agents, "agent")
                require(stmt, a["source_packet"], packets, "source packet")
                packets.add(a["name"])
            elif stmt.kind == "communicate":
                require(stmt, a["source_packet"], packets, "source packet")
                require(stmt, a["source_agent"], agents, "source agent")
                require(stmt, a["target_agent"], agents, "target agent")
                if a["session"] is not None:
                    require(stmt, a["session"], sessions, "session")
                packets.add(a["target_packet"])
            elif stmt.kind in {"bind", "quarantine", "endorse", "authorize", "write_memory"}:
                require(stmt, a["packet"], packets, "packet")
                require(stmt, a["agent"], agents, "agent")
                if stmt.kind == "write_memory" and a["memory_class"] not in PROVENANCE_CLASSES:
                    fail(stmt, f"unknown memory class {a['memory_class']!r}")
                if a.get("proof") is not None:
                    require(stmt, a["proof"], proofs, "proof")
            elif stmt.kind == "plan":
                require(stmt, a["agent"], agents, "agent")
                require(stmt, a["packet"], packets, "packet")
                if a["effect"] not in EFFECTS:
                    fail(stmt, f"unknown effect {a['effect']!r}")
                if a["proof"] is not None:
                    require(stmt, a["proof"], proofs, "proof")
                actions.add(a["action"])
            elif stmt.kind in {"execute", "feedback"}:
                require(stmt, a["action"], actions, "action")
                require(stmt, a["agent"], agents, "agent")
            elif stmt.kind == "proof":
                if a["proof_kind"] not in PROOF_KINDS:
                    fail(stmt, f"unknown proof kind {a['proof_kind']!r}")
                if a.get("resource_mode", "persistent") not in PROOF_RESOURCE_MODES:
                    fail(stmt, f"unknown proof resource mode {a.get('resource_mode')!r}")
                if a["name"] in proofs:
                    fail(stmt, f"proof {a['name']!r} already declared")
                if a["proof_kind"] == "capability":
                    require(stmt, a["agent"], agents, "agent")
                    if a["effect"] not in EFFECTS:
                        fail(stmt, f"unknown effect {a['effect']!r}")
                else:
                    require(stmt, a["packet"], packets, "packet")
                    if a.get("agent") is not None:
                        require(stmt, a["agent"], agents, "agent")
                for premise in a.get("premises", ()):
                    require(stmt, premise, proofs, "premise proof")
                proofs.add(a["name"])
            elif stmt.kind in {"attest_origin", "attest_relevance"}:
                require(stmt, a["packet"], packets, "packet")
                require(stmt, a["agent"], agents, "agent")
                if stmt.kind == "attest_origin":
                    require(stmt, a["lineage"], lineages, "lineage")
                proofs.add(a["proof"])
            elif stmt.kind == "admit":
                require(stmt, a["packet"], packets, "packet")
                require(stmt, a["agent"], agents, "agent")
                for proof in a["proofs"]:
                    require(stmt, proof, proofs, "admission proof")
            elif stmt.kind == "reject_candidate":
                require(stmt, a["packet"], packets, "packet")
                require(stmt, a["agent"], agents, "agent")
            elif stmt.kind == "contract":
                if a["template"] not in CONTRACT_TEMPLATES:
                    fail(stmt, f"unknown contract template {a['template']!r}")
                if a["name"] in contracts:
                    fail(stmt, f"contract {a['name']!r} already declared")
                if a["template"] == "feedback_deadline" and (a["within"] or 0) <= 0:
                    fail(stmt, "feedback deadline must be positive")
                contracts.add(a["name"])
            elif stmt.kind == "begin_transaction":
                if transaction is not None:
                    fail(stmt, f"nested transaction inside {transaction!r} is not supported")
                transaction = a["name"]
            elif stmt.kind in {"commit_transaction", "rollback_transaction"}:
                if transaction != a["name"]:
                    fail(stmt, f"transaction {a['name']!r} is not active")
                transaction = None
            elif stmt.kind == "session":
                if a["name"] in sessions:
                    fail(stmt, f"session {a['name']!r} already declared")
                if len(a["participants"]) < 2:
                    fail(stmt, "a session requires at least two participants")
                for participant in a["participants"]:
                    require(stmt, participant, agents, "session participant")
                sessions.add(a["name"])
            elif stmt.kind in {
                "session_transition",
                "start_session",
                "session_terminal",
                "verify_session",
            }:
                require(stmt, a["session"], sessions, "session")
                if stmt.kind == "session_transition":
                    require(stmt, a["sender"], agents, "sender")
                    require(stmt, a["receiver"], agents, "receiver")
            elif stmt.kind == "secret":
                secrets.add(a["name"])
            elif stmt.kind == "metadata":
                if a["secret"] is not None:
                    require(stmt, a["secret"], secrets, "secret")
                    warnings.append(
                        f"line {stmt.line_number}: public metadata {a['name']!r} "
                        f"depends on private secret {a['secret']!r}"
                    )
            elif stmt.kind in {"assert", "show", "check_contracts", "verify_receipts"}:
                pass
            else:  # pragma: no cover - parser/checker mismatch guard
                fail(stmt, f"static checker does not recognize {stmt.kind!r}")

        if not module_seen:
            warnings.append("program has no module declaration")
        if transaction is not None:
            raise OSLStaticError(f"unclosed transaction {transaction!r}")

        symbol_counts = {
            "lineages": len(lineages),
            "agents": len(agents),
            "spaces": len(spaces),
            "vectors": len(vectors),
            "operators": len(operators),
            "packets": len(packets),
            "proofs": len(proofs),
            "actions": len(actions),
            "contracts": len(contracts),
            "sessions": len(sessions),
            "secrets": len(secrets),
        }
        payload = {
            "ok": True,
            "statement_count": len(statements),
            "symbol_counts": symbol_counts,
            "warnings": warnings,
            "statement_kinds": dict(sorted(counts.items())),
        }
        return StaticReport(
            ok=True,
            statement_count=len(statements),
            symbol_counts=symbol_counts,
            warnings=tuple(warnings),
            report_digest=digest(payload),
        )


def parse_and_check(source: str) -> tuple[tuple[Statement, ...], StaticReport]:
    statements = parse_program(source)
    report = StaticChecker().check(statements)
    return statements, report
