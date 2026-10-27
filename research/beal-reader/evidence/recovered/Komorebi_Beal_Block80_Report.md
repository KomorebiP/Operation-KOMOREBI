# Beal research, Block80
## Restricted primitives and an explicit affine obstruction

Release8.0.0,22 September2026. The bare first-stage equation now has a global
solution on the justified finite ramification set. The remaining geometric
first-stage question is reduced to an explicit affine cokernel test with seven
or eight coordinates. Those actual coordinates have not been evaluated.

NONE of the eight residual patterns is eliminated. This is a written conditional
result with exact finite arithmetic, not a Beal proof, Lean certificate, or
independent mathematical review.

## 1. No auxiliary ramification is needed for the bare p-equation

Let Sigma consist of the nine actual beta-support primes and the fixed primes
above2,3,5,7, together with infinity. Poitou--Tate gives the relevant restricted
H2 injection after its dual Sha1 is checked. OverQ(sqrt5), class number one and
the fundamental unit phi reduce the kernel to a power of phi. Its exact local
symbol at7 is nonzero, so the kernel is zero. The frozen local alpha/beta data
then force

    [alpha cup beta]=0 in H2(G_(K,Sigma),k).

Hence a continuous p0 with dp0=-alpha cup beta exists without adding conductor
primes. This does not assume an actual higher representation to construct its
first-stage cochain. It is an existence proof, not a numerical global p0.

At a fixed place, write beta=(chi^-1-1)lambda_v. The unique primitive satisfying
the local first-order trace condition is

    p_v^fix=lambda_v chi^-1 alpha.

Its difference from p0 is an ordinary local character. These are the fixed-local
affine targets, not independent choices of p at each completion.

## 2. The complete restricted ordinary localization matrix

The global ordinary H1 has dimension10 overk=F49. Its local target has dimension24:
three fixed unramified coordinates, three seven-adic coordinates, and two per
support prime. The fourteen global Sigma-unit relations have full rank14. An
explicit24-by-10 matrix J parametrizes their entire kernel, exactly the global
localization image.

The corrected self-conductor beta Frobenius calculation supplies every toric
row, including at primes where beta RAMIFIES. Norm-q cyclotomic generators and
unit parts pi_q/q are checked in two ways. The old beta inertia normalization is
converted to the ordinary local Artin generator; omitting that scale would change
the problem.

After six fixed-local zero conditions and nine toric difference conditions,
A=EJ is a15-by-10 matrix:

|Pattern|rank|homogeneous k-dimension|affine cokernel k-dimension|
|---|---:|---:|---:|
|A|7|3|8|
|B|7|3|8|
|C|8|2|7|
|D|7|3|8|

The remaining characters ramify only at the minus-congruence primes307,797,1483;
Pattern C has only307,1483. This is a result about DIFFERENCES, not about the
absolute inertia of p0. Pattern C improves from the old dimension4 to2. A small
certificate is the matrix [[3,1],[5,2]], determinant1, acting on its two former
plus directions.

With the additional COMMON pointwise semilinear frame condition, the conditional
numbers of first-stage choices become343,343,49,343. They are not representation
counts and do not establish a nonempty affine set.

## 3. The exact remaining affine test

For one bare global p0, form the15-vector t(p0). Its six fixed entries are the
coordinates of p_v^fix-p0|_v. At a support prime q its entry is

    -h_q*c_q - c_q*p0(F_q) + b_q*p0(T_q).

Here c_q=beta(T_q), b_q=beta(F_q), h_q=(q^2-1)/7 mod7, in the prescribed local
normalization. A desired global p exists at Stage P iff

    A*z=t(p0)

has a solution. The supplied full left-null matrix N gives the equivalent test

    N*t(p0)=0.

Changing the bare primitive shifts t by an image vector; the obstruction is
therefore canonical in coker A. The code evaluates a supplied target and returns
obstruction coordinates and a character correction when one exists.

NO ARITHMETIC TARGET HAS BEEN SUPPLIED OR COMPUTED. In particular, zero is not
being substituted for p0. Some of the7/8 linear obstruction coordinates might
vanish for additional structural reasons, but no such evaluation is claimed.
The upper q and mod343 integral-lifting problems remain even after Stage P passes.

## 4. Checks and limits

Primary and separate finite programs agree on their complete result JSON, using
different field bases, norm algorithms, self-conductor unit calculations and rank
certificates. The separate program checks the unit pi_q/q by a Hensel lift of the
cyclotomic root modulo q^2. It imports no primary or predecessor arithmetic.

The computations include592 residue-symbol evaluations per implementation,
seven direct self-uniformizer checks,16 independent rank-minor certificates,
12348 Frobenius-lift identity cases,560 synthetic image tests, and a supplied-
target evaluator with84 image/nonimage cases,40 origin-invariance checks,
16 malformed inputs rejected and12348 fixed-local primitive identity cases.
These synthetic checks do not count or construct arithmetic solutions.

The final execution/ZIP audit is external to the immutable package. The original
Block79 archive remains exact, including all nested history. The default replay
rebuilds the current finite assertions only; the optional flag adds just one
immediate Block79 default run. No new point counts, Lean run, or independent
mathematical reviewer is claimed.

A too-strong initial primitive-generator check and a wrapper syntax error stopped
those attempts before their results were accepted. They were corrected and are
preserved as rejected source. All earlier failures remain in the predecessor.

## Next obligation

Compute the actual canonical affine class N*t(p0), not another homogeneous rank.
A direct arithmetic defining extension for p0, or a relative-duality evaluation
of the same class, is required. If nonzero it excludes that first-stage branch;
if zero it supplies a finite family for the next q and integral compatibility
calculation. The matrices are ready, but their arithmetic input is not.

The eight bounded patterns, unrestricted conductors/depths, minus component,
actual global realization, independent upstream acceptance, other signature
branches and full Beal remain unresolved.
