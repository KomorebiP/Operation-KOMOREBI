# A bounded repair contract for the IUT numerical comparison

Status: **reduction and elementary diagnostic, not an IUT repair**.

Base: RR4, archive digest recorded in INPUTS.json. This route reads prior
multichannel work only as a reminder to account for numerical scales. It makes
no claim that a filter-bank identity models the full IUT construction.

## The exact arrow to reconstruct

Write Q for the real number denoted −|log(q)|, T for −|log(Θ)|, and
S = {x in R : x <= T}. All are measured in the one fixed numerical convention
used by the proposed application. The target implication is Q in S, equivalently
Q <= T. This is the conclusion of IUT III, Step (xi-f).

A useful audit must first specify the actual collection of output objects O,
the input object I, a construction or relation taking I to O, and the numerical
maps on both. An abstract relation between O and I is not, by definition, an
inequality between their numerical values.

One sufficient witness contract is:

1. Construct an output object o in O whose numerical log-volume V(o) is
   defined in the same normalization as Q and T.
2. Prove Q <= V(o) using the actual comparison maps and their action on
   normalized determinant degrees.
3. Prove V(o) <= T from the specified hull/container.

Then Q <= T follows by transitivity. An approximate version is sufficient if
for every eta>0 an output o_eta has Q-eta <= V(o_eta) <= T: if Q>T, take
eta=(Q-T)/2 to get a contradiction. Exact realization V(o)=Q is stronger than
necessary. This does not assert that such witnesses exist in IUT.

The next mathematical task is to derive this witness or an equally strong
numerical inequality from the full inputs to Theorem 3.11. Calling the output
representable, related, or simultaneously expressible does not alone supply
Step 2; one must write the implication those properties actually prove.

## Independent elementary scale check

Let L_1,L_2 be ordered one-dimensional real vector spaces, let u_i>0 be marked
elements, and let phi:L_1->L_2 be the order-preserving linear isomorphism with
phi(u_1)=u_2. Let d_i:L_i->R be positive linear isomorphisms. Then

    d_2 o phi = kappa d_1,
    kappa = d_2(u_2)/d_1(u_1).

Proof: two linear maps out of a one-dimensional vector space agree precisely
when they agree on one nonzero vector. Evaluating on u_1 gives the displayed
scalar. Consequently an isomorphism preserving the marked object preserves
its numerical degree only when the two chosen numerical normalizations agree.

For example, choose L_i=R, u_i=1 and phi=id, while d_1(x)=x and
d_2(x)=j²x with j>=2. The marked ordered spaces are identified and the degrees
differ by j². This counterexample applies only to the bare abstract-to-number
inference stated here. It is not a counterexample to Theorem 3.11 or to IUT,
whose additional structure has not been modeled or checked in this note.

## What a repair must preserve

Specify degree normalization before crossing a comparison, compute the scalar
or determinant contribution of every map, and prove that any allowed
indeterminacy has the required numerical effect. If the conclusion weakens to
Q <= T+E, keep E explicit through the eventual height inequality. A formally
consistent diagram with uncontrolled E does not establish abc. Conversely, a
noncommutative diagram is not automatically fatal: the issue is a proved bound
in the required direction, rather than commutativity for its own sake.

This contract neither declares every possible IUT repair impossible nor
asserts that the published input already supplies the witness. It makes the
uncertain implication concrete enough to inspect without assuming it.

## Route disposition and continuation

- Outcome: primary disputed passage localized, numerical witness target
  isolated, bare isomorphism-to-equal-degree implication refuted.
- Evidence: source extraction checked; scale lemma proved above. No theorem
  about all IUT maps has been proved and no formal proof assistant was run.
- Open continuation: reconstruct the normalized determinant-degree map from
  the exact (IPL), (SHE), (APT), hull and log-Kummer definitions used in
  Step (xi-e), and derive the witness inequality or find a counterexample
  satisfying those full hypotheses. A counterexample satisfying only this
  elementary model is insufficient.
- Resumption condition: the relevant comparison is written as an explicit
  mathematical map or relation with the numerical normalization and error
  budget stated. This route remains open; the bounded extraction alone does
  not establish or reject that stronger statement.
