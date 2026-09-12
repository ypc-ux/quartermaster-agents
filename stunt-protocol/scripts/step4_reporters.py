#!/usr/bin/env python3
"""Stunt Protocol Engine — Step 4: Build the list. Names, not inboxes.

Pull the byline from every coverage story, then find the person.
The address comes after (Step 4b). No API key required — uses public
search + Muck Rack profiles, which are public and free.
"""

import json, re
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "data"
STATUSES = ["found", "verified", "pitched", "replied", "closed"]

MASTHEAD_DOMAINS = {
    "The Verge": "theverge.com",
    "TechCrunch": "techcrunch.com",
    "Adweek": "adweek.com",
    "Marketing Week": "marketingweek.com",
    "Campaign": "campaignlive.co.uk",
    "PRWeek": "prweek.com",
    "The Drum": "thedrum.com",
    "Fast Company": "fastcompany.com",
    "Business Insider": "businessinsider.com",
    "The Guardian": "theguardian.com",
}


def load_reporters():
    p = OUTPUT_DIR / "reporters.json"
    return json.load(open(p)) if p.exists() else {"reporters": []}


def save_reporters(data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(OUTPUT_DIR / "reporters.json", "w"), indent=2)


def parse_byline(text):
    """Extract a byline from raw coverage text. Returns (name, outlet)."""
    # Common patterns: "By Jane Doe", "Jane Doe, TechCrunch"
    m = re.search(r"\bBy\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    if m:
        name = m.group(1)
    else:
        # "Jane Doe" at start of line followed by outlet
        m2 = re.search(r"^([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[,\|·]?\s*$", text.strip(), re.MULTILINE)
        name = m2.group(1) if m2 else None
    # Detect staff/editor bylines
    if name is None and re.search(r"\b(Staff|Editor|Newsroom)\b", text, re.I):
        return "(unbylined)", None
    return name, None


def add_reporter(name, outlet, coverage_url, coverage_headline, coverage_date, beat="", linkedin_url="", x_handle="", confidence="U"):
    """Add one row. One row per person — append coverage to note if duplicate."""
    data = load_reporters()
    # Dedupe by name + outlet
    for r in data["reporters"]:
        if r.get("name") == name and r.get("outlet") == outlet and name not in ("(unbylined)", "(unavailable)"):
            r["note"] = (r.get("note", "") + f"; {coverage_url}").strip("; ")
            save_reporters(data)
            print(f"[Stunt Protocol] Merged extra coverage into {r['reporter_id']} ({name})")
            return r
    n = len(data["reporters"]) + 1
    row = {
        "reporter_id": f"rep-{n:03d}",
        "name": name,
        "outlet": outlet or "",
        "outlet_domain": MASTHEAD_DOMAINS.get(outlet or "", ""),
        "coverage_url": coverage_url,
        "coverage_headline": coverage_headline,
        "coverage_date": coverage_date,
        "beat": beat,
        "linkedin_url": linkedin_url,
        "x_handle": x_handle,
        "email": "",
        "email_source": "",
        "confidence": confidence,
        "status": "found" if name not in ("(unbylined)", "(unavailable)") else ("verified" if name == "(unbylined)" else "closed"),
        "note": "",
    }
    if name == "(unbylined)":
        row["beat"] = ""
        row["confidence"] = "U"
    if name == "(unavailable)":
        row["note"] = "page would not load"
    data["reporters"].append(row)
    save_reporters(data)
    print(f"[Stunt Protocol] Found reporter {row['reporter_id']}: {name} @ {outlet}")
    return row


def search_linkedin(name, outlet):
    """Construct the search query used to find the LinkedIn profile.
    The agent runs this search; we return the query + a search URL.
    Reading Google's index of a LinkedIn page is not scraping. Told to search, not scrape."""
    q = f'"{name}" "{outlet}" linkedin'
    from urllib.parse import quote_plus
    return {"query": q, "url": f"https://www.google.com/search?q={quote_plus(q)}"}


def run():
    """Demo with seed reporters from the famouscampaigns coverage set."""
    print("[Stunt Protocol] Step 4: Build the list.")
    seed = [
        {"name": "James Vincent", "outlet": "The Verge", "url": "https://www.theverge.com/", "headline": "Agency builds fake fan blog, gets caught in 48 hours", "date": "2006-12-12"},
        {"name": "Sarah Perez", "outlet": "TechCrunch", "url": "https://techcrunch.com/", "headline": "This PR stunt made the front page of every outlet", "date": "2019-05-03"},
        {"name": "(unbylined)", "outlet": "Adweek", "url": "https://www.adweek.com/", "headline": "The agency that turned a mistake into a campaign", "date": "2021-03-09"},
    ]
    for s in seed:
        add_reporter(s["name"], s["outlet"], s["url"], s["headline"], s["date"])
    for r in load_reporters()["reporters"]:
        if r["name"] not in ("(unbylined)", "(unavailable)"):
            print(f"  {r['reporter_id']} search -> {search_linkedin(r['name'], r['outlet'])['url'][:70]}...")


if __name__ == "__main__":
    run()
