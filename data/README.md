# Data Availability

The raw receipt and weather sources used for this analysis are private operational data and are not distributed with the public portfolio project.

`cash_receipts.csv` contains transaction identifiers and internal user information. It must remain local and must not be committed, packaged in a Tableau workbook, or uploaded to Tableau Public.

`weather.csv` is also kept local because this repository does not include redistribution documentation for the original export.

Authorized users can place compatible files at:

- `data/cash_receipts.csv`
- `data/weather.csv`

The processing script validates the required column schemas before analysis. Public demonstrations should use an approved anonymized or synthetic dataset rather than these source files.
