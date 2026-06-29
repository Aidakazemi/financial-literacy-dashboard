#!/usr/bin/env python3
"""
Financial Literacy Dashboard — Data Pipeline
Fetches live data from FRED API and compiles curated research data
from FINRA NFCS 2024, Fed SCF 2022, FDIC 2023, and BEA.
Outputs JSON files consumed by the dashboard frontend.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import sys

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "js")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# FRED API helper
# ─────────────────────────────────────────────
def fetch_fred(series_id, limit=60, frequency=None, units=None):
    """Fetch a FRED series and return list of {date, value} dicts."""
    if not FRED_API_KEY:
        print(f"  [WARN] No FRED_API_KEY — skipping live fetch for {series_id}")
        return []

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    if frequency:
        params["frequency"] = frequency
    if units:
        params["units"] = units

    url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        obs = [
            {"date": o["date"], "value": float(o["value"])}
            for o in data.get("observations", [])
            if o["value"] != "."
        ]
        # Return chronological
        return list(reversed(obs))
    except Exception as e:
        print(f"  [ERROR] FRED fetch failed for {series_id}: {e}")
        return []


# ─────────────────────────────────────────────
# Curated / static research data
# (sourced from FINRA NFCS 2009-2024, Fed SCF 2022,
#  FDIC National Survey of Unbanked 2023, BEA)
# ─────────────────────────────────────────────

NFCS_LITERACY_SCORES = {
    "source": "FINRA Foundation National Financial Capability Study (NFCS), 2009–2024",
    "note": "% adults answering 5+ of 7 financial knowledge questions correctly",
    "series": [
        {"year": 2009, "pct_5plus": 42},
        {"year": 2012, "pct_5plus": 39},
        {"year": 2015, "pct_5plus": 37},
        {"year": 2018, "pct_5plus": 34},
        {"year": 2021, "pct_5plus": 28},
        {"year": 2024, "pct_5plus": 27},
    ],
}

NFCS_BIG5_TOPICS = {
    "source": "FINRA NFCS 2024 — Individual question correct-answer rates",
    "data": [
        {"topic": "Numeracy / Interest", "pct_correct": 74},
        {"topic": "Inflation Impact", "pct_correct": 58},
        {"topic": "Mortgage Basics", "pct_correct": 66},
        {"topic": "Bond Prices vs Rates", "pct_correct": 28},
        {"topic": "Risk Diversification", "pct_correct": 35},
        {"topic": "Compound Interest", "pct_correct": 52},
        {"topic": "Stock Risk", "pct_correct": 61},
    ],
}

NFCS_DEMOGRAPHICS = {
    "source": "FINRA NFCS 2024 — Financial literacy by demographic group",
    "by_age": [
        {"group": "18–24", "pct_5plus": 21, "financial_fragile_pct": 52},
        {"group": "25–34", "pct_5plus": 24, "financial_fragile_pct": 48},
        {"group": "35–44", "pct_5plus": 27, "financial_fragile_pct": 44},
        {"group": "45–54", "pct_5plus": 26, "financial_fragile_pct": 42},
        {"group": "55–64", "pct_5plus": 31, "financial_fragile_pct": 37},
        {"group": "65+",   "pct_5plus": 35, "financial_fragile_pct": 28},
    ],
    "by_education": [
        {"group": "No HS Diploma",   "pct_5plus": 13, "has_retirement_pct": 17},
        {"group": "HS Diploma",      "pct_5plus": 22, "has_retirement_pct": 37},
        {"group": "Some College",    "pct_5plus": 25, "has_retirement_pct": 54},
        {"group": "College Grad",    "pct_5plus": 39, "has_retirement_pct": 80},
        {"group": "Post-Grad",       "pct_5plus": 46, "has_retirement_pct": 87},
    ],
    "by_income": [
        {"group": "< $25k",          "pct_5plus": 16, "financial_fragile_pct": 68},
        {"group": "$25k–$50k",       "pct_5plus": 22, "financial_fragile_pct": 55},
        {"group": "$50k–$75k",       "pct_5plus": 27, "financial_fragile_pct": 42},
        {"group": "$75k–$100k",      "pct_5plus": 33, "financial_fragile_pct": 31},
        {"group": "$100k+",          "pct_5plus": 44, "financial_fragile_pct": 18},
    ],
    "by_race": [
        {"group": "White",           "pct_5plus": 32},
        {"group": "Black",           "pct_5plus": 16},
        {"group": "Hispanic",        "pct_5plus": 17},
        {"group": "Asian",           "pct_5plus": 35},
        {"group": "Other",           "pct_5plus": 21},
    ],
}

NFCS_FRAGILITY_TRENDS = {
    "source": "FINRA NFCS 2009–2024 — Financial fragility: could not cover $2k emergency in 30 days",
    "series": [
        {"year": 2009, "fragile_pct": 50},
        {"year": 2012, "fragile_pct": 47},
        {"year": 2015, "fragile_pct": 46},
        {"year": 2018, "fragile_pct": 42},
        {"year": 2021, "fragile_pct": 36},
        {"year": 2024, "fragile_pct": 42},
    ],
}

NFCS_EMERGENCY_SAVINGS = {
    "source": "FINRA NFCS 2024 — Emergency fund coverage (3 months expenses)",
    "pct_have_3mo_fund": 46,
    "pct_have_3mo_fund_2021": 53,
    "note": "7-percentage-point drop from 2021 to 2024",
}

NFCS_CREDIT_BEHAVIOR = {
    "source": "FINRA NFCS 2024 — Credit card behaviors",
    "data": [
        {"behavior": "Pay full balance each month", "pct": 45},
        {"behavior": "Pay minimum only",            "pct": 20},
        {"behavior": "Pay more than min, less than full", "pct": 23},
        {"behavior": "Sometimes skip payment",      "pct": 12},
    ],
}

SCF_WEALTH_GAPS = {
    "source": "Federal Reserve Survey of Consumer Finances (SCF) 2022",
    "median_net_worth": [
        {"group": "White families",    "median_net_worth_k": 285},
        {"group": "Black families",    "median_net_worth_k": 44},
        {"group": "Hispanic families", "median_net_worth_k": 51},
        {"group": "Other families",    "median_net_worth_k": 168},
    ],
    "retirement_by_age": [
        {"age_group": "Under 35",  "median_retirement_k": 18},
        {"age_group": "35–44",     "median_retirement_k": 45},
        {"age_group": "45–54",     "median_retirement_k": 115},
        {"age_group": "55–64",     "median_retirement_k": 185},
        {"age_group": "65–74",     "median_retirement_k": 200},
        {"age_group": "75+",       "median_retirement_k": 130},
    ],
}

FDIC_BANKING_ACCESS = {
    "source": "FDIC National Survey of Unbanked and Underbanked Households 2023",
    "unbanked_pct": 4.2,
    "underbanked_pct": 14.2,
    "by_income": [
        {"income": "< $15k",    "unbanked_pct": 15.0},
        {"income": "$15k–30k",  "unbanked_pct": 8.0},
        {"income": "$30k–50k",  "unbanked_pct": 3.5},
        {"income": "$50k+",     "unbanked_pct": 0.9},
    ],
    "top_reasons_unbanked": [
        {"reason": "Don't have enough money", "pct": 40},
        {"reason": "Don't trust banks",        "pct": 25},
        {"reason": "Privacy concerns",         "pct": 17},
        {"reason": "Fees too high",            "pct": 38},
        {"reason": "No nearby bank",           "pct": 9},
    ],
}

STATE_LITERACY = {
    "source": "FINRA Foundation NFCS 2024 — State-level financial literacy (% scoring 5+ of 7)",
    "data": [
        {"state": "MN", "state_name": "Minnesota",      "pct_5plus": 38},
        {"state": "NH", "state_name": "New Hampshire",  "pct_5plus": 37},
        {"state": "WI", "state_name": "Wisconsin",      "pct_5plus": 36},
        {"state": "VT", "state_name": "Vermont",        "pct_5plus": 36},
        {"state": "CO", "state_name": "Colorado",       "pct_5plus": 35},
        {"state": "UT", "state_name": "Utah",           "pct_5plus": 35},
        {"state": "ND", "state_name": "North Dakota",   "pct_5plus": 34},
        {"state": "SD", "state_name": "South Dakota",   "pct_5plus": 34},
        {"state": "VA", "state_name": "Virginia",       "pct_5plus": 34},
        {"state": "MA", "state_name": "Massachusetts",  "pct_5plus": 33},
        {"state": "CA", "state_name": "California",     "pct_5plus": 25},
        {"state": "TX", "state_name": "Texas",          "pct_5plus": 26},
        {"state": "FL", "state_name": "Florida",        "pct_5plus": 24},
        {"state": "NY", "state_name": "New York",       "pct_5plus": 25},
        {"state": "MS", "state_name": "Mississippi",    "pct_5plus": 18},
        {"state": "AL", "state_name": "Alabama",        "pct_5plus": 19},
        {"state": "AR", "state_name": "Arkansas",       "pct_5plus": 20},
        {"state": "WV", "state_name": "West Virginia",  "pct_5plus": 19},
        {"state": "NM", "state_name": "New Mexico",     "pct_5plus": 20},
        {"state": "LA", "state_name": "Louisiana",      "pct_5plus": 21},
    ],
}

NFCS_FINTECH_ADOPTION = {
    "source": "FINRA NFCS 2024 — Digital financial tool adoption",
    "data": [
        {"tool": "Mobile banking",            "pct_use": 81},
        {"tool": "P2P transfers (Venmo, etc)", "pct_use": 65},
        {"tool": "Mobile payments in store",  "pct_use": 53},
        {"tool": "Buy Now Pay Later (BNPL)",  "pct_use": 28},
        {"tool": "Crypto assets",             "pct_use": 18},
        {"tool": "Robo-advisors",             "pct_use": 11},
        {"tool": "AI financial advice",       "pct_use": 20},
    ],
}

NFCS_KEY_STATS = {
    "pct_financially_literate_5plus_2024": 27,
    "pct_financially_fragile_2024": 42,
    "pct_no_emergency_fund_3mo_2024": 54,
    "pct_no_retirement_savings_working_age": 32,
    "annual_cost_financial_illiteracy_usd_bn": 415,
    "pct_overspending_income_2024": 34,
    "pct_pay_only_min_credit_card": 20,
    "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}


# ─────────────────────────────────────────────
# FRED live series
# ─────────────────────────────────────────────
FRED_SERIES = {
    "personal_savings_rate": "PSAVERT",          # Personal Saving Rate
    "household_debt_to_income": "TDSP",          # Debt Service Payments as % of Disposable Income
    "consumer_credit_outstanding": "TOTALSL",    # Total Consumer Credit, $Billions
    "credit_card_delinquency": "DRCCLACBS",      # CC delinquency rate
    "median_household_income": "MEHOINUSA672N",  # Real median HH income
    "cpi_all": "CPIAUCSL",                       # CPI — cost of living context
    "fed_funds_rate": "FEDFUNDS",                # Fed funds rate — interest cost context
}


def build_payload():
    payload = {
        "meta": {
            "title": "U.S. Personal Financial Literacy Dashboard",
            "description": "Research-grade data on financial literacy, fragility, wealth gaps, and resource access across American households.",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sources": [
                "FINRA Foundation National Financial Capability Study (NFCS) 2009–2024",
                "Federal Reserve Survey of Consumer Finances (SCF) 2022",
                "FDIC National Survey of Unbanked & Underbanked Households 2023",
                "Federal Reserve Economic Data (FRED) — St. Louis Fed",
                "Bureau of Economic Analysis (BEA)",
            ],
        },
        "key_stats": NFCS_KEY_STATS,
        "literacy_over_time": NFCS_LITERACY_SCORES,
        "literacy_by_topic": NFCS_BIG5_TOPICS,
        "demographics": NFCS_DEMOGRAPHICS,
        "fragility_trends": NFCS_FRAGILITY_TRENDS,
        "emergency_savings": NFCS_EMERGENCY_SAVINGS,
        "credit_behavior": NFCS_CREDIT_BEHAVIOR,
        "wealth_gaps_scf": SCF_WEALTH_GAPS,
        "banking_access_fdic": FDIC_BANKING_ACCESS,
        "state_literacy": STATE_LITERACY,
        "fintech_adoption": NFCS_FINTECH_ADOPTION,
        "fred_live": {},
    }

    # Fetch live FRED series
    print("Fetching FRED live series...")
    for key, series_id in FRED_SERIES.items():
        print(f"  → {series_id} ({key})")
        obs = fetch_fred(series_id, limit=80)
        payload["fred_live"][key] = {
            "series_id": series_id,
            "observations": obs,
        }

    return payload


if __name__ == "__main__":
    print("=" * 60)
    print("Financial Literacy Dashboard — Data Pipeline")
    print(f"Run at: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    payload = build_payload()

    out_path = os.path.join(OUTPUT_DIR, "dashboard_data.js")
    with open(out_path, "w") as f:
        f.write("// Auto-generated by fetch_data.py — do not edit manually\n")
        f.write("// Source: FINRA NFCS 2024, Fed SCF 2022, FDIC 2023, FRED API\n")
        f.write(f"// Updated: {payload['meta']['last_updated']}\n\n")
        f.write("window.DASHBOARD_DATA = ")
        json.dump(payload, f, indent=2)
        f.write(";\n")

    # Also write raw JSON to data/
    raw_path = os.path.join(DATA_DIR, "dashboard_data.json")
    with open(raw_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\n✓ Data written to {out_path}")
    print(f"✓ Raw JSON written to {raw_path}")
    print(f"  Key stats: {json.dumps(payload['key_stats'], indent=2)}")
