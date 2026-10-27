# Audit: IUT III Corollary 3.12

## Scope

This audit used the user-supplied May 2020 IUT III PDF and followed the chain around Theorem 3.11, Remark 3.11.1, Proposition 3.9, Remark 3.9.5, Corollary 3.12, and Remarks 3.12.1–3.12.3. IUT IV was checked to confirm that the later explicit estimate genuinely uses the theta-value \(j^2\) weighting.

This document is an audit of proof structure, not a proof that IUT is false.

## Source landmarks

- IUT III Theorem 3.11 begins around PDF p. 153.
- Remark 3.11.1 begins around p. 159.
- Corollary 3.12 begins around p. 173.
- Step (xi) occupies roughly pp. 181–185.
- Remark 3.12.2 begins around p. 187.
- IUT IV Theorem 1.10 begins around p. 22; explicit \(q^{j^2}\)-dependent estimates occur around pp. 27–29.

## What is clearly established in the 2020 formulation

1. Distinct arithmetic-holomorphic structures are not naively identified.
2. Theorem 3.11 provides a multiradial representation modulo named indeterminacies.
3. Remark 3.11.1 identifies three logical/interface properties:
   - IPL: input prime-strip link,
   - SHE: simultaneous holomorphic expressibility,
   - APT: algorithmic parallel transport.
4. The paper explicitly warns that APT is not merely a set-theoretic map carrying one region into another.
5. Holomorphic hulls are introduced because raw possible images are not directly comparable with the line-bundle objects defining the q-pilot.
6. The determinant / tensor-power / normalization layer is nontrivial.
7. Log-volume removes or compresses certain indeterminacies into scalar information.

## Load-bearing transition

Step (xi-d) produces comparable scalar objects:

\[
\mathbb R_{\le -|\log\Theta|}
\qquad\text{and}\qquad
-|\log q|.
\]

Step (xi-e) states that the possible output log-volumes are linked/related to the fixed q-pilot input log-volume.

Step (xi-f) then concludes

\[
-|\log q|\in\mathbb R_{\le -|\log\Theta|},
\]

and therefore

\[
-|\log q|\le -|\log\Theta|.
\]

## Audit conclusion

The final inequality follows immediately **if the membership statement is established**.

The audit did not locate, in the exposed theorem interface of IUT III, an explicit general lemma of the form

\[
\text{IPL}+\text{SHE}+\text{APT}
\Longrightarrow
\text{q-pilot witness is realized in the transported/hulled theta-output family}.
\]

Structural relatedness, simultaneous definability, and functoriality do not imply such membership as a matter of abstract logic. Therefore a representation-neutral reconstruction must identify an additional witness-preservation/containment theorem.

A sufficient form would be something like

\[
Q_{\rm pilot}
\preceq
\operatorname{Hull}(T(\Theta_{\rm pilot}))
\]

inside the common comparison representation, after the required determinant and normalization operations.

Monotonicity of log-volume would then yield Corollary 3.12 immediately.

## Important limitation

This is **not** enough to declare a gap in the whole IUT literature. Theorem 3.11 itself delegates much of its content to definitions and earlier papers. The missing witness statement could be encoded in upstream results from the mono-theta, absolute anabelian, Frobenioid, Kummer, or log-shell machinery. That must be checked explicitly.

## Why the \(j^2\) normalization matters

IUT IV's explicit estimate sets the local parameter using the valuation of \(q_{v_j}^{j^2}\), and subsequent weighted averages retain a negative term proportional to \(j^2\log(q)\). Therefore any witness-preservation theorem used to justify Corollary 3.12 must be compatible with the normalization data required by this later calculation.

## KTG translation

Let

\[
T(\Theta)
\]

be the transported theta-output family, \(H\) the hull, and \(\Phi\) the log-volume observable. Then Corollary 3.12 has the safe abstract form

\[
W:\quad Q\preceq H(T(\Theta)),
\]

\[
\Phi(Q)\le \Phi(H(T(\Theta))).
\]

The second line is monotonicity. The first line is the load-bearing witness theorem.
