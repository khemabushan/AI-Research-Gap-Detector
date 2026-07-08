"""
Small, dependency-free text normalization helpers shared across services.
"""
import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace/newlines into single spaces and trim."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def strip_latex_artifacts(text: str) -> str:
    """
    arXiv abstracts frequently contain raw LaTeX (e.g. $\\alpha$, \\emph{...}).
    This is a light best-effort cleanup, not a full LaTeX parser.
    """
    if not text:
        return ""
    text = re.sub(r"\$\$?(.*?)\$\$?", r"\1", text)  # inline/display math
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)  # \emph{word} -> word
    text = re.sub(r"\\[a-zA-Z]+", "", text)  # stray commands like \noindent
    return normalize_whitespace(text)


def normalize_title_for_dedup(title: str) -> str:
    """
    Produce a comparison key for near-duplicate title matching:
    lowercase, strip accents/punctuation, collapse whitespace.
    """
    if not title:
        return ""
    title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    return normalize_whitespace(title)


def truncate(text: str, max_chars: int = 4000) -> str:
    """Guard against oversized inputs going into embedding/LLM calls."""
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."
