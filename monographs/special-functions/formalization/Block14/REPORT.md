# SF-LEAN-B14: autonomous projections and constant linear decoupling

For every positive real quadruple q,r,a,b and nonzero complex row c, the
actual functional field on all zero-constant analytic vector inputs admits
an arbitrary scalar functional of cX exactly when

\[
q=a,\qquad r=b,\qquad c=\gamma(1,-1),\quad\gamma\ne0.
\]

The projected field is then identically zero. Every constant complex 2x2
matrix with two autonomous rows has determinant zero, so no invertible
constant linear coordinate change decouples the operator. This includes
all scale coincidences and requires no contraction hypothesis.

Both an entire-input version and a local analytic-germ version are proved.
Entire inputs are genuinely complex differentiable at every point and have
zero initial values. Local inputs are analytic at zero; scalar projections
and fields are actual Filter.Germ values at the neighborhood filter of zero.
Autonomy is constancy on projection fibers. The explicit factorization
theorems equate this to existence of an arbitrary scalar functional H on
the whole scalar-function or scalar-germ space. No quadratic, continuous,
local or finite-jet ansatz is imposed on H.

`lean/CoupledOperator.lean` adds **27 theorem declarations**, including
supporting lemmas, for **369 registered names**. All **57 fresh replay steps**
pass across fourteen coupled modules: 330 theorem axiom audits, fourteen
kernel replays, four expected rejections and one positive fixture. The
finite core's 39-name evidence is inherited. Mathlib imports are cached,
not freshly rebuilt or replayed. Review provenance is self-review.

## Argument and exact source correspondence

Authority: H.1 and S1-S3 in
`monograph/sections_v11/coupled_structure_full.tex`, lines 9-115, at base
`297118ccc10550500619224d44f168f6491d02e5`. Manuscripts and reading PDFs
retain their bytes. The five claim-map groups cover all 27 new names once.

The scalar polynomial f(z)=1-(1-z/q)(1-z/r)(1-z/a)(1-z/b) vanishes at zero
and equals one at each scale node, including repeated nodes. For inputs
(xf,yf), the projected field at z=1 is (c1+c2)(1+xy). Compare the following
pairs on equal scalar-projection fibers:

- (0,0) and (c2*f,-c1*f);
- (f,0) and ((1+c2)*f,-c1*f);
- (0,f) and (c2*f,(1-c1)*f).

Subtracting the resulting identities gives (c1+c2)c1=(c1+c2)c2=0. If
c1+c2 were nonzero, both coordinates would vanish and their sum would be
zero, a contradiction. Thus c2=-c1; for a nonzero row, c1 is nonzero.
No derivative of a possibly arbitrary scalar functional is used.

Compare the entire inputs (z,z) and (0,0). Their projection is zero and
their field comparison gives qr=ab. Compare (z^2+z,z) and (z^2,0); their
scalar projections agree. The field identity and the first product identity
give q^2*r=a^2*b. Multiplying qr=ab by a and subtracting shows
(q-a)qr=0. Positivity permits cancellation, so q=a and then r=b. The
source's third monomial identity is redundant for this recovery and is not
registered as a missing obligation. Conversely ordered row equality and
c1+c2=0 cancel the entire field for arbitrary input functions, without any
analytic hypothesis. The zero row is handled separately in the generalized
classification, rather than divided out.

Every autonomous matrix row sums to zero. The two row-sum equations force
the actual 2x2 determinant to vanish. The pinned matrix theorem equates
matrix IsUnit with IsUnit of its determinant, giving the invertibility
contradiction. No assumption that the two rows are already nonzero is needed
for the determinant identity.

For local germs, constant dilation tends to zero at zero. Thus the field
respects component-germ representatives; the projection and field are
analytic at zero. A local autonomous germ operator restricts to entire
inputs. Equal entire scalar projections yield equal field germs, and
complex analytic identity extends this equality to the whole plane.
The entire classification then applies. Conversely the proved pointwise
zero field gives local germ autonomy directly. The same classification
and decoupling obstruction follow with genuinely local analytic inputs.

## Evidence, edge cases and continuation

The positive interface exercises both arbitrary-functional formulations,
the coincident half-scale exceptional row, arbitrary input functions,
noncontracting positive scales (2,3,2,3), the zero row, failure of a
single-coordinate row, component-germ representative invariance and
invertible matrix exclusion. A swapped unequal contraction example proves
canonical U=V but excludes every nonzero autonomous row. Rejection fixtures
attempt swapped-row autonomy, coordinate-row autonomy, removal of the
nonzero-row guard and a placeholder.

`declarations.json`, `CLAIM_MAP.json`, `SELF_REVIEW.md`, `IO_MANIFEST.json`
and the raw replay receipt bind names, claims, review and exact execution.
`SOURCE_MANIFEST.json` seals immutable phase records and inputs. Replay
`tools/verify_coupled_operator.py` with the pinned Lean/Mathlib environment
and a new external work directory. It installs nothing, makes no network
request and checks input stability at the end. Root archive manifests remain
older release snapshots.

The registered main H.1 contract is complete. Its odd-input-only remark and
tensor/rank explanatory derivations are not new registered certificates.
Next major target is Appendix J's arbitrary-radius disk-majorant ladder,
outer-radius Taylor error and exact evaluator refinement. Some ancillary F
correspondence, I's resolution mechanisms and broad A-E analytic chapters
remain. No exhaustive manuscript-wide claim map or completion percentage
is asserted. Ordinary type convergence remains conditional; the G.2
nonzero-defect guard is retained.
