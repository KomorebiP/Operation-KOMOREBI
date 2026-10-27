# What the six views establish

These notes accompany Foundations 0.8.0 and Propositions 80--87. The figures separate a deterministic repair improvement from a different dependent-data example. They are not a benchmark report.

The first figure compares proved upper bounds for the same perturbed operator family. The next two show confidence intervals and their relation to a sufficient probability-domain constraint. Their saved data come from one seeded rational five-node Markov example, not from physical measurements and not from a repeated empirical coverage study.

The fourth view is a genuine three-dimensional curved moment cone. The fifth distinguishes prediction of a future observation from prediction of an entire record. The sixth displays probability masses under the five-node reference measure, not density values under a continuous measure.

All plots are generated from formulas or released calculation records. Their source script and data ledger are included. The mathematical proofs and exact certificate replay, not plotted samples, establish continuum or all-time claims.

\newpage

# 1. A smaller checked repair

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/41_smaller_repair.pdf}
\end{center}

The reset weight changes from $1/8$ to $1/32$. Both families are checked on the discovered domain and on the separate comparison domain. The degree-two deterministic coefficient box still has radius $1/4096$ in its declared coordinates.

The plotted quantities are upper bounds, not observed errors. The first bound becomes trivial at horizon eight. The improved bound remains below one through horizon 29. All-horizon probability validity does not imply all-horizon closeness of record laws.

\newpage

# 2. Confidence along one dependent path

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/42_confidence_intervals.pdf}
\end{center}

The feature dictionary is fixed: the previous observation and its square. Two regressions use exact conditional moment identities. The intervals are outward-rounded rational bounds from a time-uniform self-normalized theorem. The generating parameter lines are used only for separate verification, not by the learner.

The probability statement is conditional on the declared model and observation protocol. One saved seed does not estimate a coverage rate. The experiment uses exact rational transition probabilities on five nodes, not a continuous signal rounded afterward.

\newpage

# 3. The entire uncertainty set matters

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/43_confidence_geometry.pdf}
\end{center}

The diamond $|a|+|b|\leq1$ is a sufficient validity region, not a claimed maximal one. An early rectangle extends beyond it, so this particular whole-set certificate is withheld. That does not prove the fitted point or generating process invalid.

At 262,144 transitions the full outer rectangle lies inside the diamond with common density floor $31/125$. The model requires no reset correction in this separate structured example. Trying to certify only the fitted center would not cover all statistically admitted parameters.

\newpage

# 4. A curved domain with structured uncertainty

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/44_moment_cone.pdf}
\end{center}

The domain is $\bigl(\begin{smallmatrix}m&x\\x&y\end{smallmatrix}\bigr)\succeq0$ and $m-y\geq0$. On the unit-mass slice it becomes $x^2\leq y\leq1$. Every observed value $u$ gives a boundary state $(1,u,u^2)$.

The uncertain parameters alter the likelihood of each observation but preserve the same posterior ray. This structure supports a robust curved-domain certificate even though free output-coordinate perturbations could leave the cone. The wireframe illustrates the domain; the matrix and scalar inequalities specify it exactly.

\newpage

# 5. Two meanings of a long-horizon claim

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/45_prediction_horizons.pdf}
\end{center}

The full-record bound grows with length and becomes trivial at 37. The one-time marginal bound remains at most $2437/22320$, approximately $0.10919$, for all future times. It uses the common reference-component lower bound $31/125$.

The dotted curve is a finite Float64 comparison with the separately known generator. It is neither the confidence bound nor a proof of long-time convergence. Arbitrarily long records can distinguish two close models even when every one-time marginal remains close.

\newpage

# 6. A prediction with a declared probability measure

\begin{center}
\includegraphics[width=0.96\textwidth,height=0.51\textheight,keepaspectratio]{../figures/46_conditional_probabilities.pdf}
\end{center}

At the last observation $1/2$, the fitted center gives a probability at each possible next node. The bars give exact extrema over the parameter rectangle, rendered numerically. The dotted masses are the common lower reference component used by the contraction proof.

The next state after a node is observed is exactly $(1,u,u^2)$ for every parameter in the family. That agreement does not mean the probabilities of the node agree. Probability meaning, posterior state, parameter uncertainty and record prediction remain separate parts of the certificate.
