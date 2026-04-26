"""
Analyze coplanarity shift using a 10 × 10 height grid.

The script fits the best plane per part, calculates coplanarity metrics, compares
current vs. previous month, and generates simple plots.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def fit_plane_and_metrics(part_df: pd.DataFrame) -> dict:
    x = part_df["x"].to_numpy()
    y = part_df["y"].to_numpy()
    z = part_df["height_um"].to_numpy()

    A = np.column_stack([x, y, np.ones_like(x)])
    coeff, *_ = np.linalg.lstsq(A, z, rcond=None)
    z_fit = A @ coeff
    residuals = z - z_fit

    return {
        "peak_to_valley_um": float(residuals.max() - residuals.min()),
        "rms_residual_um": float(np.sqrt(np.mean(residuals**2))),
        "plane_x_slope": float(coeff[0]),
        "plane_y_slope": float(coeff[1]),
        "product_test_score": float(part_df["product_test_score"].iloc[0]),
    }


def make_part_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (month, part_id), part_df in df.groupby(["month", "part_id"]):
        metrics = fit_plane_and_metrics(part_df)
        metrics.update({"month": month, "part_id": part_id})
        rows.append(metrics)
    return pd.DataFrame(rows)


def save_plots(part_summary: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    REPORTS.mkdir(exist_ok=True)

    # Box plot
    data = [
        part_summary.loc[part_summary["month"] == "previous", "rms_residual_um"],
        part_summary.loc[part_summary["month"] == "current", "rms_residual_um"],
    ]
    plt.figure(figsize=(7, 5))
    plt.boxplot(data, tick_labels=["previous", "current"])
    plt.title("Coplanarity RMS residual: previous vs current")
    plt.ylabel("RMS residual distance (µm)")
    plt.tight_layout()
    plt.savefig(REPORTS / "coplanarity_boxplot.png", dpi=160)
    plt.close()

    # ECDF plot
    plt.figure(figsize=(7, 5))
    for month in ["previous", "current"]:
        vals = np.sort(part_summary.loc[part_summary["month"] == month, "rms_residual_um"].to_numpy())
        y = np.arange(1, len(vals) + 1) / len(vals)
        plt.plot(vals, y, label=month)
    plt.title("Empirical cumulative distribution of coplanarity")
    plt.xlabel("RMS residual distance (µm)")
    plt.ylabel("Cumulative probability")
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORTS / "coplanarity_ecdf.png", dpi=160)
    plt.close()

    # Performance relationship
    plt.figure(figsize=(7, 5))
    plt.scatter(part_summary["rms_residual_um"], part_summary["product_test_score"], alpha=0.5)
    plt.title("Product test score vs coplanarity")
    plt.xlabel("RMS residual distance (µm)")
    plt.ylabel("Product test score")
    plt.tight_layout()
    plt.savefig(REPORTS / "performance_vs_coplanarity.png", dpi=160)
    plt.close()

    # Difference heatmap
    avg_maps = {}
    for month in ["previous", "current"]:
        avg_maps[month] = (
            raw_df[raw_df["month"] == month]
            .groupby(["y", "x"])["height_um"]
            .mean()
            .unstack()
            .to_numpy()
        )
    diff = avg_maps["current"] - avg_maps["previous"]

    plt.figure(figsize=(6, 5))
    plt.imshow(diff)
    plt.title("Average height map difference: current - previous")
    plt.xlabel("x grid")
    plt.ylabel("y grid")
    plt.colorbar(label="Height difference (µm)")
    plt.tight_layout()
    plt.savefig(REPORTS / "height_difference_map.png", dpi=160)
    plt.close()


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    raw_df = pd.read_csv(DATA / "coplanarity_measurements.csv")
    part_summary = make_part_summary(raw_df)

    month_summary = (
        part_summary.groupby("month")
        .agg(
            parts=("part_id", "count"),
            mean_rms_residual_um=("rms_residual_um", "mean"),
            median_rms_residual_um=("rms_residual_um", "median"),
            mean_peak_to_valley_um=("peak_to_valley_um", "mean"),
            mean_product_test_score=("product_test_score", "mean"),
        )
        .reset_index()
    )

    # Simple correlation as a practical first-pass link.
    corr = part_summary["rms_residual_um"].corr(part_summary["product_test_score"])
    month_summary["overall_corr_rms_vs_product_score"] = corr

    part_summary.to_csv(REPORTS / "coplanarity_part_metrics.csv", index=False)
    month_summary.to_csv(REPORTS / "coplanarity_summary.csv", index=False)
    save_plots(part_summary, raw_df)

    print(month_summary.to_string(index=False))
    print(f"\nCorrelation between RMS residual and product score: {corr:.3f}")
    print("Saved reports and plots in reports/.")


if __name__ == "__main__":
    main()
