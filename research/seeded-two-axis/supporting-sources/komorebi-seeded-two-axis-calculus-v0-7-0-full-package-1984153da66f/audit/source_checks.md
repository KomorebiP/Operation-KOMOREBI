# External dependency verification

Checked 26 September 2026 (user-local date). Primary HTML sources were read directly. This is an exact dependency/notation check, not a comprehensive novelty search. Source files are not bundled; no cached-source hashes are claimed. Citations in the manuscript distinguish prior machinery from the present deductions.

## 1. Cones

The Stacks Project, Section 13.9, Tag 014D, Definition 13.9.1 and Lemma 13.9.2.
https://stacks.math.columbia.edu/tag/014D

Used: cochain cone convention and the dependence of a cone comparison on the specified homotopy. The manuscript keeps the square homotopy as part of the input. It does not infer a canonical comparison from equality only in a homotopy category. The total-cofiber/excision statement is proved by finite-colimit interchange in the stable setting. Overlap classification: established convention and direct categorical deduction.

## 2. Koszul complexes

The Stacks Project, Section 15.29, Tag 0621, Definitions 15.29.1–2 and Lemmas 15.29.4, 15.29.7–8, 15.29.12.
https://stacks.math.columbia.edu/tag/0621

Used: exterior algebra differential, invariance under invertible changes of the coefficient row, iterated cones, tensor presentation. The source's exterior degree k is homological degree k. The manuscript places it in cohomological degree -k, with differential degree +1 and the two-variable matrix (-b,a)^t followed by (a,b). Change-of-basis and tensor statements are translated with these signs. The integral gcd result is proved by an explicit unimodular row reduction; no novelty is claimed for this classical algebraic mechanism. The selected lemmas, not webpage comments, are the inputs.

## 3. Triangulated quotient kernels

The Stacks Project, Section 13.6, Tag 05RA, Definition 13.6.1 and Lemmas 13.6.2, 13.6.8–10.
https://stacks.math.columbia.edu/tag/05RA

Used: kernels of exact functors are thick and Verdier quotient kernels are the saturated/thick class. This supports the homotopy-category kernel calculation. It does not alone provide all infinity-categorical functor coherence. That input is separated in the next source. Overlap classification: standard quotient machinery.

## 4. Stable localization

Brad Drew, Verdier quotients of stable quasi-categories are localizations, arXiv:1511.08287v1, Definition 1.1 and Theorem 1.3.
https://arxiv.org/html/1511.08287v1

Used: the stable Verdier quotient and its identification with localization at morphisms with cofibers in the chosen stable subcategory. The selected subcategory here is the constructor-invariant thick closure of the specified square interaction residuals. The universal exact factorization applies after proving constructors preserve that kernel. Coherent action data descend from supplied data, not from a new existence assumption. Overlap classification: established exact input; K36 is its application to the selected interaction class.

## Application boundary

The principal-ideal reconstruction proof is included directly and was checked using universal properties and finite induction. The matrix criterion uses a supplied verified Smith form; its basis changes are part of the finite certificate. No search in this release establishes historical novelty of the seeded package, no external source proves the project's uninstantiated arithmetic globalization implication, and no inference is made from failure to locate a source.
