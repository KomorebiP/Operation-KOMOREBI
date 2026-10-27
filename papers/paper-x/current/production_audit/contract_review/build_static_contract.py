from pathlib import Path
import json,hashlib,re,datetime
base=Path('/workspace/scratch/fbc994080222/paper_x_baseline/inner/Paper_X')
manifest_path=Path('/workspace/scratch/fbc994080222/paper_x_production_build/PUBLICATION_SOURCE_MANIFEST.json')
manifest=json.loads(manifest_path.read_text()); modules={r['module']:r for r in manifest['modules']}
claims=json.loads((base/'publication/CLAIM_RECORDS.json').read_text())
# Static interfaces selected from the exact staged source. These are not asserted
# to be mechanically proved translations of the corresponding manuscript text.
selection={
'2.1':[('Residual','residual_exhaustive'),('Residual','residual_unique'),('Residual','fibers_disjoint')],
'2.2':[('Residual','no_crossing_finite'),('Residual','no_crossing_limit'),('Residual','positive_depth_mod')],
'2.3':[('Residual','zeroth_order_obstruction')],
'3.2':[('Reconstruction','represented_local_algebra_reconstruction'),('Reconstruction','localReconstructionEquiv')],
'3.3':[('Compactness','finite_branch_compactness')],
'3.4':[('SmoothModels','smooth_model_count'),('SmoothMaps','smooth_point_count'),('IntegralCharts','integralPointEquiv'),('SmoothModels','modelDigitEquiv')],
'4.2':[('ComplexCohomology','chainCohomologyPacketEquiv'),('PacketCohomology','cohomologyPacketEquiv')],
'5.3':[('Counting','weighted_chart_count_max'),('Counting','count_via_chart')],
'6.2':[('SmoothModels','smooth_model_zeta'),('Zeta','actual_smooth_zeta')],
'6.3':[('Zeta','actual_weighted_zeta')],
'6.4':[('Singular','singular_root_count'),('SingularZeta','actual_singular_zeta')],
'6.6':[('BranchingDimension','actual_singular_dimension'),('Singular','compatible_root_family_zero')],
'7.3':[('DirectedSeeds','directed_minimum_seed')],
'8.2':[('ConditionalArithmeticSpine','adelic_finite_depth_completion'),('ClassCommonSpine','unframed_common_spine_completion')],
'8.3':[('SystemCompletion','system_empty_level_obstruction'),('Compactness','indexed_empty_level_obstruction')],
'9.1':[('Claim91ConstructedClosure','finite_arithmetic_system_separator'),('Claim91ConstructedClosure','existentialArithmeticCoverage')],
'9.2':[('StrictCompatibleCarrierCompletion','compatible_carrier_summand_completion')],
'10.1':[('JointOccupancy','joint_isProj'),('JointOccupancy','trace_eq_dimension'),('JointOccupancy','trace_integer_unique'),('RequiredPacketOccupancy','occupied_iff_positiveTrace')],
'11.1':[('ConditionalOccupiedSystemCompletion','conditional_occupied_system_completion')],
'11.2':[('SpineExistenceCriterion','full_existence_boundary'),('SpineExistenceCriterion','system_iff_residual_and_higher'),('RequiredPacketOccupancy','all_positiveTrace_iff_witnesses')],
}
notes={
'2.1':'The three source theorems express exhaustive, unique and disjoint fibers for a supplied reduction map. No arithmetic reduction-map existence is asserted.',
'2.2':'Finite reachability assumes root preservation; infinite statement uses explicit finite-precision convergence. positive_depth_mod is a natural-number example bridge, not a general adic-arithmetic theorem.',
'2.3':'Publication route SeedBoundary is navigation/context; the direct general obstruction is owned by Residual. SeedBoundary instead contains infinite-graph source-count counterexamples.',
'3.2':'Main endpoint reconstructs a unique local continuous coefficient-preserving algebra hom from a compatible family; localReconstructionEquiv gives the local-ring-hom bijection. Representability is assumed externally. ReconstructionLocal is related twisting/locality support rather than the reconstruction endpoint.',
'3.3':'FiniteLevels of a supplied Tower plus nonempty all levels yields a Branch. Tower includes total reduction maps. This is conditional finite-set compactness.',
'3.4':'smooth_model_count is the supplied algebra-isomorphism transfer of the actual power-series point count. Its owner SmoothModels is a source-bearing adjunct beyond the published SmoothMaps/IntegralCharts routes. integralPointEquiv and modelDigitEquiv support the integral-branch and residue-stream clauses; no representability/chart isomorphism is manufactured.',
'4.2':'These are definitions producing linear equivalences, not theorem declarations. The genuine graded-complex endpoint is chainCohomologyPacketEquiv; cohomologyPacketEquiv uses the custom three-term complex interface. Both require the finite complete orthogonal projectors.',
'5.3':'Counts independent actual ideal-quotient tuples. count_via_chart transfers counts only with a separately supplied chart equivalence. Nat subtraction is truncated and matches max(m-w,0).',
'6.2':'smooth_model_zeta counts actual coefficient-algebra maps conditional on a supplied formal-model algebra isomorphism; actual_smooth_zeta is the ideal-chart series formula. Both are infinite formal power series.',
'6.3':'actual_weighted_zeta uses a supplied upper bound M on all weights, a truncated initial polynomial, and an explicit geometric tail. The manuscript specializes M to maximal weight and rewrites its coefficient; static mapping does not certify that algebraic rewrite.',
'6.4':'The first endpoint counts actual roots over a finite-residue DVR; the second gives the actual-root formal-series identity. e>0 is retained.',
'6.6':'The endpoint is the actual logarithmic finite-level counting limit. compatible_root_family_zero separately proves every compatible integral root tower is zero; counting dimension is not branch-space dimension.',
'7.3':'Finite supplied directed graph only. Source counts and minimum seed rank do not establish any arithmetic transport graph or admissibility.',
'8.2':'ConditionalArithmeticSpine.adelic_finite_depth_completion packages the full spine (including determinant/local realization) and is reached through later route closure; ClassCommonSpine provides a polynomial/local-condition predecessor. Explicit finite-level occupancy, continuity and inverse-limit closure remain hypotheses.',
'8.3':'Publication route SpineCompletionBoundary supplies explanatory countermodels, not this general endpoint. General framed system obstruction is SystemCompletion.system_empty_level_obstruction, with abstract indexed-tower obstruction in Compactness. The source for a literal full-spine class formulation should be checked separately if exact manuscript equivalence is claimed.',
'9.1':'Constructed occurrence discharges the external API premise; supplied compatible irreducible constituents, character continuity, good-prime compatibility and nonisomorphism remain explicit hypotheses. No universal arithmetic-system existence is concluded.',
'9.2':'Endpoint requires supplied actual carrier-copy and initial-summand-copy equivariant presentations, multiplicity capacity, trace separator and local packets/comparisons. It proves recovery and finite-copy closure, not those inputs.',
'10.1':'Projector, field-trace dimension equality, unique natural trace preimage, and occupancy via positive natural trace are separate endpoints. CharZero is needed for trace detection/uniqueness, while trace_eq_dimension itself is field-valued and works in any characteristic.',
'11.1':'Use manuscript/conditional_completion.tex as the selected amended reading contract. Terminal is a conjunction: an indexed transported family from already completed source members, and pointwise carrier recovery for a separately supplied compatible packet/carrier at arbitrary l0. It does not identify these two families, prove all-place carrier presentations, or force nonzero selected multiplicities.',
'11.2':'Conditional finite-level/system/occupancy boundary with explicit witnesses. The required packet carriers may be different supplied spaces and are not identified with the completed system.',
}

def signature(s,start):
    # Find the first declaration-body delimiter at lexical bracket depth zero.
    i=start; stack=[]; comment=0; string=False
    pairs={')':'(',']':'[','}':'{','⦄':'⦃'}
    while i<len(s):
        if comment:
            if s.startswith('/-',i): comment+=1;i+=2;continue
            if s.startswith('-/',i): comment-=1;i+=2;continue
            i+=1;continue
        if s.startswith('/-',i): comment=1;i+=2;continue
        if s.startswith('--',i):
            k=s.find('\n',i);i=len(s) if k<0 else k+1;continue
        c=s[i]
        if c=='"':
            string=not string;i+=1;continue
        if string:
            if c=='\\':i+=2
            else:i+=1
            continue
        if c in '([{⦃':stack.append(c)
        elif c in pairs:
            if stack and stack[-1]==pairs[c]:stack.pop()
        if not stack:
            if s.startswith(':=',i):return s[start:i].rstrip(),i+2
            if re.match(r'where\b',s[i:]):return s[start:i].rstrip(),i+5
        i+=1
    raise ValueError('no declaration body')

allpairs=[]
for row in claims:
    for pair in selection[row['number']]:
        if pair not in allpairs:allpairs.append(pair)
terminal=[('ConditionalOccupiedSystemCompletion','CarrierRecoveryAt'),('ConditionalOccupiedSystemCompletion','finite_trace_separator_at'),('ConditionalOccupiedSystemCompletion','carrier_recovery_from_arithmetic_separator'),('ConditionalOccupiedSystemCompletion','conditional_occupied_system_completion')]
direct=[('HorizontalTransportCompletion','exists_transported_system_of_inverseLimitClosed'),('Claim91ConstructedClosure','finite_arithmetic_system_separator'),('StrictCompatibleCarrierCompletion','compatible_carrier_summand_completion')]
for pair in terminal+direct:
    if pair not in allpairs:allpairs.append(pair)

targets=[]
for module,short in allpairs:
    fullname='PaperX.'+module+'.'+short
    owner='PaperX.'+module
    m=modules[owner];p=Path(m['source']);raw=p.read_bytes();text=raw.decode();sha=hashlib.sha256(raw).hexdigest()
    match=re.search(r'(?m)^(?:noncomputable\s+)?(theorem|def)\s+'+re.escape(short)+r'\b',text)
    if not match:raise ValueError(fullname)
    sig,end=signature(text,match.start())
    # Stable evidence id is the actual fully-qualified declaration name.
    targets.append({'name':fullname,'module':owner,'kind':'definition' if match.group(1)=='def' else 'theorem','source':str(p),'source_relative':m['source_relative'],'source_line':text[:match.start()].count('\n')+1,'signature_end_line':text[:end].count('\n')+1,'source_sha256':sha,'manifest_source_sha256':m['source_sha256'],'source_hash_matches_manifest':sha==m['source_sha256'],'source_declaration_signature':sig,'signature_limit':'Exact raw declaration syntax only. Ambient variable/universe/include declarations add elaborated parameters; this is not a compiler-printed complete type.','origin':m['origin'],'origin_restored_relative':m['origin_restored_relative']})
records=[]
for row in claims:
    module_names={'PaperX.'+x for x in row['source_route']}
    names=['PaperX.'+m+'.'+n for m,n in selection[row['number']]]
    records.append({**row,'mapping_status':'source-located candidate interface; no machine-certified manuscript equivalence asserted','primary_target':names[0],'targets':names,'target_owners_outside_publication_routes':sorted({x.rsplit('.',1)[0] for x in names}-module_names),'review_notes':notes[row['number']]})
checks=[]
for m in manifest['modules']:
    p=Path(m['source']);sha=hashlib.sha256(p.read_bytes()).hexdigest()
    checks.append({'module':m['module'],'source_sha256':sha,'manifest_source_sha256':m['source_sha256'],'matches':sha==m['source_sha256']})
report={
 'schema':'paper-x-static-target-contract-v1',
 'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'STATIC_SOURCE_RECONCILED_NOT_COMPILER_ACCEPTANCE',
 'scope':'Twenty publication route records mapped to exact staged source-located candidate interfaces, plus checked-conditional terminal quartet and direct predecessor endpoints. Not a whole-paper proof audit or a claim of manuscript/formal equivalence.',
 'baseline_root':str(base),
 'source_manifest':str(manifest_path),
 'source_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
 'publication_claim_records_sha256':hashlib.sha256((base/'publication/CLAIM_RECORDS.json').read_bytes()).hexdigest(),
 'selected_amended_manuscript_contract':str(base/'manuscript/conditional_completion.tex'),
 'module_count':manifest['count'],'missing_modules':manifest['missing'],
 'all_staged_module_hashes_match_manifest':all(x['matches'] for x in checks),
 'record_count':len(records),'explicit_target_count':len(targets),
 'kind_convention':{'Lean def':'definition','Lean theorem':'theorem'},
 'records':records,'targets':targets,
 'terminal':{'module':'PaperX.ConditionalOccupiedSystemCompletion','source_sha256':'ba15fd1ea175fecfcc705243c75d1061c8bdf500221dafe86f29fe1c5d21c5e0','targets':['PaperX.'+m+'.'+n for m,n in terminal],'direct_imports':modules['PaperX.ConditionalOccupiedSystemCompletion']['imports'],'direct_called_predecessor_targets':['PaperX.'+m+'.'+n for m,n in direct],'logical_scope':'Two independent conjuncts: transported completed target family, and carrier recovery at an arbitrary selected coefficient place. No equality tying the two witness families; zero multiplicities permitted.'},
 'source_identity_checks':checks,
 'limits':['No Lean build, environment owner resolution, complete elaborated-type printing, or axiom computation was performed by this static review.','Published module routes are navigation evidence, not one-to-one exact theorem correspondences; 20 route records do not establish 20 mechanically proved translations.','Historical checked-conditional acceptance records do not substitute for the production replay owned by the build agent.','Later residual-system attempts and fixture scopes are excluded by the selected production manifest.']}
out=Path('/workspace/scratch/fbc994080222/paper_x_production_audit/contract_review/TARGET_CONTRACT.json')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Compact machine-audit inputs, with source binding duplicated so consumers need not join.
Path(out.parent/'EXPLICIT_TARGETS.json').write_text(json.dumps({'source_manifest_sha256':report['source_manifest_sha256'],'targets':targets},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'report':str(out),'records':len(records),'targets':len(targets),'modules':len(checks),'hash_mismatches':[x for x in checks if not x['matches']],'kinds':{k:sum(t['kind']==k for t in targets) for k in ['theorem','definition']},'terminal':report['terminal']},indent=2))
