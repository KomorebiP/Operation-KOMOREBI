# Language model contribution disclosure

The following disclosure appears immediately before the bibliography in the final manuscript:

> An OpenAI language model was used to help reorganize the original manuscript, test alternative theorem formulations, draft portions of the exposition, and design finite verification calculations. Its mathematical suggestions affected the packet intermediate representation, the small core recompression theorem, the product chain error bound, the quantized precision program, the exact tree compiler, the local recompilation theorem, and the separation of benchmark contracts. The author is responsible for checking every statement, proof, citation, computation, and measured claim in any submitted version. The model is not an author.

## Locations affected

- Section 2: packet intermediate representation and output contracts
- Section 5: compact small core recompression and product error propagation
- Section 8: continuous and discrete precision assignment
- Section 9: exact tree compilation, error budget compilation, and local recompilation
- Sections 10 through 12: timing scopes, fair matching, and benchmark interpretation
- Verification package: deterministic test design and source integrity checks

The disclosure is intentionally specific. It does not characterize the model contribution as grammar correction only. The human author remains responsible for independent verification and for all submission decisions.
