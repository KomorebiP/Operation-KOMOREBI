# Mathematical specification

## 1. Typed datum

A generative deformation datum is

```text
G = (T, X, pi: D -> X, Phi, R, tau, kappa, V)
```

where `D_x = pi^{-1}(x)` is the direction fiber at object `x`, `Phi` evaluates one direction, `R` is a path congruence, `tau` is a completion rule, `kappa` is a cost, and `V` is a validity predicate.

## 2. Raw forest

A length `n` path is a compatible sequence `d_1,...,d_n` with

```text
x_k = Phi(x_{k-1}, d_k),  d_k in D_{x_{k-1}}.
```

The vertices of the raw forest are paths, not endpoints. Parenthood is prefix deletion.

## 3. Quotient graph

An extension-compatible relation identifies paths while respecting admissible continuation. The quotient is generally a directed graph or category rather than a tree.

## 4. Completion

An infinite route determines a completed object only after a topology or limit rule is declared. Summable step bounds give metric convergence. Compatible finite-level systems may instead use inverse limits.

## 5. Continuous fibers

A compact metric direction fiber is represented through finite epsilon nets. If

```text
d(Phi(x,d), Phi(y,e)) <= L_k d(x,y) + M_k rho(d,e),
```

then the sampled route error satisfies

```text
e_n <= product(L_k) e_0
       + sum_j M_j epsilon_j product_{k>j}(L_k).
```

## 6. Operadic extension

Multi-input maps `Psi_r` generate rooted typed syntax trees. Relations such as associativity and commutativity quotient those trees.

## 7. Route projectors

At depth `n`, the path Hilbert space is `l2(T_n)`. A prefix defines a cylinder projector. Every parent projector is the sum of its child projectors.

## 8. Growth

Raw path counts and quotient object counts are stored separately. Weighted path partition functions converge above the branching entropy threshold under a uniform cost lower bound.

## 9. Family certificate

A family certificate contains a parameter space, an object map, parameter actions for closure directions, exact relations, and invariants. Verified closure gives an inductive proof for every finite parameter word.
