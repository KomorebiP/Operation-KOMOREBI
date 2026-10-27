# Residual reflection and internal arithmetic, v0.10.0

## The program

A specified semantic residual-reflection class turns global failure into a small unsatisfiable subsystem. The external classification identifies this class, at a regular infinite cardinal, with fixed-domain constraint compactness, Boolean compactness, complete-filter extension and the fine complete-ultrafilter principle.

The uncountable existence assertion is encoded as a closed membership-language sentence Theta. The project also defines an explicit first-order ZFC theory, with full finite-parameter Separation and Replacement schemas, and its extension by Theta. It does not prove Theta true.

The current task is to establish the mathematical classification internally in arbitrary models of that encoded ZFC theory. All objects and function witnesses in the internal assertion must be represented inside the model.

## Existing guard and smallness

Small(K,X) means that there exist an ordinal member a of K and an internally represented injection X -> a.

Guard(K) consists of the existing initial-ordinal condition, an inductive member, and boundedness of internally small subsets of K. The latter says that any internally small subset S of K is contained in some b belonging to K.

These definitions and the base axioms are unchanged.

## The v0.9 boundary

The predecessor proved that, under Guard(K) and Extension(K),

    Fine(K) <-> SmallUnionClosed(K) <-> SmallProductClosed(K).

It already constructed the internal cone filter and proved internal Fine -> Compactness. The outstanding forward premise was SmallProductClosed(K) in arbitrary models. It had been discharged only in concrete ZFSet.

## Definable induction, not external well-foundedness

For a syntactically supplied first-order formula phi and internal transitive bound T, Foundation applied to the Separation set of counterexamples proves bounded induction.

This yields internal ordinal comparison using two nested instances of bounded definable induction. No external ordinal representation for the model is assumed. Membership well-orders have least elements for all internally represented nonempty subsets.

## Bounded rankings by compatible partial graphs

Let W be internally well-ordered by R, let offset belong to K, and assume each strict predecessor set is internally small below K.

A partial ranking is an internally represented graph g contained in W times K. Its domain is downward closed and each assigned value g(x) is the least member y of K satisfying:
1. offset is a subset of y;
2. every rank assigned to a strict R-predecessor of x belongs to y.

The recurrence, downward closure and functionality are actual first-order definable conditions.

Any two partial rankings agree wherever both are defined. Otherwise, an internal Separation set of disagreement points has an R-least member, where identical earlier assignments force the same least rank.

The collection of all partial rankings is separated from the internal powerset of W times K. Its union is a compatible partial graph. If a point is missing, the internal least missing point has all predecessors assigned. Restrict the graph to its small predecessor set, form its internal small image in K, and apply the guard to find a bound. Ordinal comparison incorporates the chosen offset, and Foundation chooses the least admissible bound.

Appending that pair produces another partial ranking, already in the union, contradicting the missing point. Thus the union is a total internal function W -> K. Its strict increase along R proves injectivity.

This is a bounded recursion construction performed inside the model. It neither assumes the existence of a total ranking nor invokes external recursion on M.

## Shifted copies and binary unions

Apply the ranking construction to an ordinal b belonging to K with chosen offset a belonging to K. Every strict predecessor is a subset of a smaller ordinal, hence small. The ranking image is small because its domain b is small, so the guard bounds it below a member c of K.

This gives an internal injection of b into c with all values at least a. Given small X -> a and Y -> b, place the second copy above a and construct an internal piecewise injection on X union Y. Collisions across the two pieces would imply a set belongs to itself. Therefore binary unions of internally small sets are small.

This result is established before product or general union closure and is not a use of those desired conclusions.

## The two-coordinate range-bound lemma

Let X and Y be internally small and f be an internally represented function X times Y -> K. Product smallness is not assumed.

For each x in X, construct the row graph y |-> f(x,y). Its image is internally small, as an internal image of Y. The guard supplies a bound c_x belonging to K.

The row-bound condition is first-order definable. Internal Choice therefore supplies a selector x |-> c_x whose graph belongs to the model. The image of that selector is internally small, as an image of X. A second use of the guard bounds all c_x below d belonging to K.

Transitivity of d implies every value of f belongs to d. Thus any internal injection X times Y -> K can be retyped as an injection into a strict member d of K.

Both families and both bounds are internal. The argument does not apply completeness or regularity to an arbitrary external collection.

## Ordinal rectangles by definable induction

For fixed K, the statement

    for every b in K and every rectangle W = a times b, Small(K,W)

is represented by an explicit first-order formula. Apply bounded definable induction to a in K.

Equip a times b with its internally represented lexicographic order. The strict predecessors of (i,j) are contained in

    (i times b) union ({i} times j).

The earlier rectangle is small by the induction hypothesis. The slice embeds into j, which is small. The binary-union theorem therefore makes each predecessor set small.

The bounded-ranking theorem gives an internal injection of the full rectangle into K. The two-coordinate range-bound lemma then shrinks its range into d belonging to K. This proves the rectangle is internally small.

All first-coordinate and second-coordinate projections used to establish least lexicographic elements are Separation sets inside the model.

## General small products and the original forward implication

For arbitrary internally small X and Y, choose internal injections into a,b in K. An explicitly constructed product graph gives an internal injection X times Y -> a times b. Ordinal-rectangle smallness and injection transport prove SmallProductClosed(K).

The old consumers now apply without an extra arithmetic premise:

    Guard(K) and Extension(K) -> Fine(K) -> Compactness(K) -> Reflection(K).

In particular, both original closed forward sentences are semantic consequences of the encoded ZFC axioms in every membership structure.

The entire cardinal-square/order-type infrastructure proposed in v0.9 is unnecessary for this regular-guarded proof. No novelty is claimed for the ordinary set-theoretic conclusion.

## Remaining boundary

The internal Compactness -> Extension converse is not yet proved. The complete arbitrary-model classification therefore remains unfinished in one direction.

An assumed model of KZFC yields an internal compactness witness, but no model is produced. No uncountable cardinal existence, independence, relative consistency, new strength or derived-residual classification is claimed. All-model semantic consequences have not been exported as a derivation in a separate first-order proof calculus.
