# Claim ledger — ABC sliding-window / two-axis sieve

| ID | Statement | Class | Evidence | Open dependencies |
|---|---|---|---|---|
| ORD-TAIL | `sum_{p>Y} log p/((p-1)ord_p(q)) = O_q(Y^-1/2)` | Unconditional | Group primes by order, Chebyshev | None |
| PRIME-POWER-BUDGET | `sum_{p^e<=X,e>=2} log p = O(sqrt X)` | Unconditional | Chebyshev, elementary sum | None |
| EXPONENT-WINDOW | Uniform weighted bound `O_q(Y^-1/2+sqrt X/F)` over all length-F exponent windows | Unconditional | Order lifting and preceding lemmas | None |
| EXPONENT-SPARSITY | Exceptional exponents for ordinary squares `F^alpha<p<=F^beta` are `O(F^(1-alpha/2)+F^beta)/log F` | Unconditional | Markov with minimum log p | None |
| MULTIPLIER-WINDOW | Uniform weighted bound `O(Y^-1+sqrt X/H)` for **all** prime-power layers including Wieferich | Unconditional | Unique multiplier class mod p^e, Chebyshev | None |
| RECTANGLE | Two-axis ordinary average bounded by min of two direction bounds | Unconditional | Average either theorem | None |
| PRIME-MULTIPLIER-AVERAGE | Uniform `O_delta(1/Y)` weighted estimate among prime h<=H, for all output p^e<=H^(1-delta) including Wieferich | Unconditional from established Brun–Titchmarsh | Unique reduced residue for h, Brun–Titchmarsh, Chebyshev | Not pointwise |
| PRIME-MULTIPLIER-SPARSITY | At most `O_delta(pi(H)/(Y log Y))` prime multipliers with any large repeated p-power below cutoff | Unconditional | Markov on the weighted average | Not pointwise |
| MANY-EXPONENTS | For any F selected exponents, at most `O_delta(F*pi(H)/(Y log Y))` prime multipliers exhibit some selected event | Unconditional | Union bound | Requires F small relative to Y logY to be nontrivial |
| CRT-EXCEPTION | Given q,f,P, infinitely many prime h realize all p^2 simultaneously | Unconditional | CRT, Dirichlet | None |
| EXPLICIT-FIVE | `1+1452595321237*3^23` contains squares of 5,7,17,19,23 | Exact finite computation | Deterministic 64-bit primality and multiplication in script | None |
| ABC-HEIGHT | `c<<_eps rad(abc)^(1+eps)` for all primitive triples | OPEN | No current proof | Pointwise global height vs radical |
| LEAN | Machine-checked theorems | NOT CHECKED | Standard library Python only | Lean runtime / formalization |

The new sieve estimates are not claims of historical priority; they may be elementary specializations of familiar sieve methods. They are not a proof of ABC.
