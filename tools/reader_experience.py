"""Reading routes and introductions derived from the collection's recorded scope."""
import json
import posixpath
from urllib.parse import quote

SITE = 'https://KomorebiP.github.io/Operation-KOMOREBI/'


def link(label, target, page):
    path, sep, fragment = target.partition('#')
    return '['+label+']('+quote(posixpath.relpath(path, posixpath.dirname(page)), safe='/.-_')+sep+fragment+')'


def load(root):
    data = json.loads((root/'manifests/reader-experience.json').read_bytes())
    assert data['schema'] == 1
    assert len({x['id'] for x in data['glossary']}) == len(data['glossary'])
    return data


def introduction(root, component, assessment, page):
    config = root/'manifests/reader-experience.json'
    if not config.exists():
        return ''
    background = load(root)['background'][component['group']]
    return ('## Before you start\n\n**Suggested background:** '+background+'\n\n'
            '**Recorded results and limits:** '+assessment['scope']+'\n\n'
            '**Remaining work:** '+assessment['next_step']+'\n\n'
            'The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.\n\n'+
            ' · '.join(link(t,p,page) for t,p in [('Reading routes','docs/READING_ROUTES.md'),
            ('Glossary','docs/GLOSSARY.md'),('Claim links','docs/CLAIM_LINKS.md#'+component['id']),
            ('Download this work','docs/DOWNLOADS.md#'+component['id'])])+'\n\n')


ROUTES = {
    'NEW_READER': ('New to Komorebi', '''This route introduces the vocabulary through a small example. It assumes no familiarity with the project.

1. Read the [project introduction](../START_HERE.md) and [authorship statement](../PROJECT_STATEMENT.md).
2. Look up **realization**, **projector**, **packet** and **certificate** in the [glossary](../GLOSSARY.md).
3. Follow the [first software examples](../FIRST_RUN.md). The two-coordinate example separates a vector and reconstructs it.
4. Read the [common computational language](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md).
5. Choose one [work](../BROWSE.md). Read its introduction and recorded limits before following technical references.

Start with vectors and matrices if linear algebra is unfamiliar. You can read the work introductions without installing software.
'''),
    'MATHEMATICS': ('Read the mathematics', '''This is a suggested sequence, not a prerequisite chain for every work.

1. Read [Start here](../START_HERE.md) for the common questions and a finite identity.
2. Open [Paper I](../works/paper-i.md) for typed systems and packet coordinates.
3. Continue to [Paper II](../works/paper-ii.md) for refinement and transfer.
4. Choose a [book or companion volume](../browse/MONOGRAPHS.md) that matches your subject.
5. Use the work's **Written proofs** and **Evidence** sections for precise statements and recorded review scope.

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
2. Follow the [first-run instructions](../FIRST_RUN.md) for Python or the Linux C library.
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
    footer = '\n[Reading routes](../READING_ROUTES.md) · [Browse works](../BROWSE.md) · [Glossary](../GLOSSARY.md)\n'
    for key,(title,body) in ROUTES.items():
        out['docs/routes/'+key+'.md'] = '# '+title+'\n\n'+body+footer
    out['docs/READING_ROUTES.md'] = '# Choose a reading route\n\nStart with the task you want to complete. These routes are editorial suggestions and do not change the recorded status of any work.\n\n'+ '\n'.join('- ['+title+'](routes/'+key+'.md)' for key,(title,_) in ROUTES.items())+'\n\n[Searchable website]('+SITE+') · [Browse works](BROWSE.md) · [Glossary](GLOSSARY.md) · [First runs](FIRST_RUN.md)\n'
    glossary = '# Glossary and notation\n\nThese definitions introduce the finite computational examples. A term can have a more specific meaning in another paper. Follow its definition and hypotheses there.\n\n'
    glossary += ' · '.join('['+x['term']+'](#'+x['id']+')' for x in config['glossary'])+'\n\n'
    for x in config['glossary']:
        glossary += '<a id="'+x['id']+'"></a>\n\n## '+x['term']+'\n\n'+x['definition']+' [Definition and context]('+x['source']+').\n\n'
    glossary += '''## Symbols in the introductory example

| Symbol | Meaning in this example |
|---|---|
| x | The vector being represented |
| Pᵢ | A projector selecting component i |
| I | The identity operator |
| A | Analysis from an object to coordinates |
| S | Synthesis from coordinates to an object |
| T | An operation on the source object |
| QⱼTPᵢ | The part of T from source component i to target component j |

Symbols are local to their definitions. In another paper, the same letter can denote a different object.

[Reading routes](READING_ROUTES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)
'''
    out['docs/GLOSSARY.md']=glossary
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
