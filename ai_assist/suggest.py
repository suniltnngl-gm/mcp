"""AI-powered gap suggestions — given findings, suggest fixes."""

from typing import List

from ai_assist.client import ask, ask_smart
from review_cycle.models import ScanFinding


def suggest_fix(finding: ScanFinding) -> str:
    prompt = (
        f"Given this workspace finding:\n"
        f"- Repo: {finding.repo}\n"
        f"- Category: {finding.category}\n"
        f"- Severity: {finding.severity}\n"
        f"- Summary: {finding.summary}\n"
        f"- Detail: {finding.detail[:300]}\n\n"
        f"Suggest a concrete fix (1-2 sentences). Be specific about what file to change and how."
    )
    return ask(prompt, system="You are a workspace automation assistant. Suggest fixes concisely.")


def suggest_priority(findings: List[ScanFinding], top_n: int = 3) -> str:
    items = "\n".join(
        f"- [{f.severity}] {f.repo}: {f.summary}" for f in findings[:10]
    )
    prompt = (
        f"Given these workspace findings:\n{items}\n\n"
        f"Which {top_n} should be addressed first and why? "
        f"Consider impact, dependencies, and effort."
    )
    return ask_smart(prompt)


def explain_gap(gap_type: str, detail: str) -> str:
    prompt = (
        f"Explain why this gap matters and how to fix it:\n"
        f"Gap: {gap_type}\n"
        f"Detail: {detail[:300]}\n\n"
        f"Give a concise explanation (2-3 sentences)."
    )
    return ask(prompt)
