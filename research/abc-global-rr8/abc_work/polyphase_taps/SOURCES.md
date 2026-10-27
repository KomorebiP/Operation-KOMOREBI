# Operation dictionary and source checks

The user's `Transfer_Block_Signal_Processing_Framework.pdf` was read directly
for its current contents. Relevant source identity:
`libfile_0fdfa9521eb0819186b62910edb82014`. Its Sections 2, 7, 14, 16, and 17
define residue subsequences x_j[m]=x[Nm+j], convolution taps, the synthesis
identity R(z)E(z)=z^(-d)I, finite-difference vanishing moments, and nested
base-N phase addresses. Its coefficient-ring caveat is retained.

Those definitions are translated explicitly in the new route notes. In
particular, ordinary decimation introduces no averaging denominator. A
normalized Fourier stage is a separate operation. Field reconstruction with
nonzero scalar taps is also distinguished from p-integral reconstruction.

As a primary expository cross-check, the relevant author-book sections of
Julius O. Smith's *Spectral Audio Signal Processing* were read on 25 October
2026: [Polyphase Decomposition](https://www.dsprelated.com/freebooks/sasp/Polyphase_Decomposition.html)
and [Perfect Reconstruction Filter Banks](https://www.dsprelated.com/freebooks/sasp/Perfect_Reconstruction_Filter_Banks.html).
They supply the same residue-component and matrix-inverse dictionary. They
do not assert an ABC or p-adic height inequality. The attempted Stanford-hosted
copies could not be fetched because access was restricted; the author-book
pages hosted by DSPRelated were available instead.

External article/book text is not copied into this package. The new arithmetic proofs are self-contained
relative to the retained RR3 common-power lifting decomposition. No broad
novelty search or historical-priority conclusion was undertaken.
