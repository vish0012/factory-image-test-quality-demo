from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyze_coplanarity import fit_plane_and_metrics, make_part_summary


def test_coplanarity_metrics_are_positive():
    df = pd.read_csv(ROOT / "data" / "coplanarity_measurements.csv")
    first_part_id = df["part_id"].iloc[0]
    part_df = df[df["part_id"] == first_part_id]

    metrics = fit_plane_and_metrics(part_df)

    assert metrics["peak_to_valley_um"] > 0
    assert metrics["rms_residual_um"] > 0


def test_current_month_has_higher_mean_coplanarity():
    df = pd.read_csv(ROOT / "data" / "coplanarity_measurements.csv")
    summary = make_part_summary(df)

    month_means = summary.groupby("month")["rms_residual_um"].mean()

    assert month_means["current"] > month_means["previous"]
