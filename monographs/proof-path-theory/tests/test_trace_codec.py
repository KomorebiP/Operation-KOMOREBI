from dataclasses import replace
import itertools
import json

import pytest

from proof_path_theory import ClaimNode, Justification, NodeKind, ProofField, ProofFieldViews, solve_extension
from proof_path_theory.trace_codec import (
    IndexedRule, IndexedProblem, IndexedWitness, IndexedCertificate,
    WireFormatError, WireResourceError, PROBLEM_TAG, CERTIFICATE_TAG,
    canonical_bytes, problem_to_value, problem_from_value, certificate_to_value,
    certificate_from_value, dumps_problem, loads_problem, dumps_trace_certificate,
    loads_trace_certificate, valid_indexed_problem, check_indexed_certificate,
    replay_indexed, check_indexed_witness, check_trace_json,
    index_problem, index_certificate, export_trace_exchange,
)


def chain():
    return IndexedProblem(4, (0,), (IndexedRule((0,), 1), IndexedRule((1,), 2)), (), (3,))


def positive():
    return IndexedCertificate(True, (0, 1, 2), (0, 1))


def negative():
    return IndexedCertificate(False, (0, 1, 2), (0, 1), IndexedWitness(2, (0, 1)))


def test_positive_negative_and_least_closure():
    assert check_indexed_certificate(chain(), positive())
    p = replace(chain(), negative=(2,))
    assert check_indexed_certificate(p, negative())
    assert not check_indexed_certificate(p, positive())


@pytest.mark.parametrize("n", [0, 1, 2, 2**53 + 1, 2**100 + 33])
def test_numeric_record_roundtrip_is_exact(n):
    p = IndexedProblem(n, (), (), (), ())
    assert loads_problem(dumps_problem(p)) == p
    c = IndexedCertificate(False, (n,), (n,), IndexedWitness(n, (n,)))
    assert loads_trace_certificate(dumps_trace_certificate(c)) == c


@pytest.mark.parametrize("value", [True, False, 1.0, "1", -1, None, [], {}])
def test_schema_rejects_non_natural_node_count(value):
    with pytest.raises(WireFormatError):
        problem_from_value([PROBLEM_TAG, value, [], [], [], []])


@pytest.mark.parametrize("value", [0, 1, "true", "false", None, [], {}])
def test_verdict_must_be_literal_bool(value):
    with pytest.raises(WireFormatError):
        certificate_from_value([CERTIFICATE_TAG, value, [], [], None])


@pytest.mark.parametrize("data", [
    b'["proof-path/problem/1",1.0,[],[],[],[]]',
    b'["proof-path/problem/1",1e0,[],[],[],[]]',
    b'["proof-path/problem/1",-0,[],[],[],[]]',
    b'["proof-path/problem/1",NaN,[],[],[],[]]',
    b'["proof-path/problem/1",Infinity,[],[],[],[]]',
    b' ["proof-path/problem/1",1,[],[],[],[]]',
    b'["proof-path/problem/1", 1,[],[],[],[]]',
    b'["proof-path/problem/1",1,[],[],[],[]]\n\n',
    b'{"same":1,"same":2}', b'\xff',
    b'["proof-path/problem/1",1,[],[],[],[],null]',
    b'["proof-path/problem/2",1,[],[],[],[]]',
])
def test_strict_bytes_and_versioned_shape(data):
    with pytest.raises(WireFormatError):
        loads_problem(data)


def test_one_final_lf_and_resource_boundary():
    raw = dumps_problem(chain())
    assert loads_problem(raw+b"\n") == chain()
    assert loads_problem(raw, max_bytes=len(raw)) == chain()
    with pytest.raises(WireResourceError):
        loads_problem(raw, max_bytes=len(raw)-1)
    with pytest.raises(ValueError):
        loads_problem(raw, max_bytes=True)


@pytest.mark.parametrize("update", [
    {"leaves": (4,)}, {"positive": (0, 0)}, {"negative": (3, 3)},
    {"rules": (IndexedRule((0, 0), 1),)}, {"rules": (IndexedRule((9,), 1),)},
    {"rules": (IndexedRule((0,), 9),)}, {"node_count": True},
])
def test_problem_validation_is_separate_from_syntax(update):
    p = replace(chain(), **update)
    assert not valid_indexed_problem(p)
    assert not check_indexed_certificate(p, positive())


@pytest.mark.parametrize("update", [
    {"trace": (1, 0)}, {"trace": (0, 0, 1)}, {"trace": (0, 99)},
    {"closure": (0, 1), "trace": (0,)},
    {"closure": (0, 1, 2, 3), "trace": ()},
    {"closure": (0, 1, 2, 2)}, {"closure": (0, 1, 99)},
    {"feasible": 1}, {"feasible": False, "obstruction": None},
    {"obstruction": IndexedWitness(2, (0, 1))},
])
def test_corrupt_complete_certificates_rejected(update):
    assert not check_indexed_certificate(chain(), replace(positive(), **update))


def test_causal_trace_redundancy_is_permitted():
    p = replace(chain(), negative=(2,))
    w = IndexedWitness(2, (0, 0, 1))
    assert check_indexed_witness(p, w)
    assert replay_indexed(p, w.trace, strict=True) is None
    assert replay_indexed(p, w.trace, strict=False) == (2, 1, 1, 0)
    assert check_indexed_certificate(p, replace(negative(), obstruction=w))


def test_redundancy_under_stronger_observations():
    p = replace(chain(), positive=(1,), negative=(2,))
    assert check_indexed_witness(p, IndexedWitness(2, (0, 1)))
    assert replay_indexed(p, (0, 1), strict=True) is None
    assert check_indexed_certificate(p, IndexedCertificate(False, (0, 1, 2), (1,), IndexedWitness(2, (0, 1))))


def test_direct_conflict_and_wrong_witness_target():
    p = replace(chain(), positive=(3,))
    assert check_indexed_witness(p, IndexedWitness(3, ()))
    assert not check_indexed_witness(p, IndexedWitness(2, (0, 1)))
    assert not check_indexed_witness(p, IndexedWitness(True, ()))


def test_cycles_do_not_self_justify():
    p = IndexedProblem(2, (), (IndexedRule((0,), 1), IndexedRule((1,), 0)), (), (1,))
    assert check_indexed_certificate(p, IndexedCertificate(True, (), ()))
    assert not check_indexed_witness(p, IndexedWitness(1, (0, 1)))
    assert check_indexed_certificate(replace(p, positive=(0,)),
                                    IndexedCertificate(False, (0, 1), (0,), IndexedWitness(1, (0,))))


def test_empty_field_and_zero_arity_rule():
    p = IndexedProblem(0, (), (), (), ())
    assert check_indexed_certificate(p, IndexedCertificate(True, (), ()))
    p = IndexedProblem(1, (), (IndexedRule((), 0),), (), ())
    assert check_indexed_certificate(p, IndexedCertificate(True, (0,), (0,)))
    assert not check_indexed_certificate(p, IndexedCertificate(True, (), ()))


def test_identical_rules_have_distinct_addresses():
    p = IndexedProblem(2, (0,), (IndexedRule((0,), 1), IndexedRule((0,), 1)), (), ())
    a, b = IndexedCertificate(True, (0, 1), (0,)), IndexedCertificate(True, (0, 1), (1,))
    assert check_indexed_certificate(p, a) and check_indexed_certificate(p, b)
    assert dumps_trace_certificate(a) != dumps_trace_certificate(b)


def test_original_named_export_roundtrip():
    f = ProofField([ClaimNode("a", "A", NodeKind.PREMISE), ClaimNode("b", "B", NodeKind.CLAIM),
                    ClaimNode("c", "C", NodeKind.CLAIM)],
                   [Justification("one", ("a",), "b", "test"), Justification("two", ("b",), "c", "test")],
                   premises=("a",), targets=("c",))
    views = ProofFieldViews(f)
    r = solve_extension(views, negative=("c",))
    binding, pj, cj = export_trace_exchange(views, r, negative=("c",))
    assert binding.node_names == ("a", "b", "c")
    assert binding.rule_names == ("one", "two")
    assert check_trace_json(pj, cj)
    assert loads_problem(pj) == binding.problem
    with pytest.raises(ValueError):
        export_trace_exchange(views, replace(r, feasible=True), negative=("c",))
    with pytest.raises(ValueError):
        index_problem(views, positive=("missing",))
    with pytest.raises(ValueError):
        index_certificate(binding, replace(r, rule_ids=("missing",)))


def test_replay_concatenation_small():
    p = chain()
    for size in range(4):
        for ids in itertools.product(range(3), repeat=size):
            for cut in range(size+1):
                for strict in (False, True):
                    middle = replay_indexed(p, ids[:cut], strict=strict)
                    composed = None if middle is None else replay_indexed(p, ids[cut:], strict=strict, known=middle)
                    assert replay_indexed(p, ids, strict=strict) == composed


def test_encoded_context_is_not_replaced_by_certificate():
    cert = dumps_trace_certificate(positive())
    assert check_trace_json(dumps_problem(chain()), cert)
    assert not check_trace_json(dumps_problem(replace(chain(), negative=(2,))), cert)
    assert not check_trace_json(dumps_problem(replace(chain(), leaves=())), cert)


def test_raw_record_order_is_preserved_even_when_semantics_agree():
    a = positive()
    b = replace(a, closure=(2, 0, 1))
    assert check_indexed_certificate(chain(), a) and check_indexed_certificate(chain(), b)
    assert dumps_trace_certificate(a) != dumps_trace_certificate(b)
    assert loads_trace_certificate(dumps_trace_certificate(b)) == b


def test_cli_wire_accept_and_reject(tmp_path, capsys):
    from proof_path_theory.cli import main
    p, c = tmp_path / "p.json", tmp_path / "c.json"
    p.write_bytes(dumps_problem(chain()) + b"\n")
    c.write_bytes(dumps_trace_certificate(positive()) + b"\n")
    assert main(["wire-check", str(p), str(c)]) == 0
    assert json.loads(capsys.readouterr().out)["valid"] is True
    p.write_bytes(dumps_problem(replace(chain(), negative=(2,))))
    assert main(["wire-check", str(p), str(c)]) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_cli_wire_format_error(tmp_path, capsys):
    from proof_path_theory.cli import main
    p, c = tmp_path / "p.json", tmp_path / "c.json"
    p.write_text("null")
    c.write_text("null")
    assert main(["wire-check", str(p), str(c)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "INPUT_ERROR"


def test_cli_exports_actual_field(tmp_path, capsys):
    from pathlib import Path
    from proof_path_theory.cli import main
    field = Path(__file__).resolve().parents[1] / "examples/and_dag.json"
    prefix = tmp_path / "packet"
    assert main(["wire-export", str(field), "--negative", "B", "--output-prefix", str(prefix)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "EXPORTED_CHECKED"
    assert out["feasible"] is False
    assert main(["wire-check", out["problem"], out["certificate"]]) == 0
