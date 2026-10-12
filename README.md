# CS Reply Bot

A lightweight, dependency-minimal auto-reply bot for customer service chats. It matches incoming questions against an editable FAQ file (`faq.json`) using keyword scoring, auto-opens tickets for unmatched questions, and logs every chat to an Excel file.

No API keys. No external services. Runs fully offline.

## Features

- **FAQ keyword matching** — whole-word + prefix matching (e.g. `promos` hits keyword `promo`), multi-word keyword support (`discount code` requires both words).
- **12 built-in English FAQs** — shipping, tracking, payment, returns, refunds, store hours, promos, cancel, stock, damaged items, coverage area, human agent.
- **Automatic tickets** — unmatched questions become `OPEN` tickets (`T0001`, `T0002`, …) backed by `log/tickets.json`; close them with `close_ticket()`.
- **Excel chat log** — every chat appended to `log/chat_log.xlsx` with `timestamp | sender | question | answer | faq_id | status`.
- **CLI wrapper** (`answer.py`) — prints the reply to stdout; exit `0` on FAQ hit, exit `2` on ticket fallback, exit `1` on bad usage.
- **Editable without code changes** — add or edit FAQs by editing `faq.json` only.

## Project structure

```text
cs-reply-bot/
├── bot.py        # FAQ matching engine: load_faq, normalize, score_faq, match_faq, reply
├── tickets.py    # Tickets + Excel logging: open_ticket, close_ticket, log_chat, handle_chat
├── answer.py     # CLI wrapper: python answer.py "<sender>" "<question>"
├── faq.json      # 12 English FAQs (id, question, keywords, answer)
└── log/          # Runtime data (git-ignored): chat_log.xlsx, tickets.json
```

## Requirements

- Python 3.10+
- `openpyxl` (only third-party dependency)

## Installation

```bash
git clone https://github.com/Artemis-boy/cs-reply-bot.git
cd cs-reply-bot
pip install openpyxl
```

## Usage

### CLI (simplest)

```bash
python answer.py "Budi" "Do you have any discount codes?"
# Yes! We offer a 10% discount for purchases over Rp500,000 with the code HEMAT10. Promo cannot be combined.
# exit code 0 = FAQ hit

python answer.py "Sari" "Do aliens sell here?"
# Thank you for reaching out! Our team will contact you shortly. Your question has been recorded as a ticket.
# exit code 2 = no FAQ match, ticket opened
```

### As a library

```python
from bot import reply
from tickets import handle_chat, close_ticket

# Just the answer
answer, faq_id = reply("Where is my order?")
print(answer, faq_id)   # ... tracking

# Full pipeline: reply + auto-ticket on miss + Excel log
answer = handle_chat("Budi", "Where is my order?")

# Close a ticket
close_ticket("T0001")   # True if an OPEN ticket with that ID existed
```

### Editing FAQs

Add an entry to `faq.json` — no code change needed:

```json
{
  "id": "warranty",
  "question": "Do products have a warranty?",
  "keywords": ["warranty", "guarantee", "warranty claim"],
  "answer": "All electronics include a 12-month warranty. Contact us with your order number to claim."
}
```

Tips:

- Single keywords match whole words or prefixes (`ship` matches `ships`, `shipping`).
- Multi-word keywords require ALL words to hit (`discount code` needs both).
- If two entries compete (e.g. `refund` vs `damaged`), keep their keywords disjoint — check with a quick `reply()` test.

## Example chat

```text
> Budi: How much is shipping?
< Bot:  We ship nationwide within 1-3 business days. Shipping is free for orders over Rp100,000.  [faq: shipping]

> Budi: How long does a refund take?
< Bot:  Refunds are processed within 3-5 business days after we receive the returned item, back to your original payment method.  [faq: refund_time]

> Sari: Do aliens sell here?
< Bot:  Thank you for reaching out! Our team will contact you shortly. Your question has been recorded as a ticket.  [ticket T0003 OPEN]
```

## Exit codes (`answer.py`)

| Code | Meaning                                  |
|------|------------------------------------------|
| 0    | FAQ matched, answer printed              |
| 1    | Wrong usage (need exactly sender + question) |
| 2    | No FAQ match, polite fallback printed, ticket opened |

## Limitations

- Keyword scorer, not semantic search: questions with similar words can misroute (e.g. `rocket ships` scores toward `shipping`). Keep keywords disjoint for accuracy.
- English only (Indonesian support was removed in the full-English update).
- Ticket IDs are sequential (`T0001`…) and stored in a local JSON file — fine for demo scale, not concurrent writers.

## License

MIT — free for personal and commercial use.
