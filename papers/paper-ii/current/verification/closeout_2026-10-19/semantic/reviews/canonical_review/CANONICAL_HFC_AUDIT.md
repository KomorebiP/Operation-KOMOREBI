# Canonical admissible Dunford values

**Verdict: proved as written.** For fixed h and T on a general complex Banach space, every supplied admissible cycle and open holomorphy domain give the same normalized genuine Dunford integral. Choosing one admissible representative therefore defines a value independent of the choice. No nonzero-space or nonempty-spectrum condition is present. This review audits the canonical deduction from the exact general-Cauchy theorem signature; the underlying Cauchy proof has its own independent review.

The nine admissibility fields specify an open domain, holomorphy of h there, inclusion of the actual spectrum, an actual finite integral cycle, trace inclusion in domain and resolvent set, winding one on the actual spectrum and winding zero outside the domain. No value, independence equation or Cauchy conclusion is a field.

The proof compares domains through V=(UA union UB) intersect resolventSet(T). This set is open and contains both actual traces. The same h is holomorphic on the union, and h(z) multiplied by the actual resolvent is Banach-valued holomorphic on V. Outside V, a point in the resolvent set must lie outside both domains, giving two zero windings. A point outside the resolvent set belongs to the actual spectrum, giving two unit windings. General Cauchy applies to this exact density and exterior equality. Applying the identical factor(2*pi*i)^(-1) proves the normalized integral equality.

`canonicalValue` takes an explicit Nonempty admissibility witness. It does not manufacture admissible cycles. Its representation and witness-independence theorems use the previously proved equality, so choice cannot silently supply the desired conclusion. The proof never chooses a spectrum point, and remains valid for the zero endomorphism space, empty spectrum, disconnected domains and an empty comparison domain. The general Cauchy signature includes an explicit empty-domain branch.

One independent strict compilation passed with source SHA e345fcbce413bb00601771caa71d358e72dcfc4614e7babd17cae4db52f042f5. The command/receipt and exact source/dependency hashes accompany this report. Semantic review is separate from that compiler result.

No gap was found in this canonical deduction. It does not assert unrestricted contour existence, equality for distinct h-functions agreeing only near the spectrum, or equality to a separate functional-calculus implementation. The next check is the final manuscript wrapper: it must provide genuine admissible data for the original rectifiable cycle and use the proved representation theorem.
