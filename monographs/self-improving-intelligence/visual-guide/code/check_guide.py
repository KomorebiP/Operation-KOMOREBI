#!/usr/bin/env python3
"""Focused checks for the visual companion, not a rerun of the research suite.

Exact arithmetic and local finite examples are checked here. Larger compiler
counts are verified as transcriptions of the unchanged source JSON receipts.
"""
from __future__ import annotations
import hashlib, itertools, json, math, platform, re, sys, time
from fractions import Fraction as F
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'references/source_records'
PDF=ROOT/'Self_Improving_Intelligence_Visual_Guide_v1.0.0.pdf'
GROUPS=[];COUNT=0

def require(condition: bool, message: str) -> None:
    global COUNT
    COUNT+=1
    if not condition:raise AssertionError(message)

def record(name: str):return json.loads((RECORDS/name).read_text())
def group(name,domain,fn):
    before=COUNT;fn();GROUPS.append({'name':name,'domain':domain,'checks':COUNT-before,'result':'PASS'})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    started=time.perf_counter()
    def provenance():
        q=json.loads((ROOT/'validation/source_integrity.json').read_text())
        for name,value in q['included_sources'].items():require(sha(ROOT/name)==value,f'Changed source copy: {name}')
        require(sha(ROOT/'references/Self_Improving_Intelligence_v1.0.0.pdf')==q['source_pdf_sha256'],'Source PDF changed')
    group('Included source integrity','Unchanged PDF, reference indexes and seven source JSON records',provenance)

    def cell_world():
        leaves=[]
        for reports in itertools.product((0,1),repeat=3):
            j=sum(b*(2**d) for d,b in enumerate(reports));leaves.append(j)
        require(leaves==[0,4,2,6,1,5,3,7],'Leaf ordering')
        for j in range(8):
            B=set(range(8));hist=[]
            for bit in range(3):
                report=(j>>bit)&1;hist.append(report)
                B={x for x in B if ((x>>bit)&1)==report}
                require(j in B,'True case must remain possible')
                require(len(B)==2**(2-bit),'One binary distinction per level')
            require(B=={j},'Canonical policy must identify cell')
        B=set(range(8));supports=[]
        for bit,reported in enumerate((1,0,1)):
            B={x for x in B if ((x>>bit)&1)==reported};supports.append(sorted(B))
        require(supports==[[1,3,5,7],[1,5],[5]],'Cell-five trace')
        require(1+2+4+8==15,'Stored full-tree records')
        require(3+1==4 and 7+1==8,'Online work counts')
        D=record('demonstration.json')
        require(D['checked_records']==15 and D['checked_work']=='4','Source controller agreement')
        require(D['parent_success']=='3/8' and D['child_success']=='1','Source budget results')
        require([r['report'] for r in D['canonical_bit_case5_trace']['trace']]==[1,0,1],'Source canonical reports')
    group('Eight-cell diagrams','All eight cells; canonical bit-tree leaves and highlighted cell-five path',cell_world)

    def repair_alignment():
        repairsets=[{0,1,2},{3}]
        stop=lambda S:any(S<=G for G in repairsets)
        require(stop({0,1}) and not stop({2,3}),'Balanced branch remains unresolved')
        require(stop({0,1,2}) and stop({3}),'Repair-aligned branches stop')
        # H(3/4,1/4) = 2 - (3/4) log2(3) < 1 iff 3**3 > 2**4.
        require(3**3>2**4,'Balanced query has more entropy')
        require((1+max(2,4),1+3+7)==(5,11),'Max/sum illustrative recurrence')
    group('Repair-relevant inquiry','Four-case repair split; illustrative root recurrence',repair_alignment)

    def sensor():
        pairs=list(itertools.product((0,1),repeat=2)) # x, theta
        for o in (0,1):
            possible=[p for p in pairs if p[0]^p[1]==o]
            require(len(possible)==2 and {x for x,t in possible}=={0,1},'Ambiguity remains')
            for repeats in range(1,5):
                retained=[p for p in pairs if all(p[0]^p[1]==o for _ in range(repeats))]
                require(retained==possible,'Repeated identical sensor gives no extra information')
        for x,t in pairs:require((x^t)^t==x,'Paid calibration identifies x')
        require(2+1+1==4 and 1+2+4==7,'Calibration cost/storage')
    group('Unknown sensor diagram','Four fixed model/state pairs; one to four repeated readings',sensor)

    def compiler_receipts():
        d=record('discovery_demonstration.json')
        row=next(r for r in d['comparison_rows'] if r['n']==16)
        require(row['parent']['table_reads']==576128,'Parent count')
        require(row['descendant']['table_reads']==1728,'Shortcut count')
        require(row['descendant']['phase_reads']=={'guard':320,'proposal':1280,'verification':128},'Phase sums')
        require(320+1280+64+64==1728,'Guide split of verification work')
        require(row['parent']['frontier']==row['descendant']['frontier']==[['5',31]],'Same optimal costs')
        for key in ('parent','descendant'):require(row[key]['shared_input_validation_reads']==320,'Shared input validation')
        require(sum(c['total_reads'] for c in d['development'])==21124,'All selection trials charged')
        eq=next(r for r in d['heldout_structural_cases'] if r['case']=='equality_only_control')
        require((eq['parent']['table_reads'],eq['descendant']['table_reads'])==(402,472),'Fallback count')
        require(472-402==70,'Fallback overhead')
    group('Compiler chart transcription','16-case shortcut and 4-case fallback in source receipts; no compiler rerun',compiler_receipts)

    def prefix():
        cases=0
        for C in range(1,9):
            for m in range(2,2*C+1):
                for a in range(m+1):
                    for b in range(m-a+1):
                        r=m-a-b
                        can_complete=any(a+k<=C and b+(r-k)<=C for k in range(r+1))
                        require(can_complete==(max(a,b)<=C),'Prefix completion equivalence');cases+=1
        require(max(0,3)>2 and not max(0,3)>4,'Feature conflict')
        require(max(0,5)>min(8,4) and not max(0,5)>8,'Out-of-development counterexample')
        require(5>4 and 8-5==3,'Three suffix rows skipped')
    group('Capacity and finite-fit controls','Every admissible count prefix for integer capacity 1 through 8, plus illustrated counterexamples',prefix)

    def teacher_trace():
        d=record('synthesized_rule.json')
        require(d['grammar_count']==3960 and d['context_count']==198,'Grammar and context counts')
        require(d['counters']['candidate_asts_considered']==190,'Visited candidates')
        require(d['counterexamples']==3 and d['counters']['candidate_teacher_queries']==4,'Teacher counts')
        trace=d['trace'];require([t['expression'] for t in trace]==['(a > a)','(b > a)','(b > c)','(max(a,b) > c)'],'Proposals')
        for actual,expected in zip(trace[:3],[(0,2,2,1),(0,1,2,1),(2,0,2,1)]):
            q=actual['context'];require((q['a'],q['b'],q['m'],q['c'])==expected,'Counterexample context')
    group('Four-proposal sequence','Exact three counterexamples and final expression in the source rule record',teacher_trace)

    def stream_counts():
        d=record('synthesis_demonstration.json')
        row=next(r for r in d['evaluations'] if r['cases']==64)
        stream=row['lowered']
        require(row['full_scan']['table_reads']==27744 and stream['table_reads']==19457,'64-case reads')
        require(stream['counters']['lowered_comparisons']==14209,'Added comparison count')
        require(row['full_scan']['frontier']==stream['frontier']==[['7',127]],'Protected controller costs')
        require(27744-19457==8287,'Read savings')
        require(8287-14209==-5922 and 2*8287-14209==2365,'Price reversal')
        require(F(14209,8287)>1 and F(14209,8287)<2,'Break-even threshold')
    group('Streaming chart transcription','64-case source counters and exact two-unit resource comparison',stream_counts)

    def equations():
        d=record('meta_synthesis_demonstration.json');L=d['library_learning'];Q=d['quotient']
        require((L['schema_terms'],L['probe_contexts'])==(135,9),'Probe construction')
        require(L['counters']['proposed_equations']==1068,'Proposal count')
        require((L['accepted_equations'],L['unproved_proposals'])==(336,732),'Proof admission counts')
        require(336+732==1068,'Proposal partition')
        require((Q['grammar_count'],Q['retained_candidates'])==(3960,1362),'Quotient size')
        require(d['eager_full_prover_comparator']['retained_candidates']==1352,'Stronger prior')
        require(L['library_bytes']==69518,'Library bytes')
        require(Q['counters']['schema_match_attempts']==518140,'Preparation not erased')
        A=d['capacity_rule_reacquisition']
        require((A['parent']['counters']['visited_candidates'],A['child']['counters']['visited_candidates'])==(190,76),'Reacquisition candidates')
        require((A['parent']['counters']['semantic_node_visits'],A['child']['counters']['semantic_node_visits'])==(1898,1376),'Reacquisition work')
        require(A['parent']['trace']==A['child']['trace'] and A['parent']['winner']==A['child']['winner'],'Identical evidence and answer')
        require(d['batch_semantic_node_visits']=={'parent':196384,'child':85162},'Additional source workload')
        for x in (1,2,3):require(max(x,1)==x,'Probe agreement')
        require(max(0,1)!=0,'Probe agreement is insufficient')
        for a,b in itertools.product(range(-3,4),repeat=2):
            require(a+0==a and max(a,b)==max(b,a) and (a<b)==(b>a),'Illustrated checked identities')
    group('Equation and quotient plates','Exact source counts/teacher trace; signed-integer identity examples on [-3,3]',equations)

    def weights_and_prices():
        for n in (8,32):
            w=[F(1) if i%2==0 else F(0) for i in range(n)]
            for i in range(0,n,2):require(sum(w[i:i+2])==1,'Pair repair load')
            require(sum(w)==n//2,'Total pair weight')
            require(sum(w)>1,'Universal repair invalidates old weights')
            rebuilt=[F(1)]+[F(0)]*(n-1);require(sum(rebuilt)==1,'Valid replacement weights')
        d=record('revision_demonstration.json');M=d['measured_weighted_search']
        a=M['full']['counters'];b=M['streaming']['counters'];keys=['search_model_reads','weight_additions','capacity_comparisons']
        saving=[a[k]-b[k] for k in keys];require(saving==[1552,1552,-1868],'Event vector')
        require(M['full']['witness']==M['streaming']['witness']=={'work':'5','storage':31},'Same weighted controller cost')
        for prices,expected in [((1,1,1),1236),((1,0,1),-316),((0,0,1),-1868)]:
            require(sum(p*s for p,s in zip(prices,saving))==expected,'Price-specific conclusion')
        E=d['repair_extension'];require(E['replacement_work']=={'work':'1','storage':1},'Replacement tree cost')
        require(E['after_recheck']['cost_assessment']['status']=='BLOCKED','Old cost claim remains blocked')
        require(E['after_recheck']['equations']['status']=='VALID','Unchanged arithmetic branch')
    group('Repair scope and resource ledger','8/32-case paired weights, recorded revision statuses, three exact price vectors',weights_and_prices)

    def sequential():
        count=0
        for signs in itertools.product((-1,1),repeat=4):
            E=1;cross=False
            for Y in signs:
                bet=int(Y>0);E*=1+bet*Y;cross|=E>=4
            require(cross==(sum(x>0 for x in signs)>=2),'Highlight event')
            count+=cross
        require(count==11 and F(count,16)>F(1,4),'Invalid hindsight threshold crossing')
        for n in range(1,12):
            require(sum(F(1,2**i) for i in range(1,n+1))==1-F(1,2**n),'Diminishing positive gains')
    group('Evidence and acceleration illustrations','All sixteen four-score paths and partial sums through eleven gains',sequential)

    def pdf_preflight():
        D=fitz.open(PDF);require(len(D)==36,'Guide page count');require(len(D.get_toc())==36,'Bookmarks')
        P=json.loads((ROOT/'data/page_map.json').read_text());require([p['page'] for p in P]==list(range(1,37)),'Page crosswalk complete')
        bad=[];overlaps=[];images=0
        for i,p in enumerate(D):
            text=p.get_text();require('\x00' not in text and '\ufffd' not in text,f'Missing text glyph page {i+1}')
            if i:require('[S]' in text,f'Missing source footer page {i+1}')
            images+=len(p.get_images())
            words=p.get_text('words')
            for word in words:
                r=fitz.Rect(word[:4]);
                if r.x0<20 or r.y0<3 or r.x1>592 or r.y1>789:bad.append({'page':i+1,'word':word[4],'bbox':list(r)})
            for j,w in enumerate(words):
                a=fitz.Rect(w[:4])
                for v in words[j+1:]:
                    b=fitz.Rect(v[:4]);intersection=a&b
                    if not intersection.is_empty and intersection.get_area()>.22*min(a.get_area(),b.get_area()):
                        overlaps.append({'page':i+1,'words':[w[4],v[4]],'intersection':list(intersection)})
        require(not bad,'Out-of-page words');require(not overlaps,'Overlapping word boxes')
        require(images==0,'All guide drawings must be vector, not embedded raster')
        require('−316' in D[27].get_text() and '−1,868' in D[27].get_text(),'Signed costs must extract correctly')
        require(len(D[35].get_links())==8,'Clickable reading routes')
        (ROOT/'validation/pdf_preflight.json').write_text(json.dumps({'page_count':36,'bookmarks':len(D.get_toc()),'source_footers':35,'raster_images':images,'out_of_bounds':bad,'word_overlaps':overlaps,'null_or_replacement_glyphs':0,'font_report':'See validation/pdffonts.txt; fonts embedded, standalone font files excluded.','pdf_sha256':sha(PDF)},indent=2)+'\n')
    group('PDF geometry, glyphs and navigation','All 36 pages; every extracted word; missing-glyph controls and 8 internal links',pdf_preflight)
    result={'status':'PASS','scope':'Focused companion checks. Original 336,867-assertion suite not rerun. Source algorithm counts checked as transcriptions, not new executions.','groups':GROUPS,'total_groups':len(GROUPS),'total_checks':COUNT,'arithmetic':'integers and fractions.Fraction; entropy ordering reduced to an exact integer inequality','source_pdf_sha256':sha(ROOT/'references/Self_Improving_Intelligence_v1.0.0.pdf'),'guide_pdf_sha256':sha(PDF),'non_claims':['No general proof by enumeration.','No independent external audit or agent-learning experiment.','No source compiler runtime ratio inferred from event counts.']}
    (ROOT/'validation/guide_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'validation/check_execution.json').write_text(json.dumps({'command':'python code/check_guide.py','python':sys.version,'platform':platform.platform(),'runtime_seconds':time.perf_counter()-started,'exit_status':0},indent=2)+'\n')
    print(f'PASS: {len(GROUPS)} focused groups; {COUNT} checks. Source research suite was not rerun.')

if __name__=='__main__':main()
