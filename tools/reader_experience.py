"""Reading routes and introductions derived from the collection's recorded scope."""
import json
import ast
import posixpath
import re
from urllib.parse import quote

SITE = 'https://KomorebiP.github.io/Operation-KOMOREBI/'


def link(label, target, page):
    path, sep, fragment = target.partition('#')
    return '['+label+']('+quote(posixpath.relpath(path, posixpath.dirname(page)), safe='/.-_')+sep+fragment+')'


def load(root):
    data = json.loads((root/'manifests/reader-experience.json').read_bytes())
    assert data['schema'] == 1
    assert len({x['id'] for x in data['glossary']}) == len(data['glossary'])
    identifiers={x['id'] for x in data['glossary']}
    sections={x['id'] for x in data.get('glossary_sections',[])}
    for term in data['glossary']:
        if sections:assert term['section'] in sections
        assert set(term.get('related',[])) <= identifiers
    topics=data.get('learning_topics',[])
    assert len({x['id'] for x in topics})==len(topics)
    assert len({x['example'] for x in topics})==len(topics)
    for topic in topics:
        assert set(topic['terms']) <= identifiers
    return data


def introduction(root, component, assessment, page):
    config = root/'manifests/reader-experience.json'
    if not config.exists():
        return ''
    data = load(root)
    background = data['background'][component['group']]
    text = ('## Before you start\n\n**Suggested background:** '+background+'\n\n'
            '**Recorded results and limits:** '+assessment['scope']+'\n\n'
            '**Remaining work:** '+assessment['next_step']+'\n\n'
            'The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.\n\n'+
            ' · '.join(link(t,p,page) for t,p in [('Reading routes','docs/READING_ROUTES.md'),
            ('Glossary','docs/GLOSSARY.md'),('Claim links','docs/CLAIM_LINKS.md#'+component['id']),
            ('Download this work','docs/DOWNLOADS.md#'+component['id'])])+'\n\n')
    topics=[t for t in data.get('learning_topics',[]) if component['id'] in t['works']]
    if topics:
        text+='### Worked examples for this work\n\n'
        text+='These introductory calculations lead into this work’s subject. The source and evidence links below retain the work’s recorded scope.\n\n'
        for topic in topics:
            text+='- '+link(str(topic['number'])+'. '+topic['title'],topic['example'],page)+' · '+link('Terms and source routes','docs/LEARNING_MAP.md#'+topic['id'],page)+'\n'
        text+='\n'
    return text


ROUTES = {
    'NEW_READER': ('New to Komorebi', '''This route introduces the vocabulary through a small example. It assumes no familiarity with the project.

1. Read the [project introduction](../START_HERE.md) and [authorship statement](../PROJECT_STATEMENT.md).
2. Look up **realization**, **projector**, **packet** and **certificate** in the [glossary](../GLOSSARY.md).
3. Work through [splitting and reconstructing a vector by hand](../examples/01_PACKETS.md). Continue through the [hand-worked examples](../HAND_WORKED_EXAMPLES.md) at your own pace.
4. Try the [first software examples](../FIRST_RUN.md) when you want to compare a program with the hand calculations.
5. Read the [common computational language](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md).
6. Choose one [work](../BROWSE.md). Read its introduction and recorded limits before following technical references.

Start with vectors and matrices if linear algebra is unfamiliar. You can read the work introductions without installing software.
'''),
    'MATHEMATICS': ('Read the mathematics', '''This is a suggested sequence, not a prerequisite chain for every work.

1. Read [Start here](../START_HERE.md) for the common questions and a finite identity.
2. Use the [hand-worked examples](../HAND_WORKED_EXAMPLES.md) for concrete calculations with packets, seeds, coordinates and obstructions.
3. Open [Paper I](../works/paper-i.md) for typed systems and packet coordinates.
4. Continue to [Paper II](../works/paper-ii.md) for refinement and transfer.
5. Choose a [book or companion volume](../browse/MONOGRAPHS.md) that matches your subject.
6. Use the work's **Written proofs** and **Evidence** sections for precise statements and recorded review scope.

Keep the coefficient system, topology, finiteness conditions and application assumptions with each statement. A shared vocabulary does not make the hypotheses of different works interchangeable.
'''),
    'PROOF_REVIEW': ('Inspect a proof', '''Written proofs can stand on their own. Lean coverage and software tests answer additional, separate questions.

1. Select the exact edition from a [work page](../BROWSE.md).
2. Read the written statement, hypotheses and proof. Use the [claim index](../CLAIM_LINKS.md) where a detailed map is available.
3. Read the work's evidence record and any recorded restrictions.
4. For a mapped Lean claim, compare the full formal type with the written statement. Follow its exact source and pinned reproduction instructions.
5. For computation, identify the tested inputs, arithmetic, acceptance criteria and source revision.

The [completion guide](../COMPLETION_STATUS.md#lean-coverage) explains the labels. The [verification guide](../VERIFICATION.md) separates source identity, compiler execution and mathematical review. This route does not perform a new proof audit.
'''),
    'SOFTWARE': ('Run the software', '''Choose the library and environment before installing dependencies. All software remains beta and work in progress.

1. Use the [software guide](../LIBRARIES.md) to choose a library.
2. Follow the [first-run instructions](../FIRST_RUN.md) for Python or the Linux C library. The [hand calculations](../HAND_WORKED_EXAMPLES.md) explain the basic operations without software.
3. Compare your output with the stated result and record the source revision.
4. Continue to [Komorebi Math worked examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/WORKED_EXAMPLES.md) or [Polyphase Float's complete C programs](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/README.md).
5. Use the library's testing instructions to check the operations you intend to use.

Komorebi Math supports its declared Python environments. Polyphase Float's supported build baseline is Linux x86-64, LP64 and 64-bit GMP limbs. Windows readers should use its documented Linux/WSL route.
''')}


def render_reader_pages(root, components, assessments):
    if not (root/'manifests/reader-experience.json').exists():
        return {}
    config = load(root)
    out = {}
    out.update(render_learning_pages(root, config, components))
    footer = '\n[Reading routes](../READING_ROUTES.md) · [Hand-worked examples](../HAND_WORKED_EXAMPLES.md) · [Browse works](../BROWSE.md) · [Glossary](../GLOSSARY.md)\n'
    for key,(title,body) in ROUTES.items():
        out['docs/routes/'+key+'.md'] = '# '+title+'\n\n'+body+footer
    out['docs/READING_ROUTES.md'] = '# Choose a reading route\n\nStart with the task you want to complete. These routes are editorial suggestions and do not change the recorded status of any work.\n\n'+ '\n'.join('- ['+title+'](routes/'+key+'.md)' for key,(title,_) in ROUTES.items())+'\n\n[Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Searchable website]('+SITE+') · [Browse works](BROWSE.md) · [Glossary](GLOSSARY.md) · [First runs](FIRST_RUN.md)\n'
    out['docs/GLOSSARY.md']=render_glossary(config)
    downloads='# Download one work\n\nThe [website downloads]('+SITE+'downloads.html) provide a separate reading ZIP for each work. Each contains its selected reading files, linked claim guides, available license notices, a source revision and SHA-256 checksums. The website lists file counts and sizes before download.\n\nThese are reading selections. TeX may depend on additional files, and the ZIP is not a complete Lean or software build. Use the source instructions below for a full component.\n\n'
    claims='# Follow a written claim\n\nThe [searchable claim index]('+SITE+'claims.html) begins with Paper I’s 108 correspondence records. Only 69 are labeled covered in the source record. Definitions, boundaries and documentary entries remain separately labeled. This is navigation through recorded evidence, not a new acceptance run or proof review.\n\nEach entry links the written statement and proof when recorded, the declared Lean modules and the work’s code and evidence. Module locations come from the retained declaration inventory. Code is linked at work level unless a claim-specific test is recorded. A link does not establish a new correspondence.\n\n'
    for c in components:
        identifier=c['id']
        downloads += '<a id="'+identifier+'"></a>\n\n## '+c['title']+'\n\n[Reading ZIP and contents]('+SITE+'downloads.html#'+identifier+') · '+link('Work and evidence','docs/works/'+identifier+'.md','docs/DOWNLOADS.md')+'\n\n'
        claims += '<a id="'+identifier+'"></a>\n\n## '+c['title']+'\n\n'
        if identifier=='paper-i':
            claims+='[Open the 108 recorded claim entries]('+SITE+'claims.html#paper-i).\n\n'
        else:
            claims+='A detailed statement index has not yet been transcribed for this work. Follow its written proofs and any linked correspondence map. This does not imply that a map or proof is absent from the source edition.\n\n'
        claims += link('Written proofs','docs/works/'+identifier+'.md#written-proofs','docs/CLAIM_LINKS.md')+' · '+link('Lean','docs/works/'+identifier+'.md#lean','docs/CLAIM_LINKS.md')+' · '+link('Code','docs/works/'+identifier+'.md#code','docs/CLAIM_LINKS.md')+' · '+link('Evidence','docs/works/'+identifier+'.md#evidence','docs/CLAIM_LINKS.md')+'\n\n'
    downloads+='## Obtain a full component\n\nUse Git 2.25 or later for sparse checkout. Replace COMPONENT_PATH with the exact source directory linked from the work page. Record the checked-out revision.\n\n```text\ngit clone --filter=blob:none --no-checkout https://github.com/KomorebiP/Operation-KOMOREBI.git komorebi-work\ncd komorebi-work\ngit sparse-checkout init --cone\ngit sparse-checkout set COMPONENT_PATH\ngit checkout main\ngit rev-parse HEAD\n```\n\nThis obtains the selected component and root files. Dependencies or sibling projects named by its build instructions may still need to be added. For the complete collection checks, use a full checkout as described in [Verification](VERIFICATION.md).\n\n[Browse works](BROWSE.md) · [Reading routes](READING_ROUTES.md)\n'
    claims+='[Browse works](BROWSE.md) · [Evidence labels](COMPLETION_STATUS.md)\n'
    out['docs/DOWNLOADS.md']=downloads
    out['docs/CLAIM_LINKS.md']=claims
    return {p:s.rstrip()+'\n' for p,s in out.items()}


def render_glossary(config):
    terms={x['id']:x for x in config['glossary']}
    text='# Glossary and notation\n\n'
    text+='This guide explains '+str(len(terms))+' terms used in the collection and its finite examples. '
    text+='Start with a subject below, use the [alphabetical index](#alphabetical-index), or look up [symbols](#symbols-in-the-introductory-example).\n\n'
    text+='A word can have a more specific meaning in another paper. The paper’s definitions and hypotheses take precedence. Examples and source links provide context without changing any recorded evidence status.\n\n'
    text+='[Work through the calculations by hand](HAND_WORKED_EXAMPLES.md) · [Papers, proofs, Lean and code by topic](LEARNING_MAP.md) · [First software runs](FIRST_RUN.md)\n\n'
    for section in config['glossary_sections']:
        text+='- ['+section['title']+'](#'+section['id']+')\n'
    text+='\n'
    for section in config['glossary_sections']:
        group=[x for x in config['glossary'] if x['section']==section['id']]
        text+='<a id="'+section['id']+'"></a>\n\n## '+section['title']+'\n\n'+section['description']+'\n\n'
        text+=' · '.join('['+x['term']+'](#'+x['id']+')' for x in group)+'\n\n'
        for term in group:
            text+='<a id="'+term['id']+'"></a>\n\n### '+term['term']+'\n\n'+term['definition']+'\n\n'
            if term.get('note'):text+='**Keep in mind:** '+term['note']+'\n\n'
            links=[]
            if term.get('example'):links.append('[Hand-worked example]('+term['example']+')')
            if term.get('source')!=term.get('example'):
                links.append('[Further reading]('+term['source']+')')
            topics=[t for t in config.get('learning_topics',[]) if term['id'] in t['terms'] or t['example']=='docs/'+term.get('example','')]
            if topics:
                links.append('[Papers, proofs, Lean and code](LEARNING_MAP.md#'+topics[0]['id']+')')
            elif term['section']=='claims-and-evidence':
                links.append('[How to inspect a proof](routes/PROOF_REVIEW.md)')
            links.extend('['+terms[key]['term']+'](#'+key+')' for key in term.get('related',[]))
            text+=' · '.join(links)+'\n\n'
    text+='## Symbols in the introductory example\n\n'
    text+='The examples use the following notation. The reading column spells out symbols for readers who are unfamiliar with them.\n\n'
    text+='| Symbol | Read as | Meaning here |\n|---|---|---|\n'
    for row in config['notation']:
        text+='| '+' | '.join(row)+' |\n'
    text+='\nSymbols are local to their definitions. In another paper, the same letter can denote a different object.\n\n'
    text+='## Alphabetical index\n\n'
    text+=' · '.join('['+x['term']+'](#'+x['id']+')' for x in sorted(config['glossary'],key=lambda x:x['term'].casefold()))+'\n\n'
    text+='[Reading routes](READING_ROUTES.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)\n'
    return text


def source_routes(topic, components, page):
    text=topic['scope']+'\n\n'
    text+='| Related work | Paper or book | Written proofs | Lean | Code | Evidence |\n|---|---|---|---|---|---|\n'
    for identifier in topic['works']:
        component=components[identifier]
        base='docs/works/'+identifier+'.md'
        cells=[component['title']]+[link(label,base+'#'+anchor,page) for label,anchor in
            [('Read','read'),('Proofs','written-proofs'),('Coverage and sources','lean'),('Code and setup','code'),('Status','evidence')]]
        text+='| '+' | '.join(cells)+' |\n'
    text+='\n[Related library guide and code examples]('+topic['code_guide']+'). The guide covers related constructions and their software interfaces.\n\n'
    if topic.get('check'):
        text+=link('Python arithmetic check for this example: '+topic['check']+'()', 'tools/check_hand_examples.py#L'+str(topic['_check_line']),page)+'. This checks the displayed finite calculations with exact fractions.\n\n'
    text+='The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.\n\n'
    return text


def render_learning_pages(root, config, components):
    topics=config.get('learning_topics',[])
    if not topics:return {}
    if any(t.get('check') for t in topics):
        checks=ast.parse((root/'tools/check_hand_examples.py').read_text(encoding='utf-8'))
        lines={node.name:node.lineno for node in checks.body if isinstance(node,ast.FunctionDef)}
        topics=[dict(t, _check_line=lines[t['check']]) for t in topics]
    works={c['id']:c for c in components}
    terms={x['id']:x['term'] for x in config['glossary']}
    assert all(set(t['works'])<=set(works) for t in topics)
    page='docs/LEARNING_MAP.md'
    text='# From examples to papers, proofs, Lean and code\n\n'
    text+='Choose a topic to move from a hand calculation to definitions and related source material. Each linked work has return links to these examples. These are subject routes, not new theorem-to-Lean correspondences.\n\n'
    text+='[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md)\n\n'
    text+='## Topics\n\n'+ '\n'.join('- ['+str(t['number'])+'. '+t['title']+'](#'+t['id']+')' for t in topics)+'\n\n'
    out={}
    marker='<!-- learning-navigation -->'
    for index,topic in enumerate(topics):
        text+='<a id="'+topic['id']+'"></a>\n\n## '+str(topic['number'])+'. '+topic['title']+'\n\n'
        text+=link('Work through the example',topic['example'],page)+'\n\n'
        text+='**Terms:** '+' · '.join(link(terms[x],'docs/GLOSSARY.md#'+x,page) for x in topic['terms'])+'\n\n'
        text+=source_routes(topic,works,page)+'[Back to topics](#topics)\n\n'
        example=topic['example']
        body=(root/example).read_text(encoding='utf-8').split(marker)[0].rstrip()
        body=re.sub(r'\n\[(?:Previous|Next):[^\n]+$', '', body).rstrip()
        jump='[Papers, proofs, Lean and code](#papers-proofs-lean-and-code)'
        if jump not in body:
            body=re.sub(r'(^\[All examples\][^\n]*)',lambda m:m[1]+' · '+jump,body,count=1,flags=re.M)
        body+='\n\n'+marker+'\n\n## Papers, proofs, Lean and code\n\n'
        body+='**Terms in this example:** '+' · '.join(link(terms[x],'docs/GLOSSARY.md#'+x,example) for x in topic['terms'])+'\n\n'
        body+=source_routes(topic,works,example)
        footer=[]
        if index:footer.append(link('Previous: '+topics[index-1]['title'],topics[index-1]['example'],example))
        if index+1<len(topics):footer.append(link('Next: '+topics[index+1]['title'],topics[index+1]['example'],example))
        footer.extend([link('All examples','docs/HAND_WORKED_EXAMPLES.md',example),link('Topic map',page+'#'+topic['id'],example)])
        out[example]=body+' · '.join(footer)+'\n'
    out[page]=text+'[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Reading routes](READING_ROUTES.md)\n'
    return out
