# Strengthening audit

## Decision

Paper III required revision. Paper IV was not started during this pass.

The earlier manuscript had a sound central direction, but several hypotheses were missing or stated too broadly. One filtered lifting definition was not well defined under the assumptions then printed. The finite transport section also shifted between varying fibers and literal identity edge maps without first fixing frames. Those points were corrected before the paper was treated as complete.

## Corrections made

### 1. Standing analytic hypotheses

The manuscript now states that packet projectors and coarsening maps are bounded whenever norms or Fréchet derivatives are used. Operator valued differentiability is taken in operator norm.

### 2. Taylor remainder

The packet Taylor formula now assumes continuous differentiability through order one beyond the truncation order on a neighborhood of the relevant line segment. The remainder is written as a Bochner integral.

### 3. Polynomial tree convergence

The rooted tree proof now defines finite height tree sets, identifies them with Picard iterates, and constructs a nonnegative scalar tree majorant. This makes absolute convergence explicit rather than relying on an informal tree count.

### 4. Catalan edge cases

The quadratic corollary now treats zero source norm and zero bilinear norm separately before using the positive root of the scalar majorant equation.

### 5. Packet labels on arbitrary multilinear trees

The tree reconstruction proof now inserts packet identities directly at each multilinear vertex. It no longer cites a derivative theorem for maps that need not arise as derivatives.

### 6. Refinement notation

The multilevel coarsening identity now defines the zero length composition as the identity map.

### 7. Nonlinear correction

The correction operator is now stated to be bounded and linear. The proof also verifies that the selected right inverse range is closed.

### 8. Local Lyapunov Schmidt reduction

The reduction map is now local. Its domain and target are neighborhoods rather than the whole kernel and complement. The restricted derivative is required to be a Banach space isomorphism.

### 9. Quadratic reduced obstruction

The quadratic formula now assumes at least second order differentiability.

### 10. Filtered congruence preservation

The nonlinear map is now required to preserve filtration congruences. This makes the condition on a depth class independent of its representative.

### 11. Associated graded correction map

Each depth correction map is now a module homomorphism and is required to preserve the next filtration level. The induced associated graded map is therefore well defined.

### 12. Correction classes

The solution set at one depth is stated as a coset of the kernel. It is called an affine space only when the graded pieces are vector spaces.

### 13. Lift tree

Vertices are now congruence classes rather than arbitrary representatives. A new lemma proves representative independence and identifies children with associated graded correction classes.

### 14. Complete filtered lifting

The inverse limit proof now uses completeness, continuity, the closedness of filtration submodules, and separatedness explicitly.

### 15. Spectral sequence interpretation

The first page is described as graded cohomology in general and as graded obstruction candidates only when the filtered complex is a correction or deformation complex.

### 16. Finite transport fibers

The graph section now fixes one model fiber at every vertex, or equivalently requires frames on separate isomorphic fibers. Only after this choice does it make sense to normalize tree edge matrices to the identity.

### 17. Gauge classification

The intrinsic classification is now

\[
\operatorname{Hom}(\pi_1(\Gamma,r),G)/G.
\]

The tuple description appears only after a spanning tree and a free basis are chosen. The theorem also states that both transports and gauges take values in the selected structure group.

### 18. Smooth projector regularity

Moving packet projectors are now differentiable in operator norm. The convergence theorem assumes two continuous operator norm derivatives where a second order local estimate is required.

### 19. Direct packet rotation

The proof now gives an explicit positive lower bound for the overlap blocks and uses both sides of the polar decomposition to establish invertibility.

### 20. Discrete to continuous convergence

A new one step lemma proves

\[
\mathcal U(\mathcal P(t+h),\mathcal P(t))
=
I+hK(t)+O(h^2)
\]

uniformly on compact time intervals. A telescoping product comparison then gives operator norm convergence with a global first order mesh bound.

### 21. Page flow

The final classical curvature proof now closes on the same page. The scope discussion was regrouped so that the last article page and bibliography do not contain an isolated proof symbol or a nearly empty terminal page.

## Result

The strengthened article has 40 pages, 69 proofs, 116 unique labels, and 15 cited bibliography entries. The strongest revised sections are filtered lifting, relative obstruction, finite holonomy, and smooth packet transport.
