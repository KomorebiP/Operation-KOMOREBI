#!/usr/bin/env python3
"""Resolve consolidated statement maps against preserved checked declarations."""
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source' if (ROOT / 'source').is_dir() else ROOT.parent
MANUSCRIPT = ROOT / 'manuscript' if (ROOT / 'manuscript').is_dir() else ROOT.parent / 'manuscript/consolidated'
AUDIT = ROOT / 'audit'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source_bytes(path):
    path = path.removeprefix('source/')
    if '::' in path:
        archive, member = path.split('::', 1)
        with zipfile.ZipFile(SOURCE / archive) as z:
            return z.read(member)
    return (SOURCE / path).read_bytes()

def main():
    with (AUDIT / 'DECLARATIONS.csv').open() as stream:
        declarations = {(r['qualified_name'], r['source_sha256']) for r in csv.DictReader(stream)}
    texts = {p.name:p.read_text() for p in (MANUSCRIPT / 'sections').glob('*.tex')}
    labels = {label:name for name, text in texts.items() for label in re.findall(r'\\label\{([^}]+)\}',text)}
    raw_count = sum(len(re.findall(r'\\label\{([^}]+)\}',text)) for text in texts.values())
    assert len(labels) == raw_count, 'Duplicate labels'
    refs = {value for text in texts.values() for value in re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',text)}
    assert refs <= set(labels), sorted(refs-set(labels))
    entries = []
    arithmetic = json.loads((AUDIT / 'arithmetic_map.json').read_text())
    for label, sources in arithmetic['main_statement_map'].items():
        entries.append({'label':label,'references':sources})
    lifting = json.loads((AUDIT / 'lifting_map.json').read_text())
    for item in lifting['entries']:
        entries.append({'label':item['label'],'title':item['title'],'references':item['declarations']})
    foundations = json.loads((AUDIT / 'foundations_map.json').read_text())
    modules = {item['module']:item for item in foundations['sources']}
    for item in foundations['claims']:
        references = []
        for module in item['modules']:
            source = modules[module]
            path = source['source_archive'].removeprefix('source/') + '::' + source['member']
            references += [{'source':path,'declaration':name,'sha256':source['sha256']}
                           for name in source['declarations']]
        entries.append({'label':item['label'],'title':item['scope'],'references':references})
    regularity = json.loads((AUDIT / 'regularity_map.json').read_text())
    for item in regularity['statements']:
        entries.append({'label':item['label'],'title':item['title'],'references':item['source_references']})
    assert len({x['label'] for x in entries}) == len(entries)
    resolved = []
    csv_rows = []
    for item in entries:
        label = item['label']
        assert label in labels, label
        references = []
        for ref in item['references']:
            path = ref.get('source',ref.get('path')).removeprefix('source/')
            sha = digest(source_bytes(path))
            expected = ref.get('source_sha256',ref.get('sha256',sha))
            assert sha == expected, path
            name = ref['declaration']
            assert (name,sha) in declarations, (name,path)
            references.append({'source':path,'declaration':name,'source_sha256':sha})
            csv_rows.append({'label':label,'manuscript_section':'manuscript/consolidated/sections/'+labels[label],
                             'declaration':name,'source':path,'source_sha256':sha})
        resolved.append({'label':label,'title':item.get('title',''),
                         'manuscript_section':'manuscript/consolidated/sections/'+labels[label],
                         'references':references})
    result = {'status':'PASS','mapped_statements':len(resolved),
              'resolved_statement_source_links':len(csv_rows),
              'unique_declarations_referenced':len({r['declaration'] for r in csv_rows}),
              'labels_checked':len(labels),'local_references_checked':len(refs),
              'manuscript_source_hashes':{str(p.relative_to(MANUSCRIPT)):digest(p.read_bytes())
                                          for p in sorted(MANUSCRIPT.rglob('*.tex'))},
              'expository_additions':arithmetic.get('expository_additions',[]),
              'scope':'Source identity and declared-name resolution. Mathematical correspondence is covered by the independent manuscript review, not established by this index alone.',
              'statements':resolved}
    (AUDIT / 'STATEMENT_INDEX.json').write_text(json.dumps(result,indent=2)+'\n')
    with (AUDIT / 'STATEMENT_INDEX.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['label','manuscript_section','declaration','source','source_sha256'])
        writer.writeheader(); writer.writerows(csv_rows)
    print(json.dumps({k:v for k,v in result.items() if k!='statements'},indent=2))

if __name__ == '__main__':
    main()
