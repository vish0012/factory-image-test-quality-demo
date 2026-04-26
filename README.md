# Factory Image-Test Quality Demo

This repository is a small working demo for a Software Quality Engineer assignment.

The scenario is a manufacturing environment where image-testing software must be deployed to vendor factory sites. Direct VPN access into each vendor network is not reliable, so the solution focuses on safe rollout, reproducible testing, release gates, and clear communication of production risk.

## What this demo covers

### 1. Manufacturing-floor deployment

The example uses a pull-based deployment model. Each factory site reads an approved release manifest, validates the release metadata, and only promotes a version after local checks pass.

This is meant to model a safer approach than pushing directly into vendor networks.

### 2. Image-test reproducibility

Each test result keeps the metadata needed to reproduce and debug a result later:

- input image hash
- algorithm version
- parameter hash
- binary/runtime version
- operating system
- hardware
- site and product

### 3. Release gates

The release-gate script checks whether a site/product combination should pass or needs review based on:

- crashes
- thermal throttling
- golden-set stability
- 99th-percentile processing time compared with the previous stable version

### 4. Coplanarity analysis

The coplanarity analysis fits a plane to each 10 × 10 measurement grid and calculates:

- peak-to-valley residual distance
- root-mean-square residual distance
- month-over-month shift
- relationship between coplanarity and product-test score

### 5. Communication dashboard

The dashboard is intentionally simple. It summarizes technical quality signals in terms of production risk so that engineering, factory, and leadership teams can make decisions quickly.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt

python src/generate_sample_data.py
python src/check_release_gates.py
python src/analyze_coplanarity.py
python src/make_dashboard.py
```

Open:

```text
reports/dashboard.html
```

## Repository layout

```text
factory-image-test-quality-demo/
├── README.md
├── requirements.txt
├── data/
│   ├── release_manifest.csv
│   ├── image_test_results.csv
│   └── coplanarity_measurements.csv
├── src/
│   ├── generate_sample_data.py
│   ├── check_release_gates.py
│   ├── analyze_coplanarity.py
│   └── make_dashboard.py
├── reports/
│   ├── dashboard.html
│   ├── release_gate_summary.csv
│   ├── coplanarity_summary.csv
│   └── plots
└── docs/
    └── assignment_report.md
```

## Notes

The data in this repository is synthetic. It is only used to demonstrate the workflow and the type of reasoning I would apply in a real manufacturing quality environment.
