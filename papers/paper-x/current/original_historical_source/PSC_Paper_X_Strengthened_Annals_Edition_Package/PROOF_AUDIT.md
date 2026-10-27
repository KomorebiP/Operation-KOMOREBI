# Proof audit

## Summary

The final manuscript contains 74 theorem, proposition, lemma, and corollary records. It contains 74 complete proof environments.

## Structural checks

1. Every proved record has a proof environment.
2. Every internal reference resolves.
3. Every citation resolves to the BibTeX database.
4. Every bibliography entry is cited.
5. Every label is unique.
6. No finite certificate is used in place of a uniform proof.
7. Every standard external fact is identified and cited.

## Standard external inputs

The article imports five groups of standard facts.

1. Representability of deformation functors
2. Tangent and obstruction spaces in Galois deformation theory
3. Chebotarev density, Brauer Nesbitt, and character independence
4. Support from the annihilator of a finite module
5. Completion and flatness for finite modules over Noetherian rings

## High risk proof checks

### Inverse limits

The stable core maps were checked for surjectivity. The recursive branch construction uses only this surjectivity. The finite branching theorem was checked separately through König's lemma.

### Singular level counts

Power nilpotent, diagonal nilpotent, and normal crossing counts were recomputed directly. The normal crossing count was corrected during the audit.

### Packet obstruction theory

The packet decomposition is a direct sum of subcomplexes. The cokernel criterion and finite child counts were checked packet by packet.

### Source component rank

The lower bound comes from source components with no incoming condensation edge. The upper bound follows because every vertex in a finite acyclic condensation graph is reachable from a source.

### Companion completion

The local conclusion is an inverse limit branch. The final theorem now requires a bijection from the branch space to the declared complete local realization space. Empty finite levels remain exact obstructions.

### Frobenius separator

The proof uses linear independence of the constituent characters, density of unramified Frobenius classes, and a finite evaluation lemma. The compatible carrier result is conditional on a known decomposition.

### Fitting support

The zeroth Fitting ideal proof was checked after localization. The higher Fitting convention was checked against presentation matrix rank over residue fields.

### Flat base change

The reverse support inclusion uses the fact that a flat local map is faithfully flat. Adic support then follows from flatness of Noetherian completion.

### Finite trace occupancy

The field was restricted to characteristic zero. Trace is now written as the packet dimension multiplied by the unit of the field. Rank remains the integer packet dimension.

### Infinite occupancy

The tail projection counterexample prevents an invalid infinite dimensional inference. Each positive theorem now exposes its finiteness, compactness, or Mittag Leffler hypothesis.

## Corrections made during the final audit

1. Corrected the normal crossing finite counts.
2. Rebuilt inverse limit completion around stable cores.
3. Restricted the joint spectral theorem to commuting split semisimple operators.
4. Added capacity and local stability hypotheses to the compatible carrier theorem.
5. Corrected the finite rank occupancy statement to one fixed finite dimensional carrier.
6. Replaced generic finite spectral occupancy by module support and Fitting ideals.
7. Split finite and infinite occupancy.
8. Restricted trace detection to characteristic zero.
9. Rewrote trace equalities so scalar trace is not identified with integer rank.
10. Made the vertical completion hypothesis an explicit inverse limit bijection.
11. Separated compatible carrier multiplicity from module support occupancy.
12. Removed claims that the formal theory supplies missing companions or global nonvanishing.

## Final result

The manuscript has no internally identified proof gap after these corrections. This audit is not a substitute for independent peer review, specialist arithmetic review, or a historical novelty comparison.
