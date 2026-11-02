"""Rebuild the profile's original SVG header and colorful technology badges."""

from copy import deepcopy
from html import escape
from math import ceil
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)

# Label, Devicon mark (None for technologies without a vendored mark), background.
TOOLS = {
    "c": ("C", "c", "#385473"),
    "cplusplus": ("C++", "cplusplus", "#00599c"),
    "go": ("Go", "go", "#087b98"),
    "java": ("Java", "java", "#b62d32"),
    "python": ("Python", "python", "#306998"),
    "typescript": ("TypeScript", "typescript", "#3178c6"),
    "javascript": ("JavaScript", "javascript", "#f7df1e"),
    "sql": ("SQL", None, "#256a87"),
    "react": ("React", "react", "#167b99"),
    "nextjs": ("Next.js", "nextjs", "#24292f"),
    "nodejs": ("Node.js", "nodejs", "#377a2f"),
    "fastify": ("Fastify", "fastify", "#30303d"),
    "fastapi": ("FastAPI", "fastapi", "#007f73"),
    "flask": ("Flask", "flask", "#34343d"),
    "grpc": ("gRPC", "grpc", "#087e85"),
    "webrtc": ("WebRTC", None, "#b62938"),
    "rest": ("REST", None, "#405eb5"),
    "html5": ("HTML5", "html5", "#b83a20"),
    "css3": ("CSS3", "css3", "#226bb0"),
    "tailwindcss": ("Tailwind CSS", "tailwindcss", "#0e7490"),
    "oracle": ("Oracle DB", "oracle", "#bc2d27"),
    "postgresql": ("PostgreSQL", "postgresql", "#336791"),
    "pgvector": ("pgvector", None, "#425f8c"),
    "redis": ("Redis", "redis", "#bd2b2d"),
    "kafka": ("Kafka", "kafka", "#4c3f74"),
    "bullmq": ("BullMQ", None, "#a52f39"),
    "mongodb": ("MongoDB", "mongodb", "#287b36"),
    "chromadb": ("ChromaDB", None, "#b04a26"),
    "supabase": ("Supabase", "supabase", "#176e54"),
    "firebase": ("Firebase", "firebase", "#ffca28"),
    "pytorch": ("PyTorch", "pytorch", "#c53d29"),
    "scikitlearn": ("scikit-learn", "scikitlearn", "#c45d15"),
    "numpy": ("NumPy", "numpy", "#285e9a"),
    "pandas": ("pandas", "pandas", "#403268"),
    "mastra": ("Mastra", None, "#24292f"),
    "langchain": ("LangChain", None, "#20664d"),
    "langgraph": ("LangGraph", None, "#336a53"),
    "ollama": ("Ollama", "ollama", "#444454"),
    "huggingface": ("Hugging Face", "huggingface", "#ffd21e"),
    "googleadk": ("Google ADK", None, "#2861c0"),
    "amazonwebservices": ("AWS", "amazonwebservices", "#b75e00"),
    "googlecloud": ("Google Cloud", "googlecloud", "#3468bd"),
    "cloudrun": ("Cloud Run", "cloudrun", "#3265b5"),
    "docker": ("Docker", "docker", "#176cbb"),
    "terraform": ("Terraform", "terraform", "#6344bd"),
    "githubactions": ("GitHub Actions", "githubactions", "#245fc0"),
    "git": ("Git", "git", "#c14028"),
    "envoy": ("Envoy", "envoy", "#a02678"),
    "prometheus": ("Prometheus", "prometheus", "#bf3e27"),
    "grafana": ("Grafana", "grafana", "#b95a00"),
    "jaegertracing": ("Jaeger", "jaegertracing", "#196a90"),
    "opentelemetry": ("OpenTelemetry", "opentelemetry", "#565a91"),
    "postman": ("Postman", "postman", "#c34b25"),
}


def save(path, data):
    path.write_text("\n".join(line.rstrip() for line in data.splitlines()) + "\n")


def mark(name):
    icon = deepcopy(ET.parse(ASSETS / "icons" / f"{name}.svg").getroot())
    icon.set("x", "7")
    icon.set("y", "5")
    icon.set("width", "20")
    icon.set("height", "20")
    return ET.tostring(icon, encoding="unicode")


def badge(name, label, logo, color):
    text = label.upper()
    start = 42 if logo else 12
    width = ceil(start + len(text) * 7.4 + 12)
    fg = "#17212b" if color in ("#f7df1e", "#ffca28", "#ffd21e") else "#ffffff"
    logo_svg = f'<rect width="34" height="30" fill="#ffffff"/>{mark(logo)}' if logo else ""
    save(ASSETS / "badges" / f"{name}.svg", f'''<svg xmlns="{SVG}" width="{width}" height="30" viewBox="0 0 {width} 30" role="img" aria-label="{escape(label)}">
  <title>{escape(label)}</title>
  <rect width="{width}" height="30" fill="{color}"/>
  {logo_svg}
  <text x="{start}" y="19.5" fill="{fg}" font-family="DejaVu Sans,Verdana,sans-serif" font-size="10.5" font-weight="700" letter-spacing="0.65">{escape(text)}</text>
</svg>''')


def header(theme, animate=True):
    dark = theme == "dark"
    fg, muted, green = ("#f4eee0", "#a6b5b2", "#55e0a7") if dark else ("#1b332c", "#48665c", "#087f55")
    order = [9, 3, 11, 5, 1, 8, 4, 12, 2, 10, 6, 7]
    states = [order[:]]
    for i in range(len(order) - 1):
        j = min(range(i, len(order)), key=order.__getitem__)
        order[i], order[j] = order[j], order[i]
        states.append(order[:])
    assert states[-1] == sorted(states[0])
    styles, bars = [], []
    for value in states[0]:
        positions = [state.index(value) * 13 for state in states]
        frames = [f"{i * 78 / (len(states)-1):.2f}%{{transform:translateX({x}px)}}" for i, x in enumerate(positions)]
        frames.extend([f"90%{{transform:translateX({positions[-1]}px)}}", f"100%{{transform:translateX({positions[0]}px)}}"])
        animation = f"animation:b{value} 18s ease-in-out infinite;" if animate else ""
        styles.append(f".b{value}{{transform:translateX({positions[0]}px);{animation}}}@keyframes b{value}{{{''.join(frames)}}}")
        fill = green if value % 3 else ("#f4ae61" if dark else "#b86615")
        bars.append(f'<rect class="b{value}" x="0" y="{96-value*6}" width="8" height="{value*6}" rx="2" fill="{fill}"/>')
    styles.append("@media(prefers-reduced-motion:reduce){*{animation:none!important}}")
    filename = f"header-{theme}{'' if animate else '-static'}.svg"
    save(ASSETS / filename, f'''<svg xmlns="{SVG}" width="840" height="184" viewBox="0 0 840 184" role="img" aria-labelledby="title desc">
  <title id="title">Darsh Patel — software generalist</title>
  <desc id="desc">A typographic nameplate with an actual selection-sort animation. Twelve bars move from an unsorted order to ascending order.</desc>
  <style>{''.join(styles)}</style>
  <text x="30" y="34" fill="{green}" font-family="DejaVu Sans Mono,monospace" font-size="13" letter-spacing="2">~/DARSH</text>
  <text x="27" y="105" fill="{fg}" font-family="Georgia,DejaVu Serif,serif" font-size="62" font-weight="700" letter-spacing="-2">Darsh Patel<tspan fill="{green}">.</tspan></text>
  <text x="31" y="145" fill="{muted}" font-family="DejaVu Sans Mono,monospace" font-size="17" letter-spacing="1.2">SOFTWARE GENERALIST</text>
  <g transform="translate(632 29)">{''.join(bars)}<path d="M-5 103H160" fill="none" stroke="{muted}" stroke-opacity="0.4"/></g>
  <text x="632" y="155" fill="{muted}" font-family="DejaVu Sans Mono,monospace" font-size="11" letter-spacing="0.7">selection sort / O(n²)</text>
</svg>''')


(ASSETS / "badges").mkdir(exist_ok=True)
for name, (label, logo, color) in TOOLS.items():
    badge(name, label, logo, color)
for name, label, logo, color in (
    ("github", "GitHub", "github", "#24292f"),
    ("linkedin", "LinkedIn", "linkedin", "#08669e"),
    ("portfolio", "darshpatel.dev", None, "#176a4a"),
    ("leetcode", "LeetCode", None, "#a75d00"),
):
    badge(name, label, logo, color)
for theme in ("light", "dark"):
    header(theme)
    header(theme, animate=False)

groups = (
    ("Languages", "c cplusplus go java python typescript javascript sql"),
    ("Backend & web", "react nextjs nodejs fastify fastapi flask grpc webrtc rest html5 css3 tailwindcss"),
    ("Databases & messaging", "oracle postgresql pgvector redis kafka bullmq mongodb chromadb supabase firebase"),
    ("AI & ML", "pytorch scikitlearn numpy pandas mastra langchain langgraph ollama huggingface googleadk"),
    ("Cloud & delivery", "amazonwebservices googlecloud cloudrun docker terraform githubactions"),
    ("Tools & observability", "git envoy prometheus grafana jaegertracing opentelemetry postman"),
)
sections = []
for title, names in groups:
    images = "\n".join(f'  <img src="assets/badges/{name}.svg" height="30" alt="{escape(TOOLS[name][0])}">' for name in names.split())
    sections.append(f"### {title}\n\n<p>\n{images}\n</p>")
readme = ROOT / "README.md"
before, rest = readme.read_text().split("<!-- STACK:START -->", 1)
_, after = rest.split("<!-- STACK:END -->", 1)
readme.write_text(before + "<!-- STACK:START -->\n\n" + "\n\n".join(sections) + "\n\n<!-- STACK:END -->" + after)
print(f"Built {len(TOOLS)} technology badges, four links, and animated/static headers.")
