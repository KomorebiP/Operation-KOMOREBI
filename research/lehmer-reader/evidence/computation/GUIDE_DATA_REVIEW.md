# Visual guide scientific data review

Reviewed on 9 October 2026 against the fresh computational contracts and preserved mathematical definitions. This review covers all thirty figure definitions in `visual/figures.py` and the accompanying spread text in `visual/main.tex`. It concerns scientific data, labels and scope. Page layout and font rendering receive a separate PDF inspection.

## Result

The current figure values and their corrected captions agree with the audited definitions and finite evidence. Two scope omissions were found and corrected by the guide owner before this review closed. No replay of the sixteen completed scientific suites was needed.

## Corrections made

1. The first-valuation-failure claim initially omitted its candidate domain. The stated first discrepancies at 81919, 8747 and 499 apply to primes p different from ell with ell dividing p+1. The corrected caption states both restrictions. Without excluding p=ell, the exceptional primes 2, 3 and 5 already contradict the proposed unrestricted equality. The displayed values 20/14, 8/7, 4/3 and 3/4 were correct throughout.
2. The synthetic countermodel initially displayed only q>B beside the zero parameter, while claiming preservation modulo10M at all indices. The caption and figure now explicitly choose a prime q>B with q=-1 modulo50M and tau(q)=0 modulo10M, for the fixed modulus M. Those congruences authenticate the retained residue contract. The guide also now says that no actual tau zero is established, rather than implying that the constructed zero is unconditionally distinct from the actual coefficient.

## Data and domain checks

| Figures or topic | Checked scientific contract | Outcome |
|---|---|---|
| Product and coefficient methods | Delta starts with q; tau(n) is product coefficient n−1. The three methods agree on every n from1 through512. | Correct coefficient shift and bounded claim. |
| Signed coefficient plot | Exact tau inputs through512; signed logarithm changes only the display coordinate. | Correct signs and label. No limiting-law claim. |
| Prime normalized plot | Only the97 primes through512 are selected, with largest prime509. Every exact integer satisfies tau(p)^2 ≤4p^11. The plotted ordinate is tau(p)/(2p^(11/2)). | Prime-only bound and display normalization are correct. |
| Multiplicativity and Hecke recurrence | tau(12)=tau(4)tau(3)=−370944 for the coprime factors4,3. T_r varies exponent r at a fixed prime. | Correct values and quantifier. |
| Prime reduction | A prime-power zero gives a root-of-unity ratio, followed by the rational possibilities0,1,2,3,4. Exceptional primes2,3 are handled by their known coefficients. | Correct scoped theorem illustration. |
| Parity | Odd indices in the displayed range are1,9,25,49,81, the odd squares. | Exact examples and universal classical identity are distinguished. |
| Hook and shell figures | Hooks of(4,1,1) are6,3,2,1,2,1. The shell at2 is the single vector(0,1,−3,3,−1), with norm squared20 and weight−24. | Correct hook, residue and normalization conventions. |
| Vandermonde | Denominator1!2!3!4!=288. Ten sign reversals leave the determinant sign unchanged. Distinct residues modulo5 make each weight nonzero and congruent to1. | Correct integrality and sign conventions. |
| Orbit bars at7 and31 | J(v)_i=−v_(−i mod5), retaining the original one-or-two packet multiplicity. The displayed order agrees with the lexicographic representatives at both plotted shells. | Three masses at7 total−16744. Sixteen masses at31 have eight signs of each kind and total−52843168. |
| Packet count | Prime formula p+chi_5(p), with chi_5 zero at5. The count-offset plot omits5 explicitly. | Formula illustration is labeled as a classical count. |
| Content121 | Content-one mass−25439104668 and content-eleven mass25937424601, summing to498319933. | Exact values and opposite-sign obstruction are correct. A prime shell has no second content class. |
| Primitive inversion and local factor | Square-divisor Mobius inversion, chi_5(g)g^10 scaling, and the numerator1−chi_5(p)p^10X^2. Subtraction starts at exponent2. | Correct formulas, fixed-prime domain and first coefficients. |
| Primitive square plot | For every s from1 through22, direct primitive shell enumeration at s^2 agrees with independent square-divisor inversion using the authenticated tau table. All22 values are nonzero. | Correct bounded illustration through484. The all-square conclusion remains the separately reviewed written project theorem. |
| Null transfer and interpolation | The vector(+6,−4,+1) receives(−5,+5,0) and becomes(+1,+1,+1). Arbitrary finite-orbit interpolation does not imply universal nullness. | Constructed arithmetic example is identified as schematic. The degree10(N−1) bound is presented as a project argument. |
| Dyadic refinement | Sectors use c_i=(v_i−i)/5 modulo2^k, with the involution. The illustrated child counts are schematic. | No actual binary-child-count claim is made. |
| Mixed boundary | The first eight formula values are13,47,186,737,2935,11722,46849,187319. Depth k starts at1. Sign-purity is about packet signs inside a sector. | Correct formula values and distinction from orbit uniqueness. The all-depth theorem does not rely on the plotted sample. |
| Sector7 | Ordered residue keys00000,10010,11000 have masses−1848,−17248,2352. Their Q8 correction sums are individually nonzero and sum to zero. | Correct parity keys and failure of sector localization. |
| Rank31 | At the orbit/fine-sector level the constructed-family ranks at degree cutoffs14,20,22 are5,14,15. Coarse rank stays5. | Correct rank data. The caption separates transfer surjectivity, the common-sign problem and a uniformly nonzero survivor. |
| Auxiliary roots | At499, reduced polynomial2+3U^2 has a simple root at1 that lifts to16 modulo25. At16249, the reduction(U−1)^2(U−2) equals3+U^2+U^3 modulo5. The target uses U=1. | Correct variable and root-branch interpretation. |
| Valuations | Actual candidate counts in the fresh150000 search are13847,6941,3451 for ell2,3,5. Their discrepancy counts are1,5,50. The plotted1249 example has the opposite5-adic inequality3<4. | The corrected first-failure caption uses the actual candidate domain. No larger-range or universal equality is inferred. |
| Trace-zero module | Companion matrix has trace0, determinant p^11, square−p^11I, Hodge jumps0,11 and Newton slopes11/2 twice. | Constructed local model is explicitly separated from the global Delta representation. |
| Actual survivors | For fixed M, p=-1 modulo5M and tau(p)=0 moduloM give chi_5(p)=1 and primitive series reduction(1−X^2)/(1−X^2)=1. | Theorem consequence uses actual finite joint images. No sampled density or independence claim is made. |
| Synthetic countermodel | Fix B and M. Choose q>B with q=-1 modulo50M and tau(q)=0 modulo10M. Changing the first q parameter to0 preserves that one fixed residue contract at every index. | Corrected explicit premises. No assumption that tau(q) was originally nonzero is needed. |
| Quantifier diagram | A prime chosen after each modulus need not be one fixed prime for every modulus. | Correct logical distinction. No assertion of an actual zero or solved nonvanishing theorem. |

## Exact evidence boundary

The figure generator imports the historical exact packet enumeration and the current independently checked tau table. Its logarithms, normalized heights and scaled bars are display coordinates. The source shows which figures are constructed examples and theorem illustrations. The guide captions preserve the universal theorem dependencies and the finite bounds.

The initial checked source snapshot and computational inputs are pinned below. A later mathematical edit requires a targeted re-review. Changes to spacing or typography require page QA but need not repeat the scientific suites.

```text
0608a810d8b1a341a00e5955d31000e589d2f5118a7bd1856915bcc6ec493aec  visual/figures.py
caf477d479c629fc6d8aa30ed09c8e6bbc3569f38df086772043fdf495050fbd  visual/main.tex
56a232749c6e3447646c2c604a8d5c379bc661ecd78a635a4290c63a2f2c051e  shared/figures/figure_map.json
2e7a0c777f289da7c44b81f99bb023b28546d4839477db7604b85c784778fcdc  evidence/computation/tau_plot_data_512.json
c8d393a51c7ddb41476a3decad58fd2ecb6b344d24aec7a6e38fa29c0c227a37  evidence/computation/replays/transport/results.json
0c7f83a1d5b4a0ad17fa8111413bf2fbf197aee5c0a3fd079fca1a155032ed81  evidence/computation/replays/valuations/results.json
```

## Final frozen-guide reconciliation

The final 32-page guide was reread at the source and figure-definition level. Its PDF hash is `d6e185b0e83e3390cc8627e44ec9a330781dfd9b285b873f04db19bee1ffb165`. The late scientific clarification defines the bar in overline G as reduction modulo5. That definition agrees with both normalized auxiliary polynomial examples. Expanded source citations point into the companion literature contracts, whose independent source authentication remains a separate audit. Other late figure edits move text, adjust ticks and spacing, or format the already present synthetic premise as mathematical text. They do not change a plotted value, a formula, a bound, the valuation candidate domain or the countermodel choice conditions.

The coefficient data, transport profile and valuation results have the same hashes as at the initial review. No scientific replay was repeated. The current source pins and hashes of all 30 PDF/PNG figure pairs are in `GUIDE_DATA_REVIEW.json`, which retains the initial review record and explicitly records this targeted final reconciliation. PDF page layout remains separately reviewed by the guide QA records.

```text
2723afe996b0d7ebfe717ee0881b6d57bdd6082e87420d63261c273d9e8854f3  visual/figures.py
c674665459357eccdbbbd364c3680a0b4add4c396e2ae5a962ece9e9c582ce2d  visual/main.tex
56a232749c6e3447646c2c604a8d5c379bc661ecd78a635a4290c63a2f2c051e  shared/figures/figure_map.json
2e7a0c777f289da7c44b81f99bb023b28546d4839477db7604b85c784778fcdc  evidence/computation/tau_plot_data_512.json
c8d393a51c7ddb41476a3decad58fd2ecb6b344d24aec7a6e38fa29c0c227a37  evidence/computation/replays/transport/results.json
0c7f83a1d5b4a0ad17fa8111413bf2fbf197aee5c0a3fd079fca1a155032ed81  evidence/computation/replays/valuations/results.json
db8ce879d1fb27b57d53c9b440adaed7f7bd0c0a695d85cbd5757a9371ae599f  historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/checks/packet_core.py
0aceb0f44eafc49664e7c8e7bcf214e7413c46c44197a6bf439f7a41a54b2732  evidence/computation/replays/five_core/results.json
19e7951983f49954e6d3f8582955c6e1395a2238d864c631968b266b0c23c8a3  evidence/computation/replays/content121/results.json
4d82c1f55060d03afdd1ffd779774a02c9c430489a7398af359a1998d01e370a  evidence/computation/replays/interpolation/results.json
a11142637353f1eb029f8449f1346bbaf1a3eb238dc43e29703282e5dfbc0da8  evidence/computation/replays/packet_tree/results.json
5b140c0318742830f89bb3d7a6a577fbb862d9a031c07d5922310b4acf22ce11  evidence/computation/replays/transport_independent/results.json
ef89a4061fa43f6b4284994b458155fa9d12d02ebd788e5d6a9fdb3450ba0071  shared/guide_preamble.tex
```

The separate source-application review in `evidence/literature/GUIDE_SOURCE_QA.json` pins the same final TeX and PDF hashes and records `PASS_FINAL_SOURCE_APPLICATIONS`. The imported historical packet core also matches its before/after input hash in the independent coefficient manifest.
