# Generalized family calculations

The explorer uses exact integers and reduced rational numbers. Its parameter
bounds are computational bounds, separate from the domains of the defining
families. The source index includes analytic families that it does not evaluate.
Indexing a source is not a new proof review of that source.

## Initial values and the generating numerator

Fix an integer k>=2 and integer weight c>=1. For arbitrary integer seeds
s(0),...,s(k-1), let a(n)=s(n) for n<k and

    a(n)=c sum_(j=1)^k a(n-j), n>=k.

Writing D(z)=1-c(z+...+z^k), coefficient comparison gives

    D(z) sum_(n>=0) a(n)z^n = P(z),
    P(z)=sum_(n=0)^(k-1) (s(n)-c sum_(i=0)^(n-1) s(i)) z^n.

Every coefficient of degree at least k vanishes by the recurrence; the lower
coefficients are exactly the displayed seed defects. Since D(0)=1, division is
unique as a formal series over Z. If b(n)=[z^n]D(z)^(-1), then a(n) is the
finite convolution of P with b. This proves the seeded closed formula used by
the explorer. In particular, k-1 zero seeds followed by one give P=z^(k-1).
The normalized nonzero tail instead has generating function D^(-1).

The reciprocal-power family D^(-r) uses its own initial values. Choosing an
arbitrary k-seed vector switches to the order-k recurrence (r=1); the interface
does not silently combine arbitrary k seeds with a power-r initial-value problem.
The finite binomial and hypergeometric expressions for b and D^(-r) are in
[the existing derivation](../sequence-connections/IDENTITIES.md).

## Constant coefficient recurrence

For a positive integer power r, expand D(z)^r=1+sum_(j=1)^(kr) d(j)z^j.
The coefficients of 1/D(z)^r satisfy

    a(n)=-sum_(j=1)^(kr) d(j)a(n-j), n>=kr.

The first kr coefficients are supplied by the generating function, with
negative-index coefficients zero when constructing that prefix. For a seeded
order-k problem the declared seeds replace that prefix and r=1. The modular
lab therefore uses order kr for a reciprocal power, and order k for an arbitrary
seed vector. These are different from the shorter variable-coefficient
recurrence n a(n)=c sum_j (n+(r-1)j)a(n-j).

## Complete-state modular certificates

Reduce the fixed integer recurrence and its initial values modulo m>=2.
The state at n is the complete vector (a(n),...,a(n+d-1)), where d is the
fixed recurrence order. Its successor is a deterministic function of that vector.
If state i repeats at j>i, induction on subsequent transitions proves that
every future state repeats with period j-i. Using the first repeated state
identifies the preperiod i and the least state-cycle length j-i. Repeated
individual output values alone do not imply a state repeat.

The transition need not be invertible. For example, with k=2, c=2, r=1,
nonzero-tail seeds (1,2), and m=2, the initial state is (1,0), followed by
(0,0), which then repeats. The preperiod is one and the cycle length is one.
Reaching a finite search bound without a repeated complete state supplies no
period claim. Residue-frequency charts describe only their displayed window.

The implementation reduces all coefficients to 0..m-1, with m<=256 and
d<=128. Every per-term multiplication and addition is below 2^53 before its
next reduction, so these bounded integer operations in JavaScript Number are
exact. Original coefficients and seeds are parsed and reduced using BigInt.

## Parameter-polynomial recurrence

Let t=z^N and C(t)=sum_(i>=0) (-1)^i t^i/(Ni)!. Define

    C(t)^(-r)=sum_(n>=0) P_(N,n)(r)t^n/(Nn)!.

Using C H'=-r C' H and comparing coefficients of t^(n-1) and r^k
gives, with P(n,k)=[r^k]P_(N,n)(r),

    n P(n,k)=-sum_(i=1)^n (-1)^i binom(Nn,Ni)
                      ((n-i)P(n-i,k)+i P(n-i,k-1)).

Here P(0,0)=1 and out-of-row entries vanish. This establishes the new exact
recurrence without changing the ordinary polynomial-coefficient normalization.
Its finite audit compares it to the maintained Bell-column construction.

Integrality can also be read from the finite negative-binomial expansion.
For each number ell of blocks, the coefficient of r^k in (r)_ell is the
unsigned first-kind Stirling number [ell,k]. After division by ell!, the
labelled-block sum is the number of set partitions of Nn elements into ell
blocks whose sizes are positive multiples of N. Its sign is (-1)^(n+ell).
Thus P(n,k) is a signed integer combination of such partition counts.

## Transfer composition

For anchored ordinary tails A,B,C with nonzero constant coefficients over Q,
the constructed kernels are H_AB=B/A and H_BC=C/B. Their product is C/A.
The inverse kernels compose in the reverse order. On stored prefixes, all
equalities are only modulo z^L. The leading-zero position shifts and original
index shifts add separately; each intermediate anchor cancels in the sum.
The corresponding prescribed-zero-prefix domains remain attached to the maps.
This construction uses the chosen targets and does not predict unrecorded terms.

A path in the research graph retains its individual evidence types. In
particular, composing a finite-comparison edge does not upgrade it to an
infinite identity, and matrix inversion of a coefficient table is not ordinary
convolution of its flattened cells.

## Self-review and finite verification

The displayed seed numerator, polynomial recurrence, recurrence-state cycle
argument and ordinary-kernel composition are proved as written above under
their stated domains. The source-defined analytic family cards retain their
source hypotheses and are outside this focused proof self-review. Their
formula transcriptions and source bindings are checked separately.

The finite computation command is documented before execution in the workspace
audit contract. Current completed receipts and tested ranges are recorded in
verification/sequence-library/README.md after execution. Finite checks do not
establish historical novelty or replace the uniform arguments above.
