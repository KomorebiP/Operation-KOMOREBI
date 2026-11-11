# Smith chart: exact packets and phase refinement

[Open the interactive Smith chart](https://KomorebiP.github.io/Operation-KOMOREBI/smith-chart.html) · [Extended demonstrations](../DEMONSTRATIONS.md)

**Author:** Komorebi P.  
**Status:** Interactive research demonstration with finite numerical checks. The classical Smith chart and roots-of-unity identities are not claimed as new discoveries.

## Scope

The interactive chart starts with a passive physical load \(Z=R+iX\), reference resistance \(Z_0>0\), and normalized impedance \(z=Z/Z_0\). Its reflection coordinate is

\[
\Gamma=\frac{z-1}{z+1},\qquad z=\frac{1+\Gamma}{1-\Gamma}.
\]

For a passive load \(R\geq0\), the reflection coordinate lies in the closed unit disk. A lossless line rotates \(\Gamma\) without changing its magnitude. The workbench separately displays cyclic algebraic phase rotations; these are not conflated with propagation through a line.

## Exact impedance packets

For \(|t|<1\), write \(z(t)=(1+t)/(1-t)\) and project its Taylor coefficients into residue classes modulo \(N\). Direct geometric-series summation gives

\[
\mathcal P_{N,0}z(t)=\frac{1+t^N}{1-t^N},\qquad
\mathcal P_{N,j}z(t)=\frac{2t^j}{1-t^N},\quad 1\leq j<N.
\]

Summing all \(N\) packets reconstructs \(z\). The normalized admittance is \(y=1/z\), and for even \(N\),

\[
\mathcal P_{N,j}y=(-1)^j\mathcal P_{N,j}z.
\]

For odd \(N\), parity alternates along a residue class, so the corresponding denominators are \(1+t^N\) rather than \(1-t^N\). In particular,

\[
\mathcal P_{N,0}y=\frac{1-t^N}{1+t^N},\qquad
\mathcal P_{N,j}y=\frac{2(-1)^jt^j}{1+t^N},\quad 1\leq j<N
\]

when \(N\) is odd. Refinement to order \(2N\) separates these parities.

The individual nonconstant impedance packets need not be passive functions. Their denominators also create boundary poles that cancel in the full reconstruction. Truncating or interpreting isolated packets as physical loads can therefore be misleading.

## Angular sampling and limitations

The symmetric open/short sensitivity weight is

\[
w(t)=\frac{1}{|1-t|^2}+\frac{1}{|1+t|^2}.
\]

At \(t=\rho e^{i\theta}\), it is a scalar multiple of the Poisson kernel at angle \(2\theta\), and its normalized angular density is

\[
p_\rho(\theta)=\frac{1-\rho^4}{2\pi(1-2\rho^2\cos(2\theta)+\rho^4)}.
\]

The interactive laboratory demonstrates this nonuniform sampling as a **coordinate-specific proposal**, not an optimal general-purpose interpolation method. For other analytic responses, uniform sampling can perform better. The page does not claim superiority over vector fitting, rational reconstruction, measured RF data, or noisy S-parameter recovery.

## Physical load comparisons

The interactive comparison retains two physical loads, A and B. Changing the positive reference impedance \(Z_0\) changes their reflection coefficients even when their impedances stay fixed. It is therefore incorrect to compare a pinned \(\Gamma_A\) normalized with one \(Z_0\) to a current \(\Gamma_B\) normalized with another.

The chart computes both coefficients in the **current shared reference frame**:

\[
\Gamma_A(Z_0)=\frac{Z_A-Z_0}{Z_A+Z_0},\qquad
\Gamma_B(Z_0)=\frac{Z_B-Z_0}{Z_B+Z_0}.
\]

The dashed A–B segment in the reflection disk represents the absolute complex difference \(|\Gamma_B-\Gamma_A|\). It is **not** a physical transmission-line path. The separate \(|Z_B-Z_A|\) readout stays in physical ohms, and the Swap control exchanges the physical loads without changing the shared \(Z_0\). An ideal open paired with an ideal open has zero physical difference; an ideal open paired with a finite load has an unbounded impedance separation.

This is a corrected consistency rule and interaction aid, not a new RF theorem. Session import/export retains the physical reference load and re-normalizes it using the restored current \(Z_0\).

## Reversible load editing

**Undo load** and **Redo load** track physical load coordinates R, X, and Z₀, the ideal-open state, and the pinned A reference. One completed mouse or touch drag creates one history step; canceling a drag restores its starting point. Ctrl/Cmd+Z undoes an edit, Ctrl/Cmd+Shift+Z or Ctrl+Y redoes it. Standard text-field undo remains native to the browser.

History is intentionally separate from the lossless-line length, cyclic projector order, research view, and sampling options. Reset and JSON session import establish a new load-history starting point. These controls are reversible interface operations, not additional RF transformations.

## Verification and source

Run the numerical suite in the **Verification** tab to inspect its deterministic test fixtures and reported residuals. These are finite double-precision tests, not formal proofs or hardware validation. Additional Python regression tests use exact rational arithmetic for the packet-reconstruction and admittance identities.

The implementation is maintained as [HTML source](../../website/smith-chart-body.html), [scoped CSS](../../website/assets/smith-chart.css), and [JavaScript mathematics and interactions](../../website/assets/smith-chart.js). The reader-site build includes the page in search and the sitemap. The page and source changes undergo the repository's CI checks before publication.

**What is established:** exact formulas and tested implementation behavior under stated assumptions.  
**What remains open:** novelty relative to all prior Smith-chart and polyphase literature, and measurable benefit in realistic RF measurement or model-fitting tasks.

The [Lean companion](https://github.com/KomorebiP/Operation-KOMOREBI/tree/main/formal/smith-chart-v0.1.0) formalizes the actual impedance packet series, canonical phase averages, finite-orbit Parseval identity, and finite passive-domain geometry. It also proves projector and sensitivity identities. Written derivations of the angular mean-square and sampling formulas are self-reviewed; their integral arguments and the browser implementation are not yet formalized. The finite-radius angular mean-square should not be read as a finite boundary \(H^2\) norm: it diverges as the radius approaches one.

## Direct load entry and packet selection

The workbench accepts physical impedance values and, under **Enter Γ directly**, an alternative pair of dimensionless load-reflection coordinates \(\Re\Gamma_L,\Im\Gamma_L\). The second input uses the same reference resistance \(Z_0\). Applying a new reflection point converts it through the inverse Cayley map and updates the physical load. A passive load must satisfy \(|\Gamma_L|\le 1\). Inputs outside the disk or too close to the open-circuit pole for stable double-precision conversion are rejected without changing the previous selected load. Unlike chart-pointer snapping near the endpoints, typed values inside the supported domain are not snapped to the ideal open or short.

The **Finite polynomial** view now exposes each packet-magnitude bar as a keyboard-accessible selection control. Choosing a bar changes packet index \(j\) and updates the algebraic diagnostics without changing the physical load. The bars illustrate projected values of a fixed polynomial, not angular sectors of the reflection disk.

The numerical interface checks are finite fixtures. They do not assert arbitrary-precision inversion or new RF performance results.

## Chart magnification and edit recovery

The chart provides **Zoom in**, **Zoom out**, **Center**, and **Fit** controls. Zoom magnifies the displayed SVG coordinate view, centering initially on the selected load. **Center** recenters on the currently selected load and **Fit** restores the entire reflection disk. Magnification does not change the physical impedance, reflection coefficient, lossless-line phase, cyclic projector state, or pinned reference. Chart selection continues to use the inverse SVG screen transform under zoom, so an enlarged view is not a different RF coordinate system.

At higher magnifications, the chart retains readable axis and grid labels and uses non-scaling stroke widths so the boundary is not artificially thickened. Exported SVG charts retain those view settings.

The zoom view is not included in portable session files: importing settings or resetting the workbench restores a predictable full-disk chart. **Escape** cancels an unfinished chart drag, as does loss of browser focus; a canceled edit does not create a history entry. Reset and session restoration also cancel any ongoing drag before applying their new state. The zoom controls remain hidden without JavaScript, leaving the readable mathematics and chart unchanged.

Browser regression checks were exercised at 320, 390, 768, 1024, and 1440 pixel widths. They cover view-only magnification, precision of coordinate selection after zoom, export of the visible viewport, and interrupted-drag recovery. These are interface checks, not new impedance theorems.
