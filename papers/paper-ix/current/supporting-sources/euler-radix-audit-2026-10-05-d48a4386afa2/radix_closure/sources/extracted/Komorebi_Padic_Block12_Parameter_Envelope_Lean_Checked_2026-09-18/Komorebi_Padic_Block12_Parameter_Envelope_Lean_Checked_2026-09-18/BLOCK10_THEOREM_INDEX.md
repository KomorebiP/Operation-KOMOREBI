# Block 10 theorem index

Block 10 adds an exact quotient-block evaluation of the full representative budget. All 142 theorem statements inherited from Block 09 are preserved unchanged.

## New definitions and structure

| Declaration | Role |
|---|---|
| `radixRepresentativeBudgetQRClosedForm` | Endpoint quotient/remainder form. |
| `lastRadixBlockQuotient` | `d = (B - 1) / p`. |
| `lastRadixBlockRemainder` | `s = (B - 1) % p`. |
| `radixRepresentativeBudgetLastBlockForm` | Final-block formula using `choose d 2`. |
| `radixRepresentativeBudgetClosedForm` | Arithmetic formula without a finite sum or binomial coefficient. |
| `maximumLayerCompilerClosedBudgetBound` | Closed parameter-sensitive compiler envelope. |
| `MaximumLayerCompilerClosedFormCertificate` | Proof-carrying extension of the Block 09 complexity certificate. |
| `maximumLayerCompilerClosedFormCertificate` | Constructor under prime base and positive precision. |

## New theorems

1. `radixRepresentativeBudget_succ`  
   Appending endpoint `B + 1` adds exactly `B / p + 1`.

2. `radixRepresentativeBudget_eq_qrClosedForm`  
   Exact endpoint quotient/remainder evaluation, valid for all natural bases.

3. `radixRepresentativeBudget_eq_lastBlockForm`  
   Converts the endpoint form to the final radix-block form.

4. `radixRepresentativeBudget_eq_closedForm`  
   Removes `choose d 2` and proves the arithmetic formula.

5. `radixRepresentativeBudget_eq_closedForm_explicit`  
   Definition-free statement with `d = (B - 1) / p` and `s = (B - 1) % p`.

6. `radixRepresentativeBudget_zero_endpoint`  
   Proves `R(p,0)=0`.

7. `radixRepresentativeBudget_zero_base`  
   Proves the totalized identity `R(0,B)=B`.

8. `radixRepresentativeBudget_one_base`  
   Proves `R(1,B)=B(B+1)/2`.

9. `maximumLayerCompilerBudgetBound_eq_closedBudgetBound`  
   Shows that the Block 09 finite-sum envelope equals the Block 10 closed envelope.

10. `maximumLayerCompilerTotalTests_le_closedBudgetBound`  
    Transfers the Block 09 total-cost theorem to the closed formula.

## Preservation audit

```text
Predecessor theorem statements  142
Changed statements                0
Missing statements                0
New theorem statements           10
Total theorem statements        152
```
