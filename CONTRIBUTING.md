# Contributing

## Development workflow

1. Create a feature branch from `main`.
2. Add or update tests under `tests/`.
3. Run `pytest tests/ -v` locally.
4. Open a pull request.
5. CI must pass before merge.

## Quality gates

- New analysis functions should include unit tests.
- Release-gate changes should include a clear reason.
- Synthetic data generation should stay deterministic by using a fixed random seed.

## Reporting issues

Use this format:

1. What happened
2. Expected result
3. Actual result
4. Reproduction steps
5. Environment
