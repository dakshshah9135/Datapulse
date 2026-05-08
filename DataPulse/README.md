# 📊 DataPulse — Automated CSV Data Analyzer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

Automatically analyzes any CSV dataset, computes statistics (mean, median, std, outliers), generates charts (bar + pie), detects anomalies, and produces a professional HTML report. Works on sales data, HR data, security logs, financial data — any CSV.

## Usage
```bash
python datapulse.py sales_data.csv
python datapulse.py data.csv --output my_report.html
python datapulse.py data.csv --no-report
```

## Features
- Auto-detects numeric vs categorical columns
- Statistics: mean, median, std dev, min, max, null count
- Inline SVG bar charts and pie charts — no external libraries
- Auto-generates insights (high variance, outliers, dominant values)
- Warns about missing data (>10% nulls)
- Zero dependencies — pure Python stdlib

## Structure
```
DataPulse/
├── datapulse.py            # CLI entry point
├── core/
│   ├── analyzer.py         # Statistical engine
│   └── reporter.py         # HTML + SVG chart generator
└── sample_data/
    └── sales_data.csv      # 500-row sample dataset
```

## Author
**Daksh Shah** — B.Tech Cybersecurity, SAKEC Mumbai  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-daksh--shah9135-blue)](https://linkedin.com/in/daksh-shah9135)
