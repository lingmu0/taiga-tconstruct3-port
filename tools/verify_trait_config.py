"""Check that every advertised runtime setting is consumed by gameplay code."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
def main():
    entries = json.loads((ROOT/'config/trait_defaults.json').read_text(encoding='utf-8'))
    keys = {entry['key'] for entry in entries}
    assert len(keys) == len(entries) == 126
    sources = list((ROOT/'src/main/java').rglob('*.java')) + list((ROOT/'src/platform').rglob('*.java'))
    gameplay = '\n'.join(p.read_text(encoding='utf-8') for p in sources if p.name not in ('TraitDefaults.java','TraitTuning.java','TraitConfig.java','TraitDescriptions.java'))
    used = set(re.findall(r'"((?:tools|armor|armor_rules|tool_rules)\.[A-Za-z0-9_.]+)"',gameplay))
    # Random damage bounds are accessed by their section prefix.
    used |= {group+'.'+key for group in ('tools.tantrum','tools.unstable') for key in ('minimumDamageMultiplier','maximumDamageMultiplier')}
    used -= {'tools.tantrum','tools.unstable'}
    assert keys <= used, 'Advertised settings not used: '+str(keys-used)
    assert used <= keys, 'Unknown settings used: '+str(used-keys)
    sections = {entry['key'].rsplit('.',1)[0] for entry in entries}
    traits = json.loads((ROOT/'config/traits.json').read_text(encoding='utf-8'))
    armor = json.loads((ROOT/'config/armor_traits.json').read_text(encoding='utf-8'))
    assert {'tools.'+name for name in traits} <= sections
    assert {'armor.'+name for name in armor} <= sections
    template = (ROOT/'config/taiga-traits.toml').read_text(encoding='utf-8')
    actual = {}
    section = ''
    for line in template.splitlines():
        line = line.strip()
        if line.startswith('['): section = line[1:-1]
        elif line and not line.startswith('#'):
            key, value = line.split('=',1)
            actual[section+'.'+key.strip()] = float(value.strip())
    assert actual == {entry['key']:entry['default'] for entry in entries}
    for mc in ('1.18.2','1.19.2','1.20.1'):
        for lang in ('en_us','zh_cn'):
            translations = json.loads((ROOT/f'src/generated/{mc}/assets/taiga/lang/{lang}.json').read_text(encoding='utf-8'))
            assert all('config.taiga.'+key in translations for key in keys)
    assert 'ModConfig.Type.SERVER, TraitConfig.SPEC' in (ROOT/'src/main/java/com/sosnitzka/taiga/Taiga.java').read_text()
    print('126 trait settings: complete gameplay coverage, TOML defaults, translations and synced server registration: PASS')

if __name__ == '__main__': main()
