"""Rebuild the profile's small SVG header and badges without network access."""

from copy import deepcopy
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def icon(name, x, y, size, white=False):
    element = deepcopy(ET.parse(ASSETS / "icons" / f"{name}.svg").getroot())
    element.set("x", str(x))
    element.set("y", str(y))
    element.set("width", str(size))
    element.set("height", str(size))
    if white:
        for child in element.iter():
            if child.get("fill") != "none":
                child.set("fill", "#ffffff")
    return ET.tostring(element, encoding="unicode")


def badge(filename, label, logo, color, width):
    content = f'''<svg xmlns="{SVG}" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-label="{escape(label)}">
  <title>{escape(label)}</title>
  <rect x="0.5" y="0.5" width="{width-1}" height="27" rx="6" fill="{color}"/>
  {icon(logo, 9, 6, 16, white=logo == 'github')}
  <text x="33" y="18" fill="#ffffff" font-family="DejaVu Sans,Verdana,sans-serif" font-size="11" font-weight="600">{escape(label)}</text>
</svg>
'''
    (ASSETS / "badges" / filename).write_text(content)


def header(theme):
    colors = {
        "light": ("#f0f7fa", "#d3e4ec", "#182e3d", "#426173", "#087f8c", "#e0f1f2", "#edf0fb", "#ece9fb"),
        "dark": ("#111c2a", "#2b4057", "#f0f6fc", "#b1c3d5", "#70d6dc", "#163640", "#1b2c4a", "#2d2546"),
    }
    bg, border, fg, muted, accent, tile1, tile2, tile3 = colors[theme]
    content = f'''<svg xmlns="{SVG}" width="840" height="142" viewBox="0 0 840 142" role="img" aria-labelledby="title desc">
  <title id="title">Darsh Patel — Make it happen.</title>
  <desc id="desc">A compact header with video, verified-code, and machine-learning symbols inspired by PeerShare, DevSentinel, and AlgoViz.</desc>
  <rect x="1" y="1" width="838" height="140" rx="14" fill="{bg}" stroke="{border}"/>
  <path d="M1 24V118Q1 141 24 141" fill="none" stroke="{accent}" stroke-width="3"/>
  <text x="30" y="64" fill="{fg}" font-family="DejaVu Sans,Verdana,sans-serif" font-size="37" font-weight="700" letter-spacing="-1">Darsh Patel</text>
  <text x="32" y="99" fill="{muted}" font-family="DejaVu Sans,Verdana,sans-serif" font-size="18">Make it happen.</text>
  <g transform="translate(547 37)" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <rect width="68" height="68" rx="15" fill="{tile1}" stroke="none"/>
    <rect x="14" y="19" width="40" height="30" rx="5"/>
    <path d="M30 27L41 34L30 41Z" fill="{accent}" stroke="none"/>
  </g>
  <g transform="translate(630 37)" fill="none" stroke="#7d9ee3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <rect width="68" height="68" rx="15" fill="{tile2}" stroke="none"/>
    <path d="M34 13L50 20V33C50 44 42 51 34 55C26 51 18 44 18 33V20Z"/>
    <path d="M26 33L32 39L43 27"/>
  </g>
  <g transform="translate(713 37)" fill="none" stroke="#a08be0" stroke-width="2.5" stroke-linecap="round">
    <rect width="68" height="68" rx="15" fill="{tile3}" stroke="none"/>
    <path d="M17 16V51H53M23 43L47 22"/>
    <g fill="#a08be0" stroke="none"><circle cx="24" cy="35" r="3"/><circle cx="32" cy="39" r="3"/><circle cx="36" cy="26" r="3"/><circle cx="45" cy="32" r="3"/><circle cx="49" cy="18" r="3"/></g>
  </g>
</svg>
'''
    (ASSETS / f"header-{theme}.svg").write_text(content)


def dark_icons():
    nextjs = ET.parse(ASSETS / "icons" / "nextjs.svg").getroot()
    nextjs.find(f"{{{SVG}}}circle").set("fill", "#f0f6fc")
    for stop in nextjs.iter(f"{{{SVG}}}stop"):
        stop.set("stop-color", "#111827")
    ET.ElementTree(nextjs).write(ASSETS / "icons" / "nextjs-dark.svg", encoding="unicode")
    kafka = ET.parse(ASSETS / "icons" / "kafka.svg").getroot()
    for path in kafka.iter(f"{{{SVG}}}path"):
        path.set("fill", "#e6edf3")
    ET.ElementTree(kafka).write(ASSETS / "icons" / "kafka-dark.svg", encoding="unicode")


def technology_badge(name, label, accent, width):
    mark_name = "nextjs-dark" if name == "nextjs" else name
    mark = icon(mark_name, 7, 4, 15) if name != "scikitlearn" else ""
    text_x = 29 if mark else 10
    content = f'''<svg xmlns="{SVG}" width="{width}" height="23" viewBox="0 0 {width} 23" role="img" aria-label="{escape(label)}">
  <title>{escape(label)}</title>
  <rect width="{width}" height="23" rx="4" fill="#243447"/>
  <rect width="3" height="23" rx="1.5" fill="{accent}"/>
  {mark}
  <text x="{text_x}" y="15.5" fill="#f0f6fc" font-family="DejaVu Sans,Verdana,sans-serif" font-size="10.5" font-weight="500">{escape(label)}</text>
</svg>
'''
    (ASSETS / "badges" / f"{name}.svg").write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n")


(ASSETS / "badges").mkdir(parents=True, exist_ok=True)
dark_icons()
badge("github.svg", "@darshpatel1052", "github", "#243447", 153)
badge("linkedin.svg", "LinkedIn / darshpatel52", "linkedin", "#125f91", 190)
for name, label, accent, width in (
    ("go", "Go", "#00add8", 52),
    ("nextjs", "Next.js", "#e6edf3", 76),
    ("typescript", "TypeScript", "#3178c6", 97),
    ("postgresql", "PostgreSQL", "#6fadd2", 104),
    ("docker", "Docker", "#2496ed", 78),
    ("redis", "Redis / BullMQ", "#ef5350", 119),
    ("python", "Python / Flask", "#ffd343", 115),
    ("react", "React", "#61dafb", 69),
    ("scikitlearn", "scikit-learn", "#f89939", 82),
):
    technology_badge(name, label, accent, width)
for theme in ("light", "dark"):
    header(theme)
print("Built two theme-aware headers, contrast variants, and contact/technology badges.")
