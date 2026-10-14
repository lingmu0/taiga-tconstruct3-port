"""One-time import of GPL-3.0 TAIGA data and unchanged raster assets."""
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT.parent / '.taiga-upstream'
JAVA = UPSTREAM / 'src/main/java/com/sosnitzka/taiga'

def main():
    fluids = (JAVA / 'Fluids.java').read_text()
    materials = []
    for name, color, temp in re.findall(r'new BasicTinkerFluid\("(\w+)_fluid", 0xFF([0-9a-fA-F]+), (\d+)', fluids):
        materials.append(dict(name=name, color=color.upper(), temperature=min(1500, max(500, int(temp))), tool=None))
    by_name = {m['name']: m for m in materials}
    text = (JAVA / 'TAIGA.java').read_text()
    tier_ids = {'STONE': 'minecraft:stone', 'DIAMOND': 'minecraft:diamond', 'OBSIDIAN': 'minecraft:diamond',
                'COBALT': 'minecraft:netherite', 'DURANITE': 'taiga:duranite',
                'VALYRIUM': 'taiga:valyrium', 'VIBRANIUM': 'taiga:vibranium'}
    for args in re.findall(r'integrateMaterial\(([^;]+)\);', text):
        args = [a.strip() for a in args.split(',')]
        name = args[0].strip('"').lower()
        number = lambda s: float(s.rstrip('f'))
        tool = dict(durability=int(args[3]), speed=number(args[4]), attack=number(args[5]),
                    handle=number(args[6]), tier=tier_ids[args[9]])
        tool['bow'] = {'draw':0.2,'range':0.4,'bonus':-1} if args[10] == 'shitty' else {
            'draw':number(args[10]),'range':number(args[11]),'bonus':number(args[12])}
        by_name[name]['tool'] = tool
    # Make the first tier-5 alloy reachable with cobalt/netherite tools.
    blocktext = (JAVA / 'Blocks.java').read_text()
    for name, level in re.findall(r'new BasicBlock\("(\w+)_(?:ore|block)",.*?,\s*(STONE|IRON|DIAMOND|COBALT|DURANITE|VALYRIUM|VIBRANIUM),', blocktext, re.DOTALL):
        if name in by_name:
            by_name[name]['ore_tier'] = tier_ids.get(level, 'minecraft:iron')
    ores = ['tiberium','aurorium','prometheum','duranite','valyrium','vibranium','karmesine',
            'ovium','jauxum','palladium','uru','osram','abyssum','eezo','dilithium']
    for m in materials:
        m['ore'] = m['name'] in ores
        m.setdefault('ore_tier', m['tool']['tier'] if m['tool'] else 'minecraft:netherite')
    by_name['prometheum']['ore_tier'] = 'minecraft:netherite'
    by_name['tiberium']['ore_tier'] = 'minecraft:iron'
    by_name['dilithium']['ore_tier'] = 'minecraft:diamond'
    traits_text = (JAVA / 'MaterialTraits.java').read_text()
    for name, suffix in re.findall(r'public static Material (\w+) = new Material\([^;]+?\)([^;]*);', traits_text):
        if name in by_name:
            defaults, per_stat = [], {}
            for trait, stat in re.findall(r'\.addTrait\((\w+)(?:, MaterialTypes\.(\w+))?\)', suffix):
                trait = {'instable': 'unstable'}.get(trait, trait)
                if trait in ('alien','crumbling'):
                    trait = 'taiga_' + trait
                entry = {'name': 'taiga:' + trait, 'level': 1}
                if stat:
                    per_stat.setdefault('tconstruct:' + stat.lower(), []).append(entry)
                else:
                    defaults.append(entry)
            by_name[name]['traits'] = {'default': defaults, 'perStat': per_stat}
    for m in materials:
        m.setdefault('traits', {'default': [], 'perStat': {}})
    alloys = []
    for call in re.findall(r'registerTinkerAlloy\((.*?)\);', (JAVA / 'Alloys.java').read_text(), re.DOTALL):
        stacks = re.findall(r'new FluidStack\s*\(\s*(TinkerFluids\s*\.\s*\w+|\w+Fluid)\s*,\s*(\d+)\)', call)
        parsed = []
        for fluid, amount in stacks:
            fluid = re.sub(r'\s+', '', fluid)
            if fluid.startswith('TinkerFluids.'):
                name = fluid.split('.')[-1]
                # Ardite was removed by TiC3. Hepatizon keeps the Nether alloy route.
                fluid = 'tconstruct:molten_' + ('hepatizon' if name == 'ardite' else name)
            else:
                fluid = 'taiga:molten_' + fluid[:-5]
            parsed.append({'fluid': fluid, 'amount': int(amount) * 90})
        assert len(parsed) >= 3, call
        alloys.append({'result': parsed[0], 'inputs': parsed[1:]})
    config = ROOT / 'config'
    config.mkdir(exist_ok=True)
    (config / 'materials.json').write_text(json.dumps(materials, indent=2) + '\n')
    (config / 'alloys.json').write_text(json.dumps(alloys, indent=2) + '\n')
    for language in ('en_us', 'zh_cn'):
        lang = {}
        for line in (UPSTREAM / f'src/main/resources/assets/taiga/lang/{language}.lang').read_text(encoding='utf-8').splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('material.') and key.endswith('.name'):
                    lang[key.split('.')[1]] = value
        (config / f'names_{language}.json').write_text(json.dumps(lang, ensure_ascii=False, indent=2), encoding='utf-8')
    textures = UPSTREAM / 'src/main/resources/assets/taiga/textures'
    dest = ROOT / 'src/main/resources/assets/taiga/textures'
    for source in textures.rglob('*'):
        if source.is_file() and source.suffix in ('.png', '.mcmeta'):
            rel = str(source.relative_to(textures)).replace('\\', '/').replace('blocks/', 'block/').replace('items/', 'item/')
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    shutil.copyfile(UPSTREAM / 'taiga.png', ROOT / 'src/main/resources/taiga.png')
    print('Imported', len(materials), 'fluids,', sum(m['tool'] is not None for m in materials), 'tool materials and', len(alloys), 'alloy recipes.')

if __name__ == '__main__':
    main()
