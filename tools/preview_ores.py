"""Render a local QA contact sheet from the layered block models, not game screenshots.

Pass a locally installed Minecraft client jar. Vanilla textures are read directly
for this preview and are not copied into the distributed mod or source archive.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import io
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    appearances = json.loads((ROOT / 'config/ore_appearance.json').read_text())
    rows = [(name, cfg['host']) for name, cfg in appearances.items()]
    rows += [(name, 'deepslate') for name, cfg in appearances.items() if cfg.get('deepslate')]
    sheet = Image.new('RGB', (800, 70 + 180 * len(rows)), '#25282c')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 18), 'TAIGA port.3: model texture preview (not an in-game screenshot)', fill='white')
    for x, label in [(220, 'Previous'), (410, 'Vanilla host'), (600, 'New layered ore')]:
        draw.text((x, 45), label, fill='white')
    textures = ROOT / 'src/main/resources/assets/taiga/textures/block'
    with zipfile.ZipFile(sys.argv[1]) as client:
        for index, (name, host) in enumerate(rows):
            top = 70 + index * 180
            draw.text((15, top + 55), name, fill='white')
            draw.text((15, top + 75), host, fill='#bbbbbb')
            original = Image.open(textures / f'ore/{name}.png').convert('RGBA')
            base = Image.open(io.BytesIO(client.read(f'assets/minecraft/textures/block/{host}.png'))).convert('RGBA')
            overlay = Image.open(textures / f'ore_overlay/{name}.png').convert('RGBA')
            # The block's cutout layer discards alpha below 0.5, without blending.
            overlay.putalpha(overlay.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
            composite = Image.alpha_composite(base, overlay)
            for x, tile in [(220, original), (410, base), (600, composite)]:
                sheet.paste(tile.resize((160, 160), Image.Resampling.NEAREST), (x, top))
    output = ROOT / 'build/qa/ore-comparison.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output)

if __name__ == '__main__': main()
