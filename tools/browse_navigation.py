"""Generate accessible Markdown routes to selected component resources.

Resource selections are explicit; source files and scientific labels are never
changed. Validate every resource against its own import receipt and Git tree.
"""
import json
import posixpath
import re
from urllib.parse import quote

REGISTRY = 'manifests/browse-resources.json'
GROUPS = {'papers': 'Core papers', 'monographs': 'Books and companion volumes',
          'research': 'Research programs', 'packages': 'Software packages',
          'experiments': 'Experiments'}
KINDS = {'guide', 'pdf', 'text', 'visual', 'formal_guide', 'lean', 'claims', 'code'}
CODE_EXTENSIONS = ('.py', '.c', '.cpp', '.ipynb', '.rs', '.jl', '.h', '.hpp')


def page_for(group):
    return 'docs/browse/'+group.upper()+'.md'


def card_path(component):
    return page_for(component['group'])+'#'+component['id']


def link(label, target, page):
    path, marker, anchor = target.partition('#')
    relative = posixpath.relpath(path, posixpath.dirname(page) or '.') if path else ''
    if path.endswith('/'):
        relative += '/'
    return '['+label.replace('[', '\\[').replace(']', '\\]')+']('+quote(relative, safe='/.-_')+(marker+anchor if marker else '')+')'


def table(headers, rows):
    clean = lambda v: str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |', '|'+'|'.join('---' for _ in headers)+'|']+
                     ['| '+' | '.join(clean(v) for v in row)+' |' for row in rows])+'\n'


def validate_resources(root, registry, state, tracked_paths=None):
    assert registry['schema'] == 1, 'Unsupported browse registry'
    assert re.fullmatch(r'[0-9a-f]{40}', registry['selection_revision']), 'Missing selection revision'
    primary = {c['id']:c for c in state['components'] if c['role']=='primary' and c['available']}
    rows = registry['components']
    assert len(rows)==len({r['id'] for r in rows}), 'Duplicate browse component'
    assert {r['id'] for r in rows}==set(primary), 'Browse/source component mismatch'
    count = 0
    for row in rows:
        c = primary[row['id']]
        assert row['destination']==c['destination'], 'Browse destination mismatch: '+row['id']
        assert c['group'] in GROUPS and re.fullmatch(r'[a-z0-9-]+', c['id']), c['id']
        receipt = json.loads((root/c['receipt']).read_bytes())
        assert receipt['component']==c['id'] and receipt['destination']==c['destination'], c['id']
        owned = {f['path'] for f in receipt['files']}
        seen = set()
        for a in row['resources']:
            p = a['path']
            assert isinstance(p,str) and p and not p.startswith('/') and '\\' not in p, p
            assert not any(x in ('', '.', '..') for x in p.rstrip('/').split('/')), p
            assert not any(x in p for x in (':', '#', '?')), p
            assert p not in seen, 'Duplicate resource: '+p
            seen.add(p)
            assert a['kind'] in KINDS and a['label'].strip() and '\n' not in a['label'], p
            members = {f for f in owned if f.startswith(p)} if p.endswith('/') else ({p} & owned)
            assert members, 'Resource absent from component receipt: '+row['id']+'/'+p
            if tracked_paths is not None:
                assert all(c['destination']+'/'+f in tracked_paths for f in members), 'Resource absent from Git tree: '+p
            kind = a['kind']
            if kind in ('pdf', 'visual', 'formal_guide'):
                assert p.endswith('.pdf'), 'PDF resource must link to a PDF: '+p
            if kind=='text':
                assert any(f.endswith(('.tex','.md','.txt')) for f in members), 'Text resource lacks text: '+p
            if kind=='lean':
                assert any(f.endswith('.lean') and not f.endswith('lakefile.lean') for f in members), 'Lean source entry has no declarations: '+p
            if kind=='code':
                assert any(f.endswith(CODE_EXTENSIONS) for f in members), 'Code entry lacks code: '+p
            count += 1
    return count


class Browser:
    def __init__(self, root, state, status, tracked_paths=None):
        self.registry = json.loads((root/REGISTRY).read_bytes())
        self.resource_count = validate_resources(root, self.registry, state, tracked_paths)
        self.rows = {r['id']:r for r in self.registry['components']}
        self.components = [c for c in state['components'] if c['id'] in self.rows]
        self.status = status
        self.assessments = {r['id']:r for r in status['components']}

    def held(self, c):
        return self.assessments[c['id']].get('reader_listing',{}).get('placement')=='incubator'

    def resources(self, c, kinds, page):
        return [link(a['label'],c['destination']+'/'+a['path'],page)
                for a in self.rows[c['id']]['resources'] if a['kind'] in kinds]

    def shortcuts(self, c, page):
        assets = self.rows[c['id']]['resources']
        result = []
        for kind, label in [('pdf','PDF'), ('text','Text'), ('lean','Lean'), ('code','Code')]:
            a = next((a for a in assets if a['kind']==kind), None)
            if a:
                result.append(link(label,c['destination']+'/'+a['path'],page))
        return ' · '.join(result+[link('All links',card_path(c),page)])

    def status_line(self, c, page):
        row = self.assessments[c['id']]
        labels = self.status['labels']
        fields = [('Completion','stage'), ('Lean','lean'), ('Confidence','confidence')]
        return ' · '.join('**'+title+':** '+labels[key][row[key]][0] for title,key in fields)

    def footer(self, page):
        return ' · '.join(link(t,p,page) for t,p in [('Browse hub','docs/BROWSE.md'),
                         ('Find proofs','docs/browse/PROOFS.md'),('Lean sources','docs/browse/LEAN.md'),
                         ('Code','docs/browse/CODE.md'),('Collection','README.md')])+'\n'

    def render(self):
        outputs = {}
        page = 'docs/BROWSE.md'
        text = '''# Browse papers, proofs, Lean, and code

Choose a subject below, or go straight to [written statements and proofs](browse/PROOFS.md), [Lean sources](browse/LEAN.md), or [code and scripts](browse/CODE.md).

Each work has direct file links, a source directory, and its completion, Lean, confidence, and evidence record. **PDF** opens a reading file. **Text** opens editable TeX or other source text. **Lean guide** is explanatory reading; **Lean sources** opens actual `.lean` files. Code links can include research utilities and build scripts; follow the edition's README before running them.

## Choose a collection

'''
        text += table(['Collection','Open'],[(title,link(str(sum(c['group']==g for c in self.components))+' works',page_for(g),page)) for g,title in GROUPS.items()])
        text += '''
## Follow a claim

1. Open the work's PDF or text and find the theorem, proposition, or section number.
2. Read the written argument and its assumptions. The [proof finder](browse/PROOFS.md) links manuscript text, selected claim maps, and the existing evidence record.
3. Where formalization exists, follow the [Lean source finder](browse/LEAN.md) and the edition's correspondence/build instructions. A similarly named declaration or a Lean-guide PDF does not by itself establish a correspondence.
4. Use the work's **Status and evidence** link to see what was checked and what remains open. Written proofs do not require Lean.

## Move around without opening large folders

Category pages have a linked contents list and a **Back to contents** link after every work. Use your browser's Find command (Ctrl+F or Command+F) to locate a title. Links carry file-format labels, and status is written in text rather than conveyed by color. TeX links provide source text where available; they are not a claim that every PDF is tagged for assistive technology.

The original files remain in their source directories. If a PDF is too large for GitHub's preview, use the file page's download control. A resource omitted from these selected shortcuts may still exist in the edition contents. The [complete component index](COMPONENT_INDEX.md) includes all supporting and historical collections.

## Small examples and other editions

- [Research Preview 1: mathematical note](../formal/research-preview-1/THEOREM_NOTE.md), [claim map](../formal/research-preview-1/CLAIMS.md), and [reproduction instructions](../formal/research-preview-1/REPRODUCE.md).
- [Corrected SRIC 0.3.3 runtime](../packages/sric-admission-v0.3.3/README.md) and [its bounded qualification](SRIC_REPAIR_2026-10-27.md).
- [Independent libraries and earlier software editions](LIBRARIES.md).
- [Incubator and return criteria](INCUBATOR.md). Incubator entries are marked separately on category pages and excluded from the proof, Lean, and code reading routes.

These are navigation links to preserved editions. Existing scope and scientific status still apply; no new proof review or Lean run is implied.

[Reading guide](START_HERE.md) · [Run and verify](VERIFICATION.md) · [Collection](../README.md)
'''
        outputs[page] = text
        for group,title in GROUPS.items():
            page = page_for(group)
            values = [c for c in self.components if c['group']==group]
            visible = [c for c in values if not self.held(c)]
            held = [c for c in values if self.held(c)]
            text = '# '+title+': reading and source links\n\n'+self.footer(page)
            text += '\nPDF, manuscript text, Lean sources, code, and existing evidence are linked separately. Source files may retain older edition wording; the status link gives the maintained assessment.\n\n<a id="contents"></a>\n\n## Contents\n\n'
            text += table(['Work','Quick links'],[(link(c['title'],'#'+c['id'],page),self.shortcuts(c,page)) for c in visible])
            if held:
                text += '\n### Incubator sources\n\nThese incomplete implementation entries retain their incubator placement and return criteria.\n\n'
                text += '\n'.join('- '+link(c['title'],'#'+c['id'],page) for c in held)+'\n'
            for c in visible+held:
                s = self.assessments[c['id']]
                text += '\n<a id="'+c['id']+'"></a>\n\n## '+c['title']+'\n\n'
                if self.held(c):
                    text += '**Incubator:** '+link('Read the limits and return criteria','docs/INCUBATOR.md#'+c['id'],page)+'.\n\n'
                text += self.status_line(c,page)+'\n\n'
                text += s.get('reader_summary',c['summary'])+'\n\n'
                sections = [('Read',{'pdf','text','guide','visual'}),
                            ('Formal sources and claim guides',{'lean','formal_guide','claims'}),
                            ('Code and scripts',{'code'})]
                for label,kinds in sections:
                    links = self.resources(c,kinds,page)
                    if links:text += '**'+label+':** '+ ' · '.join(links)+'\n\n'
                if s.get('reader_guide'):
                    text += link('Maintained edition guide',s['reader_guide'],page)+'\n\n'
                text += link('Status and evidence','docs/STATUS_CATALOG.md#'+c['id'],page)+' · '+link('All edition files',c['destination']+'/',page)+' · '+link('Source-file receipt',c['receipt'],page)+'\n\n'
                text += '[Back to contents](#contents) · '+link('Browse all collections','docs/BROWSE.md',page)+'\n'
            outputs[page] = text
        for name,title,kinds,intro in [
            ('PROOFS','Find written statements and proofs',{'pdf','text','claims'},
             'Open the manuscript or claim guide, then search for the statement number or section. A selected text source may be part of a multi-file manuscript. These links locate writing and existing evidence; they do not certify every statement. Follow **All links** for visual guides, Lean, code, and the exact edition.'),
            ('LEAN','Find Lean source files',{'lean'},
             'Every source link below contains `.lean` files. The recorded coverage text describes the existing assessment, not a new compiler run. Read the linked work guide for imports, toolchain requirements, correspondence maps, and accepted execution records. Lean-guide PDFs appear on those work pages separately.'),
            ('CODE','Find code and scripts',{'code'},
             'These are entry points to runtime code, examples, checks, and utilities supplied with each edition. Some are build or audit scripts. Read **All links** and the edition README for setup and effects before running them. All software remains beta / work in progress.')]:
            page = 'docs/browse/'+name+'.md'
            text = '# '+title+'\n\n'+self.footer(page)+'\n'+intro+'\n\n'
            text += 'Jump to: '+' · '.join('['+t+'](#'+g+')' for g,t in GROUPS.items())+'\n'
            for group,label in GROUPS.items():
                text += '\n<a id="'+group+'"></a>\n\n## '+label+'\n\n'
                entries = []
                for c in self.components:
                    if c['group']!=group or self.held(c):continue
                    links = self.resources(c,kinds,page)
                    if not links:continue
                    if name=='LEAN':
                        links.append('Coverage: '+self.status['labels']['lean'][self.assessments[c['id']]['lean']][0])
                    links += [link('All links',card_path(c),page),link('Status and evidence','docs/STATUS_CATALOG.md#'+c['id'],page)]
                    entries.append((c['title'],' · '.join(links)))
                text += table(['Work','Open'],entries) if entries else 'No direct resource selected in this category; use its [work index]('+posixpath.basename(page_for(group))+').\n'
            text += '\n'+self.footer(page)
            outputs[page] = text
        return {p:t.rstrip()+'\n' for p,t in outputs.items()}
