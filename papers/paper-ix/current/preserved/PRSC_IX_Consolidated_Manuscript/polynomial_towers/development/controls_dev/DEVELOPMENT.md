# Tower verification controls development

The positive control module proves:

- `X² − 5` has the lower root one modulo two and modulo four, but no integer root modulo eight and therefore no all-level integer tower.
- The rectangular system `F(X,Y) = X` has a surjective finite-ring Jacobian and two distinct actual 2-adic roots congruent modulo two.
- The nonsingular system `F(X) = X − 2` has the lower root zero modulo two, but its exact integer root cannot retain zero modulo four.

Each negative file deliberately states the corresponding false extension and is required to fail with a mathematical type mismatch. An unavailable import, unknown declaration, timeout, or compiler panic is not an accepted negative outcome.

Development failures are retained in this directory:

1. `controls_compile_01.log`: repeated `--import-dir` arguments kept only the final directory. The development build was repaired using links to the existing checked import modules. The final gate uses a fresh single build directory and recompiles all project imports.
2. `controls_compile_03.log`: unrestricted simplification of the polynomial constant in `X − 2` left `constantCoeff` expressions. The proof now explicitly uses the evaluation and formal-derivative identities.
3. `controls_compile_04.log`: unused simp arguments failed warnings-as-errors. The redundant arguments were removed, with no linter disabled.

`controls_compile_02.log` is the passing earlier control-module development build before strengthening the precision counterexample to an actual nonsingular polynomial system. The final active source is frozen and checked by the combined replay report.
