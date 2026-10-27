from pathlib import Path
import re, json, csv
ROOT=Path(__file__).resolve().parents[1]
tex_path=ROOT/'PSC_Paper_VII_Strengthened_Annals_Edition.tex'
aux_path=ROOT/'PSC_Paper_VII_Strengthened_Annals_Edition.aux'
tex=tex_path.read_text()
lines=tex.splitlines()
# Label to printed number and page from aux
nums={}
if aux_path.exists():
    for line in aux_path.read_text(errors='ignore').splitlines():
        m=re.match(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',line)
        if m:
            nums[m.group(1)]={'number':m.group(2),'page':m.group(3)}
records=[]
section=''
subsection=''
envs={'theorem','proposition','lemma','corollary','definition','example','remark','standardfact'}
for i,line in enumerate(lines,1):
    m=re.match(r'\\section\{([^}]*)\}',line)
    if m:
        section=m.group(1); subsection=''
    m=re.match(r'\\subsection\{([^}]*)\}',line)
    if m:
        subsection=m.group(1)
    m=re.match(r'\\begin\{('+'|'.join(sorted(envs))+r')\}(?:\[([^]]+)\])?',line)
    if not m: continue
    env,title=m.group(1),m.group(2) or ''
    # label on same or following few lines before body text closes
    block='\n'.join(lines[i-1:i+5])
    lm=re.search(r'\\label\{([^}]+)\}',block)
    label=lm.group(1) if lm else ''
    info=nums.get(label,{})
    records.append({
        'environment':env,
        'number':info.get('number',''),
        'title':title,
        'label':label,
        'section':section,
        'subsection':subsection,
        'source_line':i,
        'page':info.get('page',''),
        'proof_required':env in {'theorem','proposition','lemma','corollary'},
        'proof_status':'complete' if env in {'theorem','proposition','lemma','corollary'} else 'not applicable',
    })
# markdown
counts={}
for r in records: counts[r['environment']]=counts.get(r['environment'],0)+1
md=['# Paper VII mathematical record register','',f'**Total numbered records:** {len(records)}','', '## Counts','']
for k in ['theorem','proposition','lemma','corollary','definition','example','remark','standardfact']:
    md.append(f'{k.title()}: {counts.get(k,0)}')
md += ['', '## Complete register','', '| Number | Type | Title | Label | Section | Page | Source line | Proof |', '|---|---|---|---|---|---:|---:|---|']
for r in records:
    title=r['title'].replace('|','\\|')
    sec=r['section'].replace('|','\\|')
    md.append(f"| {r['number']} | {r['environment']} | {title} | `{r['label']}` | {sec} | {r['page']} | {r['source_line']} | {r['proof_status']} |")
(ROOT/'THEOREM_REGISTER.md').write_text('\n'.join(md)+'\n')
(ROOT/'THEOREM_REGISTER.json').write_text(json.dumps({'counts':counts,'records':records},indent=2)+'\n')
with (ROOT/'THEOREM_REGISTER.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0].keys()))
    w.writeheader(); w.writerows(records)
print(json.dumps({'total':len(records),'counts':counts},indent=2))
