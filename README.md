# Measuring chemical safety and refusal in language models

Companion code and data for the methodological review by **Ashutosh S. Jogalekar**, Szilard Scientific LLC, Palo Alto, CA. Correspondence: ashjogalekar@gmail.com. ORCID: https://orcid.org/0009-0002-5113-2268.

Literature and analysis cutoff: **31 October 2026**. Focused coverage checks and release preparation: **5 November 2026**. This repository contains the companion analyses for a manuscript prepared for ChemRxiv submission. The manuscript has not yet been submitted or peer reviewed. The proposed study has not been run.

Repository: https://github.com/ajogalekar/chemical-safety-refusal-evaluation . The initial calculations are tagged `v0.1.0`; `v0.1.1` clarifies their documentation without changing data, code, or numerical results.

## Reproduce the calculations

From an extracted copy of this directory:

```bash
python3 reproduce.py
```

Python 3.10 or later and its standard library are sufficient. No account, API key, model run, paid service, or network access is needed. The script verifies input checksums, runs all four analyses, compares eight output files with the frozen results, runs separate arithmetic/data-integrity checks, and runs the PatAgent smoke test. It writes logs and a summary to `validation/`. The reference outputs in `expected/` are never overwritten. JSON comparisons ignore only the Python-version field and the explicitly corrected RefusalBench repeat-count description; numerical tolerances are recorded in the runner. Successful reproduction does not validate the original labels, sampling assumptions, or causal interpretations.

## What is included

- `docs/analysis-methods.md`: methods, assumptions, and limitations for the secondary analyses, drawn from the supporting information. The current reference list is in `literature/references.json`.
- `reanalysis/data/`: all input values used by the analyses. XSTest files contain a documented column projection of released annotations and prompt hashes; response and prompt prose is omitted. Biological RefusalBench contains released labels only. ChemIDBench contains transcribed sufficient counts, not reconstructed item outcomes.
- `reanalysis/code/` and `code/reanalyse_dualchem_aggregates.py`: executable analyses.
- `reanalysis/analysis/`, `results/`, and `expected/`: rerun results and preserved comparison outputs.
- `literature/`: study inventory, current claim ledger, references, source versions, retrieval records, and source URLs from saved searches. Eight studies received detailed audits; other reading depths are explicit. The search was targeted, not exhaustive or preregistered.
- `patagent/`: executable PatAgent 0.1.0 source, skill, source catalog, provenance, and historical checklist output. PatAgent is an independent evidence-linked review aid inspired by public writings, not Pat Walters or his endorsement. Its automated checks are not scientific validation.
- `figures/`, `code/make_figures.py`, and `code/draw_proposed_study.py`: figure files and generation code. Figure generation is optional and requires ReportLab; PNG generation also requires Poppler's `pdftoppm`. Fonts use Arial when installed, otherwise ReportLab's bundled Vera fonts, which can alter layout slightly.
- `schema/`: a proposed response schema and an empty data template. These are design artifacts, not observed study data.
- `validation/`: independent calculation checks, original analysis scripts, release patches, and verification records.

Cached papers, full blog text, search-result prose, private editorial rankings, personal correspondence, and credentials are not distributed. Article sources remain available through their original links. The PatAgent historical corpus metadata records 91 posts; a failed refresh prevents a claim of current exhaustive blog coverage. Neither that corpus nor a corpus refresh is required for numerical reproduction.

## Analysis boundaries

| Study | Reproduced or recalculated | Alternative analysis | Unresolved |
|---|---|---|---|
| ChemIDBench | Published paired discordant counts | Exact McNemar tests, Holm adjustment across 14 tests, paired normal intervals | Molecule identities, family dependence, scoring validity |
| XSTest | Refusal rates from released human labels | Paired same-model contrasts; bootstrap within ten fixed safe-prompt types; Holm adjustment across four tests; raw annotation agreement on all 450 responses per configuration | Related wording, new prompt types, decoding variability, answer quality |
| Biological RefusalBench | Frozen 19-model table scores under table-matching labels | Scoring-definition sensitivity; paired prompt bootstrap after averaging available repeats | Missing judge matrices, curated prompt selection, causes of snapshot differences |
| DualChem | Published paired arithmetic and rounded aggregate rates | Completed-run versus all-initiated-task denominator sensitivity; unadjusted exploratory question-level test for human assistance | Participant dependence and assignment; paired tool/no-tool outcomes |

RefusalBench's selected comparison contains 93 prompt/model groups with five outputs and one with four. Available repeats are averaged; no missing result is imputed. The correction changes explanatory text, not estimates. The maximum point-estimate shift from assigning either binary outcome to that one missing repeat is 0.43 percentage points. The DualChem completed-run increase of 2.3 points has no justified significance test from the available aggregates.

## Rights and citation

Original analysis code and PatAgent code: MIT, see `LICENSE`. Manuscript, figures, and original review documentation: CC BY 4.0, see `LICENSES/MANUSCRIPT-CC-BY-4.0.md`. Third-party data retain their own licenses; see `THIRD_PARTY_NOTICES.md` and `DATA_SOURCES.json`. Use `CITATION.cff` for this package. Cite the `v0.1.1` tag for the current documentation release; a manuscript DOI will be added when assigned. AI use in analysis and writing is described in `AI_USE.md` and the manuscript.

The code and data are published at https://github.com/ajogalekar/chemical-safety-refusal-evaluation. The tagged version and its checksummed ZIP preserve the release used by the manuscript. No manuscript DOI has been assigned. The same analysis archive can accompany the ChemRxiv submission.
