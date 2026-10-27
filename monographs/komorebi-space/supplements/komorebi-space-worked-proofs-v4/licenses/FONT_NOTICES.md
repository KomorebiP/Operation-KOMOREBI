# Font notices

The original writing and figures in the Komorebi Space release are licensed separately from the third-party font software embedded in its PDFs and vector figures. The project grants do not relicense that font software. No standalone font programs are distributed in this notice directory.

The inventory covers the three rebuilt Space reader books, their supplied predecessor PDFs, the preserved worked-proofs supplement, and its three figure PDFs. It identifies 44 distinct PostScript font names. Every recorded font is embedded. `FONT_SOURCE_IDENTITIES.json` identifies corresponding installed source files by path, name and SHA-256, and records their copyright and license fields. `FONT_SOURCE_HEADERS.txt` preserves the relevant installed Type 1 headers. These installed files document the current build environment. For older preserved figure and supplement PDFs, their identities do not establish that these exact installed file versions produced the embedded subsets.

| Font families | Original notice and terms | Included documents |
| --- | --- | --- |
| URW Palladio L | Copyright 1999 URW++ Design & Development. The inspected Type 1 headers name the GNU General Public License and explicitly permit including the font in PostScript or PDF documents regardless of the document's own license. | `GPL-2.0.txt`, `FONT_SOURCE_HEADERS.txt` |
| Nimbus Sans L | Copyright 1999 URW++ Design & Development. The historical URW base35 distribution is identified by CTAN as GNU GPL. The inspected bold Type 1 font includes the document embedding exception. The regular Type 1 font is version 1.05a, created by Primoz Peterlin in 2003, and its shorter header contains the copyright notice without repeating that license paragraph. Both exact headers are preserved. | `GPL-2.0.txt`, `FONT_SOURCE_HEADERS.txt` |
| Pazo Math | Copyright Diego Puga, 2000 and 2002. The inspected Type 1 headers name the GNU General Public License and include an explicit PostScript/PDF document embedding exception. | `GPL-2.0.txt`, `FONT_SOURCE_HEADERS.txt` |
| AMS Type 1 Computer Modern, AMS symbols and Euler | Copyright American Mathematical Society. The inspected font headers identify SIL Open Font License 1.1 and their Reserved Font Names. The exact years and names are preserved per file. | `OFL-1.1.txt`, `FONT_SOURCE_HEADERS.txt` |
| Latin Modern | Copyright Bogusław Jackowski and Janusz M. Nowacki on behalf of the TeX user groups. The installed fonts identify the GUST Font License, based on LPPL 1.3c or later. The complete upstream readme and manifest retain the authorship, support and maintenance notices. | `GUST-FONT-LICENSE.txt`, `LPPL-1.3c.txt`, `LATIN-MODERN-README.txt`, `LATIN-MODERN-MANIFEST.txt` |
| STIX | Copyright 2001–2010 STI Pub Companies, with notices for MicroPress and Elsevier portions and Reserved Font Names. SIL Open Font License 1.1. Matplotlib's notice records its conversion of the original OTF fonts to TTF. | `STIX-NOTICE.txt`, including the full OFL text |
| DejaVu | Bitstream Vera copyright and trademark notice, DejaVu changes notice, and the permission, naming and disclaimer provisions distributed with Matplotlib. | `DEJAVU-NOTICE.txt` |

The historical URW family identification is also documented at <https://ctan.org/tex-archive/fonts/urw/base35>. These are the older URW Type 1 files named in the source identities. They are not identified here with the separate license metadata of later URW Base 35 releases.

Some preserved supplement figures use embedded Type 3 fonts without Unicode mappings. Their original PDF and vector bytes remain unchanged. This notice does not claim those historical figures were regenerated or their text extraction was improved.

License texts and third-party copyright notices retain their own terms. The source identity record distinguishes verbatim document copies from the complete LPPL section extracted from the installed TeX package copyright file.
