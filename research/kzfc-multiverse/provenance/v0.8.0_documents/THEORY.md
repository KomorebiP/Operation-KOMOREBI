# Internal fine-ultrafilter compactness, v0.8.0

## Main theorem and conventions

Let M be any structure for the project's first-order membership language and suppose M satisfies its explicit ZFC axiom theory. No external well-foundedness or correctness of M's powerset is assumed.

Write x in_M y for the structure's membership relation. Every displayed set, graph and family below denotes an element of M. An internally coded function is a Kuratowski-pair graph belonging to M, with the totality, uniqueness and bounds predicates already defined in InternalResidualSentence.

Small(K,S) means there is an internal graph injecting S into a member of K. When interpreted at an initial-cardinal code in concrete ZFSet, this agrees with the predecessor's strict cardinal bound. In the new arbitrary-model proofs, it is used only internally.

The theorem is

    M models ZFC  =>  for every K in M,
      InternalFinePrinciple_M(K) => ConstraintCompactness_M(K).

The entire implication is compiled into the closed membership-language sentence fineCompactnessSentence. model_zfc_fineCompactnessSentence proves that every model of the encoded ZFC theory satisfies it. The theorem is a semantic consequence, not a separately extracted proof-calculus derivation.

## Constraint representation

The data are internal sets I, V, A, C and scopes. I indexes constraints, V indexes variables, A is the fixed value domain. E is an internally existing function space: membership in E is equivalent to being an internally coded function V -> A. The internal table C is bounded by I times E. Satisfaction of constraint i by assignment g means the internal ordered pair (i,g) belongs to C.

The scope map is an internal function I -> P_M(V). Each scope and the value domain are internally Small below K. A constraint's truth is required to depend only on the assignment graph's values on its scope. This is a declared structural condition, not a compactness assumption.

LocalSat states that each internal subset J of I with Small(K,J) admits an internal full-domain assignment satisfying all its constraints. GlobalSat asks for one internal assignment satisfying I.

ConstraintCompactness quantifies over all internally admissible data and asserts LocalSat implies GlobalSat. ConstraintReflection is its exact classical contrapositive: global failure has an internally small unsatisfiable subsystem. The equivalence between these formulations is checked and uses the same class, domains, scopes and support convention.

## Internal closure constructions

The proof builds products by separating P_M(P_M(X union Y)), proving every required ordered pair belongs to this bound. It then builds the internal function space by separating P_M(X times Y). This collection contains all and only functions represented by graphs in M. It is not claimed to contain every external function between the external member collections.

relationSet_exists accepts an actual finite-parameter first-order formula. It separates a product to construct the corresponding relation. It does not permit arbitrary external comprehension.

For a total bounded relation R from I to A, the proof constructs each fiber in P_M(A), collects the indexed fibers by Separation, uses M's encoded Choice axiom, and constructs the selected I -> A graph by another bounded formula. This proves internal_selection and, for the solution relation, localAssignmentSelector.

Composition and restriction are constructed internally. A section of the inverse of an internally surjective function gives an internal injection of its codomain into its domain. Thus small_of_surjection transports internal smallness to an internal image. All injections and compositions used in the size argument have graphs in M.

definable_image_function applies the exact Replacement schema to a real finite-parameter formula with unique outputs. It constructs both the internal image and the internal function graph. No additional closure field is added to AxiomSemantics.

## Ultrafilter selection

For an internal cover B of X, with Small(K,B), construct the family D of complements in X. The complement map is internally injective on subsets of X, so D is internally Small. If no member of B lies in U, all members of D lie in U. Internal completeness then gives a U-member realizing their relative intersection inside X. The covering property makes that intersection empty, contradicting properness.

This proves small_cover_selection without requiring pairwise disjointness.

For an internal function f : X -> A with Small(K,A), construct the internal family of fibers as an internal image of A. The image-smallness theorem justifies applying small_cover_selection. This produces a U-large fiber. Two distinct values cannot both have U-large fibers because their intersection would force two outputs of one function to be equal. These are small_fiber_selection and selected_fiber_value_unique.

No external family is passed to the internal completeness predicate.

## Reconstructing the satisfying assignment

Assume an internal fine complete ultrafilter U on P_K^M(I). Local satisfiability first gives an internal selector L assigning a solution g_J to every internal small J. For each v in V, coordinate_function builds the internal graph J |-> g_J(v). The small-fiber theorem selects its unique U-large value.

concentrated_assignment assembles the selected values into an internal graph g : V -> A by a first-order formula on V times A. It does not appeal to an external choice function that is then assumed to be internal.

Fix a constraint i with small scope S. Functional Replacement collects the coordinate agreement fibers over S as an internal family. An internal surjection from S proves this family Small. Completeness yields a U-large set on which g_J agrees with g at every variable of S. This is agreement_set.

Fineness supplies an internal U-large cone of J containing i. The intersection of the cone and the agreement set is nonempty. At a member J, the selected local assignment g_J satisfies i and agrees with g on i's scope. The declared locality condition transfers satisfaction to g. Since i was arbitrary, g satisfies every constraint.

## Exact foundational boundary

The new implication is

    internal fine complete ultrafilter principle
        => internal fixed-domain compactness
        <=> internal residual obstruction reflection.

No internal fine ultrafilter is asserted to exist. The earlier closed sentence Theta is stated in terms of internal complete-filter extension, not by definition in terms of fine ultrafilters. The internal extension-to-fine bridge and the internal compactness-to-extension converse still have to be proved. The external/concrete classification from older releases cannot simply be substituted for these internal proofs.

In particular, this release does not yet establish the full internal equivalence of Theta with the new constraint compactness schema in every ZFC model. It establishes a substantial, separately checked direction needed for that equivalence.

## Evidence versus mathematical scope

The assertions are universally quantified Lean theorems. They are not extrapolations from finite samples. The finite verification plan checks their proof terms and dependencies, source preservation, input stability and rejection controls. The ambient Lean axioms and compiler/kernel/dependency cache remain trusted. No claim of novel set-theoretic strength, uncountable existence, independence or relative consistency is made.
