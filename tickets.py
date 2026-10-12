"""CS Reply Bot - tickets + xlsx logging.

Every incoming chat is logged to log/chat_log.xlsx with columns:
timestamp | sender | question | answer | faq_id | status (ANSWERED/OPEN/CLOSED)

Unmatched questions become OPEN tickets (in-memory + JSON backup).
close_ticket(ticket_id) marks them CLOSED.
"""
import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).parent
LOG_DIR = ROOT / "log"
LOG_XLSX = LOG_DIR / "chat_log.xlsx"
TICKETS_JSON = LOG_DIR / "tickets.json"

HEADERS = ["timestamp", "sender", "question", "answer", "faq_id", "status"]


def _tickets():
    if TICKETS_JSON.exists():
        return json.loads(TICKETS_JSON.read_text(encoding="utf-8"))
    return []


def _save_tickets(tickets):
    LOG_DIR.mkdir(exist_ok=True)
    TICKETS_JSON.write_text(json.dumps(tickets, ensure_ascii=False, indent=1),
                            encoding="utf-8")


def open_ticket(sender, question):
    tickets = _tickets()
    tid = f"T{(len(tickets) + 1):04d}"
    tickets.append({"id": tid, "sender": sender, "question": question,
                    "status": "OPEN",
                    "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    _save_tickets(tickets)
    return tid


def close_ticket(ticket_id):
    tickets = _tickets()
    for t in tickets:
        if t["id"] == ticket_id and t["status"] == "OPEN":
            t["status"] = "CLOSED"
            t["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_tickets(tickets)
            return True
    return False


def log_chat(sender, question, answer, faq_id=None, status="ANSWERED"):
    LOG_DIR.mkdir(exist_ok=True)
    if LOG_XLSX.exists():
        wb = load_workbook(LOG_XLSX)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "chat_log"
        ws.append(HEADERS)
    ws.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sender,
               question, answer, faq_id or "-", status])
    wb.save(LOG_XLSX)
    return LOG_XLSX


def handle_chat(sender, question):
    """Full pipeline: reply -> ticket if unmatched -> log. Returns answer."""
    from bot import reply
    answer, faq_id, _lang = reply(question)
    if faq_id:
        log_chat(sender, question, answer, faq_id, "ANSWERED")
    else:
        tid = open_ticket(sender, question)
        log_chat(sender, question, f"[{tid}] {answer}", "-", "OPEN")
    return answer
