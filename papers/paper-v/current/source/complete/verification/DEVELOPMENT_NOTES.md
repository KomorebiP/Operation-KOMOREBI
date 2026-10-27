# Development and correction record

This record concerns only the new editorial appendix and packaging run. Original source and formal evidence were preserved unchanged.

## Corrected example-test issues

An early exact Smith-orbit test used ordinary Python division for an integer phase, inadvertently creating a floating-point value. The model was corrected to sympify inputs before division. Another equality test compared structurally different but algebraically equal complex rational expressions. It was corrected to test the simplified difference. These were exact-test implementation problems, not failures of the manuscript theorem. The final exact suite passes using the corrected rational/algebraic models.

## Corrected graphics and typesetting issues

The first compilation found an oversized object-atlas paragraph because the table followed prose without a paragraph break. It also rejected a backspace character produced by a non-raw Python string containing `\bmod`. The paragraph separation and string quoting were corrected. A subsequent compile flagged a long title; the title was shortened. Two diagnostic compiler outputs are retained under development/.

Visual inspection led to further corrections: ragged-right unhyphenated page titles, consistent lifting-plot origins, separation of numerical labels from the diagram, properly aligned sample-channel captions, white backing behind Smith-axis labels, and a fully drawn constant-mismatch circle instead of straight segments between orbit points. The discrete mask was changed to the explicitly stated radius-squared-five set, yielding 21 pixels and a ten-pixel symmetric difference; a dedicated census check was added. A symbolic circle-equation check was also added. The final suite therefore has 181 checks, rather than the earlier draft's 179.

The continuous Fourier curves and sensitivity curves use floating-point display coordinates only. Exact endpoint identities, rational increments, and finite models are tested separately. No interval certification of those plotted curves is claimed.

## Runtime and replay scope

A requested streaming terminal session was unavailable before one setup command could execute; the same setup was run through a supported non-streaming command. The original-source audit subsequently passed all 69 Python tests, 18 figure-pair regeneration, numerical-record comparison, and the 39-page original manuscript rebuild. No original proof source or numerical implementation required modification.

The final appendix compiles with no overflow, underfull-box, or unresolved-reference warnings. The combined PDF preserves original and appendix page text and rendered appearance. No Lean invocation occurred in this task. Compiler/axiom success records inside original_snapshot are inherited, not new.
