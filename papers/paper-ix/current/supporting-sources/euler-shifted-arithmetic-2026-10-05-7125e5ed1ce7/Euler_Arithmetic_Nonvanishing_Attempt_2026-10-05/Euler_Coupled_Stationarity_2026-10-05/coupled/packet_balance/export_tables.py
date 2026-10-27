from pathlib import Path
from fractions import Fraction
import json,csv
root=Path(__file__).resolve().parent
obj=json.loads((root/'packet_ledger.json').read_text())
with (root/'normalized_rational_residues.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','T','q_or_group','group','channel','residue_mod_2_to_16','normalized_valuation','certified_normalized_bits_at_exact_stationary_point'])
 for rec in obj['cases']:
  for p in rec['packets']+[{'q':g,'group':g,**val} for g,val in rec['groups'].items()]:
   for ch in ['value','half_derivative','second_derivative']:
    a=p[ch];shift=a['denominator_power_of_two'];x=int(a['raw_residue'])%(1<<(shift+16))
    w.writerow([rec['label'],rec['T'],p['q'],p['group'],ch,str(Fraction(x,1<<shift)),a['normalized_valuation'],a['stable_at_actual_stationary_point_raw_bits']-shift])
with (root/'valuation_layers.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','channel','raw_layer_valuation','normalized_layer_valuation','packet_qs','raw_layer_sum_valuation','normalized_cumulative_valuation','cumulative_zero_to_full_precision'])
 for rec in obj['cases']:
  for ch,ls in rec['layers'].items():
   shift=179 if ch=='half_derivative' else 178
   for a in ls:w.writerow([rec['label'],ch,a['raw_layer_valuation'],a['raw_layer_valuation']-shift,' '.join(map(str,a['q'])),a['layer_sum_valuation'],a['cumulative_valuation']-shift,a['cumulative_zero_to_precision']])
