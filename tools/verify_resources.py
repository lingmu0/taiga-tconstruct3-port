"""Non-launch validation of registries, assets, schemas and survival progression."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = json.loads((ROOT / 'config/materials.json').read_text())
ALLOYS = json.loads((ROOT / 'config/alloys.json').read_text())
TRAITS = json.loads((ROOT / 'config/traits.json').read_text(encoding='utf-8'))
COMPATIBILITY = json.loads((ROOT / 'config/compatibility.json').read_text(encoding='utf-8'))
ARMOR_MATERIALS = json.loads((ROOT / 'config/armor_materials.json').read_text(encoding='utf-8'))
ARMOR_TRAITS = json.loads((ROOT / 'config/armor_traits.json').read_text(encoding='utf-8'))
ALL_MODIFIERS = set(TRAITS) | {'armor_'+trait for trait in ARMOR_TRAITS}
ORE_APPEARANCE = json.loads((ROOT / 'config/ore_appearance.json').read_text(encoding='utf-8'))
DEEPSLATE = {name for name, appearance in ORE_APPEARANCE.items() if appearance.get('deepslate')}
LEVELS = {'minecraft:stone':1,'minecraft:iron':2,'minecraft:diamond':3,'minecraft:netherite':4,
          'taiga:duranite':5,'taiga:valyrium':6,'taiga:vibranium':7}
SOLID = [m for m in MATERIALS if m['name'] not in ('magma','nitronite')]
BLOCKS = {m['name']+'_block' for m in SOLID} | {m['name']+'_ore' for m in SOLID if m['ore']} | {'meteoritecobble_block','obsidioritecobble_block'}
BLOCKS |= {'deepslate_'+name+'_ore' for name in DEEPSLATE}
FLUIDS = {f'{prefix}molten_{m["name"]}' for m in MATERIALS for prefix in ('','flowing_')}
ITEMS = BLOCKS | {m['name']+'_'+form for m in SOLID for form in ('ingot','nugget','dust')} | {f'molten_{m["name"]}_bucket' for m in MATERIALS} | {'tiberium_crystal','dilithium_crystal'}

def load(path): return json.loads(path.read_text(encoding='utf-8'))

def local_id(value, domain):
    if not value.startswith('taiga:'): return
    assert value.split(':',1)[1] in domain, 'Unregistered local ID: '+value

def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values(): yield from walk(child)
    elif isinstance(value,list):
        for child in value: yield from walk(child)

def progression():
    # Start with vanilla netherite-tier equipment; later levels must be earned.
    reachable = {'minecraft:lava','tconstruct:molten_obsidian','tconstruct:molten_cobalt','tconstruct:molten_hepatizon',
                 'taiga:molten_basalt','taiga:molten_magma','taiga:molten_meteorite'}
    tier = 4
    changed = True
    while changed:
        before = (len(reachable),tier)
        for material in MATERIALS:
            if material['ore'] and LEVELS[material['ore_tier']] <= tier:
                reachable.add('taiga:molten_'+material['name'])
        if tier >= 5: reachable.add('taiga:molten_obsidiorite')
        for recipe in ALLOYS:
            if all(i['fluid'] in reachable for i in recipe['inputs']): reachable.add(recipe['result']['fluid'])
        for material in MATERIALS:
            if material['tool'] and 'taiga:molten_'+material['name'] in reachable:
                tier = max(tier,LEVELS[material['tool']['tier']])
        changed = before != (len(reachable),tier)
    unreachable = [m['name'] for m in MATERIALS if 'taiga:molten_'+m['name'] not in reachable]
    assert not unreachable, 'Unreachable materials: '+repr(unreachable)
    assert tier == 7
    return len(reachable)

def ore_changes(root, old):
    assets, data = root / 'assets/taiga', root / 'data/taiga'
    for name, appearance in ORE_APPEARANCE.items():
        sprite = (ROOT / f'src/main/resources/assets/taiga/textures/block/ore_overlay/{name}.png').read_bytes()
        assert sprite[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>IIBB', sprite[16:26]) == (16,16,8,6), name
        variants = [(name+'_ore', appearance['host'])]
        if name in DEEPSLATE: variants.append(('deepslate_'+name+'_ore', 'deepslate'))
        for block, host in variants:
            model = load(assets / f'models/block/{block}.json')
            assert model['textures']['base'] == 'minecraft:block/'+host
            assert model['textures']['overlay'] == 'taiga:block/ore_overlay/'+name
            assert len(model['elements']) == 2
            if not old: assert model['render_type'] == 'minecraft:cutout_mipped'
    for name in DEEPSLATE:
        normal, deep = name+'_ore', 'deepslate_'+name+'_ore'
        targets = load(data / f'worldgen/configured_feature/{normal}.json')['config']['targets']
        assert {t['target']['block']:t['state']['Name'] for t in targets} == {
            'minecraft:stone':'taiga:'+normal, 'minecraft:deepslate':'taiga:'+deep}
        # Deep variants retain fortune/silk-touch behavior and the original output.
        expected_loot = json.dumps(load(data / f'loot_tables/blocks/{normal}.json')).replace('taiga:'+normal, 'taiga:'+deep)
        assert load(data / f'loot_tables/blocks/{deep}.json') == json.loads(expected_loot)
        normal_melt = load(data / f'recipes/melting/{normal}.json')
        deep_melt = load(data / f'recipes/melting/{deep}.json')
        assert deep_melt['ingredient'] == {'item':'taiga:'+deep}
        for key in ('type','result','temperature','rate'): assert deep_melt[key] == normal_melt[key]
        for kind in ('smelting','blasting'):
            original = data / f'recipes/{kind}/{normal}.json'
            if original.exists():
                recipe = load(data / f'recipes/{kind}/{deep}.json')
                assert recipe['ingredient'] == {'item':'taiga:'+deep}
                assert recipe['result'] == load(original)['result']
        for domain in ('blocks','items'):
            assert 'taiga:'+deep in load(root / f'data/forge/tags/{domain}/ores/{name}.json')['values']
            assert 'taiga:'+deep in load(root / f'data/forge/tags/{domain}/ores_in_ground/deepslate.json')['values']
        # Mining progression must apply identically to both variants.
        for path in (root / 'data').glob('*/tags/blocks/needs_*_tool.json'):
            values = load(path)['values']
            assert ('taiga:'+normal in values) == ('taiga:'+deep in values), path
    eezo = load(data / 'worldgen/configured_feature/eezo_ore.json')['config']['targets']
    assert eezo == [{'target':{'predicate_type':'minecraft:block_match','block':'minecraft:bedrock'},'state':{'Name':'taiga:eezo_ore'}}]
    placement = load(data / 'worldgen/placed_feature/eezo_ore.json')['placement']
    height = next(p['height'] for p in placement if p['type'] == 'minecraft:height_range')
    assert height['min_inclusive'] == {'absolute':-64} and height['max_inclusive'] == {'absolute':-60}
    if old:
        native = (ROOT / 'src/platform/1.18.2/java/com/sosnitzka/taiga/NativeWorldgen.java').read_text()
        assert 'Blocks.BEDROCK), Taiga.block("eezo_ore")' in native
        for name in DEEPSLATE: assert f'Blocks.DEEPSLATE), Taiga.block("deepslate_{name}_ore")' in native
        platform = (ROOT / 'src/platform/1.18.2/java/com/sosnitzka/taiga/Platform.java').read_text()
        assert 'Dist.CLIENT' in platform and 'RenderType.cutoutMipped()' in platform

def verify(mc):
    root = ROOT / f'src/generated/{mc}'
    assets = root / 'assets/taiga'
    data = root / 'data/taiga'
    old = mc == '1.18.2'
    items = ITEMS | ({name+'_'+slot for name in ARMOR_MATERIALS for slot in ('helmet','chestplate','leggings','boots')} if old else set())
    compatibility = COMPATIBILITY['versions'][mc]
    metadata = (root / 'META-INF/mods.toml').read_text(encoding='utf-8')
    assert f'version="{COMPATIBILITY["mod_version"]}"' in metadata
    for mod, version_range in {
        'forge': f'[{compatibility["loader"]},)',
        'mantle': f'[{compatibility["mantle"]},)',
        'tconstruct': f'[{compatibility["tconstruct"]},{compatibility["tconstruct_max"]})'
    }.items():
        section = metadata.split(f'modId="{mod}"', 1)[1].split('[[', 1)[0]
        assert f'versionRange="{version_range}"' in section, (mc, mod, version_range)
    build = (ROOT / f'forge-{mc}/build.gradle').read_text(encoding='utf-8')
    assert f"net.minecraftforge:forge:{mc}-{compatibility['forge']}" in build
    assert f"Mantle:{mc}-{compatibility['mantle']}" in build
    assert f"TConstruct:{mc}-{compatibility['tconstruct']}" in build
    count = 0
    tc_version = compatibility['tconstruct']
    tc_jar = ROOT / f'.deps/maven/slimeknights/tconstruct/TConstruct/{mc}-{tc_version}/TConstruct-{mc}-{tc_version}.jar'
    with zipfile.ZipFile(tc_jar) as upstream:
        upstream_files = set(upstream.namelist())
        upstream_generator = json.loads(upstream.read('assets/tconstruct/tinkering/materials/cobalt.json'))['generator']
    for cast in ('multi_use','single_use'):
        for form in ('ingot','nugget'):
            assert f'data/tconstruct/tags/items/casts/{cast}/{form}.json' in upstream_files
    for path in root.rglob('*.json'):
        value = load(path)
        count += 1
        for obj in walk(value):
            if 'item' in obj and isinstance(obj['item'],str): local_id(obj['item'], items)
            if 'fluid' in obj and isinstance(obj['fluid'],str): local_id(obj['fluid'], FLUIDS)
            if 'Name' in obj: local_id(obj['Name'], BLOCKS | {f'molten_{m["name"]}' for m in MATERIALS})
            if obj.get('type') == 'minecraft:item': local_id(obj['name'], items)
            for key in ('model','parent'):
                model = obj.get(key)
                if isinstance(model,str) and model.startswith('taiga:'):
                    relative = 'models/'+model.split(':',1)[1]+'.json'
                    assert (assets / relative).is_file() or (ROOT / 'src/main/resources/assets/taiga' / relative).is_file(), model
                elif isinstance(model,str) and model.startswith('tconstruct:'):
                    assert 'assets/tconstruct/models/'+model.split(':',1)[1]+'.json' in upstream_files, model
            if 'textures' in obj:
                for texture in obj['textures'].values():
                    if texture.startswith('taiga:'):
                        relative = texture.split(':')[1]
                        assert (ROOT / f'src/main/resources/assets/taiga/textures/{relative}.png').exists(), texture
    for item in items: assert (assets / f'models/item/{item}.json').is_file(), item
    for block in BLOCKS:
        assert (assets / f'blockstates/{block}.json').is_file(), block
        assert (data / f'loot_tables/blocks/{block}.json').is_file(), block
    for material in SOLID:
        name = material['name']
        for large, small in [('block','ingot'),('ingot','nugget')]:
            packed = load(data / f'recipes/crafting/{name}_{large}_from_{small}.json')
            unpacked = load(data / f'recipes/crafting/{name}_{small}_from_{large}.json')
            assert packed['pattern'] == ['###','###','###']
            assert packed['key']['#']['item'] == f'taiga:{name}_{small}'
            assert packed['result'] == {'item':f'taiga:{name}_{large}'}
            assert unpacked['ingredients'] == [{'item':f'taiga:{name}_{large}'}]
            assert unpacked['result'] == {'item':f'taiga:{name}_{small}','count':9}
    for material in MATERIALS:
        if not material['tool']: continue
        name = material['name']
        stats = load(data / f'tinkering/materials/stats/{name}.json')['stats']
        head = stats['tconstruct:head']
        assert head['durability'] == material['tool']['durability']
        assert ('harvestTier' if old else 'mining_tier') in head
        assert ('miningSpeed' if old else 'mining_speed') in head
        assert ('tconstruct:extra' if old else 'tconstruct:binding') in stats
        assert 'tconstruct:limb' in stats and 'tconstruct:grip' in stats
        traits = load(data / f'tinkering/materials/traits/{name}.json')
        for entries in [traits['default'],*traits['perStat'].values()]:
            for entry in entries: assert entry['name'].split(':')[1] in ALL_MODIFIERS, entry
        rendering = load(assets / f'tinkering/materials/{name}.json')['generator']
        supported_key = 'supported_stats' if 'supported_stats' in upstream_generator else 'supportedStats'
        assert supported_key in rendering
        assert isinstance(rendering['transformer']['color_mapping']['palette'], type(upstream_generator['transformer']['color_mapping']['palette']))
    for material in MATERIALS:
        bucket = load(assets / f'models/item/molten_{material["name"]}_bucket.json')
        # Forge 40 registers DynamicBucketModel as forge:bucket, not fluid_container.
        assert bucket['loader'] == ('forge:bucket' if old else 'tconstruct:fluid_container')
    enum_source = (ROOT / 'src/main/java/com/sosnitzka/taiga/Trait.java').read_text()
    assert set(re.findall(r'\("([a-z_]+)"\)',enum_source)) == set(TRAITS)
    definitions = list((data / 'tinkering/materials/definition').glob('*.json'))
    assert len(definitions) == 30
    assert len(list((data / 'recipes/alloy').glob('*.json'))) == 28
    assert len(list((data / 'worldgen/placed_feature').glob('*.json'))) == 15
    for path in (data / 'worldgen/placed_feature').glob('*.json'):
        feature = load(path)['feature'].split(':')[1]
        assert (data / f'worldgen/configured_feature/{feature}.json').is_file(), feature
    if not old:
        feature_names = {'taiga:'+p.stem for p in (data / 'worldgen/placed_feature').glob('*.json')}
        injected = {feature for p in (data / 'forge/biome_modifier').glob('*.json') for feature in load(p)['features']}
        assert feature_names == injected, (feature_names,injected)
    for language in ('en_us','zh_cn'):
        lang = load(assets / f'lang/{language}.json')
        for trait in TRAITS: assert 'modifier.taiga.'+trait+'.description' in lang
        for item in items:
            assert ('block.taiga.' if item in BLOCKS else 'item.taiga.')+item in lang, item
        for material in MATERIALS:
            name = material['name']
            label = lang['fluid.taiga.molten_'+name]
            assert label == lang['fluid_type.taiga.molten_'+name] == lang['fluid.taiga.flowing_molten_'+name]
        for tier in ('duranite','valyrium','vibranium'):
            label = lang['stat.tconstruct.harvest_tier.taiga.'+tier]
            # A short value keeps the entire stat on one line in the material book.
            assert 1 <= len(label) <= 2 and '.' not in label
    assert set(load(assets / 'mantle/colors.json')['harvest_tier.taiga']) == {'duranite','valyrium','vibranium'}
    ore_changes(root, old)
    print(mc, ':', count, 'JSON files,', len(items),'items,',len(FLUIDS),'fluid IDs, 30 materials, 37 tool + 18 armor traits: PASS')

def jars():
    for mc in ('1.18.2','1.19.2','1.20.1'):
        path = ROOT / f'forge-{mc}/build/libs/taiga-{mc}-forge-{COMPATIBILITY["mod_version"]}.jar'
        assert path.is_file(), 'Build missing: '+mc
        with zipfile.ZipFile(path) as jar:
            names = set(jar.namelist())
            assert 'META-INF/mods.toml' in names and 'LICENSE' in names and 'NOTICE.md' in names
            for cls in ('Taiga','Platform','Catalog','TaigaModifier','TraitLogic','TraitEvents','DepositFeature',
                        'ArmorCatalog','ArmorTrait','ArmorModifier','ArmorEvents','ArmorPlatform','ArmorBalance',
                        'TraitDefaults','TraitTuning','TraitConfig','TraitDescriptions','TraitStatRefresh'):
                assert f'com/sosnitzka/taiga/{cls}.class' in names, cls
            if mc == '1.18.2':
                assert 'com/sosnitzka/taiga/LegacyArmorItem.class' in names
                assert 'com/sosnitzka/taiga/LegacyArmorRendering.class' in names
            assert not any(n.startswith(('slimeknights/','net/minecraft/','net/minecraftforge/')) for n in names)
            data_files = {p.relative_to(ROOT / f'src/generated/{mc}').as_posix():p for p in (ROOT / f'src/generated/{mc}').rglob('*') if p.is_file()}
            for name, source in data_files.items(): assert jar.read(name) == source.read_bytes(), 'Stale packaged resource: '+name
            for source in (ROOT / 'src/main/resources').rglob('*'):
                if source.is_file():
                    name = source.relative_to(ROOT / 'src/main/resources').as_posix()
                    assert jar.read(name) == source.read_bytes(), 'Stale shared resource: '+name
            assert jar.read('LICENSE') == (ROOT / 'LICENSE').read_bytes()
            assert jar.read('NOTICE.md') == (ROOT / 'NOTICE.md').read_bytes()
        print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())

if __name__ == '__main__':
    assert len(MATERIALS) == 39
    progression()
    for mc in ('1.18.2','1.19.2','1.20.1'): verify(mc)
    runpy.run_path(str(ROOT / 'tools/verify_armor.py'), run_name='__main__')
    runpy.run_path(str(ROOT / 'tools/verify_trait_config.py'), run_name='__main__')
    jars()
