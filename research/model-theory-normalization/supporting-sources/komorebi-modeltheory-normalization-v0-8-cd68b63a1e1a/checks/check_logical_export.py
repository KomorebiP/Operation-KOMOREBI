"""Independent AST/transcription checker, with no import of matrix_logic/discovery.

It checks the caller's expected source, the original matrix certificate, and
literal formula structure. Mathematical soundness is supplied by the Lean bridge.
"""
from __future__ import annotations
import ast, json, re
from hashlib import sha256
from checks.check_certificate import check, require

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def sh(x): return sha256(canon(x)).hexdigest()
def neg(a): return ['imp',a,['false']]
def conjunction(a,b): return neg(['imp',a,neg(b)])
def term(word,obs,var):
    v=['free',var]
    for a in word:v=['action',a,v]
    return ['observe',obs,v]

def check_logical(spec,cert,artifact):
    result=check(spec,cert)
    require(isinstance(artifact,dict),'logical artifact must be an object')
    require(set(artifact)=={'schema','source_sha256','certificate_sha256','profile','tests','terms','formula','test_count','term_horizon','quantifier_rank','coordinate_count','non_claims'},'logical schema fields')
    require(artifact['schema']=='komorebi-matrix-logical-code-v0.3','logical version')
    require(artifact['source_sha256']==sh(spec) and artifact['certificate_sha256']==sh(cert),'logical source/certificate binding')
    require(artifact['profile']=={'modulus':spec['p']**spec['r'],'initial_interface':'all_states','word_order':'left_to_right','quantifier_domain':'encoded_image','language':'state_guard + original_actions + original_observations + named_values'},'logical profile')
    tests=cert['raw_tests']
    require(artifact['tests']==tests,'logical tests changed')
    truth=['imp',['false'],['false']]; f=truth
    for t in reversed(tests):f=conjunction(['eq',term(t['word'],t['observation'],0),term(t['word'],t['observation'],1)],f)
    f=conjunction(conjunction(['state',['free',0]],['state',['free',1]]),f)
    require(canon(artifact['formula'])==canon(f),'wrong logical formula or missing state guard')
    require(canon(artifact['terms'])==canon([term(t['word'],t['observation'],0) for t in tests]),'wrong coding terms')
    require(artifact['test_count']==len(tests),'test count')
    require(artifact['term_horizon']==max((len(t['word']) for t in tests),default=0),'horizon')
    require(artifact['quantifier_rank']==0 and artifact['coordinate_count']==cert['dimension'],'wrong resource statement')
    return {'status':'PASS','tests':len(tests),'coordinates':result['coordinates']}

def literal_list(text,anchor):
    tail=text.split(anchor,1)[1];start=tail.index('[');depth=0
    for j,ch in enumerate(tail[start:],start):
        depth+=int(ch=='[')-int(ch==']')
        if depth==0:return ast.literal_eval(tail[start:j+1])
    raise ValueError('unclosed literal')

def check_lean_literals(spec,cert,text):
    m=spec['p']**spec['r']
    require(f'abbrev R := Fin {m}\n' in text,'literal modulus')
    require(literal_list(text,'def actions :')==spec['actions'],'literal action mismatch')
    require(literal_list(text,'def observations :')==spec['observations'],'literal observations mismatch')
    for anchor,key in [('  encoding :=','basis'),('  transitions :=','transitions'),('  decoder :=','observation_decoder'),('  combinations :=','basis_combinations'),('  change :=','V'),('  inverse :=','V_inverse')]:
        require(literal_list(text,anchor)==cert[key],'literal '+key)
    tests=[(t['word'],t['observation']) for t in cert['raw_tests']]
    require(literal_list(text,'def discoveredTests :')==tests,'literal logical test mismatch')
    require('theorem test_list_checked : discoveredTests = matrixTests data := by decide' in text,'missing list binding')
    for token in ['axiom ', 'sorry', 'native_decide','Lean.ofReduceBool']:
        require(token not in text,'untrusted proof escape')
    return {'status':'PASS'}
