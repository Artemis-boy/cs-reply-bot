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
    """Count keyword hits (ID + EN keywords). Matches whole words or prefixes
    (e.g. 'promos' hits keyword 'promo'). Returns int score."""
    qwords = normalize(question).split()
    q = set(qwords)
    hits = 0
    for kw in entry.get("keywords_id", []) + entry.get("keywords_en", []):
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


def detect_lang(question):
    """ID vs EN detection. Indonesian wins on majority ID words, because
    loanwords like 'cancel'/'promo' appear in Indonesian sentences too."""
    id_markers = {"yang", "dan", "saya", "anda", "kamu", "bagaimana", "berapa",
                  "apakah", "bisa", "ada", "di", "ke", "dari", "untuk", "dengan",
                  "sudah", "belum", "tidak", "ya", "tolong", "mau", "kapan",
                  "mana", "ini", "itu", "pesanan", "barang", "toko", "batal"}
    en_markers = {"where", "how", "what", "when", "is", "are", "do", "does",
                  "my", "order", "shipping", "return", "refund", "payment",
                  "track", "cancel", "discount", "store", "open", "the", "a"}
    words = set(normalize(question).split())
    id_hits = len(words & id_markers)
    en_hits = len(words & en_markers)
    # tie or no markers -> Indonesian (primary audience)
    return "en" if en_hits > id_hits else "id"


def reply(question, faq=None):
    """Return (answer_text, faq_id_or_None, lang).

    Falls back to a polite ticket message when nothing matches.
    """
    entry, _ = match_faq(question, faq)
    lang = detect_lang(question)
    if entry:
        ans = entry.get(f"answer_{lang}") or entry.get("answer_id")
        return ans, entry.get("id"), lang
    if lang == "en":
        return ("Thank you for reaching out! Our team will contact you "
                "shortly. Your ticket has been recorded."), None, lang
    return ("Terima kasih sudah menghubungi kami! Tim kami akan segera "
            "menghubungi Anda. Pertanyaan Anda sudah tercatat sebagai tiket."), None, lang
