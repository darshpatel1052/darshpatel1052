"""Download existing tools' complete SVG output without drawing or editing it."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads((ROOT / "assets/widgets/sources.json").read_text())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stats-only", action="store_true", help="Refresh changing statistics only")
args = parser.parse_args()


def fetch(item):
    path, source = item
    data = subprocess.check_output([
        "curl", "--fail", "--silent", "--show-error", "--location",
        "--retry", "2", "--retry-delay", "2", "--retry-all-errors",
        "--connect-timeout", "10", "--max-time", "45", source["url"],
    ])
    svg = ET.fromstring(data)
    assert svg.tag == "{http://www.w3.org/2000/svg}svg", f"Not an SVG: {path}"
    label = " ".join(svg.itertext()).casefold()
    if source.get("icon_count"):
        groups = svg.findall("./{http://www.w3.org/2000/svg}g")
        assert len(groups) == source["icon_count"], f"Incomplete icon grid: {path}"
    else:
        assert source["label"].casefold() in label, f"Unexpected card: {path}"
    assert len(data) > 1000, f"Incomplete card: {path}"
    for error in ("something went wrong", "rate limit exceeded", "user not found", "could not resolve to a user", "failed to fetch", "internal server error", "deployment_disabled"):
        assert error not in label, f"Service error in {path}: {error}"
    assert b"<script" not in data.lower(), f"Unexpected script in {path}"
    if "github-" in path:
        assert "total prs" in label and "total commits" in label, f"Missing GitHub data: {path}"
    return path, data


selected = {path: source for path, source in SOURCES.items() if not args.stats_only or source["refresh"]}
# Validate the complete set before replacing any last-good image. An error
# response must never become the profile's visible card.
with ThreadPoolExecutor(max_workers=3) as pool:
    ready = list(pool.map(fetch, selected.items()))
for path, data in ready:
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.read_bytes() != data:
        destination.write_bytes(data)
print(f"Downloaded and validated {len(ready)} unmodified service-generated widgets.")
