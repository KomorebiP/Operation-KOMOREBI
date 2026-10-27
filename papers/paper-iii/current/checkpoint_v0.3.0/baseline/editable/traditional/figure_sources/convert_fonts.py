"""Preserve the bundled Nimbus Sans design in PDF-compatible TrueType fonts.

Matplotlib's PDF backend labels CFF/OpenType input as CIDFontType2.  Its
TrueType path is unambiguous.  FontTools converts cubic outlines to quadratic
ones with maximum error 0.5/1000 em; font metrics and Unicode maps are retained.
The original bundled fonts and their license remain the authoritative source.
"""
from pathlib import Path
import hashlib
import json
import os
import time
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


def converted_fonts():
    base=Path(__file__).resolve().parent
    out=base/'fonts';out.mkdir(exist_ok=True)
    record_path=out/'conversion.json'
    record=json.loads(record_path.read_text()) if record_path.exists() else {}
    paths=[]
    for weight in ['Regular','Bold','Italic','BoldItalic']:
        source=base.parent/'fonts'/f'NimbusSans-{weight}.otf'
        target=out/f'NimbusSans-{weight}.ttf'
        fingerprint=hashlib.sha256(source.read_bytes()).hexdigest()
        if not target.exists() or record.get(weight,{}).get('source_sha256')!=fingerprint or record.get(weight,{}).get('recipe')!='quadratic-v2':
            font=TTFont(source,recalcTimestamp=False)
            glyph_set=font.getGlyphSet()
            glyphs={}
            for name in font.getGlyphOrder():
                pen=TTGlyphPen(None)
                glyph_set[name].draw(Cu2QuPen(pen,max_err=.5,reverse_direction=True))
                glyphs[name]=pen.glyph()
            font['glyf']=newTable('glyf');font['glyf'].glyphs=glyphs
            font['loca']=newTable('loca')
            font['maxp']=newTable('maxp');font['maxp'].tableVersion=0x00010000
            for key,value in {'maxZones':2,'maxTwilightPoints':0,'maxStorage':0,
                              'maxFunctionDefs':0,'maxInstructionDefs':0,'maxStackElements':0,
                              'maxSizeOfInstructions':0}.items():
                setattr(font['maxp'],key,value)
            font['post'].formatType=2.0
            font['post'].extraNames=[]; font['post'].mapping={}
            del font['CFF ']
            font.sfntVersion='\x00\x01\x00\x00'
            # A fixed valid timestamp keeps the derived font deterministic.
            font['head'].created=3874348800; font['head'].modified=3874348800
            for name in font['name'].names:
                if name.nameID in {1,16}:
                    name.string='Komorebi Nimbus Sans'.encode(name.getEncoding())
                elif name.nameID in {4,6}:
                    name.string=('KomorebiNimbusSans-'+weight).encode(name.getEncoding())
            temp=target.with_suffix('.pending.ttf');font.save(temp)
            before=target.stat().st_mtime if target.exists() else 0
            modified=max(time.time(),before+2);os.utime(temp,(modified,modified));os.replace(temp,target)
            record[weight]={'source_sha256':fingerprint,'derived_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                           'max_outline_error_em':0.0005,'metrics':'retained','recipe':'quadratic-v2'}
        paths.append(target)
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    return paths


if __name__=='__main__':
    for path in converted_fonts(): print(path)
