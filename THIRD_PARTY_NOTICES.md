# Third-party data and sources

**XSTest.** Paul Röttger, Hannah Rose Kirk, Bertie Vidgen, Giuseppe Attanasio,
Federico Bianchi, and Dirk Hovy. *XSTest: A Test Suite for Identifying Exaggerated
Safety Behaviours in Large Language Models*. NAACL 2024, pp. 5377–5400.
https://aclanthology.org/2024.naacl-long.301/ . Released under CC BY 4.0 in
https://github.com/paul-rottger/xstest at tree
`d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d`.
The included CSVs retain only the fields used in analysis plus prompt hashes;
no annotation value or row order is changed. Original file hashes and the
projection are documented in DATA_SOURCES.json. The original license text is
in LICENSES/XSTest-CC-BY-4.0.txt. No endorsement is implied.

**Biological RefusalBench.** Lukas Weidener, Marko Brkić, Mihailo Jovanović,
Emre Ulgac, and Aakaash Meduri. *RefusalBench: Why Refusal Rate Misranks Frontier
LLMs on Biological Research Prompts*. arXiv:2605.21545v1.
https://arxiv.org/abs/2605.21545v1 . The Hugging Face dataset card explicitly
licenses the data under MIT and links the repository license. The original
license and pinned dataset card are retained in LICENSES/. The adjudicated
CSV is unmodified; the three post-frozen models are excluded by analysis code,
not removed from the input. No prompt text or raw response text is included.

**ChemIDBench and DualChem.** Numerical facts were transcribed from published
tables, with exact source locators in the scripts, supplement, and data-source
record. These transcriptions do not include copyrighted article text, figures,
or reconstructed item-level outcomes. Underlying publications retain their
own rights.

**PatAgent source material.** Practical Cheminformatics posts, guest posts,
coauthored papers, and other cited sources retain their authors' rights.
The release contains bibliographic metadata, links, and derived checklist
recommendations, not the cached full-text blog corpus or paper PDFs. PatAgent
is not Pat Walters and carries no claim of his endorsement.

**Optional dependencies.** Python, ReportLab, Poppler, and the optional MCP
SDK are separately installed dependencies and are not distributed here.
