#!/usr/bin/env python3
"""Standalone Ragas evaluation script.

Usage:
    python eval/run_eval.py --dataset eval/test_dataset.json --output eval/results.json
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.evaluation import run_evaluation


async def main():
    parser = argparse.ArgumentParser(description="Run Ragas evaluation on RAG pipeline")
    parser.add_argument("--dataset", default="eval/test_dataset.json", help="Path to test dataset JSON")
    parser.add_argument("--output", default="eval/results.json", help="Path to write results JSON")
    args = parser.parse_args()

    print(f"Running evaluation with dataset: {args.dataset}")
    result = await run_evaluation(args.dataset)

    # Write results
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Results written to: {args.output}")

    # Print summary
    print("\n=== Aggregate Scores ===")
    for metric, score in result["aggregate"].items():
        print(f"  {metric}: {score:.4f}")

    print(f"\n=== Per-Question Results ({len(result['results'])} questions) ===")
    for r in result["results"]:
        print(f"\n  Q: {r['question']}")
        print(f"  A: {r['answer'][:100]}...")
        if r.get("scores"):
            for metric, score in r["scores"].items():
                print(f"    {metric}: {score:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
