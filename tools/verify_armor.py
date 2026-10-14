"""Validate native armor integration, legacy tags/recipes, and pure balance rules."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text(encoding='utf-8'))
ARMOR = read(ROOT / 'config/armor_materials.json')
TRAITS = read(ROOT / 'config/armor_traits.json')
COMPAT = read(ROOT / 'config/compatibility.json')
SLOTS = ('helmet','chestplate','leggings','boots')
FACTORS = (11,16,15,13)

def verify(mc):
    root = ROOT / f'src/generated/{mc}'
    baseline = COMPAT['versions'][mc]['tconstruct']
    jar_path = ROOT / f'.deps/maven/slimeknights/tconstruct/TConstruct/{mc}-{baseline}/TConstruct-{mc}-{baseline}.jar'
    with zipfile.ZipFile(jar_path) as jar:
        files = set(jar.namelist())
        def resolve_tag(tag, seen=None):
            seen = set() if seen is None else seen
            assert tag not in seen, 'Cyclic item tag: '+tag
            seen = seen | {tag}
            namespace, path = tag.split(':',1)
            filename = f'data/{namespace}/tags/items/{path}.json'
            entries = json.loads(jar.read(filename))['values'] if filename in files else []
            if (root / filename).is_file():
                local = read(root / filename)
                entries = ([] if local.get('replace') else entries) + local['values']
            result = set()
            for entry in entries:
                value = entry if isinstance(entry,str) else entry['id']
                if value.startswith('#'): result.update(resolve_tag(value[1:],seen))
                else: result.add(value)
            return result
        if mc == '1.18.2':
            for tag in ('tconstruct:modifiable','tconstruct:modifiable/durability','tconstruct:modifiable/armor/worn'):
                members = resolve_tag(tag)
                for name in ARMOR:
                    for slot in SLOTS: assert f'taiga:{name}_{slot}' in members, (tag,name,slot)
        else:
            cobalt = json.loads(jar.read('data/tconstruct/tinkering/materials/stats/cobalt.json'))['stats']
            assert 'slimeknights/tconstruct/tools/stats/PlatingMaterialStats.class' in files
            for slot in SLOTS:
                assert 'tconstruct:plating_'+slot in cobalt
                assert f'data/tconstruct/recipes/tools/parts/casting/{slot}_plating_gold_cast.json' in files
            assert 'data/tconstruct/recipes/tools/parts/casting/maille_gold_cast.json' in files
        for name, armor in ARMOR.items():
            for language in ('en_us','zh_cn'):
                lang = read(root / f'assets/taiga/lang/{language}.json')
                for key in TRAITS:
                    assert lang['modifier.taiga.armor_'+key]
                    assert lang['modifier.taiga.armor_'+key+'.description']
            material_stats = read(root / f'data/taiga/tinkering/materials/stats/{name}.json')['stats']
            material_traits = read(root / f'data/taiga/tinkering/materials/traits/{name}.json')
            expected_primary = {'name':'taiga:armor_'+armor['plating'],'level':1}
            expected_maille = {'name':'taiga:armor_'+armor['maille'],'level':1}
            if mc == '1.18.2':
                assert not any('plating_' in s or s == 'tconstruct:maille' for s in material_stats)
                for index, slot in enumerate(SLOTS):
                    item = f'{name}_{slot}'
                    definition = read(root / f'data/taiga/tinkering/tool_definitions/{item}.json')
                    base = definition['stats']['base']
                    assert base['tconstruct:durability'] == armor['durability_factor']*FACTORS[index]
                    assert base['tconstruct:armor'] == armor['armor'][index]
                    assert base['tconstruct:armor_toughness'] == armor['toughness']
                    assert definition['traits'] == [expected_primary,expected_maille]
                    assert definition['slots'] == {'upgrades':2,'defense':3,'abilities':1}
                    recipe = read(root / f'data/taiga/recipes/armor/building/{item}.json')
                    assert recipe['result']['item'] == 'taiga:'+item
                    assert recipe['key']['m'] == {'item':'taiga:'+name+'_ingot'}
                    assert sum(row.count('m') for row in recipe['pattern']) == (3,6,5,4)[index]
                for kind in ('station','repair_kit'):
                    repair = read(root / f'data/taiga/recipes/armor/repair/{name}_{kind}.json')
                    assert repair['repair_material'] == 'taiga:'+name
                    assert {entry['item'] for entry in repair['tool']} == {'taiga:'+name+'_'+s for s in SLOTS}
            else:
                for index, slot in enumerate(SLOTS):
                    stats = material_stats['tconstruct:plating_'+slot]
                    assert set(stats) == set(cobalt['tconstruct:plating_'+slot])
                    assert stats['durability'] == armor['durability_factor']*FACTORS[index]
                    assert stats['armor'] == armor['armor'][index]
                    assert stats['toughness'] == armor['toughness']
                    assert stats['knockback_resistance'] == armor['knockback_resistance']
                assert material_stats['tconstruct:maille'] == {}
                assert material_traits['perStat']['tconstruct:armor'] == [expected_primary]
                assert material_traits['perStat']['tconstruct:maille'] == [expected_maille]
                rendering = read(root / f'assets/taiga/tinkering/materials/{name}.json')['generator']
                supported = rendering['supported_stats' if mc == '1.20.1' else 'supportedStats']
                assert all(s in supported for s in ('tconstruct:armor_plating','tconstruct:armor_maille','tconstruct:maille'))
                assert (root / f'data/taiga/recipes/materials/{name}_casting.json').is_file()
                # Confirm the native armor selects the plate and maille stat families.
                native = json.loads(jar.read('data/tconstruct/tinkering/tool_definitions/plate_chestplate.json'))
                assert any(m.get('parts') == ['tconstruct:chestplate_plating','tconstruct:maille'] for m in native['modules'])
        # Protect pre-existing weapon/bow stats and traits against this armor extension.
        previous = ROOT / f'release/taiga-{mc}-forge-2.0.0-port.3.jar'
        if previous.is_file():
            with zipfile.ZipFile(previous) as old:
                for name in ARMOR:
                    for kind in ('stats','traits'):
                        filename = f'data/taiga/tinkering/materials/{kind}/{name}.json'
                        before = json.loads(old.read(filename))
                        after = read(root / filename)
                        if kind == 'stats':
                            for key, value in before['stats'].items(): assert after['stats'][key] == value
                        else:
                            assert before['default'] == after['default']
                            for key, value in before['perStat'].items(): assert after['perStat'][key] == value
    print(mc, ': 30 armor designs, native/legacy integration, crafting, repairs, traits and weapon regression: PASS')

def balance_checks():
    out = ROOT / 'build/armor-tests'
    out.mkdir(parents=True, exist_ok=True)
    java_home = os.environ.get('JAVA_HOME')
    def command(name):
        candidate = Path(java_home) / 'bin' / (name+'.exe') if java_home else None
        if candidate and candidate.is_file(): return str(candidate)
        found = shutil.which(name)
        assert found, 'Java 17+ JDK required for balance checks'
        return found
    src = ROOT / 'src/main/java/com/sosnitzka/taiga'
    subprocess.run([command('javac'),'--release','17','-encoding','UTF-8','-d',str(out),
                    str(src/'ArmorTrait.java'),str(src/'ArmorBalance.java'),str(src/'TraitDefaults.java'),str(src/'TraitTuning.java'),
                    str(ROOT/'tests/ArmorBalanceTest.java')],check=True)
    subprocess.run([command('java'),'-cp',str(out),'ArmorBalanceTest'],check=True)

if __name__ == '__main__':
    materials = read(ROOT / 'config/materials.json')
    assert set(ARMOR) == {m['name'] for m in materials if m['tool']}
    enums = (ROOT / 'src/main/java/com/sosnitzka/taiga/ArmorTrait.java').read_text()
    assert set(re.findall(r'\("([a-z_]+)"\)',enums)) == set(TRAITS)
    for armor in ARMOR.values():
        assert 1 <= armor['durability_factor'] <= 60
        assert len(armor['armor']) == 4 and sum(armor['armor']) <= 16
        assert 0 <= armor['toughness'] <= 3 and 0 <= armor['knockback_resistance'] <= 0.1
        assert armor['plating'] in TRAITS and armor['maille'] in TRAITS
    for version in COMPAT['versions']: verify(version)
    balance_checks()
