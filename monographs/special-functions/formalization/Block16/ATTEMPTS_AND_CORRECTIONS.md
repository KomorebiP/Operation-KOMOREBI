# Routes and development corrections

Base `b5faff8889c48150e1fa41be11b6a3d2c47f493b`. SF-B16-NORMALIZATION targets the all-index rational identity.
Mechanism: factorial-scale the ordinary solution, cancel each binomial
summand using choose*k!*(m-k)!=m!, then use strong-induction uniqueness.
The n=1 discriminator distinguishes derivative 2qr from ordinary qr/3.
Outcome: proved. Direct normalization followed by ordinary uniqueness is
deferred, not exhausted; resume for a reverse normalized-sequence interface.
Finite output comparisons cannot prove the universal target and were not used.

SF-B16-ARRAY targets finite append semantics and conversion. Mechanism:
prove every next-step dependency lies in the stored prefix, identify the
list with ofFn of the infinite recurrence, and use mapIdx/getElem identities.
Outcome: proved, including last=0. Transfer to the existing polynomial and
analytic endpoint certificate succeeds with its original hypotheses.

Five development revisions are preserved as source/log pairs. Corrections
concerned unfolding the oddFactorial wrapper before rational casts, exposing
recursive calls to the termination checker, reducing function applications,
projection simplification under strict linters, explicit list optional-index
lemmas rather than an expanding default simp, selecting ofFn's final-element
identity explicitly and replacing deprecated dif_pos with dite_eq_left.
The first shell print encountered a Windows Unicode encoding error after
Lean had written its complete diagnostics; subsequent runs used Python UTF-8
mode. No mathematical counterexample or failed mechanism was inferred from
these implementation errors. The final source compiles with warnings as errors.

The separately preserved batch preflight accepted all four expected failures
and the positive fixture. Accepted fresh replay recompiles each fixture
separately and binds final production inputs. Diagnostics and intermediate
sources are not accepted proof evidence. No numerical fit, random experiment,
novelty claim, delegated agent or delayed mathematical run supports this block.
