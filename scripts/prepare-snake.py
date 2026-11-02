"""Validate both generated snakes before publishing motion-aware/static SVGs."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

source = Path(sys.argv[1])
destination = Path(__file__).resolve().parents[1] / "assets" / "activity"
namespace = {"svg": "http://www.w3.org/2000/svg"}
prepared = {}

for theme in ("light", "dark"):
    svg = (source / f"snake-{theme}.svg").read_text()
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg", "Expected an SVG"
    assert len(root.findall(".//svg:rect", namespace)) >= 300, "Missing contribution cells"
    assert "@keyframes" in svg, "Missing snake animation"
    assert "<script" not in svg and "<foreignObject" not in svg, "Unexpected active content"
    assert svg.rstrip().endswith("</svg>"), "Incomplete SVG"
    motion = "<style>@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>"
    still = "<style>*{animation:none!important}</style>"
    for suffix, extra in (("", motion), ("-static", still)):
        data = svg.rstrip()[:-6] + extra + "</svg>\n"
        ET.fromstring(data)
        prepared[f"snake-{theme}{suffix}.svg"] = data

destination.mkdir(parents=True, exist_ok=True)
for name, data in prepared.items():
    (destination / name).write_text(data)
print("Validated both contribution graphs and prepared motion/static variants.")
