"""Build the auditable statement/assumption/evidence register from curated inputs.

Dependency entries are a reviewed principal map, not kernel-extracted proof terms.
Related test suites provide finite examples, not execution of general proofs.
"""
from pathlib import Path
import ast, hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
GROUPS=[(1,13,'Realization and predictive closure','checks/exact_foundation_checks.py'),
(14,25,'Learning and stability','checks/learning_stability_checks.py'),
(26,37,'Controlled stochastic realization','checks/controlled_stochastic_checks.py'),
(38,49,'Probability-domain certificates','checks/certified_domain_checks.py'),
(50,61,'Curved domains and continuous observations','checks/curved_continuous_checks.py'),
(62,70,'Discovery, approximation and evidence','checks/discovery_evidence_checks.py'),
(71,79,'Robust curved certificates','checks/robust_curved_checks.py'),
(80,87,'Data-supported domains','checks/data_supported_checks.py')]
# References describe implemented sectors and are not equivalence claims.
BINDINGS={
14:('observable_reference','learn_delay','Exact finite delay learner under supplied closure and span assumptions'),
15:('observable_reference','fit_closed_span','Exact sampled-span interpolation and kernel compatibility'),
16:('stochastic_reference','noisy_core_bound','Related finite fixed-core perturbation bound, not a general noisy-coordinate learner'),
25:('observable_reference','learn_delay','Autonomous finite example only'),
28:('stochastic_reference','fit_core','Population-table reconstruction with declared full-rank coverage'),
32:('stochastic_reference','finite_subspace_report','Finite matrix singular-subspace report'),
33:('stochastic_reference','noisy_core_bound','Fixed-core perturbation calculation'),
39:('cone_reference','verify_certificate','Exact supplied finite-generator witness replay'),
40:('cone_reference','verify_certificate','Vertex witnesses replayed separately in the related suite'),
41:('cone_reference','minimum_mixture_repair','Explicit simplicial mixture sector, not general convex fitting'),
45:('cone_reference','search_interval','Bounded two-coordinate interval search, not the general enumerator'),
49:('cone_reference','verify_certificate','Deterministic witness portion; statistical assumptions are external'),
50:('continuous_reference','verify_certificate','Supplied symmetric-matrix/congruence witness sector'),
51:('continuous_reference','verify_certificate','Exact two-by-two matrix embedding example'),
52:('continuous_reference','VerifiedInstrument','Finite polynomial reference class only'),
53:('continuous_reference','verify_certificate','Sufficient polynomial positivity certificate replay'),
54:('continuous_reference','fit_population_moments','Exact event/moment tables with supplied rank and degree'),
60:('continuous_reference','recognize_template','Fixed-template recognition, not geometry discovery'),
61:('continuous_reference','fit_population_moments','Worked continuous polynomial sector only'),
62:('quadratic_reference','verify_quadratic','Exact oriented quadratic witness'),
63:('quadratic_reference','discover_quadratic','Restricted invariant-form/rank-one-image discovery'),
64:('sequential_reference','positive_coefficients','Positive approximation in a finite symbolic example'),
65:('sequential_reference','reconstruct_bernstein','Finite coefficient reconstruction; no unknown-basis learner'),
66:('sequential_reference','anytime_radius','Declared elementary time-uniform radius'),
68:('sequential_reference','dependent_example','One seeded conditional-mismatch illustration'),
71:('robust_reference','replay_certificate','Uniform margin certificate and uncertainty-budget check'),
73:('robust_reference','make_certificate','Explicit center-reset repair witness construction'),
74:('robust_reference','propose_geometry','Numerical proposal only; not the theorem\'s unknown true-metric assumptions'),
75:('robust_reference','replay_polynomial','Exact complete tensor-Bernstein subdivision replay'),
76:('robust_reference','replay_certificate','Coefficient-box inclusion in declared coordinates'),
77:('robust_reference','make_certificate','Finite candidate construction; no complete general search implemented'),
78:('robust_reference','replay_certificate','Deterministic set certificate only, not upstream statistical coverage'),
79:('robust_reference','replay_certificate','Nominal and comparison-domain witnesses for one deterministic example'),
80:('robust_reference','replay_certificate','Upper certificate; exact lower separator is in the related suite'),
81:('data_certificate_reference','radius','Scalar specialization only, not general vector online regression'),
82:('data_certificate_reference','sufficient_statistics','Observable scalar specialization; general matrix learner not implemented'),
83:('data_certificate_reference','probability_row','Fixed two-parameter family and five-node measure'),
84:('data_certificate_reference','confidence_box','Exact rational scalar intervals and outward rounding'),
85:('data_certificate_reference','make_certificate','Finite parameter rectangle and declared measure constants'),
87:('data_certificate_reference','replay_certificate','Data fingerprint, statistics, radii and whole-rectangle validity; assumptions not inferred')}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def spans(text): return {int(m.group(1)):m for m in re.finditer(r'\*\*Proposition (\d+)\..*?\\square\$',text,re.S)}
def main():
    text=(ROOT/'theory/FOUNDATIONS.md').read_text(encoding='utf-8')
    old=(ROOT/'provenance/0.8.0/FOUNDATIONS.md').read_text(encoding='utf-8')
    current=spans(text); before=spans(old)
    sections=list(re.finditer(r'^# (\d+)\. (.+)$',text,re.M))
    entries=[]
    for line in (ROOT/'theory/register_spec.txt').read_text().splitlines():
        number,kind,deps,assumptions,boundary=line.split('|'); i=int(number); m=current[i]
        title=re.match(r'\*\*Proposition \d+\. (.*?)\*\*',m.group(0),re.S).group(1).strip().rstrip('.')
        sec=[s for s in sections if s.start()<m.start()][-1]
        lo,hi,group,suite=next(g for g in GROUPS if g[0]<=i<=g[1])
        row={'id':i,'title':title,'kind':kind,'part':group,
             'source':'theory/FOUNDATIONS.md','section':int(sec.group(1)),
             'section_title':sec.group(2),'context_start_line':text.count('\n',0,sec.start())+1,
             'statement_start_line':text.count('\n',0,m.start())+1,
             'proof_end_line':text.count('\n',0,m.end())+1,
             'statement_proof_sha256':hashlib.sha256(m.group(0).encode()).hexdigest(),
             'predecessor_statement_proof_sha256':hashlib.sha256(before[i].group(0).encode()).hexdigest(),
             'changed_from_080':m.group(0)!=before[i].group(0),
             'principal_internal_dependencies':[int(x) for x in deps.split(',') if x],
             'required_assumptions':assumptions,'does_not_establish':boundary,
             'proof_status':'Written proof; inherited 0.9.0 editorial review and unchanged 1.0 span. No proof kernel or independent reviewer.',
             'related_suite':{'path':suite,'sha256':digest(ROOT/suite),
                    'scope':'Block-level finite examples and controls. Not a theorem-by-theorem formal verification.'},
             'implementation':None}
        if i in BINDINGS:
            mod,symbol,scope=BINDINGS[i]; path=ROOT/'checks'/f'{mod}.py'; tree=ast.parse(path.read_text())
            node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==symbol)
            row['implementation']={'path':path.relative_to(ROOT).as_posix(),'symbol':symbol,
                'start_line':node.lineno,'end_line':node.end_lineno,'sha256':digest(path),'scope':scope}
        entries.append(row)
    register={'version':'1.0.0','source_sha256':digest(ROOT/'theory/FOUNDATIONS.md'),
        'proposition_count':87,'new_propositions':0,'proof_kernel_verified':False,
        'independent_external_review':False,
        'dependency_semantics':'Curated principal internal dependencies, not a complete formal proof graph. Standard background is identified in the manuscript.',
        'evidence_semantics':'Statement hashes prove identity only. Test records validate finite cases. Implementation links specify a restricted sector.',
        'entries':entries}
    (ROOT/'PROOF_REGISTER.json').write_text(json.dumps(register,indent=2)+'\n')
    out=['# Proof, assumptions and evidence register','',
         '**Foundations 1.0.0. Frozen scope: 87 propositions. No new numbered results.**','',
         'This register records the source location, principal internal dependencies, necessary inputs and strongest claim boundary for each proposition. Code links identify a reference implementation or finite illustration, not an executable general proof. All general proofs remain written arguments in the cumulative volume. No Lean kernel or independent external referee was used.','',
         'Read the entire indicated section before applying a proposition. Assumptions can precede its bold statement. The dependency map is curated rather than extracted from formal proof terms. In particular, Proposition 9 uses Proposition 12, a forward reference in the presentation. The map is acyclic.','',
         'All 87 statement-and-proof spans are byte-identical to the immediate 0.9.0 predecessor. The earlier P72 dimension clarification is retained. Relative to preserved 0.8.0, exactly that one correction remains. The release-freeze checker verifies the immediate predecessor separately.','',
         'The machine-readable JSON contains full source and code hashes. Hashes identify artifacts; they do not establish truth. The manuscript retains primary-source attribution for the classical ingredients.','']
    for lo,hi,name,suite in GROUPS:
        out += ['\\newpage',f'# {name}',f'Propositions {lo}–{hi}. Related finite suite: `{suite}`.','']
        for row in entries:
            if not lo<=row['id']<=hi: continue
            i=row['id']; deps=', '.join('P'+str(x) for x in row['principal_internal_dependencies']) or 'No principal internal prerequisite recorded'
            out += [r'\Needspace{9\baselineskip}',f"## P{i}. {row['title']}",'',
            f"**Location and role.** Section {row['section']}, source lines {row['context_start_line']}–{row['proof_end_line']}. {row['kind'].capitalize()}. Principal dependencies: {deps}.",'',
            f"**Requires.** {row['required_assumptions']}",'',f"**Boundary.** {row['does_not_establish']}",'']
            impl=row['implementation']
            if impl:
                out += [f"**Code link.** `{impl['path']}`, `{impl['symbol']}`, lines {impl['start_line']}–{impl['end_line']}. {impl['scope']}.",'']
            else:
                out += ['**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.','']
            if i==72: out+=['**Correction.** The mass-only case has no nonzero mass-preserving perturbation. The added dimension hypothesis excludes that case. The inherited exact regression checks cover both sides of this boundary.','']
    (ROOT/'theory/PROOF_REGISTER.md').write_text('\n'.join(out)+'\n')
    (ROOT/'PROOF_REGISTER.md').write_text('\n'.join(out)+'\n')
    print('Built 87-row proof register with',sum(x['implementation'] is not None for x in entries),'restricted implementation links.')
if __name__=='__main__':main()
