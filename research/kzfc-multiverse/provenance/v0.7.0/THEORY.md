# Explicit ZFC and the internally interpreted residual sentence

## 1. Scope and predecessor

The authoritative predecessor is v0.6.0. All its 20 mathematical modules and 210 named theorem declarations are preserved unchanged. Six modules add 80 declarations, including supporting semantic lemmas, for 290 in total.

The predecessor classified the small-domain, small-scope residual compactness principle by complete-filter extension, then encoded the guarded existence assertion as a closed membership-language sentence Theta. It interpreted that sentence in ZFSet and adjoined it to an unspecified base theory. The present block supplies the actual ZFC axiom theory, proves its concrete modelhood, and gives a fully internal reading of the sentence in arbitrary membership structures.

No uncountable existence principle is assumed or proved.

## 2. Exact first-order base theory

The language is unchanged: no function symbols, one binary membership relation, and logical equality. The ZFC theory is the range of an explicit AxiomCode-to-sentence function. AxiomCode has eight fixed constructors: extensionality, empty set, pairing, union, powerset, infinity, foundation and choice. It also has Separation and Replacement constructors, each indexed by a natural number n and an actual formula with n free parameter variables and one or two distinguished variables.

The fixed sentences have their usual exact forms. Pairing and union assert exactly the intended members. Powerset includes precisely the internal subsets. Infinity supplies an internally inductive set. Foundation supplies a member disjoint from the nonempty set. Choice supplies a set-coded Kuratowski-pair graph with exactly the required domain, an element selected from each nonempty member, and unique output.

For every formula phi(x,p), Separation is the universal closure over the finite tuple p of

    forall A, exists B, forall x,
      x in B iff x in A and phi(x,p).

For every formula psi(x,y,p), Replacement is the universal closure of

    forall A,
      [forall x in A, exists unique y, psi(x,y,p)] implies
      exists B, forall y,
        y in B iff exists x in A, psi(x,y,p).

There is no restriction on formula complexity and no numerical bound on n. A formula may refer to the source set through a parameter assigned that source set, so parameters do not exclude the usual source-dependent schema instances. The newly bound image set is not free in the relation formula. The closure implementation deterministically relabels the indexed parameters into bound variables and uses the existing all-binders constructor. It does not use an externally interpreted predicate or a choice of variable enumeration.

This is a first-order schema. In an arbitrary structure, it does not demand Separation or Replacement for every external predicate on the structure.

## 3. Arbitrary-structure axiom semantics

GeneralMembershipSemantics provides generic interpretation of the capture-free Option-variable binders and primitive membership formulas. AxiomSemantics spells out the meaning of each fixed axiom and of every syntax-indexed schema instance using the structure's relation.

Lean proves, for every membership structure M,

    M models zfcTheory iff AxiomSemantics(M).

The right side contains precisely the stated axioms. It contains no compactness result, cofinality theorem, ordinal representation theorem, external well-foundedness hypothesis, or internal/external absoluteness assumption.

All witnesses are elements of M. This remains meaningful even when M is not externally transitive or its internal sets disagree with external collections.

## 4. Concrete ZFSet model

The proof that ZFSet satisfies the explicit theory is uniform over every schema formula and every finite parameter assignment.

Separation uses the actual ZFSet separator. Replacement restricts attention to the small carrier of the source set, chooses its uniquely specified outputs, and forms their ZFSet range. The uniqueness condition proves that the constructed range is exactly the required image.

Choice is verified with an actual range of Kuratowski pairs. The proof checks graph entries, membership of each selected output in its source set, and uniqueness. It does not insert an external function in place of the required internal graph witness.

The fixed axioms use the concrete empty set, pair, union, powerset, omega and foundation operations. This proves

    ZFSet models zfcTheory.

This is a theorem in Lean's surrounding type theory. It is not an internal ZFC derivation of Con(ZFC).

## 5. The residual sentence's internal reading

InternalResidualSentence separately defines products, function graphs, graph injectivity, embeddings, smallness, filters, relative intersections, completeness and the guard using only the model's membership relation and internally existing witnesses.

For example, internal Small(K,S) means that some a in K has an internally existing injective graph from S to a. It does not mean that the externally computed cardinality of S is below an external cardinal attached to K.

Likewise, completeness quantifies only over internally existing subset families with internally witnessed smallness. All intersection witnesses are relative to the carrier, so the earlier empty-family convention is retained.

The guard is the same syntactic transitivity/initiality, inductive-member and small-subset-boundedness guard as before. In arbitrary structures this is its literal internal predicate. The present block does not newly prove a comparison with an external Cardinal interface in such structures.

Lean proves for every membership structure M,

    M models Theta iff GuardedExtension(M).

No axioms on M are needed for this syntax-interpretation identity. It is not an assertion that M satisfies either side.

## 6. Actual KZFC theory

Define

    kzfcTheory := zfcTheory union {Theta}.

The arbitrary-structure theorem is

    M models kzfcTheory iff
      AxiomSemantics(M) and GuardedExtension(M).

The concrete model theorem now discharges the base-model premise left open in v0.6.0:

    ZFSet models kzfcTheory iff ResidualExistence,
    ZFSet models kzfcTheory iff FilterExtensionExistence.

These are exact equivalences, not proofs of their right-hand sides. A modelhood implication is provided under an explicit residual-existence hypothesis, without adding such a hypothesis to the environment.

## 7. Internal regression theorems

Pairing and Foundation alone imply that no element is a member of itself and that membership has no two-cycle. The proofs form an internal pair and apply the internal foundation statement. They do not use an external rank or external well-foundedness.

A single zero-parameter Separation instance, using the formula not(x in x), proves that no universal set exists. Foundation is not needed for this argument. This verifies that schema instantiation is operational rather than merely an uninterpreted label.

These familiar consequences are regression checks of the formal encoding, not new set-theoretic discoveries.

## 8. Remaining proof boundary

The explicit first-order base theory and arbitrary-structure interpretation are complete for the definitions supplied here. The full compactness/filter classification remains the predecessor's mathematical theorem in Lean types and concrete ZFSet.

Still missing is a coded internal constraint/residual principle and a complete comparison with internal filter extension in arbitrary ZFC models, or an extracted derivation in a specified object-language proof calculus. The new axiom-semantics and sentence-interpretation identities do not supply that deeper classification automatically.

No uncountable witness, independence, relative consistency, new consistency strength, or priority claim is made. The known strong-compactness interpretation of the previously classified all-sets principle is retained with its existing source boundary.
