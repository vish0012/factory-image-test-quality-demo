"""
Generate synthetic sample data for the SQE factory quality demo.

The data is fictional and exists only to demonstrate the quality-engineering workflow.
"""

from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RNG = np.random.default_rng(42)


def make_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def generate_release_manifest() -> None:
    rows = [
        {
            "site": "Site A",
            "product": "CameraModule-X",
            "machine": "A-IMG-001",
            "os": "Windows",
            "artifact_type": "DLL",
            "algorithm_version": "2.4.1",
            "parameter_version": "p17",
            "config_version": "cfg-2026-04",
            "rollout_stage": "pilot_site",
            "previous_version": "2.4.0",
            "signature_verified": True,
            "install_window": "maintenance",
        },
        {
            "site": "Site B",
            "product": "CameraModule-X",
            "machine": "B-IMG-014",
            "os": "Windows",
            "artifact_type": "DLL",
            "algorithm_version": "2.4.0",
            "parameter_version": "p16",
            "config_version": "cfg-2026-03",
            "rollout_stage": "broader_rollout",
            "previous_version": "2.3.9",
            "signature_verified": True,
            "install_window": "maintenance",
        },
        {
            "site": "Site C",
            "product": "CameraModule-Y",
            "machine": "C-MAC-006",
            "os": "macOS",
            "artifact_type": "ServerApp",
            "algorithm_version": "2.4.1",
            "parameter_version": "p22",
            "config_version": "cfg-2026-04",
            "rollout_stage": "pilot_machine",
            "previous_version": "2.4.0",
            "signature_verified": True,
            "install_window": "maintenance",
        },
    ]
    pd.DataFrame(rows).to_csv(DATA / "release_manifest.csv", index=False)


def generate_image_test_results(n: int = 12000) -> None:
    sites = np.array(["Site A", "Site B", "Site C"])
    products = np.array(["CameraModule-X", "CameraModule-Y"])

    rows = []
    for i in range(n):
        site = RNG.choice(sites, p=[0.38, 0.34, 0.28])
        product = RNG.choice(products, p=[0.65, 0.35])
        algorithm_version = "2.4.1" if site in ["Site A", "Site C"] else "2.4.0"
        parameter_hash = make_hash(f"{site}-{product}-{algorithm_version}")
        input_hash = make_hash(f"image-{i}-{site}-{product}")

        base_ms = 92 if product == "CameraModule-X" else 108
        site_penalty = 36 if site == "Site C" else 0
        processing_time_ms = max(20, RNG.normal(base_ms + site_penalty, 18))

        false_positive = RNG.random() < (0.006 if site != "Site C" else 0.011)
        false_negative = RNG.random() < (0.004 if site != "Site C" else 0.009)
        crash = RNG.random() < (0.0001 if site == "Site C" else 0.0)
        thermal_throttle = RNG.random() < (0.0 if site != "Site C" else 0.002)

        passed = not (false_positive or false_negative or crash)

        rows.append(
            {
                "test_id": f"T{i:06d}",
                "site": site,
                "product": product,
                "input_image_hash": input_hash,
                "algorithm_version": algorithm_version,
                "parameter_hash": parameter_hash,
                "binary_version": f"{algorithm_version}-build-1042",
                "os": "Windows" if site != "Site C" else "macOS",
                "hardware": "VisionStation-v3",
                "processing_time_ms": round(processing_time_ms, 2),
                "false_positive": false_positive,
                "false_negative": false_negative,
                "crash": crash,
                "thermal_throttle": thermal_throttle,
                "passed": passed,
            }
        )

    pd.DataFrame(rows).to_csv(DATA / "image_test_results.csv", index=False)


def generate_coplanarity_measurements(parts_per_month: int = 300) -> None:
    rows = []
    grid_x, grid_y = np.meshgrid(np.arange(10), np.arange(10))

    for month in ["previous", "current"]:
        for part_idx in range(parts_per_month):
            # Base plane and noise
            tilt_x = RNG.normal(0.12, 0.04)
            tilt_y = RNG.normal(-0.06, 0.03)
            bow_strength = RNG.normal(0.0, 0.12)

            if month == "current":
                # Simulate a real month-over-month shift: slightly more bow and tilt.
                tilt_x += 0.06
                bow_strength += 0.22

            x_centered = grid_x - grid_x.mean()
            y_centered = grid_y - grid_y.mean()
            bow = bow_strength * ((x_centered**2 + y_centered**2) / 20.0)

            height = 40 + tilt_x * grid_x + tilt_y * grid_y + bow + RNG.normal(0, 0.18, size=(10, 10))

            # Synthetic final product performance. Higher coplanarity tends to lower score.
            rough_metric = float(height.max() - height.min())
            performance_score = 100 - 2.2 * rough_metric + RNG.normal(0, 1.5)

            for r in range(10):
                for c in range(10):
                    rows.append(
                        {
                            "month": month,
                            "part_id": f"{month[:1].upper()}-{part_idx:04d}",
                            "x": c,
                            "y": r,
                            "height_um": round(float(height[r, c]), 4),
                            "product_test_score": round(float(performance_score), 3),
                        }
                    )

    pd.DataFrame(rows).to_csv(DATA / "coplanarity_measurements.csv", index=False)


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    generate_release_manifest()
    generate_image_test_results()
    generate_coplanarity_measurements()
    print("Sample data generated in data/.")
