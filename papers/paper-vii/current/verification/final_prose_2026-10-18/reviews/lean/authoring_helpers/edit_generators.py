from pathlib import Path
import json

H=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18/editable/lean_guide')
OUT=Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_lean_prose')
changes=json.loads((OUT/'REPLACEMENTS.json').read_text())
def edit(file,before,after,category='Natural generated prose'):
    p=H/file;text=p.read_text()
    assert text.count(before)==1,(file,text.count(before),before)
    assert before!=after
    p.write_text(text.replace(before,after,1))
    changes.setdefault(file,[]).append({'before':before,'after':after,'exact_occurrences':1,'category':category})

edit('chapters/seed_packets.tex',"The preceding theorem constructs these local packets from each factor's cyclic symmetry.","The preceding theorem can construct these local packets from each factor's cyclic symmetry.",'Preserve general input scope')
edit('chapters/finite_limits.tex','Rewrite the inverse-of-invertible notation to the nonsingular matrix inverse','Rewrite the inverse supplied by the invertibility instance as the nonsingular matrix inverse')
edit('chapters/finite_limits.tex','The finite-circle dispersion expression','The dispersion expression for the finite circle')
edit('chapters/reading.tex','an abstract C-star-algebra estimate','an estimate in an abstract C-star algebra')
edit('Paper_VII_Lean_Guide_Final.tex','The following map preserves all 19 ledger scopes and resolves their current formal endpoints.','The following map reproduces all 19 ledger scope statements verbatim and resolves their current formal endpoints.','Distinguish preserved records from authored prose')

f='assemble.py'
font_old="font=TTFont(HERE/'fonts/DejaVuSansMono.ttf')\ncmap={k for t in font['cmap'].tables for k in t.cmap}\nmathfont=TTFont(HERE/'fonts/latinmodern-math.otf')"
font_new="""def matching_font(filename, family):
    bundled=HERE/'fonts'/filename
    if bundled.is_file():
        return bundled
    try:
        installed=Path(subprocess.check_output(
            ['fc-match','-f','%{file}',family],text=True).strip())
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise RuntimeError('Font lookup failed for '+family) from error
    if not installed.is_file() or installed.name!=filename:
        raise RuntimeError('Matching font file required: '+filename)
    return installed

font=TTFont(matching_font('DejaVuSansMono.ttf','DejaVu Sans Mono'))
cmap={k for t in font['cmap'].tables for k in t.cmap}
mathfont=TTFont(matching_font('latinmodern-math.otf','Latin Modern Math'))"""
edit(f,font_old,font_new,'Use exact matching installed fonts when bundled files are absent')
edit(f,"+str(record['start_line'])+'--'+str(record['end_line'])+r'; excerpt ","+str(record['start_line'])+' to '+str(record['end_line'])+r'. Excerpt ")
edit(f,"+n+'}; '+r'\\code{'","+n+'}, '+r'\\code{'")
edit(f,"+str(r['line'])+'; '+state", "+str(r['line'])+', '+state")
edit(f,'The dependencies below are read from both public imports and import-all commands. Duplicate imports count once. Import-all is significant in this Lean module edition because private implementation details can be needed by downstream proofs.','The dependencies below are read from public imports and commands of the form import all. Duplicate imports count once. Importing all declarations matters in this Lean module edition because downstream proofs can require private implementation details.')
edit(f,"('; '.join(r'\\code{'","(', '.join(r'\\code{'")
edit(f,'The following are the nine manifest packages; replay should use the locked revisions, including inherited dependencies.','The following are the nine packages in the manifest. Replay should use the locked revisions, including inherited dependencies.')
edit(f,"+str(r['start_line'])+'--'+str(r['end_line'])+'; declaration '","+str(r['start_line'])+' to '+str(r['end_line'])+'. Declaration '")

f='navigation.py'
needle="relations=next(ast.literal_eval(node.value) for node in old.body if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='relations' for v in node.targets))"
replacement=needle+"\n"+'''# Preserve the historical map while expressing the current navigation in prose.
reviewed_relations={
    'strong:theorem:001':'Item 2.1 gives the same orbit dimension result.',
    'strong:theorem:002':'Item 2.2 gives the same sharp minimum number of seeds.',
    'strong:corollary:001':'Item 2.3 relates the local orbit to reduced support.',
    'strong:proposition:001':'Item 2.4 constructs the basis by addressed local X gates.',
    'strong:corollary:002':'Item 3.1 formalizes the cyclic specialization.',
    'strong:theorem:006':'Item 3.2 formalizes finite grouping of tensor packets.',
    'strong:theorem:007':'Item 4.1 covers every finite circuit depth.',
    'strong:theorem:008':'Item 4.2 gives both operator unitarity identities.',
    'strong:corollary:005':'Item 4.2 gives the operator identity. The probability corollary is proved in the traditional text.',
    'strong:theorem:010':'Item 5.1 proves packet invariance for the exponential of a fixed generator.',
    'strong:theorem:011':'Item 5.2 gives the commutator leakage bound. The norm equality for the off-diagonal corner is proved in the traditional text.',
    'strong:theorem:012':'Item 6.3 gives the canonical connection identities along a curve.',
    'strong:theorem:014':'Item 6.1 proves the differentiated equation in moving coordinates.',
    'strong:theorem:018':'Item 6.4 gives projected manifold curvature and gauge gluing. The local formulas in orthonormal frames are proved in the traditional text.',
    'strong:corollary:008':'Item 7.1 proves trace invariance for block diagonal observables.',
    'strong:standardfact:001':'Item 7.2 proves complete positivity and trace preservation for finite Kraus channels. The Choi equivalence is proved in the traditional text.',
    'strong:theorem:026':'Item 8.1 gives the criterion for unnormalized error families and recovery on their span. The traditional text also uses a quotient formulation.',
    'strong:theorem:027':'Item 8.1 reduces general positive Gram data by spectral diagonalization.',
    'strong:theorem:028':'Item 8.1 uses one total recovery for normalized channels in the error span.',
    'strong:corollary:011':'The identities for syndrome cross errors support item 8.1. The traditional text supplies the measurement interpretation.',
    'strong:theorem:029':'Item 9.1 gives the projected resolvent with both required invertibility hypotheses.',
    'strong:theorem:030':'Item 9.1 relates invertibility of the full matrix and its Schur complement. The traditional text adds spectral and eigenvector formulations.',
    'strong:theorem:036':'Item 10.1 constructs the shifted exponential and proves its positivity and spectral bounds under the stated hypotheses.',
    'strong:theorem:039':'Item 11.1 gives the scalar bound in one dimension. The traditional text proves the summed result in d dimensions.',
    'strong:proposition:011':'ConstraintAudit formalizes finite compression to the common kernel.'}
if set(reviewed_relations)!=set(relations):
    raise RuntimeError('Historical relation inventory changed')
relations=reviewed_relations'''
edit(f,needle,replacement)
edit(f,'Additional written statement. No corresponding named endpoint in the current 25-module development.','The traditional statement has no corresponding named endpoint among the current 25 modules.')
edit(f,"'supp1':'Packet algebra, symmetry and measurements. Corrected resolvent, spacing condition, and finite constraint audit.',","'supp1':'This supplement develops packet algebra, symmetry and measurements. It states the corrected resolvent and spacing hypotheses and audits finite constraints.',")
edit(f,"'supp2':'Addressed computational seed, tensor refinement, moving coordinates, canonical connection, and Kraus amplification.',","'supp2':'This supplement constructs an addressed computational seed, tensor refinements, moving coordinates, the canonical connection and Kraus amplification.',")
edit(f,"'supp3':'Actual orbit spaces, sharp seed counts, independently defined Schmidt rank, cyclic characters, and Euclidean exponential.',","'supp3':'This supplement derives orbit spaces and sharp seed counts. It defines Schmidt rank independently and develops cyclic characters and the Euclidean exponential.',")
edit(f,"'supp4':'Actual-exponential leakage, chart projected curvature, and total orthogonal-syndrome recovery.',","'supp4':'This supplement proves leakage for the exponential, projected curvature in a chart and total recovery from orthogonal syndromes.',")
edit(f,"'supp5':'General Gram spectral reduction, actual recovery necessity, density/operator bridge, finite references, and error spans.',","'supp5':'This supplement proves spectral reduction for general Gram data, necessity from recovery, the bridge from states to operators, and correction with finite references and error spans.',")
edit(f,"'supp6':'Constructed range local products, smooth transitions, global connection, gauge law, and actual manifold curvature.'}","'supp6':'This supplement constructs local products for the range, smooth transitions and the global connection. It proves the gauge law and manifold curvature formula.'}")
edit(f,'Strengthened statements and the endpoint boundary','Strengthened statements and their formal counterparts')
edit(f,'This index includes all 79 proof-bearing named statements in strengthened Part II.','This index includes all 79 named statements with proofs in strengthened Part II.')
edit(f,'They do not enlarge the 19-item ledger or the 323-declaration inventory.','The formal ledger still contains 19 items, and the declaration inventory still contains 323 entries.')
edit(f,'Number; printed & Strengthened statement','Number (page) & Strengthened statement')
edit(f,"esc(r['number'])+'; '+r['printed_page']+' & '","esc(r['number'])+' ('+r['printed_page']+') & '")
edit(f,'The source-bound endpoint map records the current result.','The endpoint map ties each current result to its source.')

OUT.joinpath('REPLACEMENTS.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'files':len(changes),'replacements':sum(map(len,changes.values()))}))
