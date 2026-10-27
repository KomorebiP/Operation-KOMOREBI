# The missing global marking as an actual protected obstruction

Use the field K=Q(i), places v_2 above 2 and v_3 above 3, and finite
local coordinates from PROOF_NOTE.md. Write sigma_j:K->K_(v_j) for the
canonical injective field embeddings. This note defines an additive
Komorebi Space extension problem before testing it. It adds no height
estimate and makes no statement of formal Lean verification.

## Declared view system and protected data

Take a three-object view category, with arrows local_2->global and
local_3->global and no nonidentity composites. Its additive fibers are

    F(global)=K,
    F(local_2)=K_(v_2),       F(local_3)=K_(v_3),

and the restrictions are sigma_2 and sigma_3. A coherent section is a
triple (x,y_2,y_3) with y_j=sigma_j(x). Prescribe

    y_2=2^m,                 y_3=1,             m>=1.

The permitted corrections change the global coordinate x only. The
two prescribed local values are protected. Let

    R=K_(v_2) direct_sum K_(v_3),
    Delta:K->R,              Delta(x)=(sigma_2(x),sigma_3(x)),
    Q=R/Delta(K).

All groups and maps here are ordinary additive groups and homomorphisms.
No topological closedness, Hilbert norm, or completion statement is used.
The quotient is defined from the allowed correction image, independently
of whether the prescribed data extend.

The protected obstruction class is

    omega_m=[(2^m,1)] in Q.                                (1)

One can obtain the sign-reversed class from the raw extension with global
coordinate zero and the convention delta(x,y)=(sigma_j(x)-y_j)_j.
Vanishing is unchanged by that sign. It is the additive extension
obstruction of Komorebi Space under these declared fibers and corrections.

## Explicit nonvanishing and nonexistence

The class (1) is nonzero. If it were zero, some x in K would satisfy

    sigma_2(x)=2^m,             sigma_3(x)=1.

Because sigma_3 is injective and sigma_3(1)=1, the second equality forces
x=1. The first would then imply 1=2^m in the characteristic-zero field
K_(v_2), which is false for m>=1. This contradiction proves nonvanishing.

Consequently no coherent section can extend the two protected local
values. This is an exact two-place certificate of failure of the intended
global marking for the adelic family. It is independent of its complex
phase, its height, and all other finite components.

The weak adelic view system in PROOF_NOTE.md has an exact coherent point
because it has not imposed this single common global K-coordinate.
Adding the global source coordinate and these restriction maps exposes
the obstruction. Thus the failure is not a defect in strict gluing: the
stronger view system has different prescribed compatibility equations,
and the displayed nonzero class explains why they cannot be satisfied.

## What this does and does not resolve

This supplies a concrete arithmetic instance of the framework's protected
extension obstruction. It does not classify diagonal membership for
arbitrary adelic families, give a decision procedure for general quotient
membership, or bound the height of actual diagonal triples.

Genuine global a+b=c inputs have the same global coordinate in all their
local views. Their corresponding marking obstructions vanish by the
supplied global elements. Establishing an ABC height saving on that
vanishing-obstruction locus is still a separate arithmetic theorem. The
construction here prevents a false globalization of the weak ambient
families from being used as evidence for that theorem.
