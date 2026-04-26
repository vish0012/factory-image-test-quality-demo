"""
Check release gates for image-testing software.

This script demonstrates how technical metrics can be translated into release decisions.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

PREVIOUS_STABLE_P99_MS = 150.0
P99_LIMIT_MS = PREVIOUS_STABLE_P99_MS * 1.20


def decide_status(row: pd.Series) -> str:
    if row["crashes"] > 0:
        return "REVIEW"
    if row["thermal_events"] > 0:
        return "REVIEW"
    if row["p99_processing_time_ms"] > P99_LIMIT_MS:
        return "REVIEW"
    return "PASS"


def describe_risk(row: pd.Series) -> str:
    risks = []
    if row["crashes"] > 0:
        risks.append("crash risk")
    if row["thermal_events"] > 0:
        risks.append("thermal risk")
    if row["p99_processing_time_ms"] > P99_LIMIT_MS:
        risks.append("throughput risk")
    return ", ".join(risks) if risks else "no immediate production risk"


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA / "image_test_results.csv")

    summary = (
        df.groupby(["site", "product", "algorithm_version"])
        .agg(
            tests=("test_id", "count"),
            crashes=("crash", "sum"),
            thermal_events=("thermal_throttle", "sum"),
            false_positives=("false_positive", "sum"),
            false_negatives=("false_negative", "sum"),
            p99_processing_time_ms=("processing_time_ms", lambda s: s.quantile(0.99)),
            pass_rate=("passed", "mean"),
        )
        .reset_index()
    )

    summary["p99_limit_ms"] = P99_LIMIT_MS
    summary["release_gate_status"] = summary.apply(decide_status, axis=1)
    summary["production_risk"] = summary.apply(describe_risk, axis=1)

    output_path = REPORTS / "release_gate_summary.csv"
    summary.to_csv(output_path, index=False)

    print(summary.to_string(index=False))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
