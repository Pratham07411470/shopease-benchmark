"""
check_results.py — Benchmark accuracy checker for the autonomous tester.

Compares the tester's findings against the ground truth (ground_truth.json)
and outputs a precision/recall score.

Usage:
    python benchmark/check_results.py <path-to-report.json>

The report JSON is the tester's output (artifacts/<site>/report.json or the
job's `report` field from the database).

Output:
    BUG DETECTION SCORE
    ─────────────────────────────────────────────────────────
    Found:   7 / 10 planted bugs
    Missed:  3 bugs (BUG-002, BUG-008, BUG-009)
    False positives: 1 (reported a bug that isn't real)
    ─────────────────────────────────────────────────────────
    Recall:    70.0%  (bugs found / total planted)
    Precision: 87.5%  (real bugs / all reported bugs)
    F1 Score:  77.8%
"""

from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any


GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"


def load_ground_truth() -> Dict[str, Any]:
    with open(GROUND_TRUTH_PATH) as f:
        return json.load(f)


def load_report(report_path: str) -> List[Dict[str, Any]]:
    """Load tester findings from a report JSON file."""
    with open(report_path) as f:
        data = json.load(f)
    # Support both {findings: [...]} and bare list
    if isinstance(data, list):
        return data
    return data.get("findings", data.get("bugs", []))


def bug_is_detected(bug: Dict, findings: List[Dict]) -> tuple[bool, str]:
    """
    Check if a planted bug was detected by the tester.
    Matches on detection_keywords in the finding's title, description, or hypothesis.
    Returns (found: bool, matched_finding: str)
    """
    keywords = [kw.lower() for kw in bug.get("detection_keywords", [])]
    bug_page = bug.get("page", "").lower()

    for finding in findings:
        text = " ".join([
            str(finding.get("title", "")),
            str(finding.get("description", "")),
            str(finding.get("finding", "")),
            str(finding.get("hypothesis", "")),
            str(finding.get("recommendation", "")),
        ]).lower()

        # Check if detection keywords match
        keyword_hits = sum(1 for kw in keywords if kw in text)
        if keyword_hits >= max(1, len(keywords) // 3):
            return True, finding.get("title") or finding.get("hypothesis") or "unnamed finding"

    return False, ""


def check_false_positives(findings: List[Dict], truth_bugs: List[Dict]) -> List[Dict]:
    """
    Identify findings that don't match any planted bug (potential false positives).
    Note: some may be real bugs we didn't plant — human review needed.
    """
    false_positives = []
    for finding in findings:
        text = " ".join([
            str(finding.get("title", "")),
            str(finding.get("description", "")),
            str(finding.get("finding", "")),
            str(finding.get("hypothesis", "")),
        ]).lower()

        matched_any_bug = any(
            sum(1 for kw in [k.lower() for k in bug.get("detection_keywords", [])] if kw in text) >= 1
            for bug in truth_bugs
        )
        if not matched_any_bug:
            false_positives.append(finding)

    return false_positives


def score_findings(findings: List[Dict]) -> Dict[str, Any]:
    """
    Score a list of tester findings against the ground truth.
    Returns a dict with recall, precision, f1, found, missed, false_positives.
    Used programmatically by the orchestrator for auto-scoring.
    """
    truth = load_ground_truth()
    planted_bugs = truth["bugs"]
    total_planted = len(planted_bugs)

    found_bugs  = []
    missed_bugs = []

    for bug in planted_bugs:
        detected, matched = bug_is_detected(bug, findings)
        if detected:
            found_bugs.append({**bug, "_matched_finding": matched})
        else:
            missed_bugs.append(bug)

    false_positives = check_false_positives(findings, planted_bugs)

    recall    = len(found_bugs) / total_planted if total_planted else 0
    precision = len(found_bugs) / (len(found_bugs) + len(false_positives)) if (len(found_bugs) + len(false_positives)) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "total_planted": total_planted,
        "found":         len(found_bugs),
        "missed":        len(missed_bugs),
        "false_positives": len(false_positives),
        "recall":    round(recall * 100, 1),
        "precision": round(precision * 100, 1),
        "f1":        round(f1 * 100, 1),
        "found_bugs":  [b["id"] for b in found_bugs],
        "missed_bugs": [b["id"] for b in missed_bugs],
    }


def run(report_path: str) -> None:
    truth = load_ground_truth()
    planted_bugs = truth["bugs"]
    total_planted = len(planted_bugs)

    try:
        findings = load_report(report_path)
    except FileNotFoundError:
        print(f"ERROR: Report file not found: {report_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in report: {e}")
        sys.exit(1)

    print("\n" + "═" * 60)
    print("  SHOPEASE BENCHMARK — BUG DETECTION RESULTS")
    print("═" * 60)
    print(f"  Planted bugs  : {total_planted}")
    print(f"  Tester findings: {len(findings)}")
    print("─" * 60)

    found_bugs = []
    missed_bugs = []

    for bug in planted_bugs:
        detected, matched = bug_is_detected(bug, findings)
        if detected:
            found_bugs.append(bug)
            print(f"  ✓  {bug['id']} [{bug['severity'].upper():8}]  {bug['title'][:45]}")
            print(f"         matched: {matched[:55]}")
        else:
            missed_bugs.append(bug)
            print(f"  ✗  {bug['id']} [{bug['severity'].upper():8}]  {bug['title'][:45]}")

    false_positives = check_false_positives(findings, planted_bugs)

    print("─" * 60)

    recall    = len(found_bugs) / total_planted if total_planted else 0
    precision = len(found_bugs) / (len(found_bugs) + len(false_positives)) if (len(found_bugs) + len(false_positives)) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n  Found   : {len(found_bugs)} / {total_planted} planted bugs")
    if missed_bugs:
        print(f"  Missed  : {', '.join(b['id'] for b in missed_bugs)}")
    print(f"  False + : {len(false_positives)} (findings not matching any planted bug — may be real bugs)")

    print()
    print(f"  Recall    : {recall*100:.1f}%  (bugs found / bugs planted)")
    print(f"  Precision : {precision*100:.1f}%  (planted bugs found / total findings)")
    print(f"  F1 Score  : {f1*100:.1f}%")
    print("═" * 60)

    # Breakdown by severity
    print("\n  BREAKDOWN BY SEVERITY")
    print("─" * 40)
    for severity in ["critical", "high", "medium", "low"]:
        sev_planted = [b for b in planted_bugs if b["severity"] == severity]
        sev_found   = [b for b in found_bugs   if b["severity"] == severity]
        if sev_planted:
            print(f"  {severity.upper():10} {len(sev_found)}/{len(sev_planted)} found")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Try to find the most recent report automatically
        artifacts_dir = Path(__file__).parent.parent / "artifacts"
        reports = sorted(artifacts_dir.rglob("report.json"), key=os.path.getmtime, reverse=True)
        if reports:
            print(f"No report path given. Using most recent: {reports[0]}")
            run(str(reports[0]))
        else:
            print("Usage: python benchmark/check_results.py <path-to-report.json>")
            print("       or run with no args to use the most recent artifacts/*/report.json")
            sys.exit(1)
    else:
        run(sys.argv[1])
