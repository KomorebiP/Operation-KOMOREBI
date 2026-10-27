# Fonts embedded in the reviewed-core reader

The reader embeds subsets from URW Palladio L, Pazo Math, and the AMS Type 1 distribution (Computer Modern, Euler, and AMS symbol fonts). The six preserved Python-generated figures embed DejaVu Sans subsets. No standalone font software is redistributed. The PDF font inventory is recorded in the reproduction output.

The exact installed Type 1 font source files and their own copyright and license declarations are recorded in `FONT_SOURCE_IDENTITIES.json`. The Palladio and Pazo headers both contain an explicit PostScript/PDF document embedding exception to their GNU GPL terms. `GPL-2.0.txt` preserves the applicable historical GPL text. AMS font headers identify the SIL Open Font License 1.1; its full text is in `OFL-1.1.txt`. `DEJAVU_NOTICE.txt` preserves the DejaVu/Bitstream notice from the installed distribution. The original figure PDFs are retained byte-for-byte; their earlier build environment has not been relabeled as a new font build.

Primary package references: https://ctan.org/pkg/urw-base35 ; https://ctan.org/pkg/mathpazo ; https://ctan.org/pkg/amsfonts . Font license declarations were also checked against the actual files used for this build, rather than inferred solely from current package web pages. Font and third-party terms remain separate from the project's licenses for original prose and software.
