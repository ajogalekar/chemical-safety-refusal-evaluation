# Coverage and reading depth

This review selects studies to cover important measurement and design patterns in chemical safety and refusal. It is not an exhaustive bibliography or systematic review. The inventory records 59 sources and their reading depths; the manuscript cites 52 references. Eight studies received detailed audits. Focused methods readings do not imply examination of every supplement, code file, or outcome.

| Pattern | Representative sources examined |
|---|---|
| Chemical safety, protective advice, and refusal scoring | SynthRefusal, ChemSafetyBench, LabSafety Bench, ChEmREF, SafeSci, SciSafeEval, SoSBench |
| Same-entity identifiers and identity assistance | SynthRefusal, ChemIDBench; SMILES-Prompting as an identifier-related safety comparison with wording confounding |
| Fixed-model prompt changes and excessive refusal | XSTest; OR-Bench and related benchmarks as context |
| Refusal versus answer content and task accomplishment | StrongREJECT, AgentHarm, DualChem |
| Chemical agent safeguards and whole-system evaluation | SciGuard/SciMT; AgentHarm as a synthetic-agent comparator |
| Knowledge-aware abstention and mechanistic interventions | Factual Refusal Index, unified mechanistic refusal analysis, Arditi and colleagues, confidence-intervention work; grounded RefusalBench as a distinct source |
| Retrieval context, knowledge proxies, and multimodal questions | RAGRefuse, ChemComp, WMDP, MaCBench safety component |
| Paired benign/adversarial tasks and scoring validation | FORTRESS, XSTest, DualChem; biological RefusalBench for scoring-definition sensitivity |
| Human assistance and practical execution | DualChem; OpenAI 2024 randomized human comparison; novice biology studies; selected chemical-agent execution reports as methodological comparators |
| Chemical data and statistical validation | Bender, Walters and coauthors; Nicholls; primary paired-test, multiplicity, and clustered-resampling sources |

Additional screening on 5 November considered **SciHazard**, arXiv:2607.18665v1, especially §§3.2, 4–5, and **SciRisk-Bench**, arXiv:2606.18936v1, §§3.1–3.3. These were not fully audited or ranked and are not counted among the 59 inventory records. SciHazard combines separate refusal/content measurements, judge validation, and model/agent comparisons; judged executability is not an executed experiment. SciRisk-Bench adds risk annotations and safety judgments across disciplines. These combinations add examples within patterns already represented, rather than a missing comparison design requiring a new full audit. This is a scope decision, not an adverse paper-level judgment.

Sources: https://arxiv.org/html/2607.18665v1 and https://arxiv.org/html/2606.18936v1 . No claim of first invention of outcome separation, safeguards, or rigorous evaluation is made.

The search ended 31 October 2026, with focused checks of additional pre-cutoff studies completed 5 November. Exact queries were not retained for every early search batch. Saved search files in this release retain source URLs and hashes of the original local search records; copyrighted search-result prose is omitted. Some source materials were inaccessible, as recorded in the supplement and retrieval logs. A source that was discovered but unread remains labeled as such.
