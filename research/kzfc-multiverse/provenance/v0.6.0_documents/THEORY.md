# A closed membership-language residual existence sentence

## 1. Predecessor and goal

The v0.5.0 checkpoint constructed a membership-only parameter formula Phi(K). At the initial-ordinal ZFSet code of any cardinal kappa, its realization is equivalent to CompleteFilterExtension(kappa). For regular kappa, the preceding classification identifies this with FixedDomainKRR(kappa) for the declared small-domain, small-scope constraint class.

Those 17 mathematical modules are unchanged. The current goal is to turn the parameter formula into the intended closed sentence without accidentally admitting the already proved aleph0 instance.

## 2. Independent set predicates for the guard

All predicates in this section quantify over ordinary sets. None mentions filters, ultrafilters, compactness or residuals.

An initial cardinal code is defined by

    Initial(K) := Ordinal(K) and
      for every a in K, there is no injection K -> a.

Here an injection is the predecessor's explicit Kuratowski-pair graph, not an extra symbol. The ordinal predicate is the characterization as a transitive set of transitive sets. Its equivalence with the well-ordered von Neumann ordinal notion uses the concrete ZFSet foundation API.

Lean proves

    Initial(K) <-> exists kappa, K = initialOrdinal(kappa).

For the reverse direction, write K as the set code of an ordinal o. The initial ordinal of card(o) is no larger than o. If it were strictly smaller, it would be a member of K admitting an injection from K, contrary to Initial(K). Thus K is precisely the initial ordinal of its cardinal. This theorem treats all possible set witnesses, not merely ones selected in advance.

Define

    Inductive(W) := empty in W and
      for every a in W, a union {a} is in W;
    InductiveMember(K) := exists W in K, Inductive(W).

Every inductive set contains all finite von Neumann ordinals, by induction. If it is itself an ordinal, it is at least omega. Since every member of an ordinal is an ordinal, an inductive member of initialOrdinal(kappa) forces omega < initialOrdinal(kappa), hence aleph0 < kappa. Conversely, omega itself is an inductive member whenever aleph0 < kappa.

Therefore

    InductiveMember(initialOrdinal(kappa)) <-> aleph0 < kappa.

This avoids introducing omega as a constant symbol in the language. It does not assert that every ordinal above omega is inductive.

## 3. Regularity as strict boundedness

Use the predecessor's exact set-coded smallness:

    Small(K,S) := exists a in K, an injection S -> a.

At an initial-cardinal code, this is equivalent to card(S) < kappa.

Define

    SmallSubsetsBounded(K) := for every S subset K,
      Small(K,S) implies exists b in K, S subset b.

The bound is strict: every member of S lies below b, and b itself lies below K.

For every infinite cardinal kappa, Lean proves

    SmallSubsetsBounded(initialOrdinal(kappa)) <-> IsRegular(kappa).

Forward from regularity: enumerate the members of S using its small carrier, take the supremum of their ordinal ranks plus one, and use the cofinality bound to show that this supremum is still below kappa. It supplies the required b.

Reverse: take any cofinal subset of kappa's ordinal carrier. If it had cardinality below kappa, its ordinal image would be a small set S. The asserted strict bound b would contradict cofinality. Therefore every cofinal subset has cardinality at least kappa, giving kappa <= cof(kappa). Combined with infinitude, this is Mathlib's IsRegular predicate.

No regularity assumption is inserted into the definition of SmallSubsetsBounded. The equivalence is proved.

## 4. The complete guard

    Guard(K) := Initial(K) and InductiveMember(K)
                  and SmallSubsetsBounded(K).

The checked exact characterization is

    Guard(K) <-> exists kappa,
      K = initialOrdinal(kappa) and IsRegular(kappa) and aleph0 < kappa.

The guard is neither vacuous nor a hidden compactness assumption. It fails at aleph0. It holds at every infinite successor cardinal. The predecessor proves complete-filter extension false at those same successors, so passing the guard does not imply satisfying Phi.

## 5. Actual membership-only syntax

The new formula macros encode transitivity, ordinalhood, initiality, successor, inductiveness, an inductive member, and boundedness of small subsets. They reuse the predecessor's actual formula constructors, capture-free Option binders, set-coded injection and smallness macros.

Every macro has a proved realization theorem. The language still has no function symbols and exactly one binary nonlogical relation symbol, membership. Equality is logical equality. No cardinal, regularity, smallness, filter or truth predicate is added as an atomic symbol.

The closed sentence is

    Theta := exists K, Guard(K) and Phi(K).

Its type is `language.Sentence`, not a one-free-variable formula. The expression itself has no external cardinal parameter. The interpretation theorem remains universe-polymorphic in the metatheory.

## 6. Closed-sentence classification

The principal theorem is

    ZFSet |= Theta <-> FilterExtensionExistence.

The right side means

    exists kappa, IsRegular(kappa) and aleph0 < kappa
      and CompleteFilterExtension(kappa).

The proof starts with an arbitrary set witness for Theta, uses the exact guard classification to recover its cardinal kappa, then applies the unchanged interpretation of Phi. Conversely, a witness to the independently stated cardinal principle yields its initial-ordinal code and the required formula realization.

Composing with the predecessor gives

    ZFSet |= Theta <-> ResidualExistence.

These are equivalences of existence assertions, not proofs that an uncountable witness exists.

## 7. Regression theorems

The unguarded closed sentence exists K, Phi(K) is proved true via aleph0. The guard rejects this witness. A nonregular cardinal cannot pass the guard. Every infinite successor passes the guard but cannot satisfy Phi, so no such successor is a guarded witness. These are universally quantified Lean proofs with the stated hypotheses, not bounded numerical tests.

The predecessor's integer-tower obstruction, finite-prefix failure and caution about residual-degree packing are preserved. The current sentence classifies only the already specified semantic constraint principle, not arbitrary derived residual towers.

## 8. Adjoining the sentence to a base theory

For an explicitly supplied theory T in the same membership language define

    Extend(T) := T union {Theta}.

For every structure M in the membership language, Lean proves

    M |= Extend(T) <-> (M |= T and M |= Theta).

In the concrete ZFSet structure this combines with the classification to give

    ZFSet |= Extend(T) <-> (ZFSet |= T and ResidualExistence).

This is not an encoded ZFC theorem unless an explicit ZFC axiom theory is supplied and the relevant obligations are proved. T is an argument, not implicitly identified with ZFC or with the ambient structure's complete theory.

Truth of Theta is also transported across elementary equivalence by Mathlib's ordinary sentence semantics. This does not assert absoluteness under forcing, arbitrary submodels or changes of internal cardinality.

## 9. Remaining foundational boundary

The closed-sentence task is complete. The still missing task is an internal comparison over an explicit first-order ZFC axiom theory or an appropriate arbitrary-model interpretation. That work must keep internally existing sets, functions, cardinals and completeness separate from externally computed ones. Concrete ZFSet adequacy alone cannot discharge it.

In particular, this release does not assert Theta true, derive an uncountable large cardinal from ZFC, establish independence or give a relative-consistency theorem. It supplies a precise candidate sentence with a checked concrete interpretation.

The existing all-sets strong-compactness terminology is retained with the predecessor's source boundary. No new consistency strength, theorem priority or first-formalization claim is made.
