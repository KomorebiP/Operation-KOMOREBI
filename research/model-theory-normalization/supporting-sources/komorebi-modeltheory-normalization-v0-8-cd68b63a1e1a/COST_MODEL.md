# Written cost model, distinct from formal runtime verification

## Proved inputs

The accepted Lean statements establish exact insertion and normalization, identical
worklist results, enough fuel o+krd+1, at most H=rd acceptances, returned test horizon
below H, temporary coefficient peak K=m[2m(m+1)]^d, and at most 2b Euclidean recursive
divisions when the second input is below 2^b. These are the formal inputs below.

## Model and units

Assume m=p^r, p prime, positive precision or the separately trivial r=0 case.
Let beta=1+ceil(log2 m) and let B=O((d+1)beta) denote a conservative signed operand
bit budget. Use dense arrays and cache a value within a primitive loop rather than
re-evaluating its defining expression. Integer addition/comparison on B-bit numbers
costs O(B); schoolbook multiplication and long division cost O(B^2). Euclidean gcd
and the explicit extended-Euclid recurrence use O(B) such division/multiplication
steps, hence the deliberately coarse O(B^3) bound. This can be improved; optimality
is not claimed. Abstract dimension/index/queue overhead is charged separately.

These are stipulated bit-operation semantics for the analysis. There is no theorem
here proving that Lean's compiler, runtime, primitive gcd, bignum division, allocation
or kernel reduction has exactly those costs. In particular function-valued vectors
must not be interpreted as an implicit guarantee of the same array evaluation cost.

## One membership test and one insertion

Triangular membership performs at most d pivot divisions and d(d-1)/2 tail products:
O((d+1)^2 B^2) bit operations under this model.

Raw insertion has d extended-gcd levels and 2d(d-1) individual tail products, plus
additions. Bottom-up normalization has d(d-1)/2 pivot divisions and binomial(d,3)
tail products. A conservative per-acceptance total is

    O((d+1) B^3 + (d+1)^3 B^2).

The operand bound is valid anew after each normalized insertion. It does not grow
with the number of accepted tests. This is the essential missing size control
supplied in v0.8.

## Source rows and complete discovery

Let N=o+kH, H=rd. There are at most N popped candidates. A candidate word has length
at most H (the final pending dependent children can be one longer than returned
words). Reconstructing its row from the original matrices costs at most
O((H+1)(d+1)^2 beta^2) using residue arithmetic reduced after each accumulation.
A single reduced multiplication/addition has numerical product/sum below m^2+m.
The Python port caches row vectors, but that optimization is not silently attributed
to the current Lean worklist, which reconstructs test rows.

Combining the bounds gives the following WRITTEN upper bound:

 O( N[(H+1)(d+1)^2 beta^2 + (d+1)^2 B^2]
      + H[(d+1)B^3 + (d+1)^3 B^2]
      + N(H+N+1) ).

The final term generously includes word/list traversal and FIFO list copying.
Storage/output constants and serialization must be specified before using this as
a bound on a particular binary file or implementation memory profile. The defining
formula lists at most H tests of length below H, so writing that syntax has polynomial
size as well. Verifying the final proof terms is NOT charged by this expression.

Since r<=log2(m) for p>=2, these bounds are polynomial in the displayed source
parameters and coefficient bit length. This is a mathematical analysis of the
specified cost model. It is NOT a Lean-proved end-to-end bit-complexity theorem,
not a wall-time measurement, and not a comparison against a competing solver.

## Next formal obligation

Define a costed evaluator with an explicit arithmetic-operation trace, prove its
value projection equals boundedPrimeDiscover, prove exact operation-count bounds,
and connect a verified integer backend to that trace. That would turn this written
cost composition into a formal executable cost theorem. Keep this separate from
optimizing formula size, minimal test selection, and higher-order/relational discovery.
