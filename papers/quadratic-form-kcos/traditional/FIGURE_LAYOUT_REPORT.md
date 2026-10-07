# Traditional figure layout revision — October 7, 2026

The edition contains 31 figures. Twenty-four matrix illustrations have clean layout derivatives; four matrix figures and all three packet figures remain byte-identical originals. Original matrix images remain unchanged in `../engine/figures_final/`. No solver runs, new measurements, or new hidden sample vectors were generated.

CSV charts preserve the archived coordinate values and row/series recipes. Each plotted line, scatter point or bar is checked against the source fields during generation; both reports retain the full artist arrays and input hashes. The early generator also verifies every archived CSV and original matrix PNG hash before and after generation.

The raw plotted vectors for files beginning `figure_05`, `figure_06`, and `figure_07` were not archived. Their replacements use exact phase-rank audit values, exact QR spectral-discrepancy audit values, and the original rounded packet-center/second-moment labels with the formal definitions. These clean summaries do not reconstruct the original singular-value or eigenvalue curves.

Annotations and equations occupy reserved white panels. Legends are external. Coincident rank curves use different marker sizes and outlines without coordinate jitter; the two dual-budget metrics use separate labeled panels. Partition labels follow the archived identifiers, including `fine_64` (which happens to contain 32 physical blocks).

All 36 proofs, 61 theorem/lemma/proposition/corollary/remark/algorithm environments and 342 display-math blocks are byte-identical to the pre-layout source snapshot (`LAYOUT_ONLY_PRESERVATION.json`). The last PDF build completed three LaTeX passes without warnings, overfull boxes, or unresolved references. Markdown converts all 31 canonical TeX captions to portable math and contains no raw HTML math spans or div wrappers.

Run `python build_traditional.py` to regenerate the layouts, PDF and Markdown. Required tools: Python with Matplotlib and NumPy, LaTeX (`pdflatex`), and Pandoc. `--skip-figures` retains the generated charts; `--skip-markdown` omits the Markdown export.

| Figure file | Final representation | Preservation source |
|---|---|---|
| `figure_01_residualization_geometry.png` | diagram relayout; same coordinates, formulas and projection relations | Original diagram relations |
| `figure_02_exact_block_kernel_assembly.png` | diagram relayout; unchanged block-sum identities and three-block connectivity | Original diagram relations |
| `figure_03_memory_law.png` | CSV relayout; notes outside axes | memory_asymptotic_sweep.csv |
| `figure_04_polyphase_lightcone.png` | structural support-array relayout; same 10 by 8 binary staircase | Original diagram relations |
| `figure_05_phase_local_rank.png` | replacement summary from exact archived rank audit; no singular-value vector reconstructed | phase_local_rank_audit.csv |
| `figure_06_qr_core_equivalence.png` | replacement identity diagram and exact archived singular-spectrum discrepancy summaries | qr_core_update_audit.csv |
| `figure_07_spectral_packets.png` | replacement centered-packet schematic and unchanged rounded original summary labels | Original rounded labels / formal definitions |
| `figure_08_partition_invariance.png` | CSV relayout; wrapped partition identifiers and external notes | partition_invariance.csv |
| `figure_09_approximate_lightcone_certificate.png` | CSV relayout of original generator; equations outside axes | approximate_lightcone_depth.csv |
| `figure_10_threshold_tradeoff.png` | CSV relayout of original generator; notes outside axes | approximate_lightcone_threshold_sweep.csv |
| `figure_11_budget_scheduler_comparison.png` | CSV relayout; legend and commentary separated | budget_scheduler_large.csv |
| `figure_12_double_buffer_model.png` | CSV relayout; formula outside axes | double_buffer_model.csv |
| `figure_13_edge_risk_vs_block_norm.png` | CSV relayout; commentary outside scatter | edge_risk_vs_block_norm.csv |
| `figure_14_dual_budget_tail_bridge.png` | CSV relayout; two labeled panels replace indistinguishable twin-axis lines | dual_budget_spectral_scheduler.csv |
| `figure_15_range_core_certification.png` | CSV relayout; wrapped commentary outside axes | certify_after_prune_range_core.csv |
| `figure_16_trace_moment_vs_weyl.png` | Unchanged original | Original PNG hash |
| `figure_17_residual_rank_completion.png` | CSV relayout; distinguish coincident curves without jitter | residual_completion_audit.csv |
| `figure_18_realistic_ld_effective_rank.png` | row order; x=ordinal; y=effective_rank; r² labels rounded to two decimals as archived figure | realistic_skat_scenarios.csv |
| `figure_19_realistic_streaming_invariance.png` | group by scenario in CSV order; x=block_size; y=kernel_relative_error | realistic_streaming_invariance.csv |
| `figure_20_realistic_deep_tail_accuracy.png` | concatenate CSVs; x=-reference_log10_p; y=max(abs(difference_decades),1e-16) using archived zero floor | realistic_deep_tail_accuracy.csv, realistic_large_deeper_tail.csv |
| `figure_21_reference_convergence.png` | CSV row order including repeated K; x=reference_K; y=abs(adaptive_minus_reference_decades) | reference_convergence.csv |
| `figure_22_noncentral_controls.png` | group df,nc in CSV order; x=-scipy_log10_p; y=max(abs(difference_decades),1e-16) using archived zero floor | noncentral_exact_controls.csv |
| `figure_23_deep_tail_precision_envelope.png` | Unchanged original | Original PNG hash |
| `figure_24_interval_deep_tail_width.png` | CSV row order; x=-target_log10_p; y=kcos_width_decades; footer ratios=multiplicative_ratio_minus_one rounded as archived to .1e | interval_deep_tail_controls.csv |
| `figure_24_signed_certificate_boundary.png` | explicit archived family order; x=tail_depth; y=certificate; tolerance=1e-8 | signed_precision_summary.csv |
| `figure_25_interval_arithmetic_vs_analytic.png` | CSV row order; x=interval_dps; y=total_width_decades_decimal or arithmetic_only_width_decades_decimal | interval_precision_sweep_1e5000.csv |
| `figure_26_accuracy_driven_refinement.png` | Unchanged original | Original PNG hash |
| `figure_27_imhof_p1e16_validation.png` | Unchanged original | Original PNG hash |
| `certificate_coverage.png` | Unchanged original | Original PNG hash |
| `runtime_scaling.png` | Unchanged original | Original PNG hash |
| `tolerance_ladder.png` | Unchanged original | Original PNG hash |

All 31 figures passed independent native-resolution inspection at pinned final hashes (`FIGURE_INDEPENDENT_REVIEW.json`). Independent preservation checks verified 197 early and 80 late plotted coordinate pairs, together with the recorded rank and discrepancy summaries (`FIGURE_DATA_PRESERVATION.json`). All 24 repaired chart placements were also inspected in 150-dpi PDF renders. The table-of-contents number columns have been widened, and its final pages 3–6 passed fresh independent inspection. Full-page review and raster-equivalence records are supplied with the combined release.
