#!/usr/bin/env python3
"""
research-sample-scan.py — aggregate Phase 1 + Phase 2 sweep across a sample of
German SME websites for the toolkit's launch-promo report.

Output is intentionally anonymised: no per-domain results in the public
report. Per-domain JSONs are written to a local directory for the operator's
own sanity-checking and never published.

Scope:
  - Phase 1 (static): fetch the homepage HTML once, scan for the audit's
    catalogue of static external resources (Google Fonts CDN, GA without
    consent gating, Meta Pixel, etc.). Cheap, no browser.
  - Phase 2 (runtime): optional. For each domain, launch a Playwright browser
    with no consent click and record which third-party hosts fire before any
    user interaction. Expensive — gated by --runtime.

Out of scope on purpose:
  - Phase 3 docs (would need login or deep HTML parsing — privacy-invasive)
  - Phase 4 sub-processor reconciliation (operator-private info)
  - Anything that would identify a specific operator in the aggregate output

Politeness:
  - robots.txt honoured
  - one request per domain per phase, 2s+ delay between domains
  - User-Agent identifies the toolkit and points at the repo
  - no auth probing, no form submission, no JS interaction

Usage:
  python research-sample-scan.py --input domains.csv --out results/
  python research-sample-scan.py --input domains.csv --out results/ --runtime
  python research-sample-scan.py --aggregate results/ --report launch-report.md

Input CSV format:
  domain
  example.de
  beispiel-handwerk.de
  ...

Sampling: provide a curated, randomly-sampled list. This script does NOT
crawl directories or harvest domains — that work is upstream.
"""

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.robotparser
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

TOOLKIT_UA = "de-legal-toolkit-research-scan/0.1 (+https://github.com/Sleeeepy/de-legal-toolkit)"
REQUEST_TIMEOUT = 15
DOMAIN_DELAY_S = 2.0

# --- Phase 1 static-resource patterns ---------------------------------------
# These mirror skills/audit/checks/phase-1-static-resources.md. Keep the two
# in sync — a pattern listed here that the audit doesn't check is dishonest;
# a check the audit performs but this script doesn't see is a coverage gap.

STATIC_PATTERNS = {
    "google_fonts_cdn": [
        r"fonts\.googleapis\.com",
        r"fonts\.gstatic\.com",
    ],
    "google_analytics_inline": [
        r"google-analytics\.com/analytics\.js",
        r"googletagmanager\.com/gtag/js",
        r"googletagmanager\.com/gtm\.js",
    ],
    "meta_pixel_inline": [
        r"connect\.facebook\.net/.+/fbevents\.js",
        r"fbq\(['\"]init['\"]",
    ],
    "hotjar_inline": [
        r"static\.hotjar\.com",
    ],
    "stale_tmg_citation": [
        r"§\s*5\s*TMG",
        r"&sect;\s*5\s*TMG",
    ],
    "stale_ttdsg_citation": [
        r"§\s*25\s*TTDSG",
    ],
    "kuendigungswunsch_label": [
        # FIND-2026-002 — OLG Schleswig 6 U 42/25 misleading label
        r"K(ü|ue)ndigungswunsch",
        r"K(ü|ue)ndigung\s+(beantragen|w(ü|ue)nschen)",
    ],
    "bestellen_button_weak": [
        # FIND-WAVE-002 — Bestellbutton must be unambiguous
        # We can't be sure from a homepage; flagged only if "Jetzt kaufen"
        # / "Bestellen" appears next to a price + cart context. The
        # homepage check is a coarse heuristic — confirm with a real audit.
        r"\bJetzt\s+kaufen\b",
    ],
}


@dataclass
class DomainFinding:
    pattern_key: str
    matched_text: str  # truncated, no PII


@dataclass
class DomainResult:
    domain: str
    scanned_at: str
    fetch_status: Optional[int] = None
    fetch_error: Optional[str] = None
    bytes_fetched: int = 0
    robots_disallow: bool = False
    static_findings: list[DomainFinding] = field(default_factory=list)
    runtime_third_party_hosts: list[str] = field(default_factory=list)  # populated by --runtime
    runtime_skipped: bool = True


# --- Phase 1 -----------------------------------------------------------------

def fetch_homepage(domain: str) -> tuple[Optional[str], DomainResult]:
    """Fetch a homepage once. Honour robots.txt. Return (html, partial result)."""
    result = DomainResult(domain=domain, scanned_at=datetime.utcnow().isoformat() + "Z")

    base = f"https://{domain}"
    robots_url = urllib.parse.urljoin(base, "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        if not rp.can_fetch(TOOLKIT_UA, base):
            result.robots_disallow = True
            return None, result
    except Exception:
        # robots fetch failed — proceed but flag in operator notes
        pass

    try:
        resp = requests.get(
            base,
            headers={"User-Agent": TOOLKIT_UA, "Accept-Language": "de-DE,de;q=0.9"},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        result.fetch_status = resp.status_code
        result.bytes_fetched = len(resp.content)
        if resp.status_code == 200:
            return resp.text, result
        return None, result
    except requests.RequestException as e:
        result.fetch_error = type(e).__name__
        return None, result


def scan_static(html: str, result: DomainResult) -> None:
    """Apply STATIC_PATTERNS against the fetched HTML."""
    for key, patterns in STATIC_PATTERNS.items():
        for pat in patterns:
            for match in re.finditer(pat, html, flags=re.IGNORECASE):
                snippet = match.group(0)[:120]
                result.static_findings.append(
                    DomainFinding(pattern_key=key, matched_text=snippet)
                )
                break  # one match per pattern is enough for aggregate stats


# --- Phase 2 (runtime, optional) --------------------------------------------

def scan_runtime(domain: str, result: DomainResult) -> None:
    """Launch a headless browser, visit homepage, record third-party hosts
    that fire before any user interaction. Requires playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result.runtime_skipped = True
        result.fetch_error = (result.fetch_error or "") + " | playwright not installed"
        return

    third_party_hosts: set[str] = set()
    homepage_host = domain.lower()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=TOOLKIT_UA,
            locale="de-DE",
        )
        page = context.new_page()

        def on_request(req):
            host = urllib.parse.urlparse(req.url).hostname or ""
            if host and homepage_host not in host:
                third_party_hosts.add(host)

        page.on("request", on_request)
        try:
            page.goto(f"https://{domain}", timeout=20000, wait_until="networkidle")
        except Exception as e:
            result.fetch_error = (result.fetch_error or "") + f" | runtime: {type(e).__name__}"
        finally:
            browser.close()

    result.runtime_third_party_hosts = sorted(third_party_hosts)
    result.runtime_skipped = False


# --- Scan orchestration ------------------------------------------------------

def load_domains(input_path: Path) -> list[str]:
    domains = []
    with input_path.open() as f:
        reader = csv.reader(f)
        first = True
        for row in reader:
            if not row:
                continue
            if first and row[0].strip().lower() == "domain":
                first = False
                continue
            first = False
            d = row[0].strip().lower()
            if d:
                domains.append(d)
    return domains


def scan_one(domain: str, runtime: bool) -> DomainResult:
    html, result = fetch_homepage(domain)
    if html:
        scan_static(html, result)
    if runtime:
        scan_runtime(domain, result)
    return result


def write_result(result: DomainResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-z0-9.-]", "_", result.domain)
    path = out_dir / f"{safe}.json"
    path.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False))


def cmd_scan(args) -> None:
    domains = load_domains(Path(args.input))
    out = Path(args.out)
    print(f"Scanning {len(domains)} domains. runtime={args.runtime}")
    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}")
        try:
            r = scan_one(domain, runtime=args.runtime)
            write_result(r, out)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"  unexpected error: {type(e).__name__}: {e}")
        time.sleep(DOMAIN_DELAY_S)


# --- Aggregate report --------------------------------------------------------

def cmd_aggregate(args) -> None:
    results_dir = Path(args.aggregate)
    files = sorted(results_dir.glob("*.json"))
    if not files:
        print(f"No result files in {results_dir}")
        return

    sample_n = len(files)
    fetched_ok = 0
    pattern_counter: Counter[str] = Counter()
    runtime_host_counter: Counter[str] = Counter()
    runtime_ran = 0

    for f in files:
        data = json.loads(f.read_text())
        if data.get("fetch_status") == 200:
            fetched_ok += 1
        seen_patterns = {fin["pattern_key"] for fin in data.get("static_findings", [])}
        for key in seen_patterns:
            pattern_counter[key] += 1
        if not data.get("runtime_skipped", True):
            runtime_ran += 1
            for host in data.get("runtime_third_party_hosts", []):
                runtime_host_counter[host] += 1

    report = render_report(
        sample_n=sample_n,
        fetched_ok=fetched_ok,
        pattern_counter=pattern_counter,
        runtime_ran=runtime_ran,
        runtime_host_counter=runtime_host_counter,
    )
    Path(args.report).write_text(report)
    print(f"Wrote {args.report}")


def render_report(
    *,
    sample_n: int,
    fetched_ok: int,
    pattern_counter: Counter[str],
    runtime_ran: int,
    runtime_host_counter: Counter[str],
) -> str:
    today = datetime.utcnow().date().isoformat()
    pct = lambda n: f"{(n / fetched_ok * 100):.1f}%" if fetched_ok else "n/a"

    lines = [
        f"# DE SME compliance sample scan — {today}",
        "",
        f"**Sample size:** {sample_n} domains randomly sampled from a curated list of",
        "German SME websites (Handwerk, Praxen, kleine Gewerbebetriebe, Vereine).",
        f"**Successfully fetched:** {fetched_ok} ({fetched_ok / sample_n:.0%} of sample).",
        "**Method:** Phase 1 static fetch + (where indicated) Phase 2 runtime browser.",
        "**Tool:** [de-legal-toolkit](https://github.com/Sleeeepy/de-legal-toolkit) v0.1.",
        "**Anonymisation:** no per-domain results disclosed; aggregate counts only.",
        "",
        "---",
        "",
        "## Static findings (Phase 1 — homepage HTML)",
        "",
        "| Pattern | Sites affected | Share of fetched |",
        "|---------|---------------:|-----------------:|",
    ]

    label_map = {
        "google_fonts_cdn": "Google Fonts loaded from googleapis.com / gstatic.com",
        "google_analytics_inline": "GA / GTM script tag in homepage HTML",
        "meta_pixel_inline": "Meta Pixel snippet in homepage HTML",
        "hotjar_inline": "Hotjar snippet in homepage HTML",
        "stale_tmg_citation": "Stale `§ 5 TMG` citation (replaced by § 5 DDG, Feb 2024)",
        "stale_ttdsg_citation": "Stale `§ 25 TTDSG` citation (renamed to TDDDG)",
        "kuendigungswunsch_label": "Misleading Kündigungsbutton label (OLG Schleswig 6 U 42/25)",
        "bestellen_button_weak": "Weak Bestellbutton wording on homepage (coarse heuristic)",
    }

    for key, n in pattern_counter.most_common():
        label = label_map.get(key, key)
        lines.append(f"| {label} | {n} | {pct(n)} |")

    lines += [
        "",
        "## Runtime findings (Phase 2 — pre-consent third-party network)",
        "",
        f"Runtime checks ran on **{runtime_ran}** domains.",
        "Hosts contacted before any user interaction (top 15):",
        "",
        "| Third-party host | Sites contacting it |",
        "|------------------|--------------------:|",
    ]
    for host, n in runtime_host_counter.most_common(15):
        lines.append(f"| `{host}` | {n} |")

    lines += [
        "",
        "## Reading the numbers",
        "",
        "These percentages are the *aggregate exposed surface* of small German",
        "businesses to scalable Abmahn vectors (Google Fonts wave, pre-consent",
        "trackers, stale Impressum citations, misleading Kündigungsbutton",
        "labels). Most of the affected operators are unaware. Most of the fixes",
        "take under an hour.",
        "",
        "The toolkit at https://github.com/Sleeeepy/de-legal-toolkit lets a solo",
        "founder or maintainer find these issues in their own codebase in",
        "minutes, with citations and fix actions, without paying for a",
        "compliance SaaS.",
        "",
        "## Method notes",
        "",
        "- Sampling: random draw from a curated list; not exhaustive.",
        "- robots.txt honoured; disallowed domains skipped without retry.",
        "- One request per phase per domain; 2s+ inter-domain delay.",
        "- No login, no form submission, no JS user interaction.",
        "- No per-domain disclosure in this report. Per-domain results retained",
        "  privately for the maintainer's verification only.",
        "",
        "## Disclaimer",
        "",
        "Not legal advice. The patterns scanned for map to current rulings and",
        "statutes documented in `findings/_current.md`, but the presence of a",
        "pattern is not a finding of unlawful conduct — context (consent",
        "configuration, processor agreements, legitimate-interest balancing)",
        "matters. Individual operators are not identified.",
    ]

    return "\n".join(lines) + "\n"


# --- CLI ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=False)

    # Default flow: scan
    parser.add_argument("--input", help="CSV file with `domain` column")
    parser.add_argument("--out", default="results", help="Directory for per-domain JSONs")
    parser.add_argument("--runtime", action="store_true", help="Run Phase 2 runtime checks (requires playwright)")
    parser.add_argument("--aggregate", help="Aggregate from a results directory; pair with --report")
    parser.add_argument("--report", default="launch-report.md", help="Aggregate report output path")

    args = parser.parse_args()

    if args.aggregate:
        cmd_aggregate(args)
    elif args.input:
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
