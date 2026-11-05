# Operator catalog finite fixtures

These two standard-library Python programs accompany the [operator catalog](../../docs/operators/catalog/README.md). They use integers and `fractions.Fraction` to check named finite examples, boundary failures, and input guards.

Run the complete suite from the repository root:

```text
python -B examples/operator_catalog/Komorebi_Operator_Refined_Checks.py
```

The refined script reruns the preserved **79 checks** and its **85 additional checks**. The import replay passed all **164**: 93 identity checks, 59 counterexample checks, and 12 guard-rejection checks. A passing counterexample check observes the intended failure; a passing guard check observes the intended rejection. Neither is an extra positive theorem.

Each record has a stable check ID, a descriptive assertion, a kind, an explicit case count, and the OP identifiers it concerns. The [named-check reference](../../docs/operators/catalog/CHECKS.md) links these records to the catalog. Some records contain several finite cases; the count of named checks is not the number of examples, operators, or proofs.

To write a fresh JSON receipt, add an explicit destination:

```text
python -B examples/operator_catalog/Komorebi_Operator_Refined_Checks.py --json /tmp/operator-catalog-results.json
```

Without `--json`, the program prints its results and writes no receipt. It also supports module execution from the repository root:

```text
python -B -m examples.operator_catalog.Komorebi_Operator_Refined_Checks
```

The programs are independent mathematical fixtures. They do not execute the full Komorebi Math library or Lean, establish untested hypotheses, or turn finite examples into a general proof. Read each entry’s scope and the actual fixture before interpreting a result.

## Source and maintenance

The programs were imported from the refined *Komorebi Operator Compendium* of 4 November 2026. The [registry](../../docs/operators/catalog/registry.json) preserves original file SHA-256 values and source revisions. The baseline program is byte-for-byte unchanged. The refined program has only packaging changes: an adjacent/package import, and optional JSON output; its mathematical fixture code is unchanged.

Run the catalog tests after editing data, generated pages, or fixtures:

```text
python -B tools/operator_catalog.py --check
python -B -m unittest discover -s tools -p test_operator_catalog.py -v
```

The tests check stable IDs and links, source pins, formula delimiters, generated-page drift, and the binding between a fresh 164-check replay and the registry. A separate small regression protects the corrected existence statement in coarse descent; it is not added to the imported suite’s count.
