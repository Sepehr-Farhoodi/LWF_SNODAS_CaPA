## Liquid Water Flux (LWF) Calculation

A Python package for calculating liquid water flux using SNODAS SWE data and CaPA precipitation data.

## What it does

This package calculates liquid water flux using the formula:

LWF(t) = SWE(t-1) - SWE(t) + P(t)

## Quick Start

### Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/lwf_calc.git
cd lwf_calc
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the pipeline:

```bash
python scripts/run_pipeline.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```


