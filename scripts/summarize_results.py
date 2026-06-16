#!/usr/bin/env python3
"""Print compact Guarded-Stage ReAct result summaries."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "main_summary.csv"


def main() -> None:
    rows = list(csv.DictReader(SUMMARY.open("r", encoding="utf-8")))
    print("Backbone        Method                       Tasks  Success  Success rate")
    print("-" * 78)
    for row in rows:
        print(
            f"{row['backbone']:<15} "
            f"{row['method']:<28} "
            f"{int(row['tasks']):>5}  "
            f"{int(row['success']):>7}  "
            f"{100 * float(row['success_rate']):>10.2f}%"
        )


if __name__ == "__main__":
    main()
