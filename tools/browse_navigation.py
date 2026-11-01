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
KINDS = {'guide', 'pdf', 'text', 'visual', 'formal_guide', 'lean_setup', 'lean', 'claims', 'code'}
FINDERS = {'PROOFS': ('written-proofs', {'pdf','text','claims'}),
           'LEAN': ('lean', {'lean'}), 'CODE': ('code', {'code'})}
CODE_EXTENSIONS = ('.py', '.c', '.cpp', '.ipynb', '.rs', '.jl', '.h', '.hpp')
# Maintained corrections live separately from receipt-bound imported editions.
# Keep both routes visible; the existing repair report defines their scope.
CORRECTED_CODE = {'research-sric-external-admission': (
    'Corrected runtime 0.3.3 (source and setup)', 'packages/sric-admission-v0.3.3/',
    'docs/SRIC_REPAIR_2026-10-27.md')}


def page_for(group):
    return 'docs/browse/'+group.upper()+'.md'


def card_path(component):
    return 'docs/works/'+component['id']+'.md'


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
            if kind=='lean_setup':
                assert p.endswith(('.md','.txt')) and not p.endswith('/'), 'Lean instructions must be a text document: '+p
            if kind=='lean':
                assert any(f.endswith('.lean') and not f.endswith('lakefile.lean') for f in members), 'Lean source entry has no declarations: '+p
            if kind=='code':
                assert any(f.endswith(CODE_EXTENSIONS) for f in members), 'Code entry lacks code: '+p
            count += 1
    return count


class Browser:
    def __init__(self, root, state, status, tracked_paths=None):
        self.root = root
        self.registry = json.loads((root/REGISTRY).read_bytes())
        self.resource_count = validate_resources(root, self.registry, state, tracked_paths)
        self.rows = {r['id']:r for r in self.registry['components']}
        self.components = [c for c in state['components'] if c['id'] in self.rows]
        self.status = status
        self.assessments = {r['id']:r for r in status['components']}

    def held(self, c):
        return self.assessments[c['id']].get('reader_listing',{}).get('placement')=='incubator'

    def resources(self, c, kinds, page):
        corrected = CORRECTED_CODE.get(c['id']) if 'code' in kinds else None
        formal = self.assessments[c['id']].get('formal_verification') if 'lean' in kinds else None
        result = []
        if formal:
            result += [link('Checked formal companion: source and reproduction', formal['source_root']+'/README.md', page)]
        if corrected:
            result += [link(corrected[0],corrected[1],page),
                       link('Repair details and recorded checks',corrected[2],page)]
        selected = [a for a in self.rows[c['id']]['resources'] if a['kind'] in kinds]
        selected.sort(key=lambda a: a['kind']!='lean_setup')
        result += [link(('Preserved original edition: ' if (corrected and a['kind']=='code') or (formal and a['kind']=='lean') else '')+a['label'],
                        c['destination']+'/'+a['path'],page)
                   for a in selected]
        return result

    def in_finder(self, c, name):
        return not self.held(c) and any(a['kind'] in FINDERS[name][1] for a in self.rows[c['id']]['resources'])

    def setup_link(self, c, page):
        guide = self.assessments[c['id']].get('reader_guide')
        if guide:
            return link('maintained edition guide',guide,page)
        guide = next((a for a in self.rows[c['id']]['resources'] if a['kind']=='guide'),None)
        return link('edition guide',c['destination']+'/'+guide['path'],page) if guide else '[reading files](#read)'

    def shortcuts(self, c, page):
        assets = self.rows[c['id']]['resources']
        result = []
        for kind, label in [('pdf','PDF'), ('text','Text'), ('lean','Lean'), ('code','Code')]:
            if kind=='code' and c['id'] in CORRECTED_CODE:
                result.append(link(label,CORRECTED_CODE[c['id']][1],page))
                continue
            a = next((a for a in assets if a['kind']==kind), None)
            if a:
                result.append(link(label,c['destination']+'/'+a['path'],page))
        return ' · '.join(result+[link('Work page',card_path(c),page)])

    def status_line(self, c, page):
        row = self.assessments[c['id']]
        labels = self.status['labels']
        fields = [('Completion','stage'), ('Lean','lean'), ('Confidence','confidence')]
        return ' · '.join('**'+title+':** '+labels[key][row[key]][0] for title,key in fields)

    def work_navigation(self):
        return '[Read](#read) · [Written proofs](#written-proofs) · [Lean](#lean) · [Code](#code) · [Evidence](#evidence)'

    def neighbours(self, c, page):
        # Keep incubator entries out of the ordinary reading sequence.
        peers = [v for v in self.components if v['group']==c['group'] and self.held(v)==self.held(c)]
        index = peers.index(c)
        links = []
        if index:
            before = peers[index-1]
            links.append(link('Previous: '+before['title'],card_path(before),page))
        if index+1 < len(peers):
            after = peers[index+1]
            links.append(link('Next: '+after['title'],card_path(after),page))
        return '\n'.join('- '+item for item in links)

    def work_page(self, c):
        page = card_path(c)
        s = self.assessments[c['id']]
        from reader_experience import introduction
        intro = introduction(self.root, c, s, page)
        examples = ' · [Worked examples](#worked-examples-for-this-work)' if '### Worked examples for this work' in intro else ''
        return_navigation = '[Back to work navigation](#work-navigation)'+examples
        text = '# '+c['title']+'\n\n'
        text += link('Browse hub','docs/BROWSE.md',page)+' / '+link(GROUPS[c['group']],page_for(c['group']),page)+'\n\n'
        text += '<a id="work-navigation"></a>\n\n'+self.work_navigation()+examples+'\n\n'
        text += self.status_line(c,page)+'\n\n'+s.get('reader_summary',c['summary'])+'\n\n'
        text += intro
        if self.held(c):
            text += '**Incubator:** '+link('Limits and return criteria','docs/INCUBATOR.md#'+c['id'],page)+'.\n\n'
        text += 'Use the links below to read this work and its supporting files. Ctrl+click (Command+click on macOS) opens a link in another tab. Your browser’s Back button returns here.\n\n'
        sections = [
            ('Read', {'pdf','visual','guide'}, 'For reading files, open the [complete file listing under Evidence](#evidence).'),
            ('Written proofs', {'text','claims'}, 'Written proofs may be in the [reading files](#read). There is no separate text or claim map linked here. The [evidence record](#evidence) describes what has been reviewed.'),
            ('Lean', {'lean','formal_guide','lean_setup','claims'}, 'No Lean source or guide is linked here. See the Lean status above and the [evidence below](#evidence) for the recorded coverage.'),
            ('Code', {'code'}, 'No code shortcut is listed for this edition. Check the [complete file listing under Evidence](#evidence).')]
        for title,kinds,empty in sections:
            text += '## '+title+'\n\n'
            edition=s.get('editorial_edition')
            if title=='Read' and edition:
                text+=link('Revised reading edition',edition['manuscript'],page)+' · '+link('Monograph PDF',edition['pdf'],page)+'\n\n'
            links = self.resources(c,kinds,page)
            if title=='Read' and c['id']=='monographs-special-functions':
                links.insert(0,'[Read online: chapters, proof appendices, figures and glossary](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-special-functions/index.html)')
            if title=='Read' and c['id'] in {'paper-v','paper-vi','paper-vii'}:
                links.insert(0,'[Read online: chapters, figures and proof links](https://KomorebiP.github.io/Operation-KOMOREBI/read/'+c['id']+'/index.html)')
            if title=='Read' and c['id']=='paper-vi':
                links.insert(1,'[Worked visual atlas: all 42 HTML plates](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vi/atlas/index.html)')
            if title=='Read' and c['id']=='paper-vii':
                links.insert(1,'[Worked visual atlas: all 40 HTML plates](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vii/atlas/index.html)')
            if title=='Read' and c['id']=='paper-viii':
                links.insert(0,'[Read online: manuscript, six appendices and figures](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-viii/index.html)')
            if title=='Read' and c['id']=='paper-ix':
                links.insert(0,'[Read online: complete manuscript, strengthening and historical appendices](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ix/index.html)')
            if title=='Read' and c['id']=='paper-x':
                links.insert(0,'[Read online: manuscript, historical continuations and final conditional completion](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-x/index.html)')
            if title=='Written proofs' and edition:
                links.insert(0,link('Mathematical discussion in the revised essay',edition['manuscript'],page))
            has_lean = any(a['kind']=='lean' for a in self.rows[c['id']]['resources'])
            if title=='Written proofs':
                text += 'Find the statement number or section in the [reading files](#read), then read its assumptions and argument. A claim map may cover only part of the written result.\n\n'
            if title=='Lean' and has_lean:
                text += 'Start with the '+self.setup_link(c,page)+' and the build instructions below. Check the correspondence records to see which written claims the Lean declarations cover. Source links lead to `.lean` files. PDF guides explain the formalization.\n\n'
            if title=='Code' and links:
                text += 'These links include code, examples, checks, or build tools. Read the '+self.setup_link(c,page)+' for setup instructions and what each command does. All software is beta and work in progress.\n\n'
            if title=='Lean' and links and not has_lean:
                text += 'The links below are guides and claim maps. No Lean source is linked here. See the [evidence record](#evidence) for the recorded coverage.\n\n'
            text += '\n'.join('- '+item for item in links)+'\n' if links else empty+'\n'
            if title=='Read' and s.get('reader_guide'):
                text += '- '+link('Maintained edition guide',s['reader_guide'],page)+'\n'
            finder = {'Written proofs':'PROOFS','Lean':'LEAN','Code':'CODE'}.get(title)
            if finder and self.in_finder(c,finder):
                text += '\n'+link('Find this work among other '+{'PROOFS':'written proofs','LEAN':'Lean projects','CODE':'code projects'}[finder],
                                  'docs/browse/'+finder+'.md#'+c['id'],page)+'\n'
            text += '\n'+return_navigation+'\n\n'
        text += '## Evidence\n\n'
        text += '- '+link('Completion, Lean coverage, confidence, and cited evidence','docs/STATUS_CATALOG.md#'+c['id'],page)+'\n'
        if s.get('review_report'):
            text += '- '+link('Latest recorded written review',s['review_report'],page)+'\n'
        if s.get('software_verification'):
            text += '- '+link('Recorded software checks',s['software_verification']['path'],page)+'\n'
        if s.get('formal_verification'):
            text += '- '+link('Separate Lean companion replay and scope',s['formal_verification']['path'],page)+'\n'
        if s.get('current_counterpart'):
            other = next(v for v in self.components if v['id']==s['current_counterpart'])
            text += '- '+link('Current counterpart: '+other['title'],card_path(other),page)+'\n'
        text += '- '+link('Source-file receipt (identity and availability)',c['receipt'],page)+'\n'
        text += '- '+link('All files in this source edition',c['destination']+'/',page)+'\n\n'
        text += 'The evidence records describe the reviews and runs completed for this edition.\n\n'
        text += return_navigation+'\n\n## Continue browsing\n\n'
        neighbours = self.neighbours(c,page)
        if neighbours:text += neighbours+'\n'
        text += '- '+link('Back to '+GROUPS[c['group']],page_for(c['group'])+'#contents',page)+'\n'
        text += '- '+link('All collections','docs/BROWSE.md',page)+'\n'
        return text

    def footer(self, page):
        return ' · '.join(link(t,p,page) for t,p in [('Browse hub','docs/BROWSE.md'),
                         ('Find proofs','docs/browse/PROOFS.md'),('Lean sources','docs/browse/LEAN.md'),
                         ('Code','docs/browse/CODE.md'),('Collection','README.md')])+'\n'

    def render(self):
        from reader_experience import render_reader_pages
        outputs = render_reader_pages(self.root, self.components, self.assessments)
        page = 'docs/BROWSE.md'
        text = '''# Browse papers, proofs, Lean, and code

[Searchable website](https://KomorebiP.github.io/Operation-KOMOREBI/) · [Reading routes](READING_ROUTES.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Reading downloads](DOWNLOADS.md)

Browse by [mathematics, computer science, physics or other](https://KomorebiP.github.io/Operation-KOMOREBI/works.html) and combine those filters with **completion stage**, **Lean coverage**, **evidence basis**, publication type and a text query. The [full-text search](https://KomorebiP.github.io/Operation-KOMOREBI/search.html) applies the same work-level classifications to indexed reading pages, claims, code and guides. Or go directly to [written statements and proofs](browse/PROOFS.md), [Lean sources](browse/LEAN.md), or [code and scripts](browse/CODE.md).

Each work has its own page with **Read**, **Written proofs**, **Lean**, **Code**, and **Evidence** sections. **PDF** opens a reading file. **Text** opens editable TeX or other source text. **Lean guide** opens explanatory reading. **Lean sources** leads to `.lean` files. Code links can include research utilities and build scripts. Read the edition's README before running them.

## Browse by discipline and verification

| Primary field | Filtered catalogue |
|---|---|
| Mathematics | [Mathematics works](https://KomorebiP.github.io/Operation-KOMOREBI/works.html?discipline=math#catalog-results) |
| Computer Science | [Computer Science works](https://KomorebiP.github.io/Operation-KOMOREBI/works.html?discipline=cs#catalog-results) |
| Physics | [Physics works](https://KomorebiP.github.io/Operation-KOMOREBI/works.html?discipline=physics#catalog-results) |
| Other | [Methodology and cross-disciplinary works](https://KomorebiP.github.io/Operation-KOMOREBI/works.html?discipline=other#catalog-results) |

These are editorial primary categories. The files remain in their original repository paths so source links and formal evidence references are preserved. A finished reading edition is not necessarily a fully proved research endpoint. **Completion**, **Lean coverage** and **evidence basis** are independent, with details in the [completion guide](COMPLETION_STATUS.md) and [status catalogue](STATUS_CATALOG.md). Filter values come from the maintained [project status manifest](../manifests/project-status.json), not inferred from a file name or its presence in a folder.

## Choose a publication type

'''
        text += table(['Collection','Open'],[(title,link(str(sum(c['group']==g for c in self.components))+' works',page_for(g),page)) for g,title in GROUPS.items()])
        text += '''
## Follow a claim

1. Open the work's PDF or text and find the theorem, proposition, or section number.
2. Read the written argument and its assumptions. The [proof finder](browse/PROOFS.md) links manuscript text, selected claim maps, and the existing evidence record.
3. Where formalization exists, follow the [Lean source finder](browse/LEAN.md) and the edition's claim maps and build instructions. A similarly named declaration or a Lean-guide PDF does not by itself establish a correspondence.
4. Use the work's **Evidence** section to see what was checked and what remains open. Written proofs do not require Lean.

## Move around without opening large folders

Category pages have linked contents and direct file shortcuts. Choose **Work page** to keep one work's paper, proofs, Lean, code, and evidence together. Each work page has a section menu, return links, and previous/next links within its collection. Proof, Lean, and code sections link to their matching finder entry. Each finder links back to the same work section. The status catalogue links back to the same work page. Older category anchors remain usable.

Use your browser's Find command (Ctrl+F or Command+F) to locate a title. Links carry file-format labels, and status is written in text rather than conveyed by color. Work pages use a single-column list layout. TeX links provide source text where available. Some PDFs may lack the tags needed by assistive technology.

The original files remain in their source directories. If a PDF is too large for GitHub's preview, use the file page's download control. If a file is not linked here, check the edition's full file listing. The [complete component index](COMPONENT_INDEX.md) includes all supporting and historical collections.

## Small examples and other editions

- [Research Preview 1: mathematical note](../formal/research-preview-1/THEOREM_NOTE.md), [claim map](../formal/research-preview-1/CLAIMS.md), and [reproduction instructions](../formal/research-preview-1/REPRODUCE.md).
- [Corrected SRIC 0.3.3 runtime](../packages/sric-admission-v0.3.3/README.md) and [its recorded checks](SRIC_REPAIR_2026-10-27.md).
- [Independent libraries and earlier software editions](LIBRARIES.md).
- [Incubator and return criteria](INCUBATOR.md). Incubator entries are marked separately on category pages and excluded from the proof, Lean, and code reading routes.

These are navigation links to preserved editions. See each work's evidence for the reviews and Lean runs completed so far.

[Reading guide](START_HERE.md) · [Run and verify](VERIFICATION.md) · [Collection](../README.md)
'''
        outputs[page] = text
        for c in self.components:
            outputs[card_path(c)] = self.work_page(c)
        for group,title in GROUPS.items():
            page = page_for(group)
            values = [c for c in self.components if c['group']==group]
            visible = [c for c in values if not self.held(c)]
            held = [c for c in values if self.held(c)]
            text = '# '+title+': reading and source links\n\n'+self.footer(page)
            text += '\nPDF, manuscript text, Lean sources, code, and existing evidence are linked separately. Source files may describe an older edition. The status link gives the current assessment.\n\n<a id="contents"></a>\n\n## Contents\n\n'
            text += '\n'.join('- '+link(c['title'],card_path(c),page) for c in visible)+'\n'
            if held:
                text += '\n### Incubator sources\n\nThese entries need more implementation work. Follow each entry for its limits and return criteria.\n\n'
                text += '\n'.join('- '+link(c['title'],'#'+c['id'],page) for c in held)+'\n'
            for c in visible+held:
                text += '\n<a id="'+c['id']+'"></a>\n\n## '+c['title']+'\n\n'
                if self.held(c):
                    text += '**Incubator:** '+link('Read the limits and return criteria','docs/INCUBATOR.md#'+c['id'],page)+'.\n\n'
                text += link('Open work page: '+c['title'],card_path(c),page)+'\n\n'
                text += self.shortcuts(c,page)+'\n\n'
                text += '[Back to contents](#contents) · '+link('Browse all collections','docs/BROWSE.md',page)+'\n'
            outputs[page] = text
        for name,title,kinds,intro in [
            ('PROOFS','Find written statements and proofs',{'pdf','text','claims'},
             'Open the manuscript or claim guide, then search for the statement number or section. A selected text source may be part of a multi-file manuscript. The evidence records state which claims have been reviewed. Follow **Work overview** for visual guides, Lean, code, and the exact edition.'),
            ('LEAN','Find Lean source files',{'lean','lean_setup','claims'},
             'Every work listed below has a selected `.lean` source file or directory. Setup instructions and correspondence maps are labeled separately. The recorded coverage text describes the existing assessment, not a new compiler run. Read the instructions for imports, toolchain requirements, and accepted execution records. Lean-guide PDFs appear on the work pages separately.'),
            ('CODE','Find code and scripts',{'code'},
             'These are entry points to runtime code, examples, checks, and utilities supplied with each edition. Some are build or audit scripts. Read **Work overview** and the edition README for setup instructions and what each command does. All software remains beta / work in progress.')]:
            page = 'docs/browse/'+name+'.md'
            text = '# '+title+'\n\n'+self.footer(page)+'\n'+intro+'\n\n'
            text += '<a id="collections"></a>\n\nJump to: '+' · '.join('['+t+'](#'+g+')' for g,t in GROUPS.items())+'\n'
            for group,label in GROUPS.items():
                text += '\n<a id="'+group+'"></a>\n\n## '+label+'\n\n'
                entries = []
                selected = [c for c in self.components if c['group']==group and self.in_finder(c,name)]
                if selected:
                    text += 'Jump to a work:\n\n'+'\n'.join('- '+link(c['title'],'#'+c['id'],page) for c in selected)+'\n\n'
                for c in selected:
                    links = self.resources(c,kinds,page)
                    if not links:continue
                    if name=='LEAN':
                        links.append('Coverage: '+self.status['labels']['lean'][self.assessments[c['id']]['lean']][0])
                    section = FINDERS[name][0]
                    section_label = 'Lean' if name=='LEAN' else section.replace('-',' ')
                    links += [link('Return to this work’s '+section_label+' section',card_path(c)+'#'+section,page),
                              link('Work overview',card_path(c),page),link('Status and evidence','docs/STATUS_CATALOG.md#'+c['id'],page)]
                    entries.append('<a id="'+c['id']+'"></a>\n\n### '+link(c['title'],card_path(c)+'#'+section,page)+'\n\n'+
                                   '\n'.join('- '+item for item in links)+'\n\n[Back to collection menu](#collections)\n')
                text += '\n'.join(entries) if entries else 'No direct resource is listed in this category. Use its [work index]('+posixpath.basename(page_for(group))+').\n'
                if not entries:text += '\n[Back to collection menu](#collections)\n'
            text += '\n'+self.footer(page)
            outputs[page] = text
        return {p:t.rstrip()+'\n' for p,t in outputs.items()}
