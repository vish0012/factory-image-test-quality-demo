"""
Create a simple one-page HTML dashboard for communication.

The dashboard converts technical signals into production-risk language.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def status_label(status: str) -> str:
    return "GREEN" if status == "PASS" else "AMBER"


def main() -> None:
    release = pd.read_csv(REPORTS / "release_gate_summary.csv")
    cop = pd.read_csv(REPORTS / "coplanarity_summary.csv")

    risk_rows = []
    for _, row in release.iterrows():
        status = status_label(row["release_gate_status"])
        risk_rows.append(
            f"""
            <tr>
              <td>{status}</td>
              <td>{row['site']}</td>
              <td>{row['product']}</td>
              <td>{row['algorithm_version']}</td>
              <td>{row['p99_processing_time_ms']:.1f} ms</td>
              <td>{row['production_risk']}</td>
            </tr>
            """
        )

    cop_rows = []
    for _, row in cop.iterrows():
        cop_rows.append(
            f"""
            <tr>
              <td>{row['month']}</td>
              <td>{row['parts']}</td>
              <td>{row['mean_rms_residual_um']:.3f} µm</td>
              <td>{row['mean_peak_to_valley_um']:.3f} µm</td>
              <td>{row['mean_product_test_score']:.2f}</td>
            </tr>
            """
        )

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>SQE Factory Quality Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 28px; line-height: 1.4; }}
    h1 {{ margin-bottom: 0; }}
    h2 {{ margin-top: 28px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f2f2f2; }}
    .note {{ background: #f8f8f8; padding: 12px; border-left: 4px solid #999; }}
    img {{ max-width: 47%; margin: 10px 1%; vertical-align: top; border: 1px solid #ddd; }}
  </style>
</head>
<body>
  <h1>SQE Factory Quality Dashboard</h1>
  <p class="note">
    Goal: translate technical quality signals into production risk.
    Example: if processing time increases at Site C, the site may process fewer units per hour,
    which can put the shift target and shipment plan at risk.
  </p>

  <h2>Release Gate Summary</h2>
  <table>
    <tr>
      <th>Status</th><th>Site</th><th>Product</th><th>Algorithm</th>
      <th>99th-percentile processing time</th><th>Production risk</th>
    </tr>
    {''.join(risk_rows)}
  </table>

  <h2>Coplanarity Summary</h2>
  <table>
    <tr>
      <th>Month</th><th>Parts</th><th>Mean RMS residual</th>
      <th>Mean peak-to-valley</th><th>Mean product score</th>
    </tr>
    {''.join(cop_rows)}
  </table>

  <h2>Plots</h2>
  <img src="coplanarity_boxplot.png" alt="Coplanarity box plot">
  <img src="coplanarity_ecdf.png" alt="Coplanarity ECDF">
  <img src="height_difference_map.png" alt="Height difference map">
  <img src="performance_vs_coplanarity.png" alt="Performance vs coplanarity">
</body>
</html>
"""
    (REPORTS / "dashboard.html").write_text(html, encoding="utf-8")
    print(f"Saved: {REPORTS / 'dashboard.html'}")


if __name__ == "__main__":
    main()
