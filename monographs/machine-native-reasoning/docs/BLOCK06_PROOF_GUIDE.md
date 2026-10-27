# Block06 — fixed-recipient artifact covering

**Machine-Native Reasoning · Core 4.2 · Komorebi P. · 10 October 2026**

## 1. Which function may the sender implement?

Let X be the case space, alpha:X->H the sender's actual record, and C the artifact type. The sender is a function from `Attained alpha` to C. This subtype contains exactly records produced by at least one case. It is not a function with access to x, and it needs no arbitrary default artifact on impossible inputs.

A fixed predicate ok(x,c) means that the same artifact c succeeds for every intended recipient in case x. Define

    Common(h,c) := for every x with alpha(x)=h, ok(x,c).

`encoder_exists_iff` proves that a valid sender exists exactly when every attained h has a common artifact. Necessity uses equality of the sender's function value on equal inputs. Sufficiency selects one element of each nonempty intersection. The construction is classical and mathematical; no efficient search over an arbitrary acceptance predicate is inferred.

A pair x,y in the same information fibre with disjoint acceptable artifact sets rules out every encoder. Merely providing a successful artifact for each known case does not satisfy this condition.

## 2. The codebook minimum is proved, not supplied

For finite X, the transmitted image of any encoder is a finite set. A codebook S is a `Hits` witness when it intersects the common-artifact set for every attained record. Every valid encoder's image is such a codebook.

Conversely, from a finite hitting codebook we construct a valid encoder whose image is contained in that codebook. This gives, for every natural k, the equivalence

    exists valid f with |image f| <= k
       iff
    exists hitting S with |S| <= k.

The code defines the minimum image cardinality and the minimum hitting-codebook cardinality separately using natural-number least witnesses. Their existence follows from feasibility; neither is an assumed optimum. `minimum_image_eq_cover` proves their equality. `minimum_common_artifact` returns one valid encoder together with its exact image and proves minimality against every competing encoder and every hitting codebook.

The central result needs finite X; the finite-artifact source theorem is a specialization. Allowing an infinite ambient artifact type does not provide an effective search procedure. The finite image argument still applies because only finitely many sender records are attained. On an empty case space the minimum is zero, even when C is empty.

Codebook cardinality is not a byte count. A catalogue of one complicated artifact is not free installation. `decoded_alphabet_bound` says that a fixed installed decoder from a finite message type must have enough symbols to realize the demanded image. It does not install that decoder or assign it zero storage and runtime.

## 3. Actual recipient inputs and outcomes

`RecipientExecution.Audience` is a heterogeneous recipient family. Recipient i has its own background type B_i, output type Y_i, background map, target map and installed interpreter. Its run function receives only B_i and the common artifact C. The hidden world is not an additional run-function argument.

The result is `completed` with a value, a work counter and a peak-space counter, or `timeout`, or `malformed`. Acceptance requires all of:

- the artifact is permitted for that recipient and case;
- the installed run completes;
- its returned value equals the target;
- its reported work and peak space fit the stated limits.

These conjuncts remain inside the one acceptance predicate used by the covering theorem. The theorem neither substitutes a newly designed decoder nor changes a recipient's budget when constructing a message. The counters are stipulated execution-model values, not measured CPU instructions or a universal semantics for external programs.

The family can have arbitrary index and background types. The source's finite setting is covered without assuming all recipients use one shared background or output representation. Tighter acceptance conditions cannot create feasibility and, when both problems are feasible, cannot lower the minimum transmitted-image size. Additional sender information can preserve a previously feasible encoder with exactly its old artifact image, but obtaining that information has not been made free.

## 4. Source sensor: one bit helps two recipients without informing the sender

The case is (b,s,n), where b is a target bit, s is a sensor convention, and n is irrelevant. The sender sees y=b XOR s.

Recipient A knows s and computes y XOR s=b. Recipient B knows b and computes y XOR b=s. Both use the same Boolean message and a fixed XOR interpreter with declared work one and peak space one. Lean proves the acceptance predicate is exactly c=y for all eight worlds and both possible artifact bits.

The direct sender transmits its observed y. It is valid for both recipients, and every valid sender must use both Boolean artifact values. The minimum codebook is exactly two. Separately, two worlds with the same display and different b prove that the sender itself cannot determine b from its own record.

Changing the fixed recipient to ignore the message prevents a valid encoder on a named case. A different correct decoder existing somewhere else does not repair that installed procedure. Correct XOR output can also fail when the reported work is two but the limit is one, when peak space exceeds its limit, or when permission is absent. Timeout and malformed outcomes are rejected explicitly.

## 5. Additional exact covering examples

**Two targets and one broadcast.** With four possible pairs of independent bits and no recipient side information, the installed recipients read respectively the first and second components of one pair-valued artifact. Joint acceptance forces that artifact to equal the entire pair. The minimum codebook has four entries. No one-bit sender followed by any fixed pair-valued decoder can satisfy both. Each projection separately has a binary explanation; those are not a single common explanation.

**Overlapping acceptable sets.** Three distinguishable cases numbered 0,1,2 each accept the two artifacts other than their own number. The two-entry codebook {0,1} meets all three constraints, and every hitting codebook has at least two entries. Thus there are three sender records but the minimum artifact image has size two. The result is a covering problem, not automatically an injective encoding of records.

If the same three cases are made indistinguishable to the sender, their acceptance sets still intersect pairwise but have empty total intersection. No common encoder exists. This proves why a pairwise test cannot replace the full fibre intersection.

**Empty attainable domain.** No cases and no artifacts still admit the empty encoder and a zero-entry codebook. Demanding a total decoder on the entire nominal Boolean record type would instead be impossible. This exposes the attained-input convention directly.

## 6. What the block does not do

The general minimizer is obtained by classical least-witness reasoning. This is not a complexity bound, an efficient extracted covering solver, or a shortest-program theorem. The proof does not establish the correctness of every externally supplied acceptance predicate. Exact expected-risk certificates from earlier blocks and exact recipient acceptance have different meanings; an approximate decision is not silently turned into zero-error recovery.

The next connected source result is Core5.1: whether the information needed by a terminal artifact can be acquired by one permitted observation tree that fits both hard execution and complete stored-controller budgets. The current theorem handles the terminal artifact condition, not that acquisition synthesis.
