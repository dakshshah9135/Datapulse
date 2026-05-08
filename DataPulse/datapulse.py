#!/usr/bin/env python3
"""
DataPulse v1.0 — Automated CSV Data Analyzer & Report Generator
Author: Daksh Shah | github.com/daksh-shah9135/datapulse

Usage:
  python datapulse.py data.csv
  python datapulse.py data.csv --output report.html
  python datapulse.py data.csv --no-report
"""
import argparse, sys, os, datetime
from core.analyzer import analyze_csv
from core.reporter import generate_report

def main():
    p = argparse.ArgumentParser(description="DataPulse — Automated CSV Data Analyzer")
    p.add_argument("csvfile", help="Path to CSV file")
    p.add_argument("--output", default=None)
    p.add_argument("--no-report", action="store_true")
    args = p.parse_args()

    if not os.path.exists(args.csvfile):
        print(f"Error: '{args.csvfile}' not found."); sys.exit(1)

    print(f"\n📊 DataPulse v1.0 — Analyzing: {args.csvfile}\n{'─'*50}")
    profile = analyze_csv(args.csvfile)

    print(f"  Rows      : {profile.rows:,}")
    print(f"  Columns   : {profile.cols}")
    print(f"\n  Column Summary:")
    for cs in profile.columns:
        if cs.col_type == "numeric":
            print(f"  [NUMERIC]     {cs.name:<25} mean={cs.mean}, min={cs.min_val}, max={cs.max_val}")
        else:
            top = cs.top_values[0][0] if cs.top_values else "—"
            print(f"  [CATEGORICAL] {cs.name:<25} unique={cs.unique}, top='{top}'")

    if profile.insights:
        print(f"\n  💡 Insights:")
        for i in profile.insights: print(f"     • {i}")
    if profile.warnings:
        print(f"\n  ⚠️  Warnings:")
        for w in profile.warnings: print(f"     • {w}")

    if not args.no_report:
        os.makedirs("reports", exist_ok=True)
        ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = args.output or f"reports/datapulse_{os.path.basename(args.csvfile)}_{ts}.html"
        generate_report(profile, out)
        print(f"\n  ✓ HTML report: {out}")

    print(f"\n  DataPulse complete.\n")

if __name__ == "__main__":
    main()
