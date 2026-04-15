"""
scorer.py — Programmatic benchmark scorer used by the orchestrator.

Called automatically after any job whose URL matches the ShopEase benchmark site.
Compares tester findings against ground_truth.json and returns recall/precision/F1.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

from benchmark.check_results import score_findings, load_ground_truth  # noqa: F401


GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"


def is_benchmark_job(url: str) -> bool:
    """Return True if the job URL is the ShopEase benchmark site."""
    if not url:
        return False
    truth = load_ground_truth()
    netloc = truth.get("meta", {}).get("url_netloc", "")
    return netloc and netloc in url


def score_job(graph) -> Dict[str, Any] | None:
    """
    Given a completed ScreenGraph, extract all findings and score against ground truth.
    Returns the score dict, or None if this isn't a benchmark job.
    """
    all_findings: List[Dict] = []
    for node in graph.nodes.values():
        all_findings.extend(getattr(node, "findings", []))

    return score_findings(all_findings)


def format_benchmark_section(score: Dict[str, Any]) -> str:
    """Return a markdown section to append to the job report."""
    found   = score["found"]
    total   = score["total_planted"]
    missed  = score.get("missed_bugs", [])
    fp      = score["false_positives"]
    recall  = score["recall"]
    prec    = score["precision"]
    f1      = score["f1"]

    lines = [
        "",
        "---",
        "",
        "## Benchmark Score — ShopEase",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Bugs found | {found} / {total} |",
        f"| Recall | {recall}% |",
        f"| Precision | {prec}% |",
        f"| **F1 Score** | **{f1}%** |",
        f"| False positives | {fp} |",
    ]

    if missed:
        lines.append(f"| Missed bugs | {', '.join(missed)} |")

    lines += [
        "",
        f"> Recall = bugs found / total planted bugs  ",
        f"> Precision = planted bugs found / total findings reported",
    ]

    return "\n".join(lines)
