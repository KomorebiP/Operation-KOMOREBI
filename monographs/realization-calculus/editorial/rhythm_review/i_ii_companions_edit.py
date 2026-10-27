#!/usr/bin/env python3
"""Apply individually reviewed rhythm edits to the two I companions only."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT = ROOT / 'editorial/rhythm_review'
BACKUP = OUT / 'i_ii_companions_before'
LEAN = 'source_i_iv/I/editable/lean_guide/Paper_I_Lean_Guide_Final.tex'
MACHINE = 'source_i_iv/I/editable/machine/Paper_I_Machine_Native_Final.tex'

edits = {
LEAN: [
('semicolon', '108 stable records; those records form a different inventory', '108 stable records. Those records form a different inventory', 'Separate two complete explanatory clauses.'),
('formulaic', 'An exact scoped result should remain exact when republished. The guide therefore retains', 'The guide retains', 'Remove a repetitive editorial maxim while retaining the scope policy.'),
('semicolon', 'The new result is documented through its own declarations and evidence; it does not change the inputs of historical row 10.', 'The new result is documented through its own declarations and evidence. It does not change the inputs of historical row 10.', 'Give the historical scope qualification its own sentence.'),
('hyphen', 'Project-namespace entries inspected by the historical audit', 'Entries in the project namespace inspected by the historical audit', 'Replace an optional modifier with a direct noun phrase.'),
('hyphen', 'Curly-braced arguments are implicit parameters inferred from use. Round-bracketed arguments are explicit inputs.', 'Arguments in braces are implicit parameters inferred from use. Arguments in parentheses are explicit inputs.', 'Use ordinary names for the punctuation instead of stacked modifiers.'),
('hyphen', 'The package disables automatic implicit-variable invention with', 'The package disables automatic invention of implicit variables with', 'State the action directly without an optional compound modifier.'),
('semicolon', r'Some resulting declarations depend on \code{Classical.choice}; the audit records this explicitly.', r'Some resulting declarations depend on \code{Classical.choice}. The audit records this explicitly.', 'Separate the dependency statement and its audit description.'),
('hyphen', 'mathematically well-defined and formally verified', 'mathematically well defined and formally verified', 'The predicative phrase does not need a hyphen.'),
('hyphen', 'the pre-existing nineteen source files', 'the nineteen existing source files', 'Remove a redundant prefix and optional hyphen.'),
('hyphen', 'The historical direct-import table is generated', 'The historical table of direct imports is generated', 'Use the noun phrase directly.'),
('hyphen', 'the vector and its range-membership proof', 'the vector and its proof of range membership', 'Replace an optional modifier with its natural complement.'),
('hyphen', 'The block-algebra development then restricts', 'The block algebra development then restricts', 'Keep the technical noun phrase block algebra open.'),
('formulaic', 'which is genuinely the full packet-to-packet Hom space.', 'which is the full packet-to-packet Hom space.', 'Remove an unnecessary intensifier.'),
('semicolon', 'Row 25 has its own nontriviality scope; the twenty-file foundational formalization retains that scope.', 'Row 25 has its own nontriviality scope. The twenty-file foundational formalization retains that scope.', 'Separate the row scope from the preservation statement.'),
('hyphen', 'A reachability obstruction is a lower-bound certificate', 'A reachability obstruction is a certificate for a lower bound', 'Use the complement instead of an optional modifier in the heading.'),
('hyphen', 'The typed-quiver model makes the distinction concrete.', 'The typed quiver model makes the distinction concrete.', 'Keep the technical noun phrase typed quiver open.'),
('hyphen', 'The strict-naturality module also handles semilinear realized actions, with explicit algebra maps and packet-label maps. Its generated-hull statement uses the exact image algebra.', 'The strict naturality module also handles semilinear realized actions, with explicit algebra maps and maps of packet labels. Its statement about the generated hull uses the exact image algebra.', 'Use open technical nouns and direct complements instead of optional compounds.'),
('semicolon', 'Surjectivity gives the appropriate rank inequality; equality and complete edge correspondence require', 'Surjectivity gives the appropriate rank inequality. Equality and complete edge correspondence require', 'Separate claims with different hypotheses.'),
('hyphen', 'It is not simply vector-space dimension.', 'It is not simply vector space dimension.', 'Use the conventional open technical noun phrase.'),
('semicolon', 'Function extensionality reduces $Ax=y$ to its coordinates; simplification evaluates the finite sum', 'Function extensionality reduces $Ax=y$ to its coordinates. Simplification evaluates the finite sum', 'Give successive proof operations separate sentences without changing either step.'),
('formulaic', 'Several important statements are deliberately certificate-explicit.', 'Several statements require explicit certificates.', 'Replace an inflated editorial description with the stated input requirement.'),
('formulaic', 'The output is a genuine rank formula for the supplied realization.', 'The output is a rank formula for the supplied realization.', 'Remove an unnecessary intensifier while retaining the supplied-realization qualification.'),
('hyphen', 'hidden in the seed-number notation.', 'hidden in the notation for the seed number.', 'Replace an optional modifier with a direct complement.'),
('hyphen', 'The primary-decomposition theorem uses', 'The primary decomposition theorem uses', 'Use the conventional open name of the construction.'),
('hyphen', 'supply the orbit-generation and extraction information for the upper bound.', 'supply the information about orbit generation and extraction for the upper bound.', 'Use open technical nouns without changing the supplied data.'),
('formulaic', 'The hard distinction is visible in the type: the existence of these quotient and extraction certificates is an input.', 'The existence of these quotient and extraction certificates is an input.', 'Remove a formulaic lead-in while retaining the exact input qualification.'),
('hyphen', 'The cyclic-matrix bridge', 'The cyclic matrix bridge', 'Keep the technical noun phrase cyclic matrix open.'),
('hyphen', 'The algebraic inverse-law pattern remains visible', 'The algebraic pattern of inverse laws remains visible', 'Replace an optional modifier with a direct complement.'),
('semicolon', 'This analytic theorem consumes the kernel inclusion; it does not independently derive graph reachability.', 'This analytic theorem uses the kernel inclusion. It does not independently derive graph reachability.', 'Use a plain verb and separate the qualification into a sentence.'),
('hyphen', 'The bilateral-shift result uses', 'The bilateral shift result uses', 'Use the conventional open technical noun phrase.'),
('semicolon', 'The audit is standalone; it is not imported by the root library aggregator.', 'The audit is standalone. It is not imported by the root library aggregator.', 'Separate two complete explanatory clauses.'),
('hyphen', 'The portable-kit verifier', 'The verifier for the portable kit', 'Use a direct complement in the heading.'),
('hyphen', 'The final count is an environment-inventory count, not a count of handwritten mathematical theorems.', 'The final count is a count of entries in the environment, not a count of handwritten mathematical theorems.', 'State what is counted without a stacked modifier.'),
('hyphen', 'shares some finite-projector material with', 'shares some material on finite projectors with', 'Use a direct complement instead of an optional compound modifier.'),
('hyphen', 'Finite linear-projector structure.', 'Finite linear projector structure.', 'Keep the technical noun phrase linear projector open.'),
('semicolon', 'Transitive ordinary-matrix support is multiplicatively closed; not the whole expanded iff criterion.', 'Transitive ordinary-matrix support is multiplicatively closed. This is not the whole expanded iff criterion.', 'Make the scope exclusion a grammatical sentence.'),
('hyphen', "is the series-level navigation record,", "is the navigation record for the series,", 'Use a direct complement instead of an optional modifier.'),
('semicolon', r'Further work is determined by the current coverage map in Section~\ref{sec:release-current}; these established results must not be treated as missing certificate constructors.', r'Further work is determined by the current coverage map in Section~\ref{sec:release-current}. These established results must not be treated as missing certificate constructors.', 'Separate navigation from the scope caution.'),
('semicolon', 'A refusal of nonempty output means the verifier is protecting the local rebuild claim; choose a new output directory.', 'A refusal of nonempty output means the verifier is protecting the local rebuild claim. Choose a new output directory.', 'Give the instruction its own sentence.'),
('hyphen', 'the stable machine-record inventory.', 'the stable inventory of machine records.', 'Use a direct complement instead of an optional modifier.'),
('semicolon', 'Rendering the resulting PDF is a separate presentation check; it is not a Lean verification step.', 'Rendering the resulting PDF is a separate presentation check. It is not a Lean verification step.', 'Separate two complete explanatory clauses.'),
],
MACHINE: [
('semicolon', r'The executable runtime has its own entrypoint under \nolinkurl{source/machine_v1.0.1/}; that path identifies the exact archived payload.', r'The executable runtime has its own entrypoint under \nolinkurl{source/machine_v1.0.1/}. That path identifies the exact archived payload.', 'Separate the location and its identity qualification.'),
('semicolon', 'its attached historical Lean tranche has eight mappings; those inherited interfaces and receipts retain their original scope.', 'its attached historical Lean tranche has eight mappings. Those inherited interfaces and receipts retain their original scope.', 'Give the inherited scope qualification its own sentence.'),
('semicolon', 'Stable identifiers connect the mathematical, formal, and computational material; statement hashes and source locators distinguish', 'Stable identifiers connect the mathematical, formal, and computational material. Statement hashes and source locators distinguish', 'Separate the two identifier functions.'),
('semicolon', r'Its source inventory and formal correspondence map are available under \nolinkurl{formal/coverage/}; compiler and replay receipts are under \nolinkurl{formal/evidence/}.', r'Its source inventory and formal correspondence map are available under \nolinkurl{formal/coverage/}, and compiler and replay receipts are under \nolinkurl{formal/evidence/}.', 'Connect parallel location clauses with a conjunction.'),
('hyphen', 'the countable Banach-space result', 'the countable result for Banach spaces', 'Use a direct complement instead of an optional compound modifier.'),
('hyphen', 'No inner-product orthogonality assumption is needed.', 'No assumption of inner product orthogonality is needed.', 'Use the technical noun phrase in a direct complement.'),
('semicolon', r'The mathematical records are located at \nolinkurl{formal/coverage/COVERAGE_108.json}; Appendix A is generated directly from those records.', r'The mathematical records are located at \nolinkurl{formal/coverage/COVERAGE_108.json}. Appendix A is generated directly from those records.', 'Separate the inventory location and the appendix provenance.'),
('semicolon', 'A runtime result therefore retains the exact interface scope explained below; it is not a certificate for every current manuscript statement.', 'A runtime result therefore retains the exact interface scope explained below. It is not a certificate for every current manuscript statement.', 'Give the scope exclusion its own sentence.'),
('semicolon', 'Runtime receipts remain attached to their original bytes; they do not transfer automatically to the mathematical inventory.', 'Runtime receipts remain attached to their original bytes. They do not transfer automatically to the mathematical inventory.', 'Separate the identity claim and its consequence.'),
('semicolon', "Its source coordinate identifies that payload's source; its KIR coordinate records validation of that version.", "Its source coordinate identifies that payload's source, and its KIR coordinate records validation of that version.", 'Connect parallel evidence-coordinate clauses with a conjunction.'),
('hyphen', 'a universal structured-error contract.', 'a universal contract for structured errors.', 'Use a direct complement instead of an optional compound modifier.'),
('hyphen', 'Block-product array and equality with directly resolved $ST$.', 'Array of block products and equality with directly resolved $ST$.', 'Use an open noun phrase in the table description.'),
('hyphen', 'The preservation flags are caller-supplied declarations.', 'The preservation flags are declarations supplied by the caller.', 'Use a direct clause instead of an optional modifier.'),
('hyphen', 'the source-linked intertwining record:', 'the intertwining record linked to the source:', 'Use a direct clause instead of an optional modifier.'),
('formulaic', 'The pass is exactly a pass for the listed operation flags. In particular, it does not construct', 'The pass applies to the listed operation flags. It does not construct', 'Remove circular repetition and an unnecessary editorial transition.'),
('formulaic', 'The correct use is sequential: identify the exact record,', 'To use the gate, identify the exact record,', 'Use a direct instruction instead of a formulaic lead-in.'),
('hyphen', 'AST coverage, action-registry consistency, source hash,', 'AST coverage, consistency of the action registry, source hash,', 'Use a direct complement instead of an optional modifier.'),
('semicolon', 'The additional traditional models and visual appendix are outside the 108-record inventory; they are not silently counted as extra machine records.', 'The additional traditional models and visual appendix are outside the 108-record inventory. They are not silently counted as extra machine records.', 'Separate the inventory scope and count qualification.'),
('hyphen', 'translates cross-references into stable-record links.', 'translates cross-references into links to stable records.', 'Use a direct complement instead of an optional modifier.'),
],
}

def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()

journal = []
files = []
for relative, replacements in edits.items():
    path = ROOT / relative
    before = path.read_text()
    after = before
    backup = BACKUP / relative
    if backup.exists():
        raise SystemExit(f'Backup already exists: {backup}')
    for category, old, new, reason in replacements:
        if after.count(old) != 1:
            raise SystemExit(f'Expected one occurrence: {relative}: {old!r}: {after.count(old)}')
        line = before[:before.index(old)].count('\n') + 1
        after = after.replace(old, new, 1)
        journal.append({'file': relative, 'before_line': line, 'category': category,
                        'old': old, 'new': new, 'rationale': reason})
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    path.write_text(after)
    files.append({'file': relative, 'backup': str(backup.relative_to(ROOT)),
                  'before_sha256': digest(before), 'after_sha256': digest(after),
                  'edits': len(replacements)})

(OUT / 'i_ii_companions_journal.json').write_text(json.dumps(journal, indent=2, ensure_ascii=False) + '\n')
(OUT / 'i_ii_companions_files.json').write_text(json.dumps(files, indent=2) + '\n')
print(json.dumps({'files': files, 'journal_entries': len(journal)}, indent=2))
