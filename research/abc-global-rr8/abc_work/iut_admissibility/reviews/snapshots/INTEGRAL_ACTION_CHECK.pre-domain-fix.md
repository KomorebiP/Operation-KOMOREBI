# Fixed integral action: the Ind2 subproblem

Base checkpoint: RR5, archive SHA-256
79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01.
This addendum leaves the earlier route files unchanged.

## Checked source interface

IUT II, **December 2020** author version, Example 1.8(iv), printed page 39,
defines Ism(G) using G-equivariant module automorphisms preserving the
unit-image lattice at every open-subgroup invariant level. IUT III,
**May 2020**, Proposition 1.2(vi), printed page 32, says the comparison maps
preserve the respective log-shells and log-volumes. Proposition 3.2(ii),
pages 98–99, constructs packet integral structures by direct sums and tensor
products. Theorem 3.11(i), pages 154–155, applies independent Ism actions to
the factor summands. These are source assertions, not an independent audit
of their anabelian reconstruction proofs.

The inference checked below is conditional on this explicit source interface:
**after fixing one realization and one finite invariant level, an Ind2
operator preserves its mono-analytic lattice I**. This does not say it
preserves the holomorphic structure sheaf, is linear over the local field,
or commutes with multiplication by an arbitrary local element q. It does
commute with rational scalars and with p-adic scalars on the finite space:
continuous additive maps are Z_p-linear by integer approximation, and
division by p then gives Q_p-linearity.

Because the induced tensor of lattice automorphisms is again a lattice
automorphism, this preservation passes to a fixed finite packet constructed
by the prescribed sums and tensor products. Varying the realization, the
finite level, or the vertical log-Kummer coordinate is not included in this
statement. In particular, it is an **Ind2-only** result, not an Ind3 result.

## Elementary fixed-lattice lemma

Let A be a finite product of finite extensions of Q_p, with maximal compact
subring O_A. Let I be a full Z_p-lattice in A and put J=O_A I. For any subset
R of A, write φ(R) for the smallest fractional O_A-ideal containing R when
such an ideal exists. For the sets below, it does exist.

Choose integers a>=b such that

\[
p^aJ\subseteq I\subseteq p^bJ.
\]

Such a pair exists: J is itself a full Z_p-lattice, I⊆J, and
commensurability gives p^aJ⊆I for sufficiently large a>=0, with b=0.
Let G be any nonempty collection of Q_p-linear automorphisms M of A
satisfying M(I)=I. Then, for every integer k,

\[
M(p^kI)=p^kI,
\qquad
\phi(I)=J,
\qquad
\phi(p^kR)=p^k\phi(R).
\tag{1}
\]

The first identity is scalar linearity. The second follows from the
definition of the O_A-span. For the third, multiplication by p^k bijects
fractional O_A-ideals and transports the condition of containing R.
Consequently, if R⊆p^kI, then

\[
\phi\!\left(\bigcup_{M\in G}M(R)\right)\subseteq p^kJ.
\tag{2}
\]

Indeed, every M(R) lies in p^kI, which lies in the fractional ideal p^kJ.
No identity φ(MR)=Mφ(R) is used or generally follows from these hypotheses.
For R=I the weaker identity φ(MI)=φ(I)=J does hold because MI=I.

## A relative depth estimate without q-linearity

Normalize each component valuation by v_p(p)=1. Let q∈A^× have the same
valuation α in every component. For any integer s, including zero and
negative integers, set

\[
t=\lfloor s\alpha\rfloor,\qquad
k=t-(a-b).
\]

Every component of q^s has valuation sα>=t, so q^sJ⊆p^tJ. Therefore

\[
q^sI\subseteq p^bq^sJ\subseteq p^{b+t}J
       \subseteq p^{b+t-a}I=p^kI.
\tag{3}
\]

Combining (2) and (3) yields

\[
\boxed{\quad
\phi\!\left(\bigcup_{M\in G}M(q^sI)\right)
\subseteq p^{\lfloor s\alpha\rfloor-(a-b)}J.
\quad}
\tag{4}
\]

This retains scalar p-depth up to the fixed lattice width a-b. It does
not require Mq=qM. If k>α, the native ideal qJ cannot be contained in the
left-hand hull: its containment in p^kJ would require α>=k in every
component. If k=α, the outer fractional ideal equals qJ, and containment
in the actual hull remains undecided. If k<α, the outer bound permits
containment and proves none. Thus the strict inequality k>α is essential.
The proof uses only valuation inequalities and remains valid for negative
s, negative k or negative α; in those regimes its exclusion criterion may
simply give no information.

For nonhomogeneous component valuations α_i, the same proof works with
t=\(\min_i\lfloor s\alpha_i\rfloor\). To exclude native containment using
a particular component, compare k with that component's α_i.

For central q=p^m, with integer m, there is an exact stronger identity:

\[
M(q^sI)=p^{ms}I,\qquad
\phi\!\left(\bigcup_{M\in G}M(q^sI)\right)=p^{ms}J.
\tag{5}
\]

Here no width is lost. The same holds for q=p^m u with
u∈Z_p^×, since such a u preserves I. An arbitrary u∈O_A^× need not preserve
I, so that extension of (5) is not assumed.

## Application boundary

The checked source interface is enough to apply (1)–(2) to Ind2 operators
on **one fixed finite realization**. To apply (3)–(4) to a proposed output,
one must additionally identify it with an orbit M(q^sI), or prove the
required initial containment in p^kI. For an actual insertion operator,
its component valuations and the lattice width must be established in that
same packet. These data are not furnished merely by knowing that the
operator is an Ism action.

The bounds above do not assume that a finite packet's holomorphic integral
structure is its mono-analytic lattice. They distinguish I from its
O_A-span J. Their inclusion conclusion can be used independently of any
volume normalization; identifying an actual IUT weighted volume with a
numerical expression for this finite A remains a separate dictionary check.
No uniform bound on a-b as the initial Theta-data, local fields or auxiliary
prime vary has been proved here. No conclusion about the full Ind1–Ind3
output union or the global eta compatibility is drawn.

The reconstruction leaves invoked by IUT III at this interface are
[AbsTopIII], Proposition 5.8(ii), Corollary 5.10(iv), and IUT II,
Corollaries 4.5(ii), 4.6(i)–(ii). Their complete proofs were not reconstructed
in this pass. Thus the arithmetic source transfer is conditional on these
explicit statements; the finite-lattice lemma (1)–(5) is independently
proved above.

Primary locators:

- [IUT II, December 2020](https://www.kurims.kyoto-u.ac.jp/~motizuki/Inter-universal%20Teichmuller%20Theory%20II.pdf)
- [IUT III, May 2020](https://www.kurims.kyoto-u.ac.jp/~motizuki/Inter-universal%20Teichmuller%20Theory%20III.pdf)

No full external source text is retained in this addendum. No computation
or proof assistant is needed for the elementary lemma and none was run.

Source-byte authentication, checked 2026-10-25 in memory:

- IUT II: 174 pages, 1,203,855 bytes, SHA-256
  `180bfa6aaddc4ae37af37acaad51f61e0a47b33b8255ad3169e28a970ae39b7c`.
  Definition inspected at printed page 39, PDF index 38, extraction lines
  1843–1847. Web references for this pass: turn81view0 and turn82view1.
- IUT III: 199 pages, 1,307,865 bytes, SHA-256
  `9a7ee3c77b1c7717210c0613eb39b6844649d0040dc3d9e1be7d544f8f91a0b9`.
  Proposition 1.2(vi) inspected at printed page 32, PDF index 31,
  extraction lines 1557–1603. Web reference: turn80view2. Packet and Ind2
  source locations also appear in SOURCE_MAP.md.
