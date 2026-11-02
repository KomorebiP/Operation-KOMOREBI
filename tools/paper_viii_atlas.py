"""Paper VIII's complete source-bound visual guide and stable-label crosswalk."""
import json
from readable_chapters import clean_tex,presentation_tex,KIND_NAMES
from worked_visual_atlas import WorkedAtlas
from paper_viii_atlas_sources import SPEC
from paper_viii_atlas_drawings import drawing_nodes
from paper_viii_atlas_descriptions import FIGURES


class PaperVIIIAtlas(WorkedAtlas):
    def read_plates(self,read):
        selected=[]
        for source,start,count in zip(self.SOURCES,(1,29),(28,4)):
            selected+=self.plates(read(source).decode('utf-8-sig'),start,count,source)
        crosswalk=json.loads(read(next(iter(self.EXTRAS))))
        from reader_atlas import digest
        if crosswalk['status']!='PASS' or crosswalk['traditional_source_sha256']!=digest(read(self.BOOK['main'])):
            raise ValueError('Paper VIII crosswalk has a different manuscript source binding')
        # The retained crosswalk's PDF checksum is stale. Its original bytes stay
        # unchanged; the current PDF pages are independently checked by the crop
        # recipe, and its stable labels are rechecked against the manuscript.
        if crosswalk['visual_pdf_sha256']!='63d0a88a9f5e055c9ddb4e862cb8ee7549342c8bb890c2f15c1c035423097801':
            raise ValueError('Review the inherited Paper VIII crosswalk PDF identity')
        if len(crosswalk['pages'])!=self.HTML_COUNT:raise ValueError('Paper VIII crosswalk inventory changed')
        for plate,row in zip(selected,crosswalk['pages']):
            if SPEC['pdf_page_checks'][plate['number']-1]!=dict(plate=plate['number'],pdf_page=plate['number']+2,title=plate['title'],locator=plate['locator']):
                raise ValueError('Paper VIII source differs from the current PDF page checks')
            if (row['visual_page'],row['title'],row['source_line_current'],row['visual_physical_pdf_page'])!=(plate['number'],plate['title'],plate['locator'],plate['number']+self.PDF_PAGE_OFFSET):
                raise ValueError('Paper VIII plate differs from its source crosswalk: '+str(plate['number']))
            plate['reference_keys']=[target['final_label'] for target in row['traditional_targets']]
            if not plate['reference_keys']:raise ValueError('Paper VIII plate has no manuscript route')
        self.crosswalk=crosswalk
        return selected

    def reference_keys(self,plate):return plate['reference_keys']

    def reference_map(self,chapters):
        references={key:(chapter,node) for _,_,chapter in chapters for key,node in chapter.labels.items() if node.get('url')==chapter.url}
        normalize=lambda s:presentation_tex(clean_tex(s)).strip()
        for row in self.crosswalk['pages']:
            for target in row['traditional_targets']:
                key=target['final_label']
                if key not in references:raise ValueError('Paper VIII manuscript label no longer resolves: '+key)
                chapter,node=references[key]
                kind='Appendix' if node['kind']=='section' and node['number'].isalpha() else ('Section' if node['kind'] in ('section','subsection','subsubsection') else KIND_NAMES.get(node['kind'],node['kind'].capitalize()))
                expected_kind='Standard fact' if key=='fact:cg' and target['kind']=='Classical input' else target['kind']
                if (node['number'],kind,normalize(node['title']))!=(target['number'],expected_kind,normalize(target['title_tex'])):
                    raise ValueError('Paper VIII crosswalk statement changed: '+key+' '+str((node['number'],kind,node['title'])))
        return references

    def reference_route(self,key,reference):
        chapter,node=reference
        return node.get('reference_label') or KIND_NAMES.get(node['kind'],node['kind'].capitalize())+' '+node['number'],chapter.url+'#'+node['id']

    def drawing_nodes(self,source,name):return drawing_nodes(source,name)

    def atlas_tex(self,text):return super().atlas_tex(text.replace(r'\captiontext{',r'\platecaption{'))

    def edition_checks(self):
        return dict(inherited_crosswalk_pdf_sha256='63d0a88a9f5e055c9ddb4e862cb8ee7549342c8bb890c2f15c1c035423097801',
            retained_pdf_sha256=self.PDF_SHA256,crosswalk_pdf_checksum_current=False,pdf_page_checks=SPEC['pdf_page_checks'],
            inherited_reference_kind_translation={'fact:cg':{'crosswalk':'Classical input','manuscript':'Standard fact'}},
            isolated_drawing_objects=self.ISOLATED_DRAWINGS,
            manuscript_targets='Stable labels, statement numbers, kinds and titles independently rechecked against the retained manuscript source')

    def edition_note(self):
        return '<p>The inherited reference crosswalk records a different PDF checksum. This conversion uses the retained PDF identified below: all 32 plate titles, printed locators and page labels were independently checked. Manuscript links use stable source labels checked against the current manuscript. The guide’s “Classical input 7.5” resolves to the manuscript’s “Standard fact 7.5” at the same label. The imported crosswalk is preserved unchanged.</p>'


TABLE_AIDS={
 (2,'L17'):dict(caption='Objects and their contracts',headers=['Symbol','Object','Question to ask'],row_header_column=0),
 (28,'L472'):dict(caption='Evidence and its precise use in the source edition',headers=['Evidence','Its precise use here'],row_header_column=0),
 (31,'L44'):dict(caption='Additive costs for keeping or splitting the common tree',headers=['Cost component','Keep','Split'],row_header_column=0),
}
ATLAS=PaperVIIIAtlas('paper-viii',SPEC,FIGURES,TABLE_AIDS)
prepare=ATLAS.prepare
render=ATLAS.render
verify=ATLAS.verify
