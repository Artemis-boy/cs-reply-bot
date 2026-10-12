"""CS Auto-Reply Bot core: FAQ keyword matching + auto tickets.

Demo portfolio project. No API keys, no real money, no personal data.
FAQ data lives in faq.json (editable without touching code).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
FAQ_PATH = ROOT / "faq.json"


def load_faq(path=FAQ_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def score_faq(question, entry):
    """Count keyword hits. Matches whole words or prefixes
    (e.g. 'promos' hits keyword 'promo'). Returns int score."""
    qwords = normalize(question).split()
    q = set(qwords)
    hits = 0
    for kw in entry.get("keywords", []):
        kw_words = normalize(kw).split()
        if not kw_words:
            continue

        def _hit(k):
            for w in qwords:
                if w == k:
                    return True
                # prefix match only for tokens >= 4 chars (avoids "do"~"discount")
                if len(w) >= 4 and len(k) >= 4 and (w.startswith(k) or k.startswith(w)):
                    return True
            return False

        if all(_hit(k) for k in kw_words):
            hits += len(kw_words)
    return hits


def match_faq(question, faq=None, min_score=1):
    """Return (best_entry, score) or (None, 0) if no FAQ matches."""
    faq = faq if faq is not None else load_faq()
    best, best_score = None, 0
    for entry in faq:
        s = score_faq(question, entry)
        if s > best_score:
            best, best_score = entry, s
    if best is None or best_score < min_score:
        return None, 0
    return best, best_score


def reply(question, faq=None):
    """Return (answer_text, faq_id_or_None).

    Falls back to a polite ticket message when nothing matches.
    """
    entry, _ = match_faq(question, faq)
    if entry:
        return entry.get("answer"), entry.get("id")
    return ("Thank you for reaching out! Our team will contact you "
            "shortly. Your question has been recorded as a ticket."), None
