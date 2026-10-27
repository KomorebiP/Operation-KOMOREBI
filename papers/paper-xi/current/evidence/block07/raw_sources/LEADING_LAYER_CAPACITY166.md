# A surviving leading symplectic layer and arbitrary-length odd-prime packets

Status: ordinary proof from the retained Bushnell–Kutzko theorems and, for the source-defined candidate, the substantial published Bushnell–Henniart arithmetic induction/descent constructor. No Lean build or bounded computation is used. Independent review is pending.

## The useful simplification

Full critical-profile rigidity is unnecessary for the trivial-stabilizer finite attachment contract. An even leading level produces a symplectic subspace that survives every later simple approximation. For the independent rank-p Heisenberg tensor sources, this single subspace already has enough dimension to hold every source plane, however many there are.

The argument below concerns the actual type in the source-defined arithmetic candidate. It does not identify that type with a separately guessed binder parameter.

## 1. Leading-layer theorem

Let F have residue field k of cardinality q and residue characteristic p. Let pi be an actual irreducible supercuspidal representation of GL_n(F) with torsion number one, where n=p^r. Suppose

    a(pi)=n+N,     N>0 even,     v_p(N)=r−1.

Then an actual maximal simple type in pi, with Heisenberg quotient W=J^1/H^1, contains a nondegenerate symplectic F_p-subspace S of dimension

    [k:F_p] (p−1)p^(r−1).

For k=F_p this is exactly (p−1)p^(r−1). The subspace is the image of the concrete congruence group U^(N/2)(A) in J^1/H^1. It is present regardless of the later critical exponents, their parities, or the number of intermediate approximation fields.

### 1.1. Actual parameter field and leading level

By BK maximal-type existence, pi contains a maximal simple type. Its positive level follows from a(pi)>n. Write its stratum as [A,N_A,0,beta], with parameter field K=F[beta]. BK 6.2.5 gives

    t(pi)=n/e(K/F).

Thus e(K/F)=n. Since [K:F] divides n, K/F is totally ramified of degree n and has residue degree one. The principal-order assertion after BK 6.2.5 gives e(A)=n. Accordingly A is the complete principal hereditary order. The established conductor formula

    a(pi)=n+n N_A/e(A)

now implies N_A=N. This is the same source-checked formula used in Block165, originating in BH1999 Section 6.1 Lemma 2 and retained in PRINCIPAL_ORDER_CONDUCTOR161.md.

Put P=rad(A), U^a(A)=1+P^a for a>=1, and m=N/2.

### 1.2. The terminal minimal approximation has degree p

Apply the defining-sequence construction BK 2.4.1–2 to beta. Write gamma for its terminal minimal approximation. Every transition has a critical level c<N, and gamma has the same A-level N as beta. All approximation residue degrees divide f(K/F)=1, and all approximation ramification degrees divide n. Therefore E=F[gamma] is totally ramified of degree d dividing n.

The scalar case is impossible: a scalar of F has A-valuation divisible by n, whereas v_p(N)=r−1. Thus gamma is noncentral and minimal in the ordinary field sense. Its field valuation is

    −v_E(gamma)=Nd/n.

Minimality, by BK 1.4.14–15, requires gcd(Nd/n,d)=1. Since d is a p-power and v_p(N)=r−1, integrality first gives p|d, while coprimality forces d=p. Hence E/F is totally ramified of degree p.

Set B=End_E(F^n), B_order=A∩B, and Q=rad(B_order). The same complete lattice chain has period n/p over E. Each P-grade has k-dimension n and each Q-grade has k-dimension n/p. In particular,

    dim_k P^m/(Q^m+P^(m+1))=n−n/p.

No assertion that E is literally a subfield of the final field K is needed. It is the actual minimal approximation field in the defining sequence.

### 1.3. The high subgroup survives every approximation

The minimal definitions BK 3.1.7–8 give

    J_order(gamma)=B_order+P^m,
    H_order(gamma)=B_order+P^(m+1).

At a nonminimal transition beta_i→beta_(i+1), with critical level c_i<N, the recursive J-order definition uses the threshold ceil(c_i/2). Since ceil(c_i/2)<=m, the inclusion P^m⊂J_order(beta_(i+1)) implies P^m⊂J_order(beta_i). Starting at gamma, induction proves

    U^m(A)⊂J^1(beta).

For H, BK 3.1.9(ii) states that H^a(beta_i)=H^a(beta_(i+1)) as soon as

    a>=floor(c_i/2)+1.

Every c_i is at most 2m−1, so this threshold is at most m. Consequently

    H^m(beta)=H^m(gamma).

Here H^m means H^1∩U^m(A). Therefore the image S of U^m(A) in W is canonically

    S = U^m(A)/H^m(beta)
      = U^m(A)/H^m(gamma)
      ≅ P^m/(Q^m+P^(m+1)).

The last group identification uses m>=1, so multiplication is additive modulo P^(m+1). Thus |S|=q^(n−n/p).

### 1.4. Its actual commutator form is nondegenerate

Choose the actual simple character theta contained in the type of pi. By the standard deep-restriction property of simple characters, theta restricts to psi_beta on U^(m+1)(A). This follows directly from BK 3.2.1–4 by induction along the defining sequence.

For u,v in U^m(A), their group commutator is in U^(2m)(A)=U^N(A), which lies in U^(m+1)(A). The terminal approximation satisfies

    beta−gamma∈P^(1−N),

because every critical level in the sequence is less than N. Hence

    (beta−gamma)([u,v]−1)∈P.

With the standard level-one additive character psi_A=psi_F∘tr_A/F, psi_A is trivial on P. We therefore have the exact equality

    theta([u,v]) = psi_beta([u,v]) = psi_gamma([u,v]).

The right side is the Heisenberg commutator pairing for the minimal simple stratum of gamma. Its quotient J^1(gamma)/H^1(gamma) is precisely U^m(A)/H^m(gamma), because J^1(gamma)=U^1(B_order)U^m(A), with U^1(B_order)⊂H^1(gamma). BK's nondegeneracy theorem for simple-character commutators therefore says that the form on S is nondegenerate.

For general k, this is a nondegenerate alternating F_p-form of dimension [k:F_p](n−n/p). For k=F_p, it has dimension n−n/p. This proves the theorem.

The argument uses no self-pair conductor and no determination of the later critical levels. Those invariants remain useful for finer arithmetic identification, but they are not needed for this finite-sector capacity claim.

## 2. Arbitrary-length odd-prime source family

Fix an odd prime p and F=F_p((t)). Let the complete marked Weil source rho be an independent tensor product of r rank-p wild Heisenberg factors at distinct positive levels

    0<h_1<...<h_r,     p∤h_i.

Here independence means the stipulated balanced-central-product description of the wild image is valid, and rho|P_F is irreducible. We do not infer independence from the inequalities alone. Suppose the retained Tsushima source calculation supplies the usual highest slope

    slope(rho)=(p+1)h_r/p.

Then rank(rho)=n=p^r and

    Swan(rho)=N=(p+1)p^(r−1)h_r.

Let Pi_BH(rho) be the published source-defined arithmetic induction/descent candidate, with its full prescribed central character, as audited in Block165. The construction is applied to the complete actual rho, including its scalar normalization. Its codomain is the torsion-one supercuspidal class, and its standard epsilon-function property gives a(Pi_BH(rho))=n+N. These are uses of the substantial classical constructor, not consequences of finite Heisenberg algebra alone and not a selection of an inverse LLC image.

For odd p, N is even and v_p(N)=r−1. The leading-layer theorem therefore puts a symplectic space of dimension

    D=(p−1)p^(r−1)

inside the actual Heisenberg quotient of a type in this same Pi_BH(rho).

The source packet is the orthogonal sum of r planes, so its symplectic dimension is 2r. The elementary inequality

    (p−1)p^(r−1)>=2r

holds for every odd p and r>=1: it suffices that 3^(r−1)>=r, which follows by induction. Thus the actual candidate's leading symplectic layer alone can receive the entire source packet.

### 2.1. Full characters and recovery for declared C={1}

Work under the same finite scalar-pushout contract as SAME_CANDIDATE_ATTACHMENT165.md: declared stabilizer C={1}, one vertex, and full source character extensions retained, with no requirement of literal old matrix-group inclusion or equality of old numerical depths with host depths.

Let P_src be the balanced C×-central product of the r supplied full source character extensions. Its quotient V_src has dimension 2r over F_p and its central-character-one Heisenberg representation has dimension p^r=n. Choose a symplectic embedding V_src→S⊂W.

The C×-pushout of the actual type character, restricted to this subspace, has the same alternating commutator as P_src. The retained extension theorem supplies a center-fixing isomorphism from P_src to that restriction. Consequently every source h∈H_i^1 is carried to the scalar theta_i(h), preserving the full character value. No shallow source values are discarded.

Let V be the image and write W=V⊥V_perp. Stone–von Neumann gives

    eta_W ≅ eta_src⊗eta_perp.

Choose a line in eta_perp and the corresponding rank-n projector e in the actual finite Heisenberg image algebra. Then e eta_W≅eta_src. Applying the retained Block159 induction/idempotent theorem to the unchanged actual extended type Lambda in Pi_BH(rho) recovers Lambda and then this exact Pi_BH(rho). All source normalization and the actual noncompact scalar remain fixed.

This proves same-candidate finite attachment for arbitrary r in this C={1} odd-prime family. Original H5, when supplied for this same candidate, remains exactly the original conditional comparison premise. We do not prove it here.

### 2.2. First new rank: GL_27

For p=3,r=3, the source has rank27 and V_src has dimension6. Put h=h_3 with 3∤h. The actual candidate has

    N=36h,       m=18h,
    dim_F3 S=27−9=18.

Thus its high layer contains the entire three-plane source packet. At least a 3^9-dimensional Heisenberg contribution is present, while the required source sector has dimension27=3^3. The six surplus symplectic pairs can be projected onto a line in their representation, together with any additional lower layers. This proves the required capacity and sector realization for the new rank27 family without solving its two possible lower critical levels.

In particular, for (h_1,h_2,h_3)=(1,2,4), N=144 and the same high subspace has dimension18. These numbers are a specialization of the universal proof, not a numerical experiment.

## 3. Why trying to force every critical level was unnecessary

At rank27, a hypothetical complete degree pattern 27→9→3 has leading level N=36h_3 and lower critical levels a<b<N. The standard full-profile conductor count would give

    Swan(End rho)=18N+6b+2a.

Comparing with the stipulated source formula 8(h_1+9h_2+81h_3) only gives

    a+3b=4h_1+36h_2.

That single linear relation does not determine both a and b, and by itself does not force each parity. Nor does it establish that all three degrees occur rather than skipping degree9. This observation is only a warning about the insufficient equations; it is not presented as an arithmetic counterexample or as existence of every numerical profile satisfying the equation.

The leading-layer theorem bypasses these unresolved profile choices. It supplies a fixed nondegenerate high subspace in every actual candidate with the two required invariants.

## 4. Dyadic capacity boundary

The leading-layer theorem itself is valid at p=2. If an actual torsion-one candidate of rank2^r has

    N=3·2^(r−1)h,     h odd,     r>=2,

then its high subspace has dimension 2^(r−1) over F_2. This alone is at least 2r for r>=4, with equality at r=4. It does not supply enough capacity by itself for r=2 or3. For r=1, N is odd and this theorem does not apply.

This is a capacity statement only. Applying it to a dyadic source requires the actual source family, its arithmetic candidate and whatever quadratic/phase markings the original contract requires. No universal dyadic attachment theorem is claimed from dimension alone.

## 5. Boundaries that remain

1. The full character attachment here is through center-fixing scalar-pushout maps. Literal embeddings of prescribed old arithmetic matrix groups are not proved.
2. No nontrivial prescribed stabilizer action is attached. Capacity does not imply equivariant placement.
3. All planes may be placed in the leading host layer. Preservation of supplied numerical ramification depths, or a specified map into individual host depth layers, would be an additional requirement and is not claimed.
4. General packet transport graphs are not handled here. The statement is for C={1} and one vertex.
5. The arithmetic induction/descent theorem is an explicit major external input. This is a new capacity/attachment consequence for its actual output, not a new elementary reconstruction of that classical constructor.
6. H5 remains conditional and refers to that unchanged actual candidate. No additional pair-factor premise is introduced.
7. No Lean verification is claimed.

## 6. Primary locators and retained dependencies

The authorized primary BK text was read at these exact results: 1.4.14–15 (minimality), 2.4.1–2 (defining sequence and degree divisibility), 3.1.7–9 (recursive orders and high-depth equality), 3.2.1–4 (deep restriction of simple characters), 3.4.1 (nondegenerate Heisenberg commutator), and 6.2.5 with the following paragraph (torsion number and principal period).

The standard conductor and published arithmetic-constructor properties are reused from the source-pinned Block165 audit and Block161 conductor proof. The finite scalar-pushout and sector-recovery arguments are exactly those retained and restated in SAME_CANDIDATE_ATTACHMENT165.md. No entire copyrighted source is copied into this continuation.
