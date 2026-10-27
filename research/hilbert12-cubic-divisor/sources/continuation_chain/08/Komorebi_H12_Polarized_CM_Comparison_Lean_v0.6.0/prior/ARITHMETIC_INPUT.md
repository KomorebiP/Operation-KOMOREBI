# Fixed arithmetic comparison input

Transcribed from the retained CM/Gauss branch proof in the Library file
Komorebi_H12_ALL_MARKDOWN_2026-10-02.md,
file_id file_00000000b3f081f582f72d0414888258.
The retrieved note defines the branch before any gamma evaluation. Its name is
PROOF(20261002-154405).md, sections 1 and 5.

Let omega=exp(2 pi i/3), beta=7^(1/3) omega^2, zeta=exp(6 pi i/7).
The cubic character is:

    a        1  2      3        4        5      6
    chi(a)   1  omega  omega^2  omega^2  omega  1.

Set X=(sum_(a=1)^6 chi(a) zeta^a)/beta, so X^3=2+3omega.
Then

    nu=(X+beta/X-beta^2)/3,
    v=-beta^2 nu-2 nu^2,
    Y=(4beta^2+beta-14)v^2+(11beta-23)v-beta^2+3beta-3,
    Z=[(-2beta^2+7beta-8)v^2+(-10beta^2+11beta+17)v]/3
        +7-beta-beta^2,
    U_alg=[Y-(1+2omega)Z]/2.

The retained proof supplies the exact algebraic interpretation. The current
interval evaluator computes these formulas independently of its gamma series;
no branch or coefficient is fitted to a gamma value.
