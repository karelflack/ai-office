"""
OSV.dev vulnerability scanner service.

Uses the OSV.dev batch query API (POST /v1/querybatch) to minimize HTTP round-trips.
Free, no API key required. Covers npm, PyPI, Go, Maven, Cargo, RubyGems.

Reference: https://google.github.io/osv.dev/post-v1-querybatch/
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# OSV ecosystem name mapping from our internal names to OSV API names
ECOSYSTEM_MAP = {
    "npm": "npm",
    "pypi": "PyPI",
    "go": "Go",
    "maven": "Maven",
    "cargo": "crates.io",
    "rubygems": "RubyGems",
}

# Batch size for OSV querybatch — keep under 1000 per API limits
OSV_BATCH_SIZE = 100


async def query_osv_batch(
    packages: list[dict[str, str]],
) -> list[list[dict[str, Any]]]:
    """
    Query OSV.dev for vulnerabilities across multiple packages in a single request.

    Args:
        packages: list of {"name": str, "version": str, "ecosystem": str}

    Returns:
        list of result lists, one per input package (same order)
    """
    queries = []
    for pkg in packages:
        osv_ecosystem = ECOSYSTEM_MAP.get(pkg["ecosystem"].lower(), pkg["ecosystem"])
        queries.append(
            {
                "version": pkg["version"],
                "package": {
                    "name": pkg["name"],
                    "ecosystem": osv_ecosystem,
                },
            }
        )

    url = f"{settings.osv_api_url}/v1/querybatch"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json={"queries": queries})
        response.raise_for_status()
        data = response.json()

    # results is a list with one entry per query; each entry has {"vulns": [...]}
    return [item.get("vulns", []) for item in data.get("results", [])]


def parse_severity(osv_vuln: dict[str, Any]) -> tuple[str | None, Decimal | None]:
    """
    Extract severity label and CVSS score from an OSV vulnerability record.

    OSV provides severity in database_specific or via the CVSS score in the
    severity array. We normalise to: CRITICAL / HIGH / MEDIUM / LOW / UNKNOWN.
    """
    severity_label: str | None = None
    cvss_score: Decimal | None = None

    # Try CVSS score from the severity array
    for sev in osv_vuln.get("severity", []):
        if sev.get("type") == "CVSS_V3":
            try:
                score = float(sev.get("score", 0))
                cvss_score = Decimal(str(round(score, 1)))
                if score >= 9.0:
                    severity_label = "CRITICAL"
                elif score >= 7.0:
                    severity_label = "HIGH"
                elif score >= 4.0:
                    severity_label = "MEDIUM"
                elif score > 0:
                    severity_label = "LOW"
            except (ValueError, TypeError):
                pass
            break

    # Fall back to database_specific severity if no CVSS
    if severity_label is None:
        db_specific = osv_vuln.get("database_specific", {})
        raw = db_specific.get("severity", "")
        if raw:
            severity_label = raw.upper()

    return severity_label, cvss_score


def extract_fixed_version(osv_vuln: dict[str, Any], ecosystem: str) -> str | None:
    """Extract the first fixed version from OSV affected ranges."""
    osv_ecosystem = ECOSYSTEM_MAP.get(ecosystem.lower(), ecosystem)
    for affected in osv_vuln.get("affected", []):
        pkg = affected.get("package", {})
        if pkg.get("ecosystem") != osv_ecosystem:
            continue
        for version_range in affected.get("ranges", []):
            for event in version_range.get("events", []):
                fixed = event.get("fixed")
                if fixed:
                    return fixed
    return None


def extract_cve_id(osv_vuln: dict[str, Any]) -> str | None:
    """Extract a CVE ID from the aliases list if present."""
    for alias in osv_vuln.get("aliases", []):
        if alias.startswith("CVE-"):
            return alias
    return None


def parse_osv_vulnerability(
    osv_vuln: dict[str, Any], ecosystem: str
) -> dict[str, Any]:
    """
    Parse a single OSV vulnerability record into a dict ready to create a CveMatch row.
    """
    severity_label, cvss_score = parse_severity(osv_vuln)
    return {
        "osv_id": osv_vuln.get("id", ""),
        "cve_id": extract_cve_id(osv_vuln),
        "severity": severity_label,
        "cvss_score": cvss_score,
        "summary": osv_vuln.get("summary"),
        "fixed_in_version": extract_fixed_version(osv_vuln, ecosystem),
    }
