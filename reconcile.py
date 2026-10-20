#!/usr/bin/env python3
"""Print the code for payments whose latest attempt succeeded."""

import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


here = Path(__file__).resolve().parent
latest = {}

with (here / "payments.jsonl").open(encoding="utf-8") as payments:
    for line in payments:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        txn_id = event["txn_id"]
        if txn_id not in latest or timestamp > latest[txn_id][0]:
            latest[txn_id] = (timestamp, event)

successful = [event for _, event in latest.values() if event["status"] == "success"]
expected = int((here / "expected.txt").read_text(encoding="utf-8").strip())
if len(successful) != expected:
    raise SystemExit(f"Expected {expected} successful payments, found {len(successful)}")

total = sum(
    (Decimal(str(event["amount"]).replace(",", "")) for event in successful),
    Decimal("0"),
)
print(f"KOYA-{total.quantize(Decimal('1'), rounding=ROUND_HALF_UP)}")
