"""Exercise whole-site coverage and capability boundaries for reading guides."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from build_reader_site import Site
from check_reader_site import Page
from reader_documents import page_path
from reading_paths import guide_model, guide_url, publish, render_guide, verify, INDEX, REPORT

ROOT=Path(__file__).resolve().parents[1]


def fixture(output):
    load=lambda name:json.loads((ROOT/'manifests'/name).read_bytes())
    registry=load('browse-resources.json');status=load('project-status.json')
    site=SimpleNamespace(root=ROOT,output=output,revision='reading-paths-test',registry=registry,
        status=status,assessments={r['id']:r for r in status['components']},
        components={r['id']:r for r in load('source-components.json')['components']},
        claims=load('claim-navigation.json'),search=[],editorial_editions={},cache=None)
    site.documents={('collection',r['reader_guide']):'' for r in status['components'] if r.get('reader_guide')}
    for name in ('rel','write','page'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader=SimpleNamespace(site=site,learning=load('reader-experience.json'),records={},lean_works={},
        paper_introductions=load('paper-introductions.json')['papers'],readable_books={})
    for component in registry['components']:
        paths=[r['path'] for r in component['resources']]
        work=component['id'];base=component['destination']+'/'
        intro=reader.paper_introductions.get(work)
        if intro:
            paths.append(intro['setup']['path'].removeprefix(base))
            claim=next(c for c in site.claims['records'] if c['id']==intro['claim'])
            paths.append(claim['statement_path'].removeprefix(base))
        receipt=load('source-imports/'+work+'.json')
        owned={f['path']:f for f in receipt['files']}
        for path in paths:
            if path not in owned:continue  # Directory shortcuts use the work's file list.
            full=base+path;reader.records[full]=dict(work=work,url=page_path(work,full))
    return reader


class ReadingPathsTests(unittest.TestCase):
    def test_all_selected_works_get_three_nonempty_paths_with_their_exact_scope(self):
        reader=fixture(Path('unused'))
        models=[guide_model(reader,c) for c in reader.site.registry['components']]
        self.assertEqual(len(models),90)
        self.assertEqual(len({m['url'] for m in models}),90)
        for model in models:
            self.assertEqual(len(model['paths']),3)
            self.assertEqual(model['scope'],reader.site.assessments[model['work']]['scope'])
            self.assertTrue(all(p['steps'] for p in model['paths']))
            self.assertTrue(all(len({s['url'] for s in p['steps']})==len(p['steps']) for p in model['paths']))

    def test_pdf_only_and_experimental_works_do_not_gain_a_formal_promise(self):
        reader=fixture(Path('unused'))
        component=next(c for c in reader.site.registry['components'] if c['id']=='gaussian-elimination-guide')
        model=guide_model(reader,component)
        self.assertEqual([p['title'] for p in model['paths']],['Worked introduction','Read the work','Evidence and limits'])
        self.assertIn('unassessed',model['scope'])
        self.assertFalse(any('Lean' in s['title'] for p in model['paths'] for s in p['steps']))
        for component in reader.site.registry['components']:
            if reader.site.assessments[component['id']]['lean']=='none':
                model=guide_model(reader,component)
                self.assertEqual(model['paths'][2]['title'],'Evidence and limits')

    def test_core_questions_setup_statements_and_proofs_remain_work_specific(self):
        reader=fixture(Path('unused'))
        for component in reader.site.registry['components'][:12]:
            model=guide_model(reader,component);work=component['id']
            intro=reader.paper_introductions[work]
            self.assertEqual(model['question'],intro['question'])
            self.assertEqual(model['limits'],intro['limits'])
            self.assertIn('#L'+str(intro['setup']['line']),model['paths'][2]['steps'][0]['url'])
            self.assertIn('written proof',model['paths'][2]['steps'][2]['title'])
        reader.paper_introductions['paper-i']['example']='refinement'
        with self.assertRaisesRegex(ValueError,'another work'):guide_model(reader,reader.site.registry['components'][0])

    def test_missing_pdf_and_cross_work_resources_fail_closed(self):
        reader=fixture(Path('unused'));component=reader.site.registry['components'][0]
        pdf=next(r for r in component['resources'] if r['kind']=='pdf')
        path=component['destination']+'/'+pdf['path']
        reader.records[path]['work']='paper-ii'
        with self.assertRaisesRegex(ValueError,'Cross-work'):guide_model(reader,component)
        del reader.records[path]
        with self.assertRaisesRegex(ValueError,'Missing published'):guide_model(reader,component)

    def test_publish_preserves_quantum_and_checker_rejects_missing_guide_or_broken_route(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=fixture(output)
            from quantum_start import publish as publish_quantum
            publish_quantum(reader,None)
            quantum=(output/guide_url('monographs-quantum-and-circuits')).read_bytes()
            rows=publish(reader)
            self.assertEqual((output/guide_url('monographs-quantum-and-circuits')).read_bytes(),quantum)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            # Stand-in destination pages retain their actual source-linked anchors.
            for row in rows:
                for target in row['targets']:
                    path,_,anchor=target.partition('#')
                    if path not in pages:pages[path]=Page('<h1>Target</h1>')
                    if anchor and anchor not in pages[path].ids:pages[path].ids.append(anchor)
                overview='collection/works/'+row['work']+'.html'
                pages.setdefault(overview,Page('<h1>Work overview</h1>'))
                pages[overview].links.append(reader.site.rel(row['url'],overview))
            documents={'source_revision':reader.site.revision}
            self.assertEqual(verify(output,documents,pages),{'works':90,'paths':270})
            self.assertEqual(len([s for s in reader.site.search if s['url']!=INDEX]),90)
            record=json.loads((output/REPORT).read_bytes());record['guides'].pop()
            (output/REPORT).write_text(json.dumps(record),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'every selected'):verify(output,documents,pages)
            (output/REPORT).write_text(json.dumps(dict(source_revision=reader.site.revision,guides=rows)),encoding='utf-8')
            pages[rows[0]['url']].links.remove(reader.site.rel(rows[0]['targets'][0],rows[0]['url']))
            with self.assertRaises(AssertionError):verify(output,documents,pages)

    def test_editorial_metadata_is_escaped_in_the_generated_guide(self):
        with tempfile.TemporaryDirectory() as folder:
            reader=fixture(Path(folder));model=guide_model(reader,reader.site.registry['components'][0])
            model['summary']='<script>unsafe</script>'
            render_guide(reader.site,model)
            text=(reader.site.output/model['url']).read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;',text)
            self.assertNotIn('<script>unsafe</script>',text)

    def test_every_work_toolbar_prominently_links_its_own_guide(self):
        from reader_documents import ReadingDocuments
        reader=fixture(Path('unused'));reader.primary_pdf=lambda work:None
        reader.manuscript_roots={}
        reader.work_route_targets=lambda work:ReadingDocuments.work_route_targets(reader,work)
        for component in reader.site.registry['components']:
            work=component['id'];page='collection/works/'+work+'.html'
            body=ReadingDocuments.work_intro(reader,work,page)
            primary=body.split('<details class="work-more">')[0]
            self.assertIn('<a class="button" href="'+reader.site.rel(guide_url(work),page)+'">Start here</a>',primary)
            self.assertEqual(Page(body).links.count(reader.site.rel(guide_url(work),page)),1)


if __name__=='__main__':unittest.main()
