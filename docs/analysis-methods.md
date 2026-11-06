# Supporting information

## Measuring chemical safety and refusal in language models

**Ashutosh S. Jogalekar**

Szilard Scientific LLC

Palo Alto, CA

**Source and analysis snapshot: 31 October 2026.** Focused checks of additional pre-cutoff studies and supplement synchronization completed 5 November 2026. This supplement gives the review methods and secondary analyses. The proposed experiments have not been run.

## S1. Coverage, inclusion, and access

### S1.1. Review depth

The manuscript reviews chemical safety and refusal, including only SynthRefusal from onepot-Bench 0. The broader audits remain in the working evidence records. General chemistry, refusal, and execution studies are labeled as methodological comparators.

We verified the six papers in the initial AI-generated list; each was a real paper matching its principal subject. Two additional candidates received detailed audits. The public claim-level synthesis and source locators are in Section S2 and `literature/claim_ledger.csv`; review depth and paper versions are recorded in `literature/study_inventory.csv`. Private editorial rankings are not part of this manuscript or its public archive.

The detailed audit set comprises onepot-Bench 0 (arXiv:2608.02595v1); ChemIDBench (2610.30903v1); AgentHarm (2410.09024v3); XSTest (NAACL 2024 final); unified mechanistic refusal analysis (2609.00760v1, with EMNLP acceptance separately verified); ChemSafetyBench (2411.16736v1); factual Refusal Index (2510.01782v2); and biological RefusalBench (2605.21545v1). The evidence ledger gives versions and dates. We did not experimentally replicate these studies [9; 10; 11; 12; 13; 14; 15; 16].

Methods-focused readings covered DualChem, SafeSci, SciSafeEval, SoSBench, LabSafety Bench, ChemBench, StrongREJECT, MolRepBench, ChemReason-Bench, ChemToolAgent, ChEmREF, ChemComp, Coscientist, ChemCrow, LLM-RDF, the two 2026 novice biology uplift studies, the threshold-exceedance framework, the confidence-and-abstention study, Arditi and colleagues, and grounded RefusalBench. The ledger records which methods or main article we read; it does not imply that we examined all code, supplements, or individual outcomes. STREAM, the abstention survey, and chemical ML evaluation guidance supply methodological context. We read the OpenAI 2024 human study for participant assignment, scoring, and stated limits, without reanalysing it [44].

Focused methods readings also covered SMILES-Prompting, SciGuard/SciMT, RAGRefuse, FORTRESS, WMDP, and MaCBench’s safety component. These cover identifier-based safety tests, agent safeguards, retrieval context, paired benign and adversarial requests, knowledge proxies, and multimodal safety questions; they did not receive full audits [47; 48; 49; 50; 51; 52].

Screening or discovery records cover HarmBench, SORRY-Bench, OR-Bench, AbstentionBench, LABSHIELD, SciKnowEval, the RAND 2024 final report, and several newer abstention methods. We retrieved full PDFs for many, but did not conduct detailed methods audits. These records document adjacent work; we do not use their numerical or causal conclusions as findings of this review.

### S1.2. Search procedure and coverage checks

We searched exact titles and terms for chemical model refusal, scientific safety benchmarks, identifier representations, knowledge-aware abstention, human uplift, chemical tools, and physical execution. We followed selected references, including those on reporting and measurement validity, and preferred primary sources to news or summaries. Source URLs from saved search batches are in `literature/search_*.json`; cached search-result prose is not redistributed. Retrieval attempts, timestamps, resolved URLs, and checksums are in `literature/retrieval*.json`. The study inventory records inclusion decisions separately from retrieval success.

We broadened the search to look for evidence against the initial skeptical hypothesis. StrongREJECT separates refusal from substantive assistance; SafeSci and SciSafeEval measure several aspects of scientific safety; DualChem uses expert rubrics and a human comparison; STREAM addresses ChemBio reporting; and chemical agent papers report experiments. Our proposal builds on these precedents by connecting controls and outcomes for chemical refusal evaluations. We do not claim to be the first to distinguish refusal from useful assistance or to call for rigorous evaluation.

The search was targeted and iterative. It continued through 31 October 2026, with focused checks of additional pre-cutoff studies completed on 5 November 2026. Search-engine results change over time, and exact queries were not saved for every early batch, so we cannot reproduce an exhaustive database search or report a PRISMA flow count or numerical recall estimate. The coverage check was not an independent systematic search by a second human reader. Retrieved but unread sources must retain that label.

### S1.3. Deliberate exclusions and ambiguous names

Biological uplift studies inform experimental design and the choice of outcomes; they do not estimate chemical assistance. General benchmarks enter where they offer a relevant control or measurement method. The central comparison excludes model cards, inaccessible private evaluations, training-only methods, general AI safety commentary, and molecular generation studies without a relevant refusal or validation question. Those sources could serve a broader review, but they do not estimate the same quantities as the studies analysed here.

At least two studies use the name “RefusalBench.” The AppliedScientific repository belongs to Weidener and colleagues' biological research-prompt study; Muhamed and colleagues' EACL paper concerns grounded language models. “ChemBench” here is Mirza and colleagues' Nature Chemistry framework, not the similarly named ChemLLM benchmark. We used SoSBench's current title and v3; its earlier title differs. ChemToolAgent also previously circulated under a tooling-focused title. The ledger records these changes so that versions are not counted as separate studies.

### S1.4. Access limitations

We could not access onepot's proprietary item-level results, baseline training data, or referenced target-identification audit supplement. We did not locate ChemIDBench's item-level outputs or unified-study code and data in the examined materials. ChemSafetyBench's advertised repository was unavailable when we attempted retrieval. We accessed the main methods for ChemCrow and LLM-RDF, but supplement retrieval failed. ChemBench supplement retrieval failed through both repository and publisher routes. An additional OpenReview uplift lead returned an access error and supports no substantive claim in this review.

AgentHarm's current public release contains 44 of the paper's 66 public base test behaviors, giving 176 rather than 264 variants. Running that release would not automatically reproduce the paper's original table. Biological RefusalBench's current labels include extra models, which we excluded to match the paper's frozen 19-model set. Proprietary training data are unknown; we cannot infer either the presence or absence of contamination.

## S2. Claim-level synthesis of the detailed audits

The evidence ledger gives detailed records and source locators. The judgments below apply to the specified claim. “Unsupported” does not describe the entire paper.

| Study and precise claim | Judgment and evidence | Consequence and repair |
|---|---|---|
| SynthRefusal (onepot): the target sets elicit different response profiles | Supported as a reported benchmark observation; §3, Fig. 4 and Table 5 distinguish five response states and compare identifiers for the same 282 established targets (281 for CAS). Item-level reproduction unavailable. | Report all five states per initiated item and paired representation results with unique-target counts. |
| SynthRefusal (onepot): the target-set contrast isolates novelty, memorization, or feasibility | Unsupported: the comparison changes target populations while using SMILES for both. It does not independently control familiarity or resources. | Retain the existing same-entity representation comparisons; measure familiarity separately; vary resources for the same target. Missing controls undermine this causal extension, not the existence of response differences. |
| ChemIDBench: performance depends strongly on identifier for the same entity | Supported by the published within-molecule comparisons; Table 14 counts reproduce. Recognition probes and name bridges strengthen the access interpretation. | Release labels for checking and family identifiers for uncertainty estimates that account for related molecules. The observed identifier effect survives these access limitations. |
| ChemIDBench: selected interventions establish transfer to new entities | Partially supported at most. Selected activation peaks and molecule-specific adapters have not established a universal binding mechanism. | Test on entities and families excluded from development, and report all selected layers and thresholds. |
| AgentHarm: attacked systems can accomplish synthetic agent tasks | Supported within the fixed synthetic environment; §§2–4 separate refusal and task scoring. | Keep variants of each base task together in the analysis. Report complete and partial success; test with real resource constraints before claiming real-world execution. |
| XSTest: system prompts change exaggerated safety refusals | Supported; same-model paired labels reproduce and large effects survive alternative analysis. | Add independently scored answer quality for a usefulness claim; sample new prompt families for a prevalence claim. Correctness was deliberately outside the original endpoint. |
| Unified analysis: shared and distinct refusal-related features exist in selected cases | Partially supported, with meaningful intervention evidence; 213 quadruples selected for behavior across six systems (§3/Appendix A). | Use unselected cases to estimate frequency and held-out cases to test transfer. Establishing the order of internal decisions requires separate experiments. |
| ChemSafetyBench: reported scores establish broad chemical competence and mechanism | Partially supported for score differences. Competence and mechanism claims require further validation of the measurements (§§3–4/Appendix D). | Validate the judge against experts, report distinct entities and templates, connect outcomes by task, and experimentally test the proposed cause of failure. |
| Factual Refusal Index: the metric summarizes knowledge-aware refusal | Partially supported under its statistical model of unobserved knowledge. Forced answers and binary response tables cannot independently reveal that knowledge. | Report the response tables, check how assumptions about unobserved knowledge affect the index, and add independent knowledge probes. |
| Biological RefusalBench: refusal behavior varies substantially across examined models | Supported on released adjudicated labels. Large snapshot differences survive alternative category aggregations. | Clarify the scoring and agreement statistic, release judge labels where possible, and keep the 47 prompt bundles intact when estimating uncertainty. |

SynthRefusal’s clean-refusal rate uses clean refusals plus answers as its denominator, excluding partial disclosures and identification failures; partial-disclosure prevalence uses all target-resolved responses. If exclusions differ by identifier, refusal rates compare different response subsets. The established-versus-designer comparison uses SMILES for both sets but changes the targets; it does not isolate novelty, familiarity, or practical feasibility. The examined version reports no Tanimoto matching.

In the unified study's vector decomposition, the lengths of the common and residual components follow algebraically from the cosine between the two unit vectors. They are therefore not independent experimental observations of the mechanism. The script documents this identity; it does not invalidate the separate activation-steering experiments.

## S3. Reanalysis methods and results

The 95% intervals below are pointwise, not adjusted for multiple comparisons; Holm adjustment applies to the reported p-values.

### S3.1. ChemIDBench: published sufficient counts

We manually transcribed discordant counts from arXiv:2610.30903v1, Appendix B.3, Table 14. Each of 14 comparisons uses n = 896 molecules. If b counts correct answers only in the first condition and c only in the second, the paired difference is (b − c)/n. The exact two-sided McNemar test uses the binomial distribution of b conditional on b + c, assuming equal probabilities of the two discordant outcomes under the null. We apply Holm correction to the 14 p-values together. Paired normal intervals use the sample variance of the −1/0/+1 difference, preserving the pairing between accuracies.

`reanalysis/code/reanalyse.py` reproduces the arithmetic from these counts and adds exact tests, multiplicity adjustment, and intervals. The counts cannot recover raw responses, identities of molecules with concordant outcomes, family clusters, or scoring errors. We did not invent those records. The largest adjusted p-value is 1.2523 × 10⁻¹¹. All 14 estimates and intervals are in `reanalysis/analysis/chemid_paired_reanalysis.csv`.

### S3.2. XSTest: released human labels

The input consists of five public v2 completion files from repository tree `d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d`. The script checks 450 prompts per configuration and reproduces rates from the 2,250 labeled outputs. The released configurations use temperature 0 and a 256-token output cap, with one output per prompt and condition. Our alternative analysis uses the 250 safe prompts and keeps each prompt's outcomes paired across configurations of the same model. We resample within each of the ten safe-prompt types, using 10,000 bootstrap replicates and seed 20261030. Full refusal and any refusal are analysed separately, with Holm correction across four paired tests.

| Same-model contrast | Endpoint | Difference, percentage points | 95% stratified prompt-bootstrap interval |
|---|---|---:|---|
| Llama 2 no system prompt minus original prompt | Full refusal | −24.0 | −29.6 to −18.8 |
| Llama 2 no system prompt minus original prompt | Full or partial refusal | −30.0 | −36.0 to −24.4 |
| Mistral guard minus no guard | Full refusal | +8.8 | +5.6 to +12.4 |
| Mistral guard minus no guard | Full or partial refusal | +17.2 | +13.2 to +21.6 |

The intervals apply to the released labels, fixed model snapshots, and ten prompt types. They do not include variation from future models or repeated stochastic generations. Shared wording may make prompts less independent than the resampling assumes. Recalculating agreement from available annotations does not replace independent expert checks of label validity.

### S3.3. Biological RefusalBench: definition sensitivity

The input is the released adjudicated-label CSV, SHA-256 `7334a11cb95ec73bbc31c1bdbb5e336843122b9ed05b4e9a7c16772f52911f81`, with 15,504 rows. We excluded three models added after the paper's frozen set, leaving 13,389 rows for 19 models and 141 prompts. Six generation slots are missing; there are no duplicate prompt/model/trial keys. The excluded model IDs are listed in `refusalbench_audit.json`.

All 19 table scores reproduce within rounding when direct and indirect refusal count as refusal. Methods §2.5 instead specifies direct refusal plus non-responsive output. We tested both definitions and direct refusal alone. Repository commit `28fd0a31a699e5a5c63a562b24812f27b6bed5a8` also calculates modal agreement fractions where the paper describes per-item Krippendorff's alpha. That code establishes what the inspected release does, not what ran historically. Individual judge labels are missing from the CSV, so we could not independently recalculate the agreement coefficient.

For benign prompts, we compared Opus 4.7 with 4.6 by averaging the available generations (up to five) within each prompt, then resampling the 47 paired prompt blocks 10,000 times with seed 20261030. Of the 94 prompt/model groups, 93 have five outputs and one has four: `enzyme_design_benign_5a18e499` for `anthropic/claude-opus-4.6`. The calculation already uses the available outputs; this repeat-count correction does not change the estimates. Refusal increased by 43.4 points (95% interval, 29.4 to 57.9) under the definition matching the tables, 45.1 (31.5 to 58.7) under the methods definition, and 43.8 (29.8 to 58.3) for direct refusal alone. For the one missing repeat in this comparison, assigning either binary outcome changes any of these point estimates by at most 0.43 percentage points; this is a sensitivity bound, not an observed or imputed result. The large difference survives the scoring inconsistency. Prompt selection and judgments about appropriate refusal limit generalization, and the analysis cannot explain what caused the model change. Author clarification could resolve the mismatch without removing the observed difference.

### S3.4. DualChem: aggregate-only sensitivity

The source is the official technical report [5].

We used the official PDF linked to the 28 October 2026 release, retrieved 31 October: §§5.1 and 6.1 and Table 4, pp. 7–9 and 24. It reports 160 questions answered correctly only with assistance and 64 only in the control condition, out of 600. These counts give a difference of 16.0 points, an exact two-sided McNemar p = 1.1418 × 10⁻¹⁰, and a paired normal interval of 11.28 to 20.72 points. These are question-level calculations. They do not adjust for repeated answers by participants or nonrandom participant assignment, both described in §5.1. The public human-baseline CSV contains 600 question-level rows but no participant identifiers (Hugging Face revision `d81fc1f06277434e7ba35d784d0ce28667007c5a`), so it does not resolve participant-level dependence.

In the web-search condition, 175/600 questions have no final answer, leaving 425 completed runs. Multiplying the reported 54.6% completed-run accuracy by 425/600 gives approximately 38.675% per initiated task. Rounding to one decimal place implies a range of approximately 38.640 to 38.710%; this is a rounding range, not a confidence interval. Accuracy without tools is 52.3% over all 600 questions. For the tested system without fallback, the all-initiated-task estimate is approximately 13.6 percentage points below the no-tool accuracy. The apparent completed-run gain of 2.3 percentage points compares different question sets (425 versus 600); its statistical significance has not been established. We could not calculate a paired comparison of individual tool and no-tool outcomes.

DualChem uses expert-written criteria for free-form answers and reports results for all items and answered items. Appendix A.7 compares human and alternative-model judges: human Fleiss' κ = 0.74, primary-judge agreement with majority human labels = 84.3%, and Cohen's κ = 0.69. These checks support the scoring, though the appendix gives too little detail about the validation sample to establish accuracy within subgroups independently. As the authors acknowledge, all benchmark questions are dual-use, limiting estimation of specificity. The response asks for difficulty, reasoning, answer, confidence, and a risk flag in that order (§5.2). Diagnostic questions in that sequence may affect the answer, so they cannot be treated as independent probes of an unprompted response.

### S3.5. What was not reproduced

We did not independently reproduce proprietary API behavior, response correctness, experiments, human randomization, or judge calibration. We did not reconstruct raw outputs from percentages. Aggregate counts cannot supply scaffold-level analyses, participant-clustered uncertainty, or missing paired cells. “Reproduction” here means recalculation from the specified released labels or counts.

## S4. Proposed experiment and minimum reporting requirements

The proposed study uses 60 entities and legitimate chemical safety questions, with 30 chemical-family blocks, two identifier forms, three information conditions, two fixed model snapshots, and two generations per condition: 1,440 answer calls. Separate identity probes for each entity/identifier/model add 240 calls. Development examples must use other entities. Optional tests of source-based answerability, synthetic permission, resource feasibility, and laboratory execution require their own samples and budgets. They are excluded from the 1,680-call total.

Before collecting data, fix the sampling frame, chemical normalization, reference answers, coverage rubric, and development/evaluation split. Report chemical-family and, where informative, scaffold counts, fingerprint similarity distributions within and between families, and safety-question categories. These describe coverage; they do not establish that the 60 entities represent chemical safety generally. Record exact prompts and model versions, reasoning-effort settings and decoding parameters, tool and token budgets, primary comparisons, smallest meaningful effects, invalid-output rules, resampling units, and any criteria for proceeding to laboratory work. Register the analysis before inspecting evaluation results. A pilot can estimate disagreement between paired responses and dependence within families, but prompts or thresholds selected using pilot results must be identified as such.

The identity bridge would supply the verified common name and SMILES together without the requested safety fact; the dossier condition would add verified facts to that same bridge. Bridge and dossier contrasts would be reported separately by initial identifier, with any combined estimate using prespecified equal weights. Recognition probes would run in separate fresh sessions and would neither feed the main task nor select its sample. Repeats would be averaged within entities before paired comparisons, and uncertainty estimated by resampling chemical-family blocks. The primary test family would be defined across outcomes, contrasts, initial identifiers, and models before Holm adjustment. Rare refusals may leave refusal differences imprecisely estimated. The dossier also changes context length and hazard salience, so its effect cannot identify factual access alone; refusal with the answer supplied does not by itself establish safety-based withholding. Figure 3 and Section 7 of the manuscript describe this unchanged 1,680-call design.

Choose baselines for the task. Identifier lookup tests whether a simple resolver handles the apparent recognition problem; direct retrieval tests whether the dossier already supplies the answer. An abstain-all rule shows how an abstention metric scores universal refusal. For a planning task with fixed resources, compare the agent with a tool-only planner and an expert given equal information. Random or majority-class predictions are useful only where the task and label distribution make them meaningful. If a baseline lacks information available to the model, the comparison measures the difference between whole systems, not models alone.

The schema records seven aspects of behavior separately. Missing values use `null` with a reason. Because the experiment has not run, `schema/response_template.csv` contains headers only. `schema/response_schema.json` separates observed behavior, judgments of appropriateness, and external execution. Refusal-reason fields record what the model says; they do not identify its internal mechanism or form a validated overall score.

Report the number of unique entities, families, templates, people, runs, and batches. Include outcomes for every initiated task and the denominators for paired or conditional results. Record label sources and adjudication, model configurations, uncertainty about training exposure, effect sizes, what each interval estimates, and every selected or tuned setting. State the strongest conclusion each stage of validation supports. This chemical data record complements STREAM's broader reporting criteria [1].

## S5. Assessment boundaries and use of review tools

PatAgent assisted the evidence review. Its cached collection contained 91 posts: 74 Blogger and 17 GitHub Pages posts, including one guest post. A failed refresh limits coverage of current posts. Recommendations are attributed to Walters and relevant coauthors; applying them to refusal evaluation is our synthesis. We inspected the statistical companion skill, but its portfolio-selection procedures did not apply. We used no automated scientific ranking.

The earlier automated audit left checklist fields unresolved for structure parsing, duplicate-label conflicts, and chemical artifacts. These checks were outside the released-label analysis and did not lower paper assessments. The package includes the postflight output at `patagent/manuscript-postflight.json`. A completed metadata checklist cannot establish a causal claim, validate a reference label, or demonstrate experimental success; those require scientific examination and sometimes new data.

AI assistance in extraction, analysis design, coding, figure preparation, writing, and revision is declared in the manuscript and documented in `AI_USE.md`. Computational checks reproduce calculations conditional on the released labels and the stated assumptions. They do not constitute independent expert validation of the source labels or interpretations. The author is responsible for the submitted work.

## References

**9.** Wang, B.; Tyrin, A. S.; Boiko, D. A. [onepot-Bench 0: towards lab-aware in silico chemistry benchmarks](https://arxiv.org/abs/2608.02595v1). arXiv:2608.02595v1, 3 August (2026).

**10.** Saadi, K.; Wang, D. [Same Molecule, Different Knowledge: Cross-Identifier Binding Failures in LLMs for Chemistry](https://arxiv.org/abs/2610.30903v1). arXiv:2610.30903v1, 22 October (2026).

**11.** Andriushchenko, M., et al. [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024v3). ICLR 2025; examined arXiv:2410.09024v3, 18 April (2025).

**12.** Röttger, P.; Kirk, H. R.; Vidgen, B.; Attanasio, G.; Bianchi, F.; Hovy, D. [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models](https://aclanthology.org/2024.naacl-long.301/). NAACL 2024, 5377–5400 (2024).

**13.** Son, Y.; Kim, S.; Kim, H. J.; Kim, T. [A Unified Mechanistic Analysis of Knowledge- and Safety-Based Refusals](https://arxiv.org/abs/2609.00760v1). arXiv:2609.00760v1, 1 September; EMNLP 2026 final version separately verified (2026).

**14.** Zhao, H., et al. [ChemSafetyBench: Benchmarking LLM Safety on Chemistry Domain](https://arxiv.org/abs/2411.16736v1). arXiv:2411.16736v1, 23 November (2024).

**15.** Pan, W.; Xu, J.; Chen, Q.; Dong, J.; Qin, L.; Li, X.; Yu, H.; Jia, X. [Can LLMs Refuse Questions They Do Not Know? Measuring Knowledge-Aware Refusal in Factual Tasks](https://arxiv.org/abs/2510.01782v2). arXiv:2510.01782v2, 16 May; ICLR 2026 (2026).

**16.** Weidener, L.; Brkić, M.; Jovanović, M.; Ulgac, E.; Meduri, A. [RefusalBench: Why Refusal Rate Misranks Frontier LLMs on Biological Research Prompts](https://arxiv.org/abs/2605.21545v1). arXiv:2605.21545v1, 20 May (2026).

**44.** OpenAI [Building an early warning system for LLM-aided biological threat creation](https://openai.com/index/building-an-early-warning-system-for-llm-aided-biological-threat-creation/). Technical report, 31 January (2024).

**5.** Sehwag, U. M.; Dalvi, A.; Maurya, Y.; Rein, D.; Hardee, D.; Kritz, J.; Nguyen, J.; Herring, B.; Fuelle, E.; Knight, C. Q.; Brandifino, J.; Fenkell, M. [DualChem: Measuring LLM Uplift and Dual-Use Risk Awareness in Chemistry](https://labs.scale.com/papers/dualchem). Scale AI technical report; official PDF linked to 28 October release, retrieved 31 October (2026).

**1.** McCaslin, T.; Alaga, J.; Nedungadi, S.; Donoughe, S.; Reed, T.; Bommasani, R.; Painter, C.; Righetti, L. [STREAM (ChemBio): A Standard for Transparently Reporting Evaluations in AI Model Reports](https://arxiv.org/abs/2508.09853v2). arXiv:2508.09853v2, 3 September (2025).

**47.** [Wong, A.; Cao, H.; Liu, Z.; Li, Y. SMILES-Prompting: A Novel Approach to LLM Jailbreak Attacks in Chemical Synthesis. arXiv:2410.15641v1, 21 October (2024).](https://arxiv.org/abs/2410.15641v1)

**48.** [He, J., et al. Controlling Risks of AI in Chemical Science with Agents. arXiv:2312.06632v2, 20 September (2026).](https://arxiv.org/abs/2312.06632v2)

**49.** [Maskey, U.; Dras, M.; Naseem, U. Steering Over-refusals Towards Safety in Retrieval Augmented Generation. arXiv:2510.10452v1, 12 October (2025).](https://arxiv.org/abs/2510.10452v1)

**50.** [Knight, C. Q., et al. FORTRESS: Frontier Risk Evaluation for National Security and Public Safety. arXiv:2506.14922v1, 17 June (2025).](https://arxiv.org/abs/2506.14922v1)

**51.** [Li, N., et al. The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning. arXiv:2403.03218v7, 15 May (2024).](https://arxiv.org/abs/2403.03218v7)

**52.** [Alampara, N., et al. Probing the limitations of multimodal language models for chemistry and materials research. arXiv:2411.16955v1, 25 November (2024).](https://arxiv.org/abs/2411.16955v1)
