# PatAgent

PatAgent is a dependency-free, evidence-linked reviewer for cheminformatics,
molecular modeling, and molecular machine-learning pipelines. It operationalizes
recurring recommendations in Pat Walters's public blog, papers, tutorials, and
code as preflight and postflight checks.

PatAgent is not Pat Walters, is not endorsed by him, and does not speak for him.
It should be described as an independent reviewer inspired by cited public work.

## Complete blog corpus

The sync command retrieves every post reported by the public Practical
Cheminformatics Blogger feed and every `_posts/*.md` file reported by Pat
Walters's public GitHub Pages repository. As verified on 2026-08-06, this is 74
archived Blogger posts plus 16 current-site posts (90 total). Counts may grow.

```bash
python3 server.py sync-corpus
python3 server.py search --query "dataset splitting leakage scaffold temporal"
```

Embedded base64 images are stripped from the text index. Guest posts remain
searchable but are tagged `authorship: guest` and down-ranked; their claims must
not be attributed to Pat.

## Mandatory pipeline gate

Run preflight before expensive compute and postflight before promoting results:

```bash
python3 server.py audit --input pipeline-preflight.json --output pat-preflight.json
python3 server.py audit --input pipeline-postflight.json --output pat-postflight.json
```

Exit code `2` means a decision-critical audit is blocked. `0` means the pipeline
may proceed, possibly with nonblocking warnings listed in the JSON report.

Minimal manifest shape:

```json
{
  "pipeline_type": "ml",
  "stage": "preflight",
  "decision_context": "decision-critical",
  "purpose": "Prioritize compounds for a measured solubility assay",
  "data": {
    "structure_parse_failures": 0,
    "conflicting_duplicate_labels": 0,
    "representation_policy_documented": true,
    "provenance_documented": true,
    "endpoint_and_units_defined": true,
    "experimental_error_estimated": true,
    "dynamic_range_relevant": true,
    "artifacts_assessed": true
  },
  "validation": {
    "split_strategy_and_rationale": "Temporal holdout matching deployment",
    "hyperparameters_tuned_on_test": false,
    "applicability_domain_reported": true
  },
  "comparison": {
    "method_count": 2,
    "baselines": ["mean predictor", "random forest"]
  },
  "reproducibility": {
    "inputs_versioned": true,
    "software_versions_recorded": true,
    "random_seeds_recorded": true
  }
}
```

Postflight adds measured overlap counts, uncertainty intervals, statistical and
practical comparisons, output-range checks, prospective/blind status, and output
provenance. Docking/co-folding, generative-design, and molecular-dynamics
manifests activate additional domain-specific gates.

## Smoke test

```bash
python3 server.py smoke-test
```

The smoke test is network-free. It checks a passing fixture, a deliberately
flawed fixture, guest-post attribution, embedded-image removal, and the stable
evidence catalog.

## Rights and citations

The local index exists for retrieval and evaluation. Reports should cite and
link the underlying post or publication, paraphrase recommendations, avoid long
verbatim passages, and respect publisher rights. Paywalled full text is never
downloaded by the wrapper.
