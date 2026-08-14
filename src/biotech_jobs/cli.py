from __future__ import annotations
import argparse, json
from pathlib import Path
from biotech_jobs.engine import Engine


def main():
    p = argparse.ArgumentParser(description="Retrieve, score, and track jobs from company career boards")
    p.add_argument("--config", default="config/companies.yml")
    p.add_argument("--db", default="output/jobs.sqlite")
    p.add_argument("--csv", default="output/ranked_jobs.csv", help="All current retrieved matches at/above threshold")
    p.add_argument("--new-csv", default="output/new_matches.csv", help="Only jobs first seen in this run")
    p.add_argument("--min-score", type=int, default=65)
    p.add_argument("--company-timeout", type=int, default=75, help="Hard wall-clock limit per company (seconds)")
    p.add_argument("--request-timeout", type=int, default=12, help="HTTP request timeout (seconds)")
    args = p.parse_args()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    engine = Engine(args.config, args.db, company_timeout=args.company_timeout, request_timeout=args.request_timeout)
    rows, errors, warnings, run = engine.run(min_score=args.min_score)
    exported = engine.export_csv(rows, args.csv, args.min_score)
    new_exported = engine.export_csv(rows, args.new_csv, args.min_score, new_only=True)
    print(json.dumps({**run, "exported_matches": exported, "new_matches": new_exported,
                      "min_score": args.min_score, "errors": errors, "warnings": warnings}, indent=2), flush=True)


if __name__ == "__main__":
    main()
