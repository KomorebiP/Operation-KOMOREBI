# Traditional edition correction and scope ledger

The 45-page strengthened manuscript and all six substantive supplement bodies are retained. Raw recovered sources are unchanged.

Source manuscript SHA-256: `95a90853604dc6aa13fc3d0c7c5b08f24340112ed01541ccfaf6f6f6e7b23f39`.

## Reasons for the final changes

The list groups editorial purposes. The unified diff below compares the raw original body directly with the final body before navigation anchors, so its added lines are the actual final statements. Assembly steps retained in JSON are procedural records and can contain intermediate text.

1. Empirical evidence is inherited.
2. Protocol requirement separated from incomplete archived metadata.
3. Local versus ambient packet block convention.
4. Explicit local projection and ambient inclusion types.
5. Ambient extension uses the actual local-coordinate projection.
6. IR evaluation fully typed.
7. Exact-evaluation local blocks fully typed.
8. Exact batch output includes actual codomain inclusion.
9. Model ledger: event counts and accumulation convention.
10. Equal-block ratio has positive denominator and nonzero dense work/storage.
11. Zero right-hand-side count allowed for count formulas but excluded from arithmetic ratio.
12. Positive reduction-factor denominator.
13. BDLR arithmetic reduction ratio excludes q=0.
14. Positive byte denominator.
15. Positive operation/bandwidth capacities.
16. Rate/intensity divisions have positive denominators.
17. Square-root capacity threshold domain.
18. Banded count uses positive width, exact integer factorization, w<p.
19. Positive Fourier order.
20. Positive Toeplitz order.
21. Tensor action/count boundary including empty tensor product.
22. Proof explicitly handles k=0 before k-1 expression.
23. Ordered exact SVD equations and rank endpoint convention.
24. Classical singular-tail formula includes all truncation endpoints.
25. Explicit arbitrary ambient competitor bridge and the two norms actually needed.
26. Empty DAG branch.
27. Proof handles empty DAG.
28. General powers enumerate walks, not only simple paths.
29. Reflexive inverse support reachability.
30. Schur support includes zero-length internal hidden paths.
31. Nonempty actual positive square-root condition-number model.
32. Classical CG condition number defined on nonempty space.
33. External CG convergence theorem uses exact arithmetic.
34. False generic common input-backward perturbation replaced by standard classical real product forward bound; Higham--Mary primary §4(4.1).
35. Forward certificate versus fixed linear-operator modeling.
36. Vector-specific estimate replaced by uniform operator certificate in product chain.
37. Uniform-bound proof repairs source domain mismatch.
38. Source amendment for unique continuous optimum.
39. Source amendment for clipped optimum.
40. Explicit endpoint multiplier distinction.
41. Stability concerns solved scores.
42. Cached local update assumes valid unaffected sibling caches.
43. Unit-task schedule includes empty graph.
44. Empty task schedule proof.
45. Physical timing/reuse model.
46. Nonnegative graph capture/time model.
47. Nonnegative materialization cost and reuse count.
48. Full equivalence under explicit nonnegative model.
49. Historical verifier record, fresh evidence in separate guide.
50. Historical unit records explicitly inherited.
51. Numerical prototype separated from exact support and compact range objects.
52. Empirical prose consistently says recorded/descriptive comparisons, retains every historical numeric value, and inserts precise archived-metadata/scope limits.
53. Historical GPU materialization rows identify sums of separate medians, rather than a complete-workflow timing median.

## Exact original-to-final manuscript diff

```diff
--- raw strengthened manuscript body
+++ final traditional manuscript body
@@ -30,7 +30,7 @@
 
 The central computational result concerns compilation. Suppose a finite rooted tree records candidate refinements. Each node may be kept as one representation or split into its children. If cost and error are additive across the selected leaves, the optimal pruning is found exactly by dynamic programming. A quantized error budget has a second exact dynamic program. The decision is stable when the score gap exceeds the perturbation in the local models. A change inside one subtree requires recomputation only along the ancestor chain. These results prove a restricted packet compiler. They do not solve unrestricted discovery or arbitrary device scheduling.
 
-The measured part uses a sanitized corpus collected on one recorded CPU and one NVIDIA GeForce RTX 3070 Ti Laptop GPU. The corpus contains 154 measured rows from sixteen suites. Regular equal block operators and block diagonal plus low rank operators show large gains. Recursive HODLR, Strassen multiplication, iterative refinement, a small Walsh Hadamard transform, and an attempted two stream overlap provide negative controls. These rows are retained because structure does not guarantee speed.
+The measured part uses a sanitized corpus collected on one recorded CPU and one NVIDIA GeForce RTX 3070 Ti Laptop GPU. The preserved corpus contains 154 recorded rows from sixteen suites. The timings are inherited observations; no GPU timing is rerun for this edition. Regular equal block operators and block diagonal plus low rank operators show large gains. Recursive HODLR, Strassen multiplication, iterative refinement, a small Walsh Hadamard transform, and an attempted two stream overlap provide negative controls. These rows are retained because structure does not guarantee speed.
 
 The article separates four sources of gain:
 \[
@@ -42,7 +42,7 @@
 \qquad
 \text{amortization}.
 \]
-A single speedup number can mix all four. The benchmark protocol therefore records case identity, output contract, timing scope, source precision, correctness reference, discovery time, compilation time, and reuse count.
+A single speedup number can mix all four. The benchmark protocol therefore requires case identity, output contract, timing scope, source precision, correctness reference, discovery time, compilation time, and reuse count. The archived rows do not satisfy every field of this ideal contract: source-value hashes and explicit correctness-reference fields are absent; setup, discovery, and reuse metadata are sparse. Recorded ratios are consequently descriptive comparisons under their stated scopes, rather than full-provenance fair matches.
 
 \begin{figure}[t]
 \centering
@@ -72,7 +72,7 @@
 \qquad
 n=\sum_{\alpha\in I}n_\alpha.
 \]
-The coordinate projector onto \(X_\alpha\) is denoted by \(P_\alpha\).
+The coordinate inclusion and projection are $\iota_\alpha:X_\alpha\to X$ and $\pi_\alpha:X\to X_\alpha$. The ambient coordinate projector is $P_\alpha=\iota_\alpha\pi_\alpha$.
 \end{definition}
 
 \begin{definition}[Packet operator representation]\label{def:packet_ir}
@@ -88,12 +88,12 @@
 \[
 B_{\beta\alpha}:X_\alpha\longrightarrow X_\beta.
 \]
-Its evaluation is
+Local blocks are identified with their ambient extensions by inclusion and projection. In particular, the notation $P_\beta AP_\alpha$ denotes either the ambient block or its restriction $X_\alpha\to X_\beta$ according to the displayed domain; $\iota_\beta B_{\beta\alpha}\pi_\alpha$ is the corresponding ambient extension. Its evaluation is
 \[
 \operatorname{eval}(\IR)
 =
 \sum_{(\beta,\alpha)\in E}
-\iota_\beta B_{\beta\alpha}P_\alpha,
+\iota_\beta B_{\beta\alpha}\pi_\alpha,
 \]
 where \(\iota_\beta:X_\beta\to X\) is the coordinate inclusion.
 \end{definition}
@@ -101,7 +101,7 @@
 \begin{theorem}[Exact evaluation]\label{thm:exact_evaluation}
 Let \(A\in\End(X)\). Set
 \[
-B_{\beta\alpha}=P_\beta AP_\alpha
+B_{\beta\alpha}=\pi_\beta A\iota_\alpha
 \]
 and let \(E\) contain exactly the nonzero blocks. Then
 \[
@@ -116,7 +116,7 @@
 AZ
 =
 \sum_{(\beta,\alpha)\in E}
-B_{\beta\alpha}P_\alpha Z.
+\iota_\beta B_{\beta\alpha}\pi_\alpha Z.
 \]
 \end{theorem}
 
@@ -244,7 +244,7 @@
 
 \section{Arithmetic, storage, and data movement}\label{sec:cost}
 
-We count one scalar multiplication and one scalar addition as two modeled floating point operations. These counts describe a representation. They do not predict wall time without a memory and launch model.
+We count one scalar multiplication and one scalar addition as two modeled floating point operations. These counts describe a declared event model for a representation. They do not predict wall time without a memory and launch model. A multiply--accumulate charges two scalar operations even for the first coefficient. Thin corrections accumulate into an already computed diagonal or sparse result. Index metadata, temporary workspace, launch overhead, discovery, transfer, and materialization are accounted for separately.
 
 \begin{theorem}[Dense and packet application counts]\label{thm:packet_counts}
 A dense \(n\) by \(n\) matrix applied to \(q\) right hand sides has modeled cost
@@ -280,13 +280,13 @@
 \end{proof}
 
 \begin{corollary}[Equal diagonal packets]\label{cor:equal_blocks}
-Suppose \(n\) is divided into equal diagonal packets of width \(b\). Then
+Let $p\ge1$ and $b\ge1$ be integers and $n=pb$. Suppose $n$ is divided into $p$ equal diagonal packets of width $b$. Then
 \[
 \flop_{\rm block}=2qnb,
 \qquad
 M_{\rm block}=nb.
 \]
-The dense to block reduction factor is
+The dense-to-block storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\ge1$:
 \[
 \boxed{
 \frac{n}{b}.
@@ -332,7 +332,7 @@
 \sum_\alpha n_\alpha^2+2nr
 }
 \]
-scalars. For equal packets of width \(b\), both ideal dense reduction factors equal
+scalars. For $n=pb$, with integers $p,b\ge1$, the ideal dense storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\ge1$:
 \[
 \boxed{
 \frac{n}{b+2r}.
@@ -385,7 +385,7 @@
 \end{proof}
 
 \begin{definition}[Arithmetic intensity]\label{def:intensity}
-The modeled arithmetic intensity is
+When the modeled byte traffic is strictly positive, the modeled arithmetic intensity is
 \[
 \Ical
 =
@@ -394,7 +394,7 @@
 \end{definition}
 
 \begin{theorem}[Roofline lower bound]\label{thm:roofline}
-Suppose a device sustains at most \(P\) modeled operations per second and at most \(W\) bytes per second. A computation that requires \(F\) operations and \(B\) bytes satisfies
+Suppose a device sustains at most $P>0$ modeled operations per second and at most $W>0$ bytes per second. A computation that requires \(F\) operations and \(B\) bytes satisfies
 \[
 \boxed{
 T\geq
@@ -404,7 +404,7 @@
 \right\}.
 }
 \]
-Equivalently, its work rate is at most
+For positive elapsed time and positive byte traffic, its work rate is at most
 \[
 \min\{P,W\Ical\}.
 \]
@@ -424,7 +424,7 @@
 \end{figure}
 
 \begin{corollary}[Capacity threshold]\label{cor:capacity}
-Let a device have available memory \(M\) bytes and scalar size \(s\). The matrix representation alone can fit only when
+Let a device have available memory $M\ge0$ bytes and scalar size $s>0$, and let $n\ge0$. The matrix representation alone can fit only when
 \[
 n\leq\sqrt{M/s}.
 \]
@@ -455,7 +455,7 @@
 The packet representation can store different exact local operator types. This section records the finite formulas used by several measured suites. The results concern representation and arithmetic. They do not assert that one implementation is fastest at every size.
 
 \begin{proposition}[Equal block banded count]\label{prop:block_banded_count}
-Let \(p=n/b\) equal packets have width \(b\). Suppose a block is active precisely when
+Let $p,b\ge1$ be integers, $n=pb$, and let $p=n/b$ equal packets have width $b$. Suppose a block is active precisely when
 \[
 \abs{i-j}\leq w,
 \qquad
@@ -514,7 +514,7 @@
 \end{proof}
 
 \begin{theorem}[Circulant spectral representation]\label{thm:circulant}
-Let \(c\in\CC^n\), with indices taken modulo \(n\), and define
+Let $n\ge1$ be an integer and $c\in\CC^n$, with indices taken modulo $n$, and define
 \[
 C(c)_{jk}=c_{j-k}.
 \]
@@ -561,7 +561,7 @@
 The fast Fourier transform evaluates the two transforms in \(O(n\log n)\) arithmetic for the usual composite lengths \cite{CooleyTukey1965}. This is an algorithmic factorization of the exact identity in \cref{thm:circulant}.
 
 \begin{corollary}[Toeplitz circulant embedding]\label{cor:toeplitz_embedding}
-Let \(T\in\CC^{n\times n}\) be Toeplitz, with first column
+Let $n\ge1$ be an integer and $T\in\CC^{n\times n}$ be Toeplitz, with first column
 \[
 (c_0,c_1,\ldots,c_{n-1})^T
 \]
@@ -611,7 +611,7 @@
 \end{proof}
 
 \begin{corollary}[Equal tensor factors]\label{cor:tensor_modewise}
-A product of \(k\) square factors of order \(d\), acting on a tensor with \(d^k\) entries, can be applied by \(k\) modewise contractions with modeled cost
+For integers $k,d\ge0$, a product of $k$ square factors of order $d$, acting on a tensor with $d^k$ entries, can be applied by $k$ modewise contractions, reusing intermediate slices, with modeled cost
 \[
 \boxed{
 2k d^{k+1}
@@ -621,7 +621,7 @@
 \end{corollary}
 
 \begin{proof}
-For one mode, there are \(d^{k-1}\) fibers of length \(d\). Multiplying each fiber by a \(d\) by \(d\) matrix costs \(2d^2\), so one mode costs \(2d^{k+1}\). Sum over the \(k\) modes.
+For $k=0$ there are no contractions and both modeled work and factor storage are zero. For $k\ge1$, one mode has $d^{k-1}$ fibers of length $d$. Multiplying each fiber by a \(d\) by \(d\) matrix costs \(2d^2\), so one mode costs \(2d^{k+1}\). Sum over the \(k\) modes.
 \end{proof}
 
 \begin{theorem}[Walsh Hadamard recursion]\label{thm:walsh_hadamard}
@@ -784,7 +784,7 @@
 \[
 \sigma_1\geq\sigma_2\geq\cdots,
 \]
-then its truncated singular value decomposition \(M_k\) is a best rank at most \(k\) approximation. It satisfies
+pad this finite sequence with zeros. For each integer $k\ge0$, its truncated singular value decomposition $M_k$ is a best rank-at-most-$k$ approximation. It satisfies
 \[
 \norm{M-M_k}_2=\sigma_{k+1}
 \]
@@ -821,7 +821,7 @@
 \[
 G=W\Sigma Z^*
 \]
-be a singular value decomposition. Define
+be an ordered thin singular value decomposition, with nonnegative nonincreasing singular values. For an integer $k\ge0$, retain $\min\{k,d\}$ columns, where $d$ is the number of supplied thin singular directions; tail singular values beyond $d$ are zero. Define
 \[
 L_k=Q_LW_k\Sigma_k^{1/2},
 \qquad
@@ -841,7 +841,7 @@
 =
 Q_LGQ_R^*.
 \]
-The two outer maps are isometries on their column spaces. They preserve the nonzero singular values and every unitarily invariant norm of the core. Truncating the singular value decomposition of \(G\) and applying \cref{fact:eym} gives the result. The compact QR dimensions equal the ranks of the factor column spaces.
+The two outer maps are isometries on their column spaces. They preserve the nonzero singular values and the spectral and Frobenius norms of the core. For every ambient rank-at-most-$k$ competitor $B$, its compression $Q_L^*BQ_R$ has rank at most $k$, and compression cannot increase either norm. Thus the core best-approximation inequality also lower-bounds the error of every ambient competitor. Truncating the singular value decomposition of \(G\) and applying \cref{fact:eym} gives the result. The compact QR dimensions equal the ranks of the factor column spaces.
 \end{proof}
 
 \begin{figure}[t]
@@ -952,7 +952,7 @@
 \[
 P_\gamma A^mP_\alpha
 \]
-is the sum over directed paths
+is the sum over directed walks (vertices may repeat)
 \[
 \alpha=\alpha_0
 \longrightarrow
@@ -1034,11 +1034,11 @@
 \end{proof}
 
 \begin{corollary}[Sequential depth]\label{cor:sequential_depth}
-The number of sequential stages in the level schedule equals one plus the length of the longest directed path.
+For a nonempty finite graph, the number of sequential stages in the level schedule equals one plus the length of the longest directed path. The empty graph has depth zero.
 \end{corollary}
 
 \begin{proof}
-The recursive level of a vertex is one plus the largest level of its predecessors. The largest level therefore counts the vertices on a longest path.
+The recursive level of a vertex is one plus the largest level of its predecessors. For a nonempty graph, the largest level therefore counts the vertices on a longest path. For an empty graph, no task is scheduled and the depth is zero.
 \end{proof}
 
 \begin{figure}[t]
@@ -1051,7 +1051,7 @@
 \subsection{Fill under elimination}
 
 \begin{theorem}[Inverse support lies in the transitive closure]\label{thm:inverse_support}
-Let \(A\) be an invertible packet operator. If there is no directed path from packet \(\alpha\) to packet \(\beta\) in \(G_A\), then
+Let \(A\) be an invertible packet operator. Reachability here includes a zero-length path from a packet to itself. If there is no directed path from packet \(\alpha\) to packet \(\beta\) in \(G_A\), then
 \[
 \boxed{
 P_\beta A^{-1}P_\alpha=0.
@@ -1076,7 +1076,7 @@
 -
 A_{RH}A_{HH}^{-1}A_{HR}.
 \]
-A retained block \((\beta,\alpha)\) can be active only if it was already active in \(A_{RR}\), or if there is a directed walk from \(\alpha\) through hidden packets to \(\beta\).
+A retained block $({\beta},{\alpha})$ can be active only if it was already active in $A_{RR}$, or if there is a directed walk from $\alpha$ through hidden packets to $\beta$. The internal hidden path may have length zero, so entrance and exit may use the same hidden packet.
 \end{proposition}
 
 \begin{proof}
@@ -1180,7 +1180,7 @@
 \[
 A=D+K
 \]
-be Hermitian positive definite with positive block diagonal part \(D\). Suppose
+act on a nonempty finite coordinate space and be Hermitian positive definite with positive definite block diagonal part $D$. Here $D^{-1/2}$ is the actual inverse of the positive square root of $D$. Suppose
 \[
 E=D^{-1/2}KD^{-1/2}
 \]
@@ -1207,13 +1207,13 @@
 \end{proof}
 
 \begin{standardfact}[Preconditioned conjugate gradient convergence]\label{fact:cg}
-Let \(A\) and \(M\) be Hermitian positive definite, and set
+Let $A$ and $M$ be Hermitian positive definite on a nonempty finite coordinate space, and set
 \[
 \kappa
 =
 \cond_2(M^{-1/2}AM^{-1/2}).
 \]
-The energy norm error of preconditioned conjugate gradient satisfies
+In exact arithmetic, the energy norm error of preconditioned conjugate gradient satisfies
 \[
 \norm{x_m-x_*}_A
 \leq
@@ -1306,25 +1306,34 @@
 \end{proof}
 
 \begin{standardfact}[Floating point matrix product model]\label{fact:rounding}
-Under the standard floating point model, a computed matrix product may be written as an exact product with a dimension dependent backward perturbation. The perturbation constant is controlled by the unit roundoff and the inner dimension when overflow and underflow are excluded.
+For real $A\in\RR^{m\times p}$ and $B\in\RR^{p\times n}$, consider ordinary dot-product matrix multiplication in uniform precision with unit roundoff $u$, no overflow or underflow, and $pu<1$. Its computed output $\widehat C$ satisfies the componentwise forward-error bound
+\[
+|\widehat C-AB|\le\gamma_p|A||B|,
+\qquad\gamma_p=\frac{pu}{1-pu}.
+\]
+Absolute values and the inequality are entrywise. Complex arithmetic, fused kernels, mixed accumulation, and tensor kernels require their own stated constants. This fact does not assert one common small input perturbation for every column, and an input-dependent rounded action is not automatically a fixed linear operator.
 \end{standardfact}
 
-Detailed forms and their hypotheses are given in \cite{Higham2002}. Packetwise use of this fact produces edge bounds \(\eps_e\) for \cref{thm:packet_error}.
+Detailed forms and their hypotheses are given in \cite{Higham2002,HighamMary2021}. For a fixed computed matrix, the bound can certify its error matrix. A rounded application to varying inputs needs a separately justified uniform certificate before it can be used as one fixed operator error in \cref{thm:packet_error}.
 
 \subsection{Several operators}
 
 \begin{corollary}[Mixed precision product chain]\label{cor:mixed_chain}
-If each factor \(A_j\) is replaced by a packetwise approximation \(\widehat A_j\), then the final operator error is bounded by \cref{thm:product_chain_error}. Each \(\norm{E_j}\) may in turn be bounded by the packet certificate in \cref{thm:packet_error}.
+If each fixed linear factor $A_j$ is replaced by a fixed packetwise linear approximation $\widehat A_j$, write $E_j=\widehat A_j-A_j=\sum_e\Delta_{j,e}P_{\alpha(j,e)}$. A uniform certificate is
+\[
+\|E_j\|\le\delta_j:=\sum_e\|\Delta_{j,e}\|\,\|P_{\alpha(j,e)}\|.
+\]
+For orthogonal packet projectors, $\delta_j\le\sum_e\|\Delta_{j,e}\|$. The final operator error is bounded by \cref{thm:product_chain_error} with these uniform $\delta_j$. The corresponding vector error is this operator bound multiplied by the input norm.
 \end{corollary}
 
 \begin{proof}
-Apply \cref{thm:packet_error} at every stage and substitute the resulting operator error bounds into \cref{thm:product_chain_error}.
+Take the supremum over unit inputs in \cref{thm:packet_error}, using $\|P_{\alpha}x\|\le\|P_{\alpha}\|\|x\|$. Substitute the resulting uniform operator error bounds into \cref{thm:product_chain_error}; the action estimate follows from submultiplicativity.
 \end{proof}
 
 \subsection{Continuous allocation}
 
 \begin{theorem}[Continuous precision allocation]\label{thm:continuous_precision}
-Let \(s_e>0\) be sensitivities and \(c_e>0\) be costs. Consider
+Let $E$ be a finite nonempty edge set, let $s_e>0$ be sensitivities and $c_e>0$ be costs, and let $\tau>0$. Consider
 \[
 \min_{\eps_e>0}
 \sum_e c_e\log\frac1{\eps_e}
@@ -1360,7 +1369,7 @@
 \end{proof}
 
 \begin{theorem}[Clipped precision allocation]\label{thm:clipped_precision}
-Add upper bounds
+Retain the finite nonempty edge set, strictly positive sensitivities and costs, and add strictly positive caps $m_e>0$ with upper bounds
 \[
 0<\eps_e\leq m_e.
 \]
@@ -1397,7 +1406,7 @@
 \frac{c_e}{\lambda s_e}
 \right\}
 \]
-is continuous and nonincreasing. It decreases from the maximal feasible value to zero. The constraint determines \(\lambda\). Strict convexity gives uniqueness of the minimizer.
+is continuous and nonincreasing. It decreases from the maximal feasible value to zero. For a strictly submaximal budget, once any coordinate is unsaturated, $\phi$ is strictly decreasing, which gives a unique multiplier. At maximal budget the only feasible vector is $(m_e)_e$ and every $0<\lambda\le\min_e c_e/(s_em_e)$ produces it. Thus the minimizing vector is unique at this endpoint while its multiplier need not be. Strict convexity gives uniqueness of the minimizer in every case.
 \end{proof}
 
 \begin{figure}[t]
@@ -1691,7 +1700,7 @@
 \end{definition}
 
 \begin{theorem}[Compiler stability]\label{thm:compiler_stability}
-Suppose the keep score and split score at every internal node change by less than \(g_v/2\). Then every strict keep or split decision in the original optimal pruning remains unchanged.
+Suppose the solved keep score and split score at every internal node change in absolute value by less than $g_v/2$. These are scores after child subproblems have been solved, rather than unconstrained changes in raw local costs. Then every strict keep or split decision in the original optimal pruning remains unchanged.
 \end{theorem}
 
 \begin{proof}
@@ -1699,7 +1708,7 @@
 \end{proof}
 
 \begin{theorem}[Local recompilation]\label{thm:local_recompilation}
-Suppose local costs change only inside the subtree rooted at \(u\). Then every dynamic programming value outside that subtree and outside the ancestor chain from \(u\) to the root remains unchanged. Recomputing the subtree at \(u\) and that ancestor chain gives the exact new global optimum.
+Suppose local costs change only inside the subtree rooted at $u$, while ancestor and sibling local models are unchanged. Use correct cached sibling values from the old solve. Then every dynamic programming value outside that subtree and outside the ancestor chain from \(u\) to the root remains unchanged. Recomputing the subtree at \(u\) and that ancestor chain gives the exact new global optimum.
 \end{theorem}
 
 \begin{proof}
@@ -1731,17 +1740,17 @@
 \subsection{Critical path}
 
 \begin{theorem}[Acyclic schedule depth]\label{thm:dag_depth}
-Let a packet task graph be acyclic. Assume every task takes one normalized stage, every edge is a dependency, and an unlimited number of independent tasks may run concurrently. The minimum possible number of sequential stages equals the number of vertices on a longest directed path.
-\end{theorem}
-
-\begin{proof}
-Every path gives a lower bound because its tasks must execute in order. The topological level schedule in \cref{thm:level_schedule} achieves exactly this depth.
+Let a packet task graph be acyclic. Assume every task takes one normalized stage, every edge is a dependency, and an unlimited number of independent tasks may run concurrently. For a nonempty finite graph, the minimum possible number of sequential stages equals the number of vertices on a longest directed path. The empty task graph has depth zero.
+\end{theorem}
+
+\begin{proof}
+Every path gives a lower bound because its tasks must execute in order. The topological level schedule in \cref{thm:level_schedule} achieves exactly this depth. With no tasks, the empty schedule has depth zero.
 \end{proof}
 
 \subsection{One time costs}
 
 \begin{theorem}[Amortization threshold]\label{thm:amortization}
-Let \(s\geq0\) be a one time setup cost. Let \(t_b\) be the baseline time per use and \(t_c\) the candidate time per use. If \(t_b>t_c\), the candidate is faster after \(R\) uses exactly when
+Let \(s\geq0\) be a one time setup cost. Let $t_b,t_c\ge0$ be the baseline and candidate times per use and let $R\in\NN$ be a reuse count. If \(t_b>t_c\), the candidate is faster after \(R\) uses exactly when
 \[
 R>
 \frac{s}{t_b-t_c}.
@@ -1772,7 +1781,7 @@
 \end{proof}
 
 \begin{corollary}[Graph replay threshold]\label{cor:graph_threshold}
-If graph capture costs \(c\), ordinary execution costs \(t_o\), and replay costs \(t_r<t_o\), then capture is profitable when
+If graph capture costs $c\ge0$, ordinary execution costs $t_o\ge0$, and replay costs $0\le t_r<t_o$, then capture is profitable when
 \[
 R>
 \frac{c}{t_o-t_r}.
@@ -1784,7 +1793,7 @@
 \end{proof}
 
 \begin{corollary}[Materialization threshold]\label{cor:materialization_threshold}
-Suppose a compressed representation costs \(t_c\) per downstream use, an explicit representation costs \(t_e\) per use, and one time materialization costs \(m\). Materialization is profitable only when
+Suppose a compressed representation costs $t_c\ge0$ per downstream use, an explicit representation costs $t_e\ge0$ per use, and one time materialization costs $m\ge0$, with reuse count $R\in\NN$. Materialization is profitable exactly when
 \[
 R>
 \frac{m}{t_c-t_e}
@@ -1870,6 +1879,8 @@
 \label{tab:suites}
 \end{table}
 
+The 154 archived rows contain recorded case identifiers, seeds, types, output contracts, and timing scopes. Source-value hashes and explicit correctness-reference fields are absent. Setup time, discovery time, and reuse count are nonnull in only two rows each; correctness errors are present in 149 rows. Equality of available metadata cannot establish the full fair-match relation in \cref{def:fair_match}. In particular, CPU-resident and GPU-device-resident scopes differ, and graph replay excludes capture while a device-resident baseline has a different raw scope. The two-stream example also compares wall time with a serial device-time scope. The values below are retained as historical observations with these limitations.
+
 \subsection{Dense precision frontier}
 
 At dimension \(4096\), the device resident dense rows gave the values in \cref{tab:dense_frontier}.
@@ -1918,11 +1929,11 @@
 \[
 14.8919
 \]
-times faster than the matched device resident dense GPU row and
+times faster than the recorded device resident dense GPU row with the same recorded case, output, and timing scope and
 \[
 235.7404
 \]
-times faster than the matched CPU dense row. The relative error was
+times faster than the recorded CPU dense row (resident CPU scope versus device-resident GPU scope). The relative error was
 \[
 8.17\times10^{-8}.
 \]
@@ -1942,11 +1953,11 @@
 \[
 10.9355
 \]
-times faster than the matched dense GPU row and
+times faster than the recorded dense GPU row (graph-replay scope versus device-resident scope) and
 \[
 153.6527
 \]
-times faster than the matched CPU dense row. Capture time was excluded from the replay scope and must be amortized separately.
+times faster than the recorded CPU dense row (resident CPU scope versus device-resident GPU scope). Capture time was excluded from the replay scope and must be amortized separately.
 
 \begin{figure}[t]
 \centering
@@ -1957,7 +1968,7 @@
 
 \subsection{Compressed products}
 
-A compressed BDLR product returns block and low rank factors. Materialization returns all matrix entries. The measured product rows show the cost of changing the output contract.
+A compressed BDLR product returns block and low rank factors. Materialization returns all matrix entries. The historical product rows illustrate the cost of changing the output contract; compressed and materialized outputs are separate computations. The GPU materialized BDLR rows at dimensions 512 and 1024 are sums of separately measured factor and expansion medians, as the raw notes state; they are not complete-workflow timing medians.
 
 \begin{figure}[t]
 \centering
@@ -1990,10 +2001,10 @@
 
 \subsection{Negative controls}
 
-The corpus retains methods that lost to their matched baselines.
+The corpus retains methods that lost in the recorded baseline comparisons. These are descriptive ratios; scope and complete-metadata qualifications apply.
 
 \begin{itemize}
-\item At dimension \(512\), recursive Strassen multiplication with leaf size \(128\) took \(7.0950\) ms, while the matched OpenBLAS dense multiplication took \(1.9597\) ms.
+\item At dimension \(512\), recursive Strassen multiplication with leaf size \(128\) took \(7.0950\) ms, while the recorded OpenBLAS dense multiplication took \(1.9597\) ms.
 \item At dimension \(2048\), the tested recursive HODLR GPU path took \(5.6079\) ms, while dense GPU multiplication took \(0.0860\) ms.
 \item The tested FP32 iterative refinement solve took \(22.0848\) ms, while the direct FP64 GPU solve took \(12.6286\) ms with a comparable final error.
 \item The two stream dense path was slower than the serial two product path.
@@ -2012,13 +2023,13 @@
 \begin{figure}[t]
 \centering
 \includegraphics[width=.78\textwidth]{21_best_gpu_speedups.pdf}
-\caption{The best matched gain differs strongly across suites. Regular packet structure dominates the largest measured rows.}
+\caption{The best recorded gain differs strongly across suites. Regular packet structure dominates the largest measured rows.}
 \label{fig:best_speedups}
 \end{figure}
 
 \section{Implementation and verification}\label{sec:implementation}
 
-The release contains a small reference implementation of the exact operators and optimization algorithms used in the paper. The mathematical interface is deliberately narrow.
+The release contains a small reference implementation of the exact operators and optimization algorithms used in the paper. The mathematical interface is deliberately narrow. This Python implementation is a numerical prototype, not extracted Lean code. Its stored-key support can retain zero-valued blocks, whereas the exact support graph uses nonzero blocks. Its reduced numerical QR is not the exact rank-compact range construction proved in Appendix F. Prototype tests and theorem proofs therefore have different targets.
 
 \begin{enumerate}
 \item A packet layout records dimensions and coordinate slices.
@@ -2030,7 +2041,7 @@
 \item Benchmark utilities audit case identity, output contracts, timing scopes, and retained negative controls.
 \end{enumerate}
 
-The full deterministic verifier performs \(37392\) checks in nine groups. It covers packet evaluation, adjoints, composition, structured primitives, recompression optimality, product chain error, graph support, Schur fill, tree compilation, precision assignment, and the benchmark corpus. The strengthened unit suite contains eleven passing tests. The original source suite contains twenty three passing tests for BDLR operations, Krylov methods, mixed precision, measured data schema, and figure generation.
+The strengthened release records a deterministic verifier with $37392$ checks in nine groups. It covers packet evaluation, adjoints, composition, structured primitives, recompression optimality, product chain error, graph support, Schur fill, tree compilation, precision assignment, and the benchmark corpus. The strengthened release records eleven passing unit tests and twenty three passing original-source tests for BDLR operations, Krylov methods, mixed precision, measured data schema, and figure generation.
 
 \begin{table}[t]
 \centering
@@ -2076,7 +2087,7 @@
 
 A finite candidate refinement tree supports a genuine packet compiler. The Lagrangian optimum, the quantized error budget optimum, and local recompilation are exact under additive hypotheses. This is narrower than unrestricted automatic discovery, but it turns one broad compiler conjecture into a proved algorithmic statement.
 
-The measured corpus shows the practical distinction between regular and irregular structure. Equal block and BDLR operators gained substantially on the recorded GPU. Recursive HODLR, Strassen, iterative refinement, a small transform, and an attempted overlap lost to matched baselines. Discovery, transfer, capture, and materialization changed the break even point.
+The measured corpus shows the practical distinction between regular and irregular structure. Equal block and BDLR operators gained substantially on the recorded GPU. Recursive HODLR, Strassen, iterative refinement, a small transform, and an attempted overlap lost to recorded baselines. Discovery, transfer, capture, and materialization changed the break even point.
 
 The computational principle is therefore precise. Remove work through a verified representation. Preserve the declared output. Compile only inside a model whose costs and errors are stated. Assign precision by sensitivity. Amortize one time costs. Keep negative controls. Treat the final timing as a property of the representation, device, kernel, and reuse regime together.
 
```

Supplement bodies retain every substantive paragraph and display. Only cover/scope summaries and layout commands are omitted; dated pending/audit statements are retained with explicit historical-checkpoint prefaces. Bibliography updates pin the classical forward-error source and a stable official CUDA archive.
