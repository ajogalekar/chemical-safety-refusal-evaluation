#!/usr/bin/env python3
"""PatAgent: evidence-linked checks for molecular modeling pipelines.

The core is dependency-free.  It provides three useful surfaces:

* ``audit`` runs preflight or postflight quality gates on a JSON manifest.
* ``sync-corpus`` builds a local, attribution-aware corpus from every public
  Practical Cheminformatics post on Blogger and Pat Walters's GitHub Pages site.
* ``search`` retrieves relevant posts from that corpus for evidence-linked review.

PatAgent is an independent reviewer inspired by public writings.  It is not Pat
Walters and does not claim to reproduce his judgment or speak on his behalf.
"""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable, Iterable
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
EVIDENCE_PATH = ROOT / "evidence.json"
SOURCE_PATH = ROOT / "corpus-sources.json"
DEFAULT_CORPUS = ROOT / "corpus" / "blog.jsonl"
DEFAULT_MANIFEST = ROOT / "corpus" / "manifest.json"

BLOGGER_FEED = "https://practicalcheminformatics.blogspot.com/feeds/posts/default"
GITHUB_TREE = "https://api.github.com/repos/PatWalters/patwalters.github.io/git/trees/master"
GITHUB_RAW = "https://raw.githubusercontent.com/PatWalters/patwalters.github.io/master/"
SITE_ROOT = "https://patwalters.github.io"

MOLECULAR_PIPELINES = {
    "cheminformatics",
    "ml",
    "qsar",
    "admet",
    "docking",
    "virtual-screening",
    "cofolding",
    "generative-design",
    "molecular-dynamics",
    "molecular-modeling",
}


class PatAgentError(ValueError):
    pass


class _TextExtractor(HTMLParser):
    """Extract visible text without retaining embedded image payloads."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg"}:
            self.ignored_depth += 1
        elif tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "tr", "div"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg"} and self.ignored_depth:
            self.ignored_depth -= 1
        elif tag in {"p", "li", "h1", "h2", "h3", "h4", "tr", "div"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)

    def text(self) -> str:
        value = html.unescape("".join(self.parts))
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\n[ \t]+", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def _http_bytes(url: str, *, accept: str = "application/json", timeout: int = 180) -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": f"PatAgent/{VERSION} (+local evidence indexer)",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    last_error: OSError | None = None
    for _ in range(3):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except OSError as exc:
            last_error = exc
    raise PatAgentError(f"failed to fetch {url}: {last_error}")


def _http_json(url: str) -> dict[str, Any]:
    return json.loads(_http_bytes(url).decode("utf-8"))


def _json_read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(rendered, encoding="utf-8")
    temp.replace(path)


def _read_input(path: str | None) -> dict[str, Any]:
    if path and path != "-":
        value = _json_read(Path(path))
    else:
        value = json.load(sys.stdin)
    if not isinstance(value, dict):
        raise PatAgentError("input must be a JSON object")
    return value


def _write_output(value: Any, path: str | None = None) -> None:
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def _clean_html(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value)
    return parser.text()


def _split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown
    end = markdown.find("\n---\n", 4)
    if end < 0:
        return {}, markdown
    header = markdown[4:end]
    body = markdown[end + 5 :]
    metadata: dict[str, Any] = {}
    current_list: str | None = None
    for raw_line in header.splitlines():
        if re.match(r"^\s+-\s+", raw_line) and current_list:
            metadata.setdefault(current_list, []).append(
                re.sub(r"^\s+-\s+", "", raw_line).strip().strip("\"'")
            )
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not match:
            continue
        key, raw_value = match.groups()
        raw_value = raw_value.strip()
        if not raw_value:
            metadata[key] = []
            current_list = key
        else:
            metadata[key] = raw_value.strip("\"'")
            current_list = None
    return metadata, body


def _clean_markdown(value: str) -> str:
    # GitHub posts embed large data:image payloads in Markdown reference lines.
    value = re.sub(
        r"(?m)^\[[^\]]+\]:\s*<?data:image/[^\n]*\n?",
        "",
        value,
    )
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", value)
    value = re.sub(r"!\[[^\]]*\]\[[^\]]*\]", " ", value)
    value = re.sub(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", value)
    value = re.sub(r"(?m)^\[[^\]]+\]:\s*\S+.*$", "", value)
    value = re.sub(r"(?m)^#{1,6}\s*", "", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = value.replace("\\=", "=").replace("\\_", "_").replace("\\.", ".")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _detect_authorship(text: str, feed_author: str = "Pat Walters") -> tuple[str, str]:
    opening = text[:1800]
    guest = re.search(
        r"(?i)\b(?:a[ \t]+)?guest[ \t]+post[ \t]+(?:written[ \t]+)?by[ \t]+"
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+(?:[ \t]+[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+){1,4})",
        opening,
    )
    if guest:
        return "guest", guest.group(1).strip()
    if feed_author.casefold() in {"pat walters", "patrick walters", "w patrick walters"}:
        return "pat-authored", "Pat Walters"
    return "other", feed_author


def _alternate_link(entry: dict[str, Any]) -> str:
    for link in entry.get("link", []):
        if link.get("rel") == "alternate":
            return str(link.get("href", ""))
    return ""


def _blogger_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    start = 1
    page_size = 25
    expected_total: int | None = None
    while expected_total is None or start <= expected_total:
        query = urlencode({"alt": "json", "max-results": page_size, "start-index": start})
        payload = _http_json(f"{BLOGGER_FEED}?{query}")
        feed = payload.get("feed", {})
        expected_total = int(feed.get("openSearch$totalResults", {}).get("$t", 0))
        entries = feed.get("entry", []) or []
        if not entries:
            break
        for entry in entries:
            raw_html = str(entry.get("content", {}).get("$t", ""))
            text = _clean_html(raw_html)
            feed_author = str(
                ((entry.get("author") or [{}])[0].get("name") or {}).get("$t", "Pat Walters")
            )
            authorship, byline = _detect_authorship(text, feed_author)
            categories = [
                str(item.get("term")) for item in entry.get("category", []) if item.get("term")
            ]
            records.append(
                {
                    "id": str(entry.get("id", {}).get("$t", "")),
                    "source": "blogger",
                    "kind": "blog-post",
                    "title": str(entry.get("title", {}).get("$t", "Untitled")),
                    "published": str(entry.get("published", {}).get("$t", "")),
                    "updated": str(entry.get("updated", {}).get("$t", "")),
                    "url": _alternate_link(entry),
                    "feed_author": feed_author,
                    "authorship": authorship,
                    "byline": byline,
                    "tags": categories,
                    "text": text,
                }
            )
        start += len(entries)
    if expected_total is not None and len(records) != expected_total:
        raise PatAgentError(
            f"Blogger sync was incomplete: expected {expected_total} posts, received {len(records)}"
        )
    return records


def _github_records() -> list[dict[str, Any]]:
    payload = _http_json(f"{GITHUB_TREE}?recursive=1")
    if payload.get("truncated"):
        raise PatAgentError("GitHub tree response was truncated")
    paths = sorted(
        str(item["path"])
        for item in payload.get("tree", [])
        if item.get("type") == "blob" and str(item.get("path", "")).startswith("_posts/")
    )
    records: list[dict[str, Any]] = []
    for path in paths:
        markdown = _http_bytes(GITHUB_RAW + quote(path, safe="/") , accept="text/plain").decode(
            "utf-8", errors="replace"
        )
        metadata, body = _split_frontmatter(markdown)
        text = _clean_markdown(body)
        authorship, byline = _detect_authorship(text)
        filename = Path(path).stem
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", filename)
        inferred_date = date_match.group(1) if date_match else ""
        slug = date_match.group(2) if date_match else filename
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        records.append(
            {
                "id": f"github:{path}",
                "source": "github-pages",
                "kind": "blog-post",
                "title": str(metadata.get("title") or slug.replace("-", " ")),
                "published": str(metadata.get("date") or inferred_date),
                "updated": "",
                "url": f"{SITE_ROOT}/{slug}/",
                "repository_path": path,
                "feed_author": "Pat Walters",
                "authorship": authorship,
                "byline": byline,
                "tags": tags,
                "text": text,
            }
        )
    return records


def sync_corpus(corpus_path: Path = DEFAULT_CORPUS, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    archived = _blogger_records()
    current = _github_records()
    records = archived + current
    records.sort(key=lambda item: (str(item.get("published", "")), str(item.get("title", ""))))
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    temp = corpus_path.with_suffix(corpus_path.suffix + ".tmp")
    digest = hashlib.sha256()
    with temp.open("w", encoding="utf-8") as handle:
        for record in records:
            line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            digest.update(line.encode("utf-8"))
            handle.write(line)
    temp.replace(corpus_path)
    authorship_counts: dict[str, int] = {}
    for record in records:
        key = str(record["authorship"])
        authorship_counts[key] = authorship_counts.get(key, 0) + 1
    manifest = {
        "schema_version": "1.0",
        "agent": "pat-agent",
        "corpus_path": str(corpus_path),
        "records": len(records),
        "source_counts": {"blogger": len(archived), "github-pages": len(current)},
        "authorship_counts": authorship_counts,
        "sha256": digest.hexdigest(),
        "coverage": "complete public Practical Cheminformatics archive at sync time",
        "attribution_note": (
            "Guest posts remain searchable but are marked guest and must not be represented as "
            "Pat Walters's own views."
        ),
    }
    _json_write(manifest_path, manifest)
    return manifest


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9+.-]{1,}", value.casefold())


def _snippet(text: str, terms: list[str], width: int = 520) -> str:
    lowered = text.casefold()
    positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - width // 4)
    end = min(len(text), start + width)
    snippet = text[start:end].strip()
    if start:
        snippet = "…" + snippet
    if end < len(text):
        snippet += "…"
    return re.sub(r"\s+", " ", snippet)


def search_corpus(query: str, corpus_path: Path = DEFAULT_CORPUS, limit: int = 8) -> dict[str, Any]:
    if not corpus_path.exists():
        raise PatAgentError(
            f"corpus not found at {corpus_path}; run sync-corpus before searching"
        )
    terms = list(dict.fromkeys(_tokens(query)))
    if not terms:
        raise PatAgentError("search query must contain at least one word")
    scored: list[tuple[float, dict[str, Any]]] = []
    with corpus_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            title = str(record.get("title", ""))
            tags = " ".join(str(item) for item in record.get("tags", []))
            text = str(record.get("text", ""))
            title_lower = title.casefold()
            tags_lower = tags.casefold()
            text_lower = text.casefold()
            score = 0.0
            for term in terms:
                score += 12.0 * title_lower.count(term)
                score += 5.0 * tags_lower.count(term)
                score += min(12, text_lower.count(term))
            if all(term in (title_lower + " " + tags_lower + " " + text_lower) for term in terms):
                score += 8.0
            if record.get("authorship") == "guest":
                score *= 0.8
            if score:
                scored.append((score, record))
    scored.sort(key=lambda item: (item[0], str(item[1].get("published", ""))), reverse=True)
    results = []
    for score, record in scored[: max(1, limit)]:
        results.append(
            {
                "score": round(score, 3),
                "title": record.get("title"),
                "published": record.get("published"),
                "url": record.get("url"),
                "authorship": record.get("authorship"),
                "byline": record.get("byline"),
                "tags": record.get("tags", []),
                "snippet": _snippet(str(record.get("text", "")), terms),
            }
        )
    return {"query": query, "corpus": str(corpus_path), "matches": len(scored), "results": results}


def _get(payload: dict[str, Any], path: str) -> tuple[bool, Any]:
    value: Any = payload
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return False, None
        value = value[part]
    return True, value


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _condition_always(_: dict[str, Any]) -> bool:
    return True


def _condition_multiple_methods(payload: dict[str, Any]) -> bool:
    found, value = _get(payload, "comparison.method_count")
    return found and isinstance(value, (int, float)) and value > 1


def _condition_allosteric(payload: dict[str, Any]) -> bool:
    found, value = _get(payload, "modeling.allosteric_relevant")
    return found and value is True


def _condition_decision_critical(payload: dict[str, Any]) -> bool:
    return payload.get("decision_context", "decision-critical") == "decision-critical"


CONDITIONS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "always": _condition_always,
    "multiple-methods": _condition_multiple_methods,
    "allosteric": _condition_allosteric,
    "decision-critical": _condition_decision_critical,
}


def _gate(
    gate_id: str,
    title: str,
    path: str,
    check: str,
    evidence: list[str],
    *,
    pipelines: Iterable[str] = MOLECULAR_PIPELINES,
    stages: Iterable[str] = ("preflight", "postflight", "full"),
    severity: str = "critical",
    condition: str = "always",
    remediation: str,
) -> dict[str, Any]:
    return {
        "id": gate_id,
        "title": title,
        "path": path,
        "check": check,
        "evidence": evidence,
        "pipelines": set(pipelines),
        "stages": set(stages),
        "severity": severity,
        "condition": condition,
        "remediation": remediation,
    }


GATES = [
    _gate("purpose-defined", "Decision and use case are defined", "purpose", "present", ["evaluation-guidelines-2022"], remediation="State the scientific question, user, decision, and cost of error."),
    _gate("inputs-versioned", "Inputs are versioned and traceable", "reproducibility.inputs_versioned", "true", ["reproducibility-2013", "code-sharing-2020"], remediation="Version inputs and record stable identifiers or checksums."),
    _gate("software-recorded", "Software versions and environment are recorded", "reproducibility.software_versions_recorded", "true", ["reproducibility-2013", "code-sharing-2020"], remediation="Capture package, model, database, and environment versions."),
    _gate("seeds-recorded", "Random seeds are recorded", "reproducibility.random_seeds_recorded", "true", ["code-sharing-2020", "method-comparison-2025"], severity="major", remediation="Record every seed and nondeterministic backend setting."),
    _gate("structure-parse", "All molecular structures parse", "data.structure_parse_failures", "zero", ["better-benchmarks-2023"], pipelines={"cheminformatics", "ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design", "molecular-modeling"}, remediation="Correct or explicitly exclude invalid structures and report every exclusion."),
    _gate("duplicate-conflicts", "Duplicate structures do not carry conflicting labels", "data.conflicting_duplicate_labels", "zero", ["better-benchmarks-2023", "tautomers-2025"], pipelines={"cheminformatics", "ml", "qsar", "admet", "virtual-screening", "generative-design"}, remediation="Canonicalize for duplicate detection, reconcile conflicts, and preserve the chosen input representation."),
    _gate("representation-policy", "Representation and standardization policy is documented", "data.representation_policy_documented", "true", ["better-benchmarks-2023", "tautomers-2025"], pipelines={"cheminformatics", "ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design", "molecular-modeling"}, remediation="Document charge, salt, stereochemistry, tautomer, protonation, and exclusion policies."),
    _gate("provenance", "Experimental provenance is preserved", "data.provenance_documented", "true", ["better-benchmarks-2023", "getting-real-2023"], pipelines={"ml", "qsar", "admet", "virtual-screening", "generative-design"}, remediation="Record source, assay protocol, lab, dates, units, qualifiers, and transformations."),
    _gate("endpoint", "Endpoint and units match the intended use", "data.endpoint_and_units_defined", "true", ["better-benchmarks-2023", "getting-real-2023"], pipelines={"ml", "qsar", "admet", "virtual-screening", "generative-design"}, remediation="Define the endpoint, units, censoring, thresholds, and their decision relevance."),
    _gate("experimental-error", "Experimental error and attainable performance are estimated", "data.experimental_error_estimated", "true", ["model-ceiling-2019", "getting-real-2023"], pipelines={"ml", "qsar", "admet"}, remediation="Estimate replicate error and simulate or derive an attainable performance ceiling."),
    _gate("dynamic-range", "Dynamic range is realistic", "data.dynamic_range_relevant", "true", ["better-benchmarks-2023", "published-isnt-right-2025"], pipelines={"ml", "qsar", "admet"}, remediation="Compare train/test ranges with the operational assay range and explain censoring."),
    _gate("artifact-review", "Assay and chemical artifacts are assessed", "data.artifacts_assessed", "true", ["better-benchmarks-2023"], pipelines={"cheminformatics", "ml", "qsar", "admet", "virtual-screening", "generative-design"}, severity="major", remediation="Assess interference, reactive motifs, aggregation, nuisance compounds, and orthogonal evidence."),
    _gate("split-rationale", "Split strategy reflects deployment", "validation.split_strategy_and_rationale", "present", ["splitting-2024", "getting-real-2023"], pipelines={"ml", "qsar", "admet", "virtual-screening", "generative-design"}, remediation="Predeclare random, cluster/Butina, temporal, or prospective splits and justify them."),
    _gate("test-untouched", "Test set is isolated from tuning", "validation.hyperparameters_tuned_on_test", "false", ["evaluation-guidelines-2022", "method-comparison-2025"], pipelines={"ml", "qsar", "admet", "virtual-screening", "generative-design"}, remediation="Move all tuning and model selection into training/validation or nested resampling."),
    _gate("split-overlap", "Duplicate and analogue leakage checks pass", "validation.detected_split_overlap_count", "zero", ["better-benchmarks-2023", "splitting-2024"], pipelines={"ml", "qsar", "admet", "virtual-screening", "generative-design"}, stages={"postflight", "full"}, remediation="Remove identity leakage and quantify scaffold, analogue, temporal, target, and assay overlap."),
    _gate("domain", "Applicability domain and train-test similarity are reported", "validation.applicability_domain_reported", "true", ["getting-real-2023", "published-isnt-right-2025"], pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design"}, remediation="Report nearest-neighbor and distribution shift analyses in the representation used by the model."),
    _gate("baseline", "Relevant simple and null baselines are included", "comparison.baselines", "present", ["getting-real-2023", "why-no-extrapolation-2025", "method-comparison-2025"], pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design"}, remediation="Include a null/mean or prevalence baseline and a credible simple or conventional method."),
    _gate("uncertainty", "Metrics include uncertainty distributions", "comparison.uncertainty_intervals_reported", "true", ["classification-tutorial-2022", "getting-real-2023", "method-comparison-2025"], stages={"postflight", "full"}, pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design", "molecular-dynamics", "molecular-modeling"}, remediation="Report fold/run distributions and confidence intervals, not only mean metrics."),
    _gate("multiplicity", "Multiple comparisons are controlled", "comparison.multiple_comparison_control", "true", ["multiple-comparisons-2019", "classification-tutorial-2022", "method-comparison-2025"], stages={"postflight", "full"}, pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design"}, condition="multiple-methods", remediation="Use a design-appropriate omnibus/pairwise protocol and multiplicity correction."),
    _gate("practical-significance", "Practical significance is separated from statistical significance", "comparison.practical_significance_discussed", "true", ["getting-real-2023", "method-comparison-2025"], stages={"postflight", "full"}, pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design"}, remediation="Report effect size, uncertainty, and whether the difference changes a real decision."),
    _gate("model-output-range", "Prediction range and extrapolation are checked", "validation.output_range_checked", "true", ["why-no-extrapolation-2025"], stages={"postflight", "full"}, pipelines={"ml", "qsar", "admet", "generative-design"}, severity="major", remediation="Compare predicted ranges with train/test ranges and flag unsupported extrapolation."),
    _gate("pose-validity", "Predicted poses pass physical and geometric checks", "modeling.pose_geometry_checked", "true", ["cofolding-2025"], pipelines={"docking", "virtual-screening", "cofolding"}, stages={"postflight", "full"}, remediation="Check clashes, strain, stereochemistry, protonation, interactions, and pose plausibility."),
    _gate("ranked-vs-oracle", "Ranked and oracle pose performance are separated", "modeling.ranked_and_oracle_reported", "true", ["cofolding-2025"], pipelines={"docking", "cofolding"}, stages={"postflight", "full"}, severity="major", remediation="Report the top-ranked result separately from the best result among generated poses."),
    _gate("training-similarity", "Protein, pocket, and ligand training similarity are assessed", "modeling.training_similarity_reported", "true", ["cofolding-2025"], pipelines={"docking", "cofolding"}, remediation="Stratify performance by protein sequence, pocket, and ligand similarity to training data."),
    _gate("allosteric", "Relevant allosteric cases are tested", "modeling.allosteric_cases_tested", "true", ["cofolding-2025"], pipelines={"docking", "cofolding"}, condition="allosteric", remediation="Include allosteric benchmarks and verify the predicted pocket, not only ligand RMSD."),
    _gate("generation-validity", "Generated molecules are chemically valid and unique", "generation.validity_and_uniqueness_reported", "true", ["generative-raise-bar-2023"], pipelines={"generative-design"}, stages={"postflight", "full"}, remediation="Report validity, uniqueness, sanitization failures, duplicates, and representation policy."),
    _gate("generation-novelty", "Novelty is measured against training examples", "generation.nearest_training_neighbors_reported", "true", ["generative-raise-bar-2023"], pipelines={"generative-design"}, stages={"postflight", "full"}, remediation="Show nearest training molecules and quantify memorization, not only database novelty."),
    _gate("generation-synthesis", "Synthesizability and artifacts are assessed", "generation.synthesis_and_artifacts_assessed", "true", ["generative-raise-bar-2023"], pipelines={"generative-design"}, stages={"postflight", "full"}, remediation="Apply chemistry review, tractable synthesis analysis, nuisance filters, and orthogonal scoring."),
    _gate("md-convergence", "Replicates and convergence are reported", "modeling.replicates_and_convergence_reported", "true", ["reproducibility-2013"], pipelines={"molecular-dynamics"}, stages={"postflight", "full"}, remediation="Run independent replicas and report equilibration, convergence, uncertainty, and sensitivity."),
    _gate("blind-or-prospective", "Claims are checked prospectively or blindly", "validation.blind_or_prospective_validation", "true", ["blind-challenges-2026"], pipelines={"ml", "qsar", "admet", "docking", "virtual-screening", "cofolding", "generative-design", "molecular-modeling"}, stages={"postflight", "full"}, severity="major", condition="decision-critical", remediation="Use a held-out, temporal, blind, or prospective evaluation before strong operational claims."),
    _gate("outputs-traceable", "Outputs and exclusions are traceable", "reproducibility.outputs_and_exclusions_recorded", "true", ["reproducibility-2013", "code-sharing-2020"], stages={"postflight", "full"}, remediation="Save configs, logs, exclusions, checksums, code revision, and machine-readable results."),
]


def _evaluate(check: str, found: bool, value: Any) -> tuple[str, str]:
    if not found:
        return "unresolved", "required field was not supplied"
    if check == "present":
        return ("pass", "documented") if _present(value) else ("fail", "value is empty")
    if check == "true":
        if value is True:
            return "pass", "confirmed"
        if value is False:
            return "fail", "explicitly false"
        return "unresolved", "expected a boolean"
    if check == "false":
        if value is False:
            return "pass", "confirmed false"
        if value is True:
            return "fail", "explicitly true"
        return "unresolved", "expected a boolean"
    if check == "zero":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return "unresolved", "expected a numeric count"
        return ("pass", "count is zero") if value == 0 else ("fail", f"count is {value}")
    raise PatAgentError(f"unknown gate check {check!r}")


def audit_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    pipeline = str(payload.get("pipeline_type", "")).strip().casefold()
    stage = str(payload.get("stage", "full")).strip().casefold()
    context = str(payload.get("decision_context", "decision-critical")).strip().casefold()
    if pipeline not in MOLECULAR_PIPELINES:
        raise PatAgentError(f"pipeline_type must be one of {sorted(MOLECULAR_PIPELINES)}")
    if stage not in {"preflight", "postflight", "full"}:
        raise PatAgentError("stage must be preflight, postflight, or full")
    if context not in {"exploratory", "decision-critical"}:
        raise PatAgentError("decision_context must be exploratory or decision-critical")
    evidence = _json_read(EVIDENCE_PATH)
    evidence_by_id = {item["id"]: item for item in evidence["sources"]}
    results = []
    for gate in GATES:
        if pipeline not in gate["pipelines"] or stage not in gate["stages"]:
            continue
        if not CONDITIONS[gate["condition"]](payload):
            continue
        found, value = _get(payload, gate["path"])
        status, detail = _evaluate(gate["check"], found, value)
        citations = []
        for source_id in gate["evidence"]:
            source = evidence_by_id[source_id]
            citations.append({"id": source_id, "title": source["title"], "url": source["url"]})
        results.append(
            {
                "id": gate["id"],
                "title": gate["title"],
                "severity": gate["severity"],
                "status": status,
                "detail": detail,
                "field": gate["path"],
                "remediation": gate["remediation"] if status != "pass" else None,
                "evidence": citations,
            }
        )
    counts = {status: sum(item["status"] == status for item in results) for status in ("pass", "fail", "unresolved")}
    blocking = [
        item["id"]
        for item in results
        if item["severity"] == "critical"
        and (item["status"] == "fail" or (item["status"] == "unresolved" and context == "decision-critical"))
    ]
    decision = "block" if blocking else ("proceed_with_warnings" if counts["fail"] or counts["unresolved"] else "proceed")
    return {
        "agent": "PatAgent",
        "agent_version": VERSION,
        "identity": "independent evidence-linked reviewer inspired by Pat Walters's public writings",
        "pipeline_type": pipeline,
        "stage": stage,
        "decision_context": context,
        "decision": decision,
        "blocking_gates": blocking,
        "counts": counts,
        "gates": results,
        "disclaimer": "PatAgent is not Pat Walters and does not speak for him.",
    }


def _smoke_test() -> dict[str, Any]:
    good = {
        "pipeline_type": "ml",
        "stage": "full",
        "decision_context": "exploratory",
        "purpose": "Rank compounds for a solubility assay follow-up.",
        "data": {
            "structure_parse_failures": 0,
            "conflicting_duplicate_labels": 0,
            "representation_policy_documented": True,
            "provenance_documented": True,
            "endpoint_and_units_defined": True,
            "experimental_error_estimated": True,
            "dynamic_range_relevant": True,
            "artifacts_assessed": True,
        },
        "validation": {
            "split_strategy_and_rationale": "temporal split",
            "hyperparameters_tuned_on_test": False,
            "detected_split_overlap_count": 0,
            "applicability_domain_reported": True,
            "output_range_checked": True,
            "blind_or_prospective_validation": True,
        },
        "comparison": {
            "method_count": 2,
            "baselines": ["mean predictor", "random forest"],
            "uncertainty_intervals_reported": True,
            "multiple_comparison_control": True,
            "practical_significance_discussed": True,
        },
        "reproducibility": {
            "inputs_versioned": True,
            "software_versions_recorded": True,
            "random_seeds_recorded": True,
            "outputs_and_exclusions_recorded": True,
        },
    }
    good_report = audit_pipeline(good)
    if good_report["decision"] != "proceed":
        raise PatAgentError("good audit fixture did not pass")
    bad = json.loads(json.dumps(good))
    bad["decision_context"] = "decision-critical"
    bad["data"]["structure_parse_failures"] = 3
    bad["data"]["conflicting_duplicate_labels"] = 2
    bad["data"]["provenance_documented"] = False
    bad["validation"]["hyperparameters_tuned_on_test"] = True
    bad["validation"]["detected_split_overlap_count"] = 4
    bad["comparison"]["baselines"] = []
    bad_report = audit_pipeline(bad)
    expected = {"structure-parse", "duplicate-conflicts", "provenance", "test-untouched", "split-overlap", "baseline"}
    if bad_report["decision"] != "block" or not expected.issubset(set(bad_report["blocking_gates"])):
        raise PatAgentError("bad audit fixture did not trigger required blockers")
    html_fixture = '<p>A guest post by Ada Lovelace</p><img src="data:image/png;base64,SECRET"><p>Models need tests.</p>'
    html_text = _clean_html(html_fixture)
    if "SECRET" in html_text or _detect_authorship(html_text) != ("guest", "Ada Lovelace"):
        raise PatAgentError("HTML cleaning or guest attribution fixture failed")
    markdown_fixture = "Text\n[image1]: <data:image/png;base64,SECRET>\nMore"
    if "SECRET" in _clean_markdown(markdown_fixture):
        raise PatAgentError("Markdown image payload stripping fixture failed")
    evidence = _json_read(EVIDENCE_PATH)
    if len(evidence.get("sources", [])) < 12:
        raise PatAgentError("evidence catalog is unexpectedly small")
    return {
        "ok": True,
        "agent_version": VERSION,
        "tests": {
            "passing_pipeline_fixture": "pass",
            "deliberately_flawed_pipeline_fixture": "blocked",
            "required_blockers_detected": sorted(expected),
            "embedded_image_payload_stripping": "pass",
            "guest_post_attribution": "pass",
            "evidence_catalog": len(evidence["sources"]),
        },
    }


def _policy() -> dict[str, Any]:
    sources = _json_read(SOURCE_PATH)
    evidence = _json_read(EVIDENCE_PATH)
    return {
        "agent": "PatAgent",
        "version": VERSION,
        "identity": "independent evidence-linked reviewer inspired by public writings",
        "automatic_scope": sorted(MOLECULAR_PIPELINES),
        "review_points": ["preflight before expensive compute", "in-flight provenance capture", "postflight before claims or decisions"],
        "corpus": sources,
        "curated_evidence_sources": len(evidence["sources"]),
        "disclaimer": "PatAgent is not Pat Walters and does not speak for him.",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("smoke-test", help="Run dependency-free audit and parser fixtures.")
    sub.add_parser("policy", help="Show activation scope, identity, and corpus policy.")
    audit = sub.add_parser("audit", help="Audit a pipeline manifest.")
    audit.add_argument("--input", default="-", help="JSON manifest path or - for stdin.")
    audit.add_argument("--output", default=None, help="Optional JSON report path.")
    sync = sub.add_parser("sync-corpus", help="Refresh the complete public blog corpus.")
    sync.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    sync.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    search = sub.add_parser("search", help="Search the synced Practical Cheminformatics corpus.")
    search.add_argument("--query", required=True)
    search.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    search.add_argument("--limit", type=int, default=8)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        if args.command == "smoke-test":
            result = _smoke_test()
        elif args.command == "policy":
            result = _policy()
        elif args.command == "audit":
            result = audit_pipeline(_read_input(args.input))
            _write_output(result, args.output)
            return 0 if result["decision"] != "block" else 2
        elif args.command == "sync-corpus":
            result = sync_corpus(Path(args.corpus), Path(args.manifest))
        elif args.command == "search":
            result = search_corpus(args.query, Path(args.corpus), args.limit)
        else:
            raise PatAgentError(f"unsupported command {args.command}")
        _write_output(result)
        return 0
    except (PatAgentError, OSError, json.JSONDecodeError) as exc:
        _write_output({"ok": False, "error": str(exc), "agent": "PatAgent"})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
