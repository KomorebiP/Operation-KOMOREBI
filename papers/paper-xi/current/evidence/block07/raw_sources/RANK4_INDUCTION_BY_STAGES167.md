# Exact compact-induction recovery for the enlarged rank-four carrier

Date: 2026-10-05. Corollary to RANK4_ENLARGED_CARRIER167.md, whose reviewed
bytes are kept unchanged. Ordinary proof submitted for independent audit.

Use that note's actual groups and notation:

    n=2a,  r=2m+1,  a>r,
    H subset J=J1(beta) normal in P=J U_B^m,
    [P:J]=2,  N=K^times J,
    pi=c-Ind_N^G(Lambda),  Lambda|J=eta.

The field K normalizes P. Consequently the following are actual groups
and actual smooth representations:

    M=K^times P,
    Sigma=Ind_N^M(Lambda),
    dim Sigma=4,
    Sigma|P=Ind_J^P(eta),
    pi is isomorphic to c-Ind_M^G(Sigma).

The representation Sigma is irreducible, and M is compact modulo the
center of G. Thus the enlarged carrier has an exact arithmetic inducing
datum for the same candidate, not merely an occurrence in its restriction.

## 1. Normalization by the actual parameter field

The units O_K^times equal U_K^1 because the residue field is F_2. They
belong to J and hence normalize P. It remains to check a uniformizer
k of K. This element has A-grade one and normalizes A.

The actual-field approximation estimate proved in Section2 of the
carrier note gives

    k=b+e,  b in Q^1,  e in P_A^(n-r+1).

The leading grade of b is the nonzero centralizing line of the primitive
derived parameter. Over F_2 it is exactly the leading grade of R, the
period-two E-chain shift. Therefore

    b=R v,  v in 1+Q^1.

In particular b is invertible and normalizes both the complete E-chain
and the complete interleaved F-chain. We can write

    k=b(1+epsilon),  epsilon in P_A^(n-r).

For u in U_B^m, the usual filtration commutator bound gives

    (1+epsilon)u(1+epsilon)^(-1)u^(-1)
       in U_A^(n-r+m).

This group is contained in U_A^a subset J, because

    n-r+m=2a-m-1>a.

Conjugation by b preserves both relevant filtrations. Since b normalizes
U_B^m, it follows that

    k U_B^m k^(-1) subset U_B^m J=P.

Also kJk^(-1)=J, as K^times normalizes its actual simple-character
groups. Thus kPk^(-1) is contained in P and contains J. Its index over
J is two, equal to [P:J], so it equals P. This proves normalization by
k, its inverse, and hence all K^times.

No equality or inclusion between the fields E and K was used. The
element b belongs to the actual outer centralizer B and only approximates
k to the stated precision.

## 2. The two inducing groups have index two

Since K^times normalizes P, the product M=K^times P is a group. Both
P/J and the conjugation action of K^times on it are defined; P/J has
order two, whose automorphism group is trivial. Therefore

    [K^times,P] subset J.

Together with J normal in P and K^times normalizing J, this proves
N=K^times J normal in M. The intersection K^times cap P is U_K^1,
which is contained in J, since P subset U_A^1. Consequently

    [M:N]=[P:J]=2.

The quotient K^times/F^times is compact because K/F is a finite totally
ramified extension, and P is compact. Hence M is compact modulo F^times.
It is open in G because it contains the open subgroup J.

## 3. The enlarged inducing representation is irreducible

Let u in P represent its nontrivial coset modulo J. The carrier note
proved that theta^u differs from theta, and therefore eta^u differs from
eta. It follows that Lambda^u differs from Lambda, since their
restrictions to J already differ. Applying finite-index Clifford theory
to N normal in M gives

    Sigma=Ind_N^M(Lambda) irreducible,
    dim Sigma=2 dim Lambda=4.

There is one N--P double coset in M, and N cap P=J. Thus restriction to
P gives the actual four-dimensional Heisenberg carrier:

    Sigma|P is isomorphic to Ind_J^P(eta).

Its central character on F^times is unchanged from Lambda, because
F^times is central and lies in N.

## 4. Exact recovery by induction in stages

Induction in stages for these open subgroups gives

    c-Ind_M^G(Sigma)
       is isomorphic to c-Ind_M^G(Ind_N^M Lambda)
       is isomorphic to c-Ind_N^G(Lambda)
       =pi.

The second induction is finite-index, so ordinary and compact induction
from N to M agree. This is an exact equality of the resulting isomorphism
classes and applies to the same fixed Lambda, including its noncompact
scalar choice. It introduces no new candidate and no H5 premise.

## Scope

This establishes the arithmetic inducing datum and exact recovery for
the enlarged carrier. It leaves unchanged the distinction between the
original two-dimensional BK quotient J/H and the new four-dimensional
actual quotient P/H0. It also leaves unchanged the source-phase and
literal extraspecial-center limitations recorded in the carrier note.

Dependency pin: RANK4_ENLARGED_CARRIER167.md SHA256
1517e26138776fe0f32d74a174d309ec5dd6a0f572a979473d8af3d20b7a4155.
