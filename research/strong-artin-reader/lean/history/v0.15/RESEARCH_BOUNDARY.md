# Research boundary after Strong Artin Lean v0.15

## Closed internally

The abstract passage from a one-prime detection theorem to a complete finite auxiliary set is closed.

For a finite-dimensional vector space `H`, a family of scalar local functionals, and a fixed admissibility predicate, if every nonzero active class is detected by one admissible label, then:

1. a detecting label is automatically new;
2. adding it strictly decreases the selected kernel;
3. the process terminates after at most the current active dimension;
4. from the empty set, exactly `finrank k H` labels are selected;
5. the simultaneous evaluation map is injective;
6. every selected label satisfies the arithmetic predicate.

## First open implication

The remaining task is to instantiate the interface with number-field auxiliary primes:

```text
v0.14 pre-Chebotarev datum
  -> finite Galois conjugacy class
  -> Chebotarev prime outside S
  -> actual Taylor--Wiles local Tate pairing
  -> OnePrimeSelectionInterface.
```

The finite-set iteration after that implication no longer needs further proof.

## Non-claims

v0.15 does not establish:

- Chebotarev realization of the selected datum;
- the local Taylor--Wiles tangent or dual-tangent calculation;
- residual packet occurrence;
- relative patching or a determinant-bearing carrier;
- ramified local attachment;
- solvable or unrestricted Strong Artin.
