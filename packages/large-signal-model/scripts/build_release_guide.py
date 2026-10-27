"""Build the release guide from structured content and measured figure assets.

Requires the paper extra: Matplotlib and ReportLab. Fonts are resolved from
Matplotlib's bundled DejaVu family, embedded in the PDF, and not distributed
as standalone files. Page text is also exported as Markdown.
"""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
import re
from functools import partial
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, XPreformatted, KeepTogether
from matplotlib import font_manager
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs'


def register_fonts() -> None:
    for name,family,weight,style in [('Body','DejaVu Serif','normal','normal'),
                                   ('BodyBold','DejaVu Serif','bold','normal'),
                                   ('Sans','DejaVu Sans','normal','normal'),
                                   ('SansBold','DejaVu Sans','bold','normal'),
                                   ('Mono','DejaVu Sans Mono','normal','normal')]:
        path=font_manager.findfont(font_manager.FontProperties(family=family,weight=weight,style=style),fallback_to_default=False)
        pdfmetrics.registerFont(TTFont(name,path))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
    pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='Sans',boldItalic='SansBold')


def main() -> None:
    register_fonts()
    data=json.loads((DOCS/'release_guide_content.json').read_text())
    width,height=A4;content_width=width-96
    styles={
        'p':ParagraphStyle('Body',fontName='Body',fontSize=9.5,leading=13.8,spaceAfter=8,splitLongWords=False),
        'h':ParagraphStyle('Heading',fontName='SansBold',fontSize=11,leading=15,spaceBefore=7,spaceAfter=5,keepWithNext=True),
        'title':ParagraphStyle('Title',fontName='SansBold',fontSize=23,leading=29,spaceAfter=16),
        'cover':ParagraphStyle('Cover',fontName='SansBold',fontSize=33,leading=40,spaceAfter=19),
        'kicker':ParagraphStyle('Kicker',fontName='Sans',fontSize=8.3,leading=12,spaceAfter=12,textColor=colors.HexColor('#4b4b4b')),
        'caption':ParagraphStyle('Caption',fontName='Sans',fontSize=8.2,leading=11.3,spaceAfter=11,textColor=colors.HexColor('#383838')),
        'note':ParagraphStyle('Note',fontName='Sans',fontSize=9,leading=13,spaceBefore=4,spaceAfter=8),
        'code':ParagraphStyle('Code',fontName='Mono',fontSize=7.75,leading=11.2,spaceBefore=3,spaceAfter=10),
        'cell':ParagraphStyle('Cell',fontName='Sans',fontSize=8.4,leading=11.7),
        'cellhead':ParagraphStyle('CellHead',fontName='SansBold',fontSize=8.5,leading=11.7),
    }
    story=[];md=['# Komorebi Large Signal Model\n\nRelease 2.3.0 · Komorebi P. · 9 October 2026\n']
    for idx,page in enumerate(data['pages']):
        if idx: story.append(PageBreak())
        story.append(Paragraph(escape(page['kicker']),styles['kicker']))
        story.append(Paragraph(escape(page['title']).replace('\n','<br/>'),styles['cover' if idx==0 else 'title']))
        md.append('\n## '+page['title'].replace('\n',' ')+'\n')
        for block in page['blocks']:
            kind=block['kind']
            if kind in ('p','h'):
                story.append(Paragraph(escape(block['text']),styles[kind]))
                md.append(('\n### ' if kind=='h' else '\n')+block['text']+'\n')
            elif kind=='note':
                cell=Paragraph(escape(block['text']),styles['note'])
                box=Table([[cell]],colWidths=[content_width],hAlign='LEFT')
                box.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f2f2f2')),
                                         ('BOX',(0,0),(-1,-1),.4,colors.HexColor('#c0c0c0')),
                                         ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
                                         ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
                story.extend([box,Spacer(1,9)]);md.append('\n> '+block['text']+'\n')
            elif kind=='code':
                text=block['text']
                story.append(XPreformatted(escape(text),styles['code']))
                md.append('\n```text\n'+text+'\n```\n')
            elif kind=='table':
                headers=block['headers'];rows=block['rows']
                weights=block.get('widths') or [1]*len(headers)
                widths=[content_width*v/sum(weights) for v in weights]
                cells=[[Paragraph(escape(v),styles['cellhead']) for v in headers]]
                cells += [[Paragraph(escape(v),styles['cell']) for v in row] for row in rows]
                tbl=Table(cells,colWidths=widths,hAlign='LEFT',repeatRows=1)
                tbl.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('VALIGN',(0,0),(-1,-1),'TOP'),
                                        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),
                                        ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#777777')),
                                        ('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d0d0d0')),
                                        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                                        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
                story.extend([tbl,Spacer(1,12)])
                md.append('\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n' + '\n'.join('| '+' | '.join(row)+' |' for row in rows)+'\n')
            elif kind=='figure':
                path=DOCS/'figures'/f"{block['name']}.png"
                with PILImage.open(path) as im: image_width,image_height=im.size
                display_width=content_width
                display_height=display_width*image_height/image_width
                # Group the figure and caption so no orphan caption appears.
                story.append(KeepTogether([Image(str(path),width=display_width,height=display_height),
                                           Spacer(1,5),Paragraph(escape(block['caption']),styles['caption'])]))
                md.append(f"\n![{block['caption']}](figures/{block['name']}.png)\n")
            else:
                raise ValueError(f'Unknown content kind: {kind}')
    def decorate(canvas,doc):
        canvas.saveState()
        canvas.setFont('Sans',7.6)
        canvas.setFillGray(.35)
        if doc.page>1:
            canvas.drawString(48,height-30,'OPERATION KOMOREBI / LARGE SIGNAL MODEL')
            canvas.drawRightString(width-48,height-30,'2.3.0')
            canvas.setStrokeGray(.72);canvas.setLineWidth(.35)
            canvas.line(48,height-36,width-48,height-36)
        canvas.setFont('Sans',7.2)
        canvas.drawString(48,25,'Komorebi P.  |  Source release and verification guide  |  9 October 2026')
        canvas.drawRightString(width-48,25,str(doc.page))
        canvas.restoreState()
    target=DOCS/'RELEASE_GUIDE.pdf'
    pdf=SimpleDocTemplate(str(target),pagesize=A4,initialFontName='Sans',leftMargin=48,rightMargin=48,topMargin=53,bottomMargin=47,
                          title='Komorebi Large Signal Model 2.3.0: Implementation and Verification Guide',
                          author='Komorebi P.',subject='Finite exact-coordinate model, continuous signals, typed regression and verification',
                          pageCompression=1)
    pdf.build(story,onFirstPage=decorate,onLaterPages=decorate,
              canvasmaker=partial(Canvas, initialFontName="Sans"))
    (DOCS/'RELEASE_GUIDE.md').write_text(''.join(md),encoding='utf-8')
    print(f'Created {target} and Markdown companion')


if __name__=='__main__':
    main()
