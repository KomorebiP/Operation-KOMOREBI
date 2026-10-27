# Block 27 manuscript review

Mode: review only, using the `mathbox:proofread-math` skill. No manuscript,
patch, or status file was edited by this reviewer.

Scope: the Block 27 changes in
`source/Projector_Resolved_Seed_Calculus_X_Block27_Amended.tex`, the complete
`source/Block27_Amendments.patch`, and the current `README.md`,
`BLOCK27_SCOPE_RESOLUTION.md`, `FIVE_PARTIALS_STATUS.md`,
`Paper_X_TwentySeventh_Block_Ledger.md`, and `NEXT_TARGET.md`.

Independence disclosure: the root agent wrote the documents. This reviewer
implemented the new `RestrictionEmbeddingConjugacy` production module and
independently recompiled the pre-existing `NumberFieldFrobeniusRestriction`
module without changing it. This is an editorial and local consistency review,
not an independent proof audit of that contributed module or the whole release.

## Resolved wording finding

In `Paper_X_TwentySeventh_Block_Ledger.md`, the sentence beginning
“Character independence does not require a supplied finite-dimensionality
hypothesis” is ambiguous in a mathematically significant way. The checked
results establish equality of characters on different Frobenius witnesses,
including Mathlib's generally defined trace. They do not establish linear
independence of characters for arbitrary-dimensional representations.
The issue was reported to the root agent, who changed the wording to
“Trace independence from Frobenius witness choices”. This reviewer re-read
the complete corrected ledger and confirmed that it now describes the proved
equality without asserting arbitrary-dimensional linear independence. The
corrected ledger SHA256 is
`cb1d01a24167833e1e6472a758be7b0ca4d595f87f028efa90e1590f0e3bdbe7`.
No unresolved objective issue remains in the reviewed scope. This reviewer
did not edit the ledger.

## Checks of the remaining text

- The displayed witness relation has the same orientation as
  `witnesses_conjugate_mod_inertia`:
  `Q_v = a • Q_u` and `gamma_v⁻¹ * (a * gamma_u * a⁻¹)` lies in inertia at `Q_v`.
- The discriminant exception is finite and is stated for the same finite normal
  number field as the restricted representation. The claimed triviality is
  that of finite inertia, and absolute inertia is killed after factorization.
- Frobenius is consistently arithmetic, with the p-power action on residues.
- The chosen/canonical embedding comparison states conjugacy by one fixed
  field automorphism, as in `restriction_conjugate`.
- The coverage assertion quantifies over every finite Galois subfield,
  finite prime exclusion, and field automorphism. The displayed occurrence is
  explicitly unproved. The interface and choice-independence results do not
  promote that existence assertion to a proved theorem.
- The original Claim 9.1 theorem and proof were independently extracted from
  the Block 26 and Block 27 manuscript files and found byte-for-byte equal.
  Their SHA256 is
  `6db3e6ea5ba2c0096666260e69eb8bad982b49cd83918f6c314212e3a8c0dc33`.
- The documents consistently retain 17 checked claims and 3 partial claims.
  Claims 8.2 and 11.2 retain their explicit conditional scopes.
- The remaining ideal-versus-valuation model comparison is disclosed.
- No new objective LaTeX, notation, grammar, or cross-reference issue was
  identified in the changed manuscript text. No mathematical-token changes
  were made.

## Validation and scope limits

`proofreading_structure.json` and `proofreading_patch.json` both record passing
checks. This review independently confirmed that their source hashes match the
current manuscript bytes. The latter records a fresh patch application with
the exact resulting source and preservation of Claim 9.1. These are source
checks only: no TeX compiler or PDF typesetting was run or claimed.

The current `PENDING_VERIFICATION` placeholders are intentional. A full build,
cumulative axiom audit, and archive replay are not certified by this document;
final numerical claims must be filled from their completed measured evidence.

## Reviewed hashes before the wording correction

| File | SHA256 |
|---|---|
| Block 27 amended LaTeX | `43b1e7bc22d1f9739303dd222d0449b9b88c6c9a87b20700eca68805ccbfbaad` |
| Block 27 patch | `f637883cf5e301d8801b11a696f418f87dc9542151f79126e38d3fa90bb787a1` |
| README | `0c710f0e55ddc378432ba3a879bcecb715b8eaeb3dc7efc186a245efa77fae7d` |
| Scope resolution | `c582ca3e9c68b5feb037ff4a3cfc9291f3ad59d2d15ee932b4948b5f9155f902` |
| Partial-claims status | `5f8499c4aa4cf38e839aa51158cb4a1ef84e8c613992b1946f787e617aa600cf` |
| Block 27 ledger | `b96e68ec6575e9c891d05ee064144b6f8f8800ffe6739b6332e3d1754d7297f3` |
| Next target | `206199ed06782b514daa068287146f9e9e1167ff887817d56ac79444e3c29044` |

## Earlier manuscript status update

After this first review, the root added Block 27 progress to the opening status
box and the final cumulative boundary paragraph. This reviewer re-read both
additions in the regenerated patch. They accurately state finite-number-field
restriction and Frobenius-choice progress while explicitly retaining the
unproved general prescribed-conjugacy prime-coverage assertion. The detailed
Block 27 mathematical passage is unchanged.

The refreshed source and patch checks passed; their recorded hashes match the
actual files. Claim 9.1's original theorem and proof were independently
extracted and compared again, with the same unchanged hash reported above.
No objective unresolved issue remains in this final reviewed mathematical and
editorial scope.

Reviewed amended source SHA256 at this intermediate revision:
`880a87164f07f5a6c532736c98d7b50cd7e6e2714f013e3d1190a43f29bddc40`.

Reviewed source patch SHA256 at this intermediate revision:
`ee4116189f1bb316c8d1b0272c139e166aef314713d643136fd8b1b4fe962d85`.

Reviewed ledger SHA256 at this intermediate revision:
`cb1d01a24167833e1e6472a758be7b0ca4d595f87f028efa90e1590f0e3bdbe7`.

Later replacement of `PENDING_VERIFICATION` with measured compiler/audit/replay
results is outside this review's numerical certification. It does not alter
the approved mathematical body if confined to those verification placeholders.

## Final rational-base scope clarification

An independent proof auditor identified a further source-scope distinction:
the manuscript uses `G_{F,S}` and does not restrict Claim 9.1 to the rational
base, whereas the new arithmetic witness and coverage modules use the absolute
Galois group of the rationals. The earlier local editorial review did not flag
this wider source-to-formalization limitation.

The root has now stated this limitation explicitly in the new mathematical
passage, README, scope resolution, partial-claims table, Block 27 ledger, and
next-target note. This reviewer re-read those additions and the source's
`G_{F,S}` occurrence. The clarification is accurate: general-base applications
still require the analogous actual-prime and norm-power Frobenius attachment
and coverage over the arithmetic base field, or a proved transfer. Neither the
rational-base interface nor the generic group separator proves that transfer.

This is a clarification of unfinished arithmetic scope, not a new Lean result.
The 17 checked / 3 partial accounting is retained. The original Claim 9.1
theorem and proof were independently extracted and compared once more; their
bytes and SHA256 are still unchanged. Refreshed structure and patch records
pass and match the final source bytes. No further objective issue was found
in this bounded rereview. No document edits were made by this reviewer.

| Final reviewed file | SHA256 |
|---|---|
| Block 27 amended LaTeX | `e4bf41c74d11e30cb392bf451ab8dff426bc77ae829266d3672ae01b77abdc0f` |
| Block 27 patch | `fc47ea31cfbd5d907dc60c6df6a20672335eb7e5cb7ef8c96b8f4572e435fee0` |
| README | `914782f2d7083e7500d16185b84ea93f80dd1e2285d5fedc600f97e06c647937` |
| Scope resolution | `4d3e5c42a11bd1320cca4698b8ec69137a46e9705c9985d42880b8bd1e92bbc1` |
| Partial-claims status | `902c952719426f64d654c505ac282db366567da1557baabe1caad0c751bb89b5` |
| Block 27 ledger | `1ae0c16b351b5527b9971de3f7f8c59bee63e5235e53dea782073ad2a56ee0f9` |
| Next target | `5c713da4d68e148dbe65208fdb82f4ab535b31bd8b5b2364a46a5e21562a3fad` |

These status-file hashes precede replacement of the intentional verification
placeholders. The numerical-certification and no-PDF limitations above remain.
