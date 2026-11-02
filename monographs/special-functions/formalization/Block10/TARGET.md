# SF-LEAN-B10 target contract

Base: `2661894c45768d240e9c2fcc4524061e404a0411` (SF-LEAN-B09).
Authority: Theorem F.2, `Explicit upper comparison`, in
`monograph/sections_v11/coupled_growth_full.tex`.

For the actual canonical functions and 0<q,r,a,b<1, certify the full-radius
upper product recurrences, F_i(1)<=2, and the geometric seed ladder
R_k=(1/Q)^k, Z_0=2, Z_(k+1)=R_(k+1)*(1+Z_k^2).
Prove its closed logarithmic bound
W_N=(2^(N+1)-1)log(2)+(2^(N+1)-N-2)log(1/Q).
Then prove the shifted logarithmic recurrence and the explicit upper bound
log(F_i(R))<=c_plus*w_i*R^rho-log(R)-D for R>=exp(1), with the manuscript's
Delta, D, S and c_plus, for any N with R_N>=3/m. Prove such N exists.
Keep the lower comparison intact. Real type objects, radial exponent limits,
F.3 proportions and broader manuscript coverage are separate later targets.

Primary route: real mean-value comparison on [0,R], positive geometric
majorants, then closed-cap induction with positive logarithmic delays.
First discriminator: prove the actual product upper recurrence at all R>=0,
including zero, and the geometric seed from the proved HasSum expansion.
Success requires the parameter-only explicit constant, real powers, exact
canonical functions and both rows, with source-bound Lean kernel evidence.

Alternative FTC route: integrate the derivative equations directly; first
uncertain step is the integral/real-embedding API. Defer if mean-value works;
resume when later integral identities are needed. Alternative supersolution
route: construct a direct weighted exponential majorant; first uncertainty
is a parameter-only seed constant valid for rho<1. Resume if the logarithmic
delay propagation stalls. Exact endpoint/threshold controls attempt to
falsify omitted premises; finite checks do not establish the universal bound.

Update proof files, claim maps, actual I/O inventories and current catalogue.
Preserve earlier block evidence, dated guides, manuscripts and reading PDFs.
Review provenance is self-review; no delegation is authorized or required.
