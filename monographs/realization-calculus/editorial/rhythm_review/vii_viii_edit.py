from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from vii_viii_scan import ROOT,OUT,FILES,spans
C=json.loads((OUT/'vii_viii_candidates.json').read_text())
Q=[c for c in C if '/traditional/monograph_atlas' not in c['file'] and '/traditional/atlas_sources/' not in c['file'] and 'semicolon' in c['types']]
EDITS=[]
def change(f,old,new,reason):
 s=(ROOT/f).read_text();n=s.count(old)
 assert n==1,(f,n,old)
 (ROOT/f).write_text(s.replace(old,new))
 EDITS.append({'file':f,'old':old,'new':new,'rationale':reason})
def semi(i,*pairs):
 c=Q[i];old=c['text'];new=old
 for a,b in pairs:
  assert a in new,(i,a)
  new=new.replace(a,b,1)
 change(c['file'],old,new,'Replace an ordinary prose semicolon with a sentence break or conjunction after contextual review.')
M={
0:[('; no GPU','. No GPU')],
1:[('; setup',', while setup')],
2:[('; $\\iota',', and $\\iota')],
3:[('The dense-to-block storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\\ge1$:', 'The following factor describes the dense-to-block storage reduction and, when $q\\ge1$, the arithmetic reduction:')],
4:[('the ideal dense storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\\ge1$:', 'the following factor describes the ideal dense storage reduction and, when $q\\ge1$, the arithmetic reduction:')],
5:[('; tail singular','. Tail singular')],
6:[('; the action','. The action')],
7:[('; correctness errors','. Correctness errors')],
8:[('; compressed and','. Compressed and'),('; they are','. They are')],
9:[('; scope and','. Scope and')],
10:[('; it cannot','. It cannot')],
12:[('; the coordinate',', and the coordinate')],
16:[('; every other',', and every other')],
19:[('; optimality','. Optimality')],
21:[('; retained and','. Retained and')],
24:[('; the sum estimate','. The sum estimate')],
26:[('; the inverse',', and the inverse')],
27:[('; it does not','. It does not')],
29:[('; the right version','. The right version')],
30:[('; the formulas',', while the formulas')],
31:[('; $k\\geq d$',', while $k\\geq d$')],
32:[('; this permits','. This permits')],
33:[('; splitting',', while splitting')],
34:[('; splitting',', while splitting')],
35:[('; adding','. Adding')],
36:[('; it is not','. It is not')],
37:[('; \\code{mergeCount_add_one}',', and \\code{mergeCount_add_one}'),('; arbitrary-precision','. Arbitrary-precision')],
38:[('; when both','. When both')],
39:[('; a hardware','. A hardware')],
40:[('; the source','. The source')],
41:[('; the library',', and the library'),('; it does not','. It does not')],
42:[('; the finite sum','. The finite sum')],
43:[('; a zero-power','. A zero-power')],
44:[('; positivity and','. Positivity and')],
45:[('; positive definiteness',', and positive definiteness'),('; it does not','. It does not')],
46:[('; simultaneous spectral','. Simultaneous spectral')],
47:[('; a nonzero',', while a nonzero')],
48:[('; it does not','. It does not')],
49:[('; finite dimensionality',', and finite dimensionality')],
50:[('; it does not','. It does not')],
51:[('; sources','. Sources')],
52:[('; unequal','. Unequal')],
53:[('; another','. Another')],
54:[('; it does not','. It does not')],
55:[('; the budget','. The budget')],
56:[('; the minimum','. The minimum')],
57:[('; an empty edge',', while an empty edge')],
58:[('; the proof','. The proof')],
59:[('; it is not','. It is not')],
60:[('; noninteractive','. Noninteractive')],
61:[('; the largest','. The largest')],
63:[('; noninteractive','. Noninteractive')],
64:[('; the ordered-SVD-data','. The ordered-SVD-data')],
65:[('; rectangular shapes','. Rectangular shapes')],
66:[('; multiplication',', but multiplication')],
67:[('; it adds','. It adds')],
68:[('; a bare matrix','. A bare matrix')],
69:[('; \\code{simp only}',', while \\code{simp only}')],
70:[('; it does not','. It does not')],
71:[('; the compiler','. The compiler')],
72:[('; the static checks','. The static checks')],
73:[('; the procedure','. The procedure')],
74:[('; tests and','. Tests and')],
75:[('; the sixth ledger','. The sixth ledger')],
76:[('; a corrected theorem','. A corrected theorem')],
77:[('; it is neither','. It is neither')],
78:[('; a diagonal block','. A diagonal block')],
79:[('; \\code{ring}',', and \\code{ring}')],
80:[('; sparse index','. Sparse index')],
81:[('; this endpoint','. This endpoint')],
82:[('; the subsequent','. The subsequent')],
83:[('; reconstruction',', and reconstruction')],
84:[('; their address','. Their address')],
85:[('; the final theorem','. The final theorem')],
86:[('; \\code{compactQ A}', '. \\code{compactQ A}')],
87:[('; it is not','. It is not')],
88:[('; its cardinality','. Its cardinality')],
89:[('; the prefix embedding','. The prefix embedding')],
90:[('; it does not','. It does not')],
91:[('; the tail indicator','. The tail indicator')],
92:[('; the successor index',', and the successor index'),('; \\code{tensorApply}', '. \\code{tensorApply}')],
93:[('; terms in','. Terms in'),('; \\code{r 0}',', and \\code{r 0}')],
94:[('; an FFT algorithm','. An FFT algorithm')],
95:[('; they do not','. They do not')],
96:[('; they are counted','. They are counted')],
97:[('; the teaching chapters','. The teaching chapters')],
98:[('; they are not','. They are not')],
99:[('; complex examples',', while complex examples')],
100:[('; keeping both',', while keeping both')],
101:[('; one is not','. One is not')],
102:[('; the additive recompression',', while the additive recompression')],
103:[('; the norm and','. The norm and')],
104:[('; its meaningful size','. Its meaningful size')],
105:[('; columns zero','. Columns zero')],
106:[('; they are not','. They are not')],
107:[('; it cannot','. It cannot')],
108:[('; splitting it','. Splitting it')],
109:[('; that can','. That can')],
111:[('; these are','. These are')],
112:[('; this two-column','. This two-column')],
113:[('; its first integer','. Its first integer')],
114:[('; it does not','. It does not')],
115:[('; it need not','. It need not')],
}
for i,pairs in M.items():semi(i,*pairs)
# Duplicate plate bodies are rendered in both the traditional and visual editions.
for chapter in ['VIII']:
 for name in ['pages.tex','extended_pages.tex']:
  src=f'source_v_viii/{chapter}/editable/visual_guide/source/{name}'
  dst=f'source_v_viii/{chapter}/editable/traditional/atlas_sources/{name}'
  old=(ROOT/dst).read_text();new=(ROOT/src).read_text()
  if old!=new:
   (ROOT/dst).write_text(new)
   for e in [x for x in EDITS if x['file']==src]:EDITS.append({**e,'file':dst,'rationale':'Synchronize duplicate plate prose. '+e['rationale']})
(OUT/'vii_viii_journal.json').write_text(json.dumps(EDITS,indent=2)+'\n')
print('edits',len(EDITS),'files',len({e['file'] for e in EDITS}))
