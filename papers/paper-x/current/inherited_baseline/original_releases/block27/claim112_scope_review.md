# Independent source-scope review: Claim 11.2

Reviewed 2026-09-08. This is a read-only mathematical/source-interface audit, not a compiler replay and not approval of any new Block 24 source. No production files were edited. Execution and source access succeeded.

## Exact target and conclusion

The corollary “Exact location of the remaining existence problem” in the Block 23 amended manuscript retains three requirements: residual companion nonemptiness at every coefficient place, nonemptiness at every higher finite depth, and positive projector trace for every required global packet. It explicitly retains finite branching and inverse-limit closure. It does not assert universal nonemptiness or universal occupancy.

**A faithful full conditional formulation is available.** For a fixed common spine and its admissible reduction forests, and a fixed family of the Section 10 carrier/operator data indexed by exactly the required packets, the following are equivalent:

1. There is a family of actual continuous representations that realizes every finite admissible level and every item of the common spine, and every required carrier has a nonzero joint eigenvector for its specified packet.
2. Every residual level is nonempty, every level of depth at least two is nonempty, and every required packet's projector has positive natural-number trace.

This equivalence requires the common-spine completion hypotheses, excluding finite-level nonemptiness because nonemptiness is on the right side of the equivalence. It also requires the actual finite-dimensional, characteristic-zero, split and commuting carrier hypotheses from Section 10. These are the literal conditional settings already described in the source. The proposed equivalence is a stronger precise formulation of the source corollary's boundary statement, with no need to prove Claim 9.1, 9.2, or the final recovery clause of Claim 11.1.

The word “and” above is essential. It does not say that a system obtained by completion embeds into each carrier, that every packet is realized by the same vector, or that the occupied carriers arise canonically from the completed representations. Those are additional claims and do not follow from this product criterion.

## Exact packet data

Section 10 fixes a characteristic-zero field E, a finite-dimensional E-vector space A, a finite family of commuting endomorphisms T_i, diagonalizable over E, and target scalars a_i in E. Targets may be absent from the spectrum. Its projector is actually constructed from the finite eigenvalue sets by the Lagrange polynomials, using zero for an absent target, then multiplied over the conditions. It is not a supplied endomorphism merely asserted to be the desired projector.

`SpectralProjectors.spectral` follows this construction. `SpectralProjectors.Split T` says that the actual eigenspaces span the space; this captures diagonalizability over the given coefficient field. `JointOccupancy.joint` is the actual product of those polynomial projectors. `jointSpace` is the intersection of the specified eigenspaces. The proofs show actual projection onto that intersection, image equality and trace equal to its dimension.

For a family of required packets, each packet can have its own field, vector space, operator-index type and finite list of conditions. That extra generality causes no gap: the source's one common field is the constant family. The set/type of required packets need not be finite. Only the list of conditions within each packet must be finite. There must be a universal quantifier over the entire supplied required-packet index; one occupied packet or a finite selection of packets is insufficient.

The source does not supply an algorithm that determines which arithmetic packets are required, nor does its corollary construct a carrier. Applying the universal conditional theorem to a particular arithmetic problem must identify its actual required index and carrier/operator data. Such application obligations do not prevent proving the universal conditional implication, provided the theorem and release never claim those inputs have been constructed.

## Meaning of positive trace

The source explicitly defines positivity by the unique nonnegative integer represented by the field-valued trace. It does not order E. For each packet, Lean already proves

- trace(joint projector) = the natural dimension of its actual joint eigenspace, cast to the field;
- uniqueness of this natural-number preimage in characteristic zero;
- existence of a nonzero joint eigenvector iff that dimension is positive;
- equivalently, existence of that vector iff the field-valued trace is nonzero.

Thus using field trace != 0 in the formal criterion is mathematically equivalent to the manuscript's trace > 0 under the stated projector and characteristic-zero hypotheses. A new interface can make the positive natural-number trace explicit using the proved dimension or an existential positive natural whose cast equals the actual trace. It must not introduce an ordered-field instance or replace the projector trace with an unrelated user-supplied integer.

Zero-dimensional carriers, empty lists of conditions, absent targets and an empty required-packet index are handled correctly by these definitions. The empty condition list gives the identity, so occupancy then means the carrier itself is nonzero. An empty required-packet index makes only the packet conjunction vacuous. It does not remove finite-level nonemptiness.

## Comparison of the existing Lean interfaces

`IndexedExistenceBoundary.all_required_packets_iff` already proves the universal packet quantifier and the residual/higher-depth separation. Its left side supplies actual integral representations, their continuous adic action, all finite allowed reductions, a supplied local condition, and occupancy in every fixed carrier. Its proof obtains finite-level nonemptiness in the forward direction by actual reduction; its reverse direction uses finite-branch completion and the actual projector trace criterion independently.

That theorem does not itself expose the completed common Frobenius polynomials, determinant family, weight relation, packet relation, and field-valued continuity. Therefore simply relabeling it would leave an interface mismatch with the now completed source common spine.

`ConditionalArithmeticSpine.adelic_finite_depth_completion` supplies precisely that strengthened completion output, using admissible conjugacy-class levels and coherent matrix choices. It exposes polynomial and determinant specifications and the selected local weight/packet relations. The local relations keep their supplied meanings; they are not definitions or constructions of Hodge–Tate or Weil–Deligne attachment. Their inverse-limit closure is an explicit source assumption.

Combining this theorem with the actual `JointOccupancy` statements yields the proposed source-faithful criterion. In the reverse direction, split residual/higher nonemptiness into every positive depth, invoke common-spine completion, and retain/construct the independent packet eigenvectors from positive trace. In the forward direction, reduce the integral representations to obtain each required allowed class and use each actual eigenvector to infer positive trace. No positive occupancy premise should be buried in the common-spine structure.

## Hypotheses that must remain visible

- Fixed chosen common spine and specified finite reductions, including local integral polynomial and determinant representatives where that interface needs them.
- Complete coefficient rings with the arithmetic finite-quotient/finite-rank setting needed to lift class levels to finite matrix frames.
- Finite allowed positive levels and total admissible reduction maps; finite branching then follows.
- Continuous finite-level admissible representations and continuous coefficient inclusions.
- Explicit inverse-limit closure of the selected full local relations.
- A fixed index of all required packets, with their actual finite-dimensional carrier and finite split commuting endomorphisms.
- Characteristic zero for converting nonzero field trace into positive natural-number trace.

Do not add finite-level nonemptiness, positive occupancy, an embedding of the system into a carrier, Frobenius quotient coverage, or an arithmetic attachment theorem as hidden assumptions of a conclusion that purports to establish them.

## Scope recommendation

Once the assembled theorem is compiled and independently checked, changing Claim 11.2 to “checked at its universal conditional source scope” is justified by the literal corollary and Section 10 definitions, consistently with the Block 23 distinction for Claim 8.2. The release must separately retain the unproved arithmetic application obligations and universal occupancy conjecture. This is partly a scope-accounting correction, not a proof that the remaining arithmetic existence problem is solved.

I did not infer this verdict from the old status paragraph. That paragraph says 11.2 is partial at arithmetic interpretation; the assessment above follows the displayed corollary, Section 10 construction and actual Lean hypotheses/conclusions. I did not run a fresh Lean build or inspect a not-yet-written Block 24 theorem. The parent must validate that final theorem and its evidence before changing the ledger.

## Evidence hashes

Baseline archive SHA-256, recomputed successfully:
`93d1d13a4dbf8bf71a8d742613c78d7fceff30bb8beb3e0225d438645fd57c70`

Reviewed source files and SHA-256:

- `source/Projector_Resolved_Seed_Calculus_X_Block23_Amended.tex`: `ee51054b0563ce7f2983f44c959926fcf4136799bdaaa8c41723c4f3b4ac53ed`
- `lean/PaperX/JointOccupancy.lean`: `c088ab5e1eedd2b3395d5592f831ab82d8ec8d0521dbd38210e771ee80cf57d4`
- `lean/PaperX/IndexedExistenceBoundary.lean`: `3fd7a505893def0c1086da57ec2354b6dd007b7a614a16a282b96600eda8da1d`
- `lean/PaperX/ConditionalArithmeticSpine.lean`: `cb8054a1da634b7753be9ea07c4d29e8aebf849edfc369294f1615c364a87438`
- `lean/PaperX/CompletionAssembly.lean`: `1900d2142d60552da6d0e8816a83eac1b4240133ea2e311ffcfa6f0e650b293c`
- `lean/PaperX/SpectralProjectors.lean`: `ee68f113d9c9788a27a16959b41c3b5e48788cbf8e20b7ee4cc0e9d60e340333`
