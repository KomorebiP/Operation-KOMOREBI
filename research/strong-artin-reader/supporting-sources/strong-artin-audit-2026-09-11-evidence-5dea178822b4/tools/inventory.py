from pathlib import Path, PurePosixPath
import zipfile,hashlib,io,json,re,collections
ROOT=Path('/mnt/data')
OUT=ROOT/'Strong_Artin_Audit_2026-09-11'
OUT.mkdir(exist_ok=True)
H=lambda x:hashlib.sha256(x).hexdigest()
archives={}; sources={}; edges=[]; roots={}; locations=[]

def scrub(t):
    # Mask nested Lean comments and strings, preserving line positions.
    out=list(t); i=0; depth=0
    while i<len(t):
        if t.startswith('/-',i):
            start=i;depth=1;i+=2
            while i<len(t) and depth:
                if t.startswith('/-',i):depth+=1;i+=2
                elif t.startswith('-/',i):depth-=1;i+=2
                else:i+=1
            for j in range(start,i):
                if out[j]!='\n':out[j]=' '
        elif t.startswith('--',i):
            j=t.find('\n',i);j=len(t) if j<0 else j
            for k in range(i,j):out[k]=' '
            i=j
        elif t[i]=='"':
            start=i;i+=1
            while i<len(t):
                if t[i]=='\\':i+=2
                elif t[i]=='"':i+=1;break
                else:i+=1
            for j in range(start,min(i,len(t))):
                if out[j]!='\n':out[j]=' '
        else:i+=1
    return ''.join(out)

def decls(t):
    s=scrub(t)
    counts=collections.Counter(re.findall(r'(?<![\w.])(?:theorem|lemma|def|abbrev|structure|instance|axiom|opaque|inductive|class)(?![\w.])',s))
    # Publicly useful source-level declaration list, not a Lean environment export.
    found=[];ns=[];scopes=[]
    pat=re.compile(r'(?<![\w.])(theorem|lemma|def|abbrev|structure|axiom|opaque|inductive|class)\s+([^\s\[({:=]+)')
    for no,line in enumerate(s.splitlines(),1):
        m=re.match(r'^\s*namespace\s+([^\s]+)',line)
        if m:ns.append(m.group(1));scopes.append(('namespace',m.group(1)))
        m=re.match(r'^\s*(?:noncomputable\s+)?section(?:\s+([^\s]+))?\s*$',line)
        if m:scopes.append(('section',m.group(1)))
        for m in pat.finditer(line):
            name=m.group(2);fq='.'.join(ns+[name])
            found.append({'kind':m.group(1),'name':name,'qualified_name_approx':fq,'line':no})
        if re.match(r'^\s*end(?:\s+[^\s]+)?\s*$',line) and scopes:
            kind,name=scopes.pop()
            if kind=='namespace':ns.pop()
    return dict(counts),found,s

def is_prod(n):
    ps=PurePosixPath(n).parts
    excluded={'verification','replay','fresh','scratch','build','.lake','development','tests','test','audit','_audit'}
    return n.endswith('.lean') and 'src' in ps and not any(p.lower() in excluded for p in ps)

def scan_archive(data,name,parent=None,member=None):
    h=H(data)
    if parent:edges.append({'parent':parent,'child':h,'member':member})
    if h in archives:
        archives[h]['aliases'].add(name);return h
    z=zipfile.ZipFile(io.BytesIO(data))
    bad=z.testzip()
    rec={'name':name,'aliases':{name},'sha256':h,'bytes':len(data),'crc_bad':bad,'sources':[],'metadata':{},'nested':[]}
    archives[h]=rec
    for n in z.namelist():
        if is_prod(n):
            b=z.read(n);sh=H(b);t=b.decode();c,d,s=decls(t)
            if sh not in sources:
                sources[sh]={'sha256':sh,'bytes':len(b),'basename':PurePosixPath(n).name,'counts':c,'declarations':d,'lines':len(t.splitlines()),'escapes':re.findall(r'\b(?:sorry|admit|axiom|opaque|sorryAx)\b',s),'locations':[],'imports':re.findall(r'^\s*(?:public\s+)?import\s+([^\n]+)',s,re.M)}
                p=OUT/'source_blobs'/sh[:16]/PurePosixPath(n).name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
                sources[sh]['audit_path']=str(p.relative_to(OUT))
            loc={'archive':h,'member':n};sources[sh]['locations'].append(loc);rec['sources'].append(sh)
        if n.endswith('.zip'):
            ch=scan_archive(z.read(n),PurePosixPath(n).name,h,n);rec['nested'].append(ch)
        elif PurePosixPath(n).name in {'RESULT.json','MANIFEST.json','README.md','CONTINUE_HERE.md','RESEARCH_BOUNDARY.md','PROOF_LEDGER.md','SHA256SUMS.txt','AGENTS.md','RESEARCH_LOG.md'} and len(PurePosixPath(n).parts)<=3:
            try:
                txt=z.read(n).decode();rec['metadata'][n]=json.loads(txt) if n.endswith('.json') else txt
            except Exception as e:rec['metadata'][n]={'parse_error':str(e)}
    return h

for p in sorted(ROOT.glob('Strong_Artin_Lean_v*.zip')):
    roots[p.name]=scan_archive(p.read_bytes(),p.name)

def closure(h):
    seen=set();out=set()
    def rec(a):
        if a in seen:return
        seen.add(a);out.update(archives[a]['sources'])
        for b in archives[a]['nested']:rec(b)
    rec(h);return seen,out

def aggregate(ss):
    c=collections.Counter()
    for s in ss:c.update(sources[s]['counts'])
    return {'source_files':len(ss),'source_lines':sum(sources[s]['lines'] for s in ss),'declarations':dict(c),'proof_declarations':c['theorem']+c['lemma'],'escape_occurrences':sum(len(sources[s]['escapes']) for s in ss)}

stats=[]
for n,h in roots.items():
    aa,ss=closure(h); stats.append({'archive':n,'sha256':h,'archive_count_in_closure':len(aa),'own_source_count':len(set(archives[h]['sources'])),'own':aggregate(set(archives[h]['sources'])),'closure':aggregate(ss)})
allss=set(sources);current=next(n for n in roots if 'v0.25.0' in n);aa,ss=closure(roots[current])
bybase=collections.defaultdict(list)
for sh,s in sources.items():bybase[s['basename']].append(sh)
variants={n:v for n,v in bybase.items() if len(v)>1}
result={'method':'Recursive nested-archive traversal; source files with src path segment excluding verification/replay/fresh/scratch/build/development/tests/audit; comments and strings masked; exact source-byte hashes deduplicate files; counts are source declaration occurrences, NOT kernel environment totals nor independent mathematical claims.','current_root':current,'top_level_archives':len(roots),'distinct_archives':len(archives),'archive_crc_failures':[x['name'] for x in archives.values() if x['crc_bad']],'available_union':aggregate(allss),'current_v025_ancestor_closure':aggregate(ss),'current_v025_ancestor_archives':sorted(archives[h]['name'] for h in aa),'same_basename_different_content':variants,'by_root':stats,'archives':{h:{**r,'aliases':sorted(r['aliases'])} for h,r in archives.items()},'edges':edges,'sources':sources}
(OUT/'inventory.json').write_text(json.dumps(result,indent=2))
(OUT/'sources.json').write_text(json.dumps(sources,indent=2))
print(json.dumps({k:result[k] for k in ['top_level_archives','distinct_archives','archive_crc_failures','available_union','current_v025_ancestor_closure','current_v025_ancestor_archives']},indent=2))
for r in stats:print(r['archive'], 'own',r['own']['proof_declarations'],'closure',r['closure']['proof_declarations'],r['closure']['source_files'])
print('MODULE VARIANTS',len(variants))
for n,v in variants.items(): print(n,len(v))
