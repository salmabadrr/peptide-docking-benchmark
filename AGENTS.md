# Project Instructions for EPIC-AMP Benchmarking

## Principles
- Prioritize reproducibility. Every step must be repeatable from raw inputs through final machine-readable outputs.
- Do not rely on undocumented assumptions about external tools.
- Verify all external tool interfaces from official GitHub repositories or official documentation before implementation.
- Do not modify external tool source code.

## Code organization
- Write small, modular functions with one clear responsibility.
- Separate pipeline stages into discrete steps:
  - preprocessing
  - docking/pose generation
  - scoring/ranking
  - evaluation
  - result aggregation
- Keep tool-specific wrappers isolated from benchmark orchestration logic.

## Logging and debugging
- Add explicit logging for all major operations, inputs, outputs, and decisions.
- Log file names, tool versions, command-line arguments, and execution status.
- Make logging configurable and store logs alongside outputs.

## Determinism
- Use fixed random seeds wherever supported by a tool or library.
- Document any non-deterministic behavior and make it explicit in the results.

## Paths and configuration
- Avoid hard-coded absolute paths.
- Use relative paths and configuration files whenever possible.
- Store paths and parameters in version-controlled config files rather than scattering them in code.

## Machine-readable results
- Save benchmark results in structured formats such as CSV and JSON.
- Include metadata for each pose, including:
  - source tool
  - input identifiers
  - pose rank(s)
  - scoring values
  - evaluation metrics
  - timestamps
- Keep raw tool outputs separate from aggregated benchmark summaries.

## Testing
- Add tests for parsers, ranking logic, and result aggregation.
- Validate that score parsing is robust to the actual output format of each tool.
- Test edge cases, including missing fields, multiple poses, and empty outputs.

## External tool integration
- Implement one wrapper per external tool.
- Confirm each tool's CLI, input/output formats, and scoring semantics from official documentation before coding.
- If a tool interface is not yet verified, mark it as `unverified` and do not assume behavior.

## Reporting
- Record exact tool versions and data sources in the benchmark metadata.
- Capture which tool produced which pose, and which ranking was used.
- Make it explicit when a pose is selected by DiffPepDock ranking versus InterPepRank ranking.

## Missing verification
- For this repository, DiffPepDock details are available in the official DiffPepBuilder README.
- InterPepRank and DockQ details are currently unverified and must be obtained from their official documentation or repositories before implementation.
