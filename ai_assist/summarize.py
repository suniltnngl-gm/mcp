"""AI-powered summaries for review cycles and search results."""

from typing import List

from ai_assist.client import ask, ask_smart
from review_cycle.models import ScanFinding, ReviewSummary


def summarize_report(findings: List[ScanFinding], summary: ReviewSummary) -> str:
    items = "\n".join(
        f"- [{f.severity}] {f.repo}: {f.summary}" for f in findings[:8]
    )
    prompt = (
        f"Workspace review complete:\n"
        f"Health score: {summary.score:.1f}/100\n"
        f"Findings: {summary.total_findings} ({summary.blockers}b/{summary.critical}c/{summary.warnings}w/{summary.infos}i)\n\n"
        f"Top findings:\n{items}\n\n"
        f"Write a 2-3 sentence executive summary of workspace health."
    )
    return ask_smart(prompt, max_tokens=256)


def explain_search_results(query: str, top_results: List[dict]) -> str:
    items = "\n".join(
        f"- {r.get('repo','?')}: {r.get('path','')[-60:]} (score {r.get('score',0)})"
        for r in top_results[:5]
    )
    prompt = (
        f"User searched for: '{query}'\n\nTop results:\n{items}\n\n"
        f"In one sentence, explain why these results are relevant to the query."
    )
    return ask(prompt, max_tokens=150)


def answer_query(query: str, context: str) -> str:
    prompt = (
        f"Based on this workspace context, answer the question concisely.\n\n"
        f"Context:\n{context[:1500]}\n\n"
        f"Question: {query}"
    )
    return ask_smart(prompt, max_tokens=512)
