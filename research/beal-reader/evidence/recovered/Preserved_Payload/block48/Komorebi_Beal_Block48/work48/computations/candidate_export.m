/*
Block48 candidate exporter. STATUS: UNEXECUTED; Magma is unavailable here.
Run from the parent directory of work47 and work48, e.g.
    magma work48/computations/candidate_export.m > candidate_export.stdout.txt

Uses exact PV source at e88f914c577ab6cf9a45e5cdd82c1993477fb423.
This recomputes a NEW decomposition. Its indices MUST NOT be identified with
the historical PV indices until Hecke fingerprints are matched.

Primary API references checked 2026-09-19 (handbook V2.29, 3 August 2026):
 https://magma.maths.usyd.edu.au/magma/handbook/text/1790
 HilbertCuspForms, NewSubspace, NewformDecomposition, Eigenform,
 HeckeEigenvalueField, HeckeEigenvalue.
 https://magma.maths.usyd.edu.au/magma/handbook/number_fields_and_orders
 SimpleExtension, IsIsomorphic, Integers/MaximalOrder, Basis,
 Factorisation, ResidueClassField(O,P), BasisMatrix, Norm.

The output keeps a fixed field isomorphism and a fixed residue map for an
entire form. It exports every base prime, not just the first split prime.
It does not certify the PV GP algdep input; it reports a necessary-condition
pre-filter using those imported polynomials, with auxiliary seven omitted.
*/

load "work47/source_records/pv_MagmaCode.m";
load "work47/source_records/pv_Data.txt";
SetSeed(480048);

DataWithoutSeven := [row : row in Data | row[1] ne 7];
assert #DataWithoutSeven eq #Data-1;
LevelsToExport := [<2,2>, <3,2>, <2,3>, <3,3>];
AuxiliariesToExport := [2,11,19,29,31,41,59,61,71];

for lev in LevelsToExport do
    N := 3^lev[1] * Factorisation(5*OK)[1][1]^lev[2];
    M := HilbertCuspForms(K,N);
    decomp := NewformDecomposition(NewSubspace(M));
    printf "LEVEL %o NORM %o DIMENSION %o ORBITS %o\n",
           lev, Norm(N), Dimension(M), #decomp;
    for idx in [1..#decomp] do
        f := Eigenform(decomp[idx]);
        ans := TheoremABound(f,DataWithoutSeven);
        keep := #ans eq 0 or 7 in ans;
        printf "PREFILTER %o %o KEEP7 %o EXCEPTIONS %o\n", lev, idx, keep, ans;
        if keep then
            L := HeckeEigenvalueField(decomp[idx]);
            printf "FORM %o %o COEFFICIENT_FIELD %o\n", lev, idx, L;
            if Type(L) eq FldRat then
                printf "RATIONAL_COEFFICIENT_FIELD RESIDUE_CHARACTERISTIC 7\n";
                for q in AuxiliariesToExport do
                    for fac in Factorisation(q*OK) do
                        P := fac[1];
                        assert Valuation(N,P) eq 0;
                        a := Rationals()!HeckeEigenvalue(f,P);
                        assert Denominator(a) eq 1;
                        printf "HECKE BASE_PRIME_BASIS %o NORM %o EXACT %o MOD7 %o\n",
                               BasisMatrix(P), Norm(P), a, GF(7)!a;
                    end for;
                end for;
            else
                E := SimpleExtension(L);
                iso_ok, toE := IsIsomorphic(L,E);
                assert iso_ok;
                OE := Integers(E);
                printf "ABSOLUTE_DEFINING_POLYNOMIAL %o\n", DefiningPolynomial(E);
                printf "ORIGINAL_FIELD_BASIS_IMAGES %o\n",
                       [Eltseq(toE(b)) : b in AbsoluteBasis(L)];
                printf "INTEGRAL_BASIS_IN_POWER_COORDINATES %o\n",
                       [Eltseq(E!b) : b in Basis(OE)];
                primes7 := Factorisation(7*OE);
                for lamidx in [1..#primes7] do
                    lam := primes7[lamidx][1];
                    k, red := ResidueClassField(OE,lam);
                    printf "PRIME7 %o RAMIFICATION %o BASIS %o RESIDUE_FIELD %o\n",
                           lamidx, primes7[lamidx][2], BasisMatrix(lam), k;
                    printf "RESIDUE_DEFINING_POLYNOMIAL %o\n", DefiningPolynomial(k);
                    printf "INTEGRAL_BASIS_RESIDUES %o\n",
                           [Eltseq(red(b)) : b in Basis(OE)];
                    for q in AuxiliariesToExport do
                        for fac in Factorisation(q*OK) do
                            P := fac[1];
                            assert Valuation(N,P) eq 0;
                            a := toE(L!HeckeEigenvalue(f,P));
                            assert IsIntegral(a);
                            printf "HECKE PRIME7 %o BASE_PRIME_BASIS %o NORM %o EXACT %o RESIDUE %o\n",
                                   lamidx, BasisMatrix(P), Norm(P), Eltseq(a),
                                   Eltseq(red(OE!a));
                        end for;
                    end for;
                end for;
            end if;
            printf "END_FORM %o %o\n", lev, idx;
        end if;
    end for;
    printf "END_LEVEL %o\n", lev;
end for;
