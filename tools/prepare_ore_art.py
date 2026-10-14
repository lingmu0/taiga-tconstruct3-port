"""Downscale approved image_gen outputs without smoothing or repainting pixels.

Optional art-authoring step: requires Pillow; normal builds use checked-in PNGs.
"""
from pathlib import Path
from PIL import Image
import json

ROOT = Path(__file__).resolve().parents[1]

def main():
    appearance = json.loads((ROOT / 'config/ore_appearance.json').read_text())
    destination = ROOT / 'src/main/resources/assets/taiga/textures/block/ore_overlay'
    destination.mkdir(parents=True, exist_ok=True)
    for name in appearance:
        with Image.open(ROOT / f'art/source/{name}.png') as original:
            assert original.mode == 'RGBA' and original.width == original.height
            sprite = original.resize((16, 16), Image.Resampling.NEAREST)
            alpha = list(sprite.getchannel('A').getdata())
            visible = sum(a >= 128 for a in alpha)
            assert 24 <= visible <= 160, (name, visible)
            assert min(alpha) == 0 and max(alpha) >= 250, name
            sprite.save(destination / f'{name}.png')
            print(name, '16x16 RGBA;', visible, 'visible pixels')

if __name__ == '__main__': main()
