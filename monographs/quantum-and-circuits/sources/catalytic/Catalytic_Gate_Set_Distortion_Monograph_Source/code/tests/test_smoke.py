from catalytic_gate_atlas import exact_affine_toffoli_census, exact_clifford_census, verify_canonical_atom


def test_linear_words() -> None:
    for modulus in (2, 3, 5, 8):
        result = verify_canonical_atom(modulus)
        assert result["ambient_matches"]
        assert result["restricted_matches"]


def test_two_qubit_clifford_entangling_defect() -> None:
    result = exact_clifford_census(2, entangling_cost=True)
    assert result["defect_count"] == 4
    assert result["maximum_defect"] == 1


def test_three_bit_affine_rigidity() -> None:
    total = exact_affine_toffoli_census(3, entangling_cost=False)
    weighted = exact_affine_toffoli_census(3, entangling_cost=True)
    assert total["defect_count"] == 0
    assert weighted["defect_count"] == 0


def test_openqasm_export() -> None:
    from catalytic_gate_atlas import gate_word_to_openqasm

    text = gate_word_to_openqasm(["H1", "CX10", "S0"], 2, title="witness")
    assert "OPENQASM 3.0;" in text
    assert "h q[1];" in text
    assert "cx q[1], q[0];" in text
    assert "s q[0];" in text
