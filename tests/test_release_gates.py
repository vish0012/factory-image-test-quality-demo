from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from check_release_gates import main


def test_release_gate_script_runs():
    main()
    output = ROOT / "reports" / "release_gate_summary.csv"
    assert output.exists()


def test_release_gate_summary_has_pass_or_review():
    main()
    output = ROOT / "reports" / "release_gate_summary.csv"
    df = pd.read_csv(output)

    assert not df.empty
    assert set(df["release_gate_status"]).issubset({"PASS", "REVIEW"})


def test_site_c_has_review_case():
    main()
    output = ROOT / "reports" / "release_gate_summary.csv"
    df = pd.read_csv(output)

    site_c = df[df["site"] == "Site C"]
    assert not site_c.empty
    assert "REVIEW" in set(site_c["release_gate_status"])
