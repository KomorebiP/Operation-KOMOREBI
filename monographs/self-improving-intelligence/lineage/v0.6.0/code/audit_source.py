#!/usr/bin/env python3
"""Document inventory and cross-reference checks, not a mathematical proof checker."""
from pathlib import Path
from collections import Counter
import argparse
import json
import re

ROOT=Path(__file__).resolve().parents[1]
STEM='Self_Improving_Intelligence_v0.6.0'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'validation'/'source_audit.json')
    args=p.parse_args();text=(ROOT/f'{STEM}.tex').read_text()
    # Ignore full-line TeX comments; do not parse unrelated labels as new theorems.
    source='\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('%'))
    labels=re.findall(r'\\label\{([^}]+)\}',source)
    refs=re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}',source)
    cites=[k.strip() for block in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',source) for k in block.split(',')]
    bibs=re.findall(r'\\bibitem\{([^}]+)\}',source)
    pairs=re.findall(r'\\begin\{(theorem|proposition)\}\[([^]]+)\]\\label\{([^}]+)\}(.*?)\\end\{\1\}\s*\\begin\{proof\}(.*?)\\end\{proof\}',source,re.S)
    counts={name:len(re.findall(r'\\begin\{'+name+r'\}',source)) for name in ('theorem','proposition','proof','definition','counterexample','figure')}
    numbers={}
    aux=ROOT/'build'/f'{STEM}.aux'
    cache=ROOT/'validation'/'document_numbers.json'
    if aux.exists():
        numbers=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux.read_text()))
        cache.write_text(json.dumps(numbers,indent=2,sort_keys=True)+'\n')
    elif cache.exists():
        numbers=json.loads(cache.read_text())
    problems={
        'duplicate_labels':[k for k,v in Counter(labels).items() if v>1],
        'missing_references':sorted(set(refs)-set(labels)),
        'missing_bibliography':sorted(set(cites)-set(bibs)),
        'unused_bibliography':sorted(set(bibs)-set(cites)),
        'duplicate_bibliography':[k for k,v in Counter(bibs).items() if v>1]}
    if counts['proof']!=counts['theorem']+counts['proposition'] or len(pairs)!=counts['proof']:
        problems['proof_pairing']=['Statement and proof environment pairing differs.']
    figurefiles=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',source)
    missing_figures=[f for f in figurefiles if not (ROOT/f).is_file()]
    if missing_figures:problems['missing_figures']=missing_figures
    result={'status':'PASS' if not any(problems.values()) else 'FAIL','counts':counts,
            'formal_statements':len(pairs),'bibliography_entries':len(bibs),'issues':problems,
            'statements':[{'kind':kind,'number':numbers.get(label),'title':title,'label':label}
                          for kind,title,label,body,proof in pairs],
            'non_claim':'Checks syntax-level inventory and references, not correctness of proofs.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    index=['# Statement index','',f'## {STEM.replace("_"," ")}','',
           'Numbers refer to the canonical PDF. Each statement has a prose proof. These are not priority claims.','',
           '| Statement | Title | Assumptions / reading |','|---|---|---|']
    scopes={
      'thm:certified-quotient':'Pure total terms, valid typed equations, finite sound normalization; no complete equivalence oracle.',
      'thm:cegis-quotient':'Ordered finite grammar, persistent counterexamples, deterministic first-mismatch teacher, original AST representatives.',
      'prop:weighted-cover':'Nonnegative feasible repair weights, immutable deterministic binary observations, finite horizon.',
      'thm:weighted-streaming':'Identical repair/query/row orders, fixed weight certificate, informative binary roots, unit costs.',
      'prop:meta-chain':'Actual acquired rule, unchanged scope gate, completed comparisons and one explicitly additive cost model.',
      'prop:search-feature':'Finite feature map and exact decision labels; no hidden capacity input.',
      'thm:grammar-refinement':'Finite grammar, complete finite teacher domain, retained counterexamples and fixed candidate order.',
      'prop:prefix-capacity':'Integer counts, C at least one, 2 <= m <= 2C, arbitrary completion of unread binary reports.',
      'thm:streaming-pruning':'Checked immutable binary unit-cost scope, singleton-success repairs, same query order and exact fallback.',
      'prop:repair-cover':'Nonempty immutable support, specified repair-success sets and binary decision trees.',
      'prop:indistinguishable':'Specified full transcript laws, disjoint successful repair sets, equal prior.',
      'prop:refinement':'Complete finite transition model and a retained-label partition.',
      'thm:synthesis':'Deterministic table-defined experiments, nonempty support, finite horizon, literal tree storage.',
      'prop:selection':'Uniform assessment error over the full candidate collection.',
      'thm:transport':'Supplied bijections preserving domains, transitions, reports, repairs and costs.',
      'prop:extension':'Executable conservative embedding with bounded additional work and storage.',
      'prop:lineage':'Conditional per-attempt validity and a summable deterministic error budget.',
      'prop:amortization':'One additive resource unit and fixed expected per-use savings.',
      'thm:progress':'Finite fully observed lineage, complete attempt outcomes, separately justified progress marks.',
      'prop:ceiling':'Fixed bounded score, uniform positive gain and nondecrease on other transitions.',
      'prop:continuation':'Invariant source domain, all local operation squares and required output map.',
      'thm:cells':'One defective cell, singleton and bit queries, unique successful repair, binary literal trees.'}
    for item in result['statements']:
        index.append(f"| {item['kind'].capitalize()} {item['number'] or item['label']} | {item['title']} | {scopes.get(item['label'], 'Explicit finite-model assumptions and limits are stated in the manuscript.')} |")
    (ROOT/'STATEMENT_INDEX.md').write_text('\n'.join(index)+'\n')
    print(f"{result['status']}: {len(pairs)} paired statements/proofs; {len(bibs)} references.")
    if result['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
