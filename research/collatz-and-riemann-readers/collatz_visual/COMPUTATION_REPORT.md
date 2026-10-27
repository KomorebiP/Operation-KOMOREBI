# Collatz visual atlas computation audit

The figures use exact Python integers and `Fraction` for every claim-supporting value. Floating point is used only to place marks on the page.

- complete_clock_controls: 2 finite checks passed.
- cylinder_instances: 79872 finite checks passed.
- seed3_clock_controls: 3 finite checks passed.
- horizon_prefix_checks: 34 finite checks passed.
- delayed_seed_checks: 14 finite checks passed.
- lift151_cases: 7 finite checks passed.
- progression1087_cases: 17 finite checks passed.
- density_inequality_checks: 48 finite checks passed.

The seed ranges, word ranges, software versions, hashes and actual runtime are recorded in `COMPUTATION_REPORT.json`. The deterministic regeneration command is `python conjecture_set/collatz_visual/figures.py`.

The cylinder test independently iterates each actual odd map, then compares its word with the residue computed by the affine formula. It also checks the affine endpoint equality for realized words. Density sums use exact binomial coefficients and rational powers.

No failure was observed in these finite checks. This does not certify the Collatz conjecture. The 1804 covered and 244 residual classes are historical aggregate counts and were not replayed. The common-height packing figure is an explicitly declared proof schematic, not orbit data. The source formulas are proved in the companion monograph.

Every positive odd map iteration is capped at 200 steps in complete-orbit plots. Independent classical and shortcut controls are capped at 500 iterations. A cap violation raises an assertion rather than silently marking the source convergent. No random sampling is used.

## Resolved authoring failures

- The first rendering run stopped at spread 16 because `linthresh` was passed to `Axes.set`. It was moved to `Axes.set_yscale` and the complete run passed.
- The initial peak arrow used a manually entered step 17 for the value 3077. Independent review found the correct step 32. The arrow now derives its location from the exact maximum index.
- Initial chart footers collided with axis labels. Footer prose was moved into the reading columns and retained in `data.json`. Plot margins are now fitted automatically, and the final figures are checked visually.
