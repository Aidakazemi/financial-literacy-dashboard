# 📊 U.S. Personal Financial Literacy Dashboard

A research-grade, self-updating GitHub Pages dashboard exploring financial literacy, fragility, wealth inequality, and access across American households.

**Live Dashboard →** `https://<your-username>.github.io/<repo-name>/`

---

## Research Questions Answered

| # | Research Question | Data Source |
|---|---|---|
| 1 | What share of Americans demonstrate basic financial literacy, and how has this changed over 15 years? | FINRA NFCS 2009–2024 |
| 2 | Which financial concepts have the largest knowledge gaps? | FINRA NFCS 2024 (Big-7 Quiz) |
| 3 | How do literacy and fragility vary by age, education, income, and race? | FINRA NFCS 2024 |
| 4 | How financially resilient are American households post-pandemic? | FINRA NFCS 2021 vs 2024 |
| 5 | What credit behaviors signal structural vulnerability? | FINRA NFCS 2024 |
| 6 | How stark are racial wealth disparities, and what do they imply for retirement security? | Federal Reserve SCF 2022 |
| 7 | Who remains excluded from the formal banking system, and why? | FDIC 2023 |
| 8 | Does FinTech adoption narrow or widen the financial inclusion gap? | FINRA NFCS 2024 |
| 9 | How does the macroeconomic environment (savings rate, debt burden) compound literacy gaps? | FRED / BEA / Fed |

---

## Data Sources

| Source | Data | Update Frequency |
|--------|------|-----------------|
| [FINRA Foundation NFCS](https://www.finrafoundation.org/national-financial-capability-study) | Financial literacy, fragility, demographics (n=25,500+) | Every 3 years (latest: 2024) |
| [Federal Reserve SCF](https://www.federalreserve.gov/econres/scfindex.htm) | Net worth, retirement savings, wealth gaps | Every 3 years (latest: 2022) |
| [FDIC Household Survey](https://www.fdic.gov/analysis/household-survey) | Banking access, unbanked/underbanked rates | Every 2 years (latest: 2023) |
| [FRED API — St. Louis Fed](https://fred.stlouisfed.org) | Personal savings rate, debt service, delinquency, Fed funds | **Weekly via GitHub Actions** |

---

## Setup Instructions

### 1. Fork / Clone This Repository

```bash
git clone https://github.com/<your-username>/fin-literacy-dashboard.git
cd fin-literacy-dashboard
```

### 2. Get a Free FRED API Key

1. Create a free account at [fred.stlouisfed.org](https://fred.stlouisfed.org/useraccount/login/secure/)
2. Go to **My Account → API Keys**
3. Request a free API key (instant approval)

### 3. Add Your API Key as a GitHub Secret

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `FRED_API_KEY`
4. Value: your 32-character key

### 4. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `docs` folder
4. Save → your dashboard will be live at `https://<username>.github.io/<repo>/`

### 5. Initial Data Build (optional — run locally)

```bash
pip install -r requirements.txt   # only standard library used currently
export FRED_API_KEY=your_key_here
python scripts/fetch_data.py
```

### 6. Weekly Auto-Refresh

The GitHub Actions workflow (`.github/workflows/weekly-refresh.yml`) runs every **Sunday at 06:00 UTC** and commits updated data automatically. You can also trigger it manually via **Actions → Weekly Data Refresh → Run workflow**.

---

## Project Structure

```
.
├── docs/                          # GitHub Pages root
│   ├── index.html                 # Main dashboard (single-page, tab navigation)
│   └── assets/
│       └── js/
│           └── dashboard_data.js  # Auto-generated data (committed by Actions)
│
├── data/
│   └── dashboard_data.json        # Raw JSON data (auto-generated)
│
├── scripts/
│   └── fetch_data.py              # Data pipeline — runs weekly via Actions
│
├── .github/
│   └── workflows/
│       └── weekly-refresh.yml     # GitHub Actions schedule
│
└── README.md
```

---

## Dashboard Sections

| Tab | Focus |
|-----|-------|
| **Overview** | National literacy rate trend + knowledge gap by topic |
| **Demographics** | Literacy & fragility by age, education, income, and race |
| **Fragility & Debt** | Emergency fund trends, credit card behaviors, fragility reversal |
| **Wealth Gaps** | Racial wealth inequality, retirement savings by age (SCF 2022) |
| **Access & FinTech** | Unbanked rates, reasons for exclusion, FinTech adoption |
| **Macro Context** | Live FRED charts: savings rate, debt service, delinquency, Fed funds |

---

## Extending the Dashboard

### Add New FRED Series

In `scripts/fetch_data.py`, add to the `FRED_SERIES` dict:
```python
FRED_SERIES = {
    ...
    "student_loan_debt": "SLOAS",     # Student loan outstanding
    "mortgage_delinquency": "DRSFRMACBS",  # Mortgage delinquency
}
```
Then add a corresponding chart in `docs/index.html`.

### Add New Research Data

Add a new Python dict in `fetch_data.py` following the existing pattern, include it in `build_payload()`, and add the visualization in `index.html`.

---

## Citation

If you use this dashboard in academic work:

> [Author]. (2024). *U.S. Personal Financial Literacy Dashboard* [Data visualization].
> Data sources: FINRA Foundation NFCS 2024; Federal Reserve SCF 2022; FDIC 2023; FRED API.
> Retrieved from https://github.com/<username>/fin-literacy-dashboard

---

## License

Data visualizations and code: MIT License.
Underlying datasets: subject to respective source licenses (all free for academic use).
