"""Fetch complete, unmodified SVG assets from the services in sources.json."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads((ROOT / "assets/sources.json").read_text())


def fetch(item):
    path, source = item
    data = subprocess.check_output([
        "curl", "--fail", "--silent", "--show-error", "--location",
        "--retry", "3", "--retry-delay", "1", "--retry-all-errors",
        "--connect-timeout", "10", "--max-time", "40", source["url"],
    ])
    svg = ET.fromstring(data)
    assert svg.tag == "{http://www.w3.org/2000/svg}svg", path
    text = " ".join(svg.itertext()).casefold()
    assert source["text"].casefold() in text, f"Missing expected label: {path}"
    assert not any(error in text for error in ("badge not found", "server error", "inaccessible", "rate limit exceeded")), path
    assert len(data) > 200 and b"<script" not in data, path
    return path, data


# Finish every download and validation before replacing any previous asset.
with ThreadPoolExecutor(max_workers=4) as pool:
    ready = list(pool.map(fetch, SOURCES.items()))

for path, data in ready:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_bytes() != data:
        target.write_bytes(data)

print(f"Fetched and validated {len(ready)} original service-generated SVGs.")
