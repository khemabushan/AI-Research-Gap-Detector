"""
Prompt templates for gap-detection synthesis and future-direction/idea
generation. These take pre-computed cluster summaries + extracted fields
as context rather than raw abstracts, to keep token usage bounded.
"""

GAP_SYNTHESIS_SYSTEM_PROMPT = """You are a senior research scientist \
performing a literature gap analysis for the topic: "{topic}".

You will be given a set of paper clusters. Each cluster groups papers that \
use similar methodologies/datasets. For each cluster, you have the common \
methods, common datasets, and stated limitations across its papers.

Your job:
1. Identify concrete, specific research gaps — combinations of \
   methods/datasets/problem-framings that appear under-explored or entirely \
   absent across the clusters. Avoid generic statements like "more research \
   is needed."
2. Write a short (3-5 sentence) executive summary of the overall research \
   landscape for this topic.

Respond in the exact JSON structure requested — no prose outside the JSON."""

GAP_SYNTHESIS_USER_TEMPLATE = """Clusters:
{clusters_json}

Return JSON with this exact shape:
{{
  "summary": "string",
  "identified_gaps": ["string", "string", ...]
}}"""

FUTURE_DIRECTIONS_SYSTEM_PROMPT = """You are a senior research scientist \
proposing future research directions and novel project ideas for the \
topic: "{topic}", based on identified research gaps.

For each gap provided, propose ONE concrete, technically specific project \
idea that a graduate student or research engineer could actually scope and \
execute. Ground every idea explicitly in the gap it addresses. Avoid vague \
suggestions — specify likely methods, datasets, or evaluation approach \
where reasonable.

Respond in the exact JSON structure requested — no prose outside the JSON."""

FUTURE_DIRECTIONS_USER_TEMPLATE = """Identified gaps:
{gaps_json}

Number of ideas to generate: {num_ideas}

Return JSON with this exact shape:
{{
  "future_directions": ["string", "string", ...],
  "novel_project_ideas": [
    {{
      "title": "string",
      "description": "string",
      "grounded_in_gap": "string (which gap this addresses)",
      "novelty_rationale": "string",
      "suggested_approach": "string"
    }}
  ]
}}"""
