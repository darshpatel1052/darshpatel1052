"""Rasterize TerminalTextEffects' Blackhole effect; no hand-drawn SVG artwork.

Install scripts/hero-requirements.txt, then run this script. The committed GIF
needs no viewer-side service, JavaScript, credentials, or scheduled workflow.
"""

from pathlib import Path
import argparse
import random

from PIL import Image, ImageDraw, ImageFont
from pyfiglet import Figlet
from terminaltexteffects import Color, Gradient
from terminaltexteffects.effects.effect_blackhole import Blackhole


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--font", default="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
args = parser.parse_args()

random.seed(1052)
name = Figlet(font="ansi_shadow", width=200).renderText("Darsh Patel").rstrip()
effect = Blackhole(name)
effect.terminal_config.canvas_width = 90
effect.terminal_config.canvas_height = 14
effect.terminal_config.anchor_text = "c"
effect.terminal_config.ignore_terminal_dimensions = True
effect.effect_config.blackhole_color = Color("58e6d9")
effect.effect_config.star_colors = tuple(Color(c) for c in ("58e6d9", "b794ff", "f5c56b"))
effect.effect_config.final_gradient_stops = tuple(Color(c) for c in ("58e6d9", "78acff", "c6a0ff"))
effect.effect_config.final_gradient_direction = Gradient.Direction.HORIZONTAL

font = ImageFont.truetype(args.font, 18)
cell_width, cell_height, margin = 11, 22, 24
size = (90 * cell_width + margin * 2, 14 * cell_height + margin * 2)
background = "#0d1117"
iterator = iter(effect)


def rasterize():
    """Render the engine's visible cells and colors in its own layer order."""
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)
    terminal = iterator.terminal
    for character in sorted(terminal._visible_characters, key=lambda char: char.layer):
        coord = character.motion.current_coord
        if not (1 <= coord.column <= 90 and 1 <= coord.row <= 14):
            continue
        visual = character.animation.current_character_visual
        if visual.hidden or visual.symbol == " ":
            continue
        color = visual.colors.fg_color.rgb_color if visual.colors and visual.colors.fg_color else "e6edf3"
        x = margin + (coord.column - 1) * cell_width
        y = margin + (14 - coord.row) * cell_height
        draw.text((x, y), visual.symbol, fill=f"#{color}", font=font, anchor="la")
    return image


frames = []
for index, _ in enumerate(iterator):
    # The effect advances at 60 ticks/s. Sampling every third tick preserves
    # the movement at 20 fps while keeping a profile-sized download.
    if index % 3 == 0:
        frames.append(rasterize().quantize(colors=128))
    if index > 1800:
        raise RuntimeError("Effect exceeded its expected duration")

still = rasterize()
target = ROOT / "assets/hero"
target.mkdir(parents=True, exist_ok=True)
still.save(target / "blackhole-static.png", optimize=True)
# Show the readable name in thumbnails and keep it on screen between cycles.
cover = still.quantize(colors=128)
sequence = [cover, *frames]
sequence[0].save(
    target / "blackhole.gif", save_all=True, append_images=sequence[1:],
    duration=[2400] + [50] * len(frames), loop=0, disposal=1, optimize=True,
)
with Image.open(target / "blackhole.gif") as check:
    assert check.n_frames > 50 and check.size == size
    assert check.info.get("loop") == 0
print(f"Generated {len(sequence)} frames, {size[0]}×{size[1]}, with TerminalTextEffects Blackhole.")
