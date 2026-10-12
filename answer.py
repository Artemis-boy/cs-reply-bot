"""CLI wrapper for the gateway agent: deterministic FAQ reply + logging.

Usage:
    python answer.py "<sender>" "<question>"

Prints the customer-facing reply to stdout (the agent sends it verbatim)
and appends the chat to log/chat_log.xlsx (tickets auto-opened on misses).
Exit 0 on FAQ hit, exit 2 on ticket fallback (still prints polite reply).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot import reply  # noqa: E402
from tickets import handle_chat  # noqa: E402

if len(sys.argv) != 3:
    print('Usage: python answer.py "<sender>" "<question>"', file=sys.stderr)
    sys.exit(1)

sender, question = sys.argv[1], sys.argv[2]
answer = handle_chat(sender, question)
print(answer)

_, faq_id = reply(question)
sys.exit(0 if faq_id else 2)
