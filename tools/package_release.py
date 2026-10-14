"""Package distributable mod jars and a complete GPL corresponding-source archive."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'release'
VERSION = json.loads((ROOT / 'config/compatibility.json').read_text(encoding='utf-8'))['mod_version']

def main():
    RELEASE.mkdir(exist_ok=True)
    for mc in ('1.18.2','1.19.2','1.20.1'):
        source = ROOT / f'forge-{mc}/build/libs/taiga-{mc}-forge-{VERSION}.jar'
        assert source.is_file(), 'Build missing: ' + mc
        shutil.copyfile(source, RELEASE / source.name)
    archive = RELEASE / f'taiga-{VERSION}-corresponding-source.zip'
    included = []
    for path in ROOT.rglob('*'):
        if not path.is_file(): continue
        relative = path.relative_to(ROOT)
        if any(part in ('.deps','.gradle','build','run','release','__pycache__','.git','.idea') for part in relative.parts): continue
        included.append(path)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for path in sorted(included): out.write(path, 'taiga_port/' + path.relative_to(ROOT).as_posix())
    shutil.copyfile(ROOT / 'README.md', RELEASE / 'README.md')
    shutil.copyfile(ROOT / 'TRAITS.md', RELEASE / 'TRAITS.md')
    shutil.copyfile(ROOT / 'ARMOR.md', RELEASE / 'ARMOR.md')
    shutil.copyfile(ROOT / 'CONFIGURATION.md', RELEASE / 'CONFIGURATION.md')
    shutil.copyfile(ROOT / 'CHANGELOG.md', RELEASE / 'CHANGELOG.md')
    shutil.copyfile(ROOT / 'config/taiga-traits.toml', RELEASE / 'taiga-traits.toml')
    shutil.copyfile(ROOT / 'LICENSE', RELEASE / 'LICENSE')
    shutil.copyfile(ROOT / 'NOTICE.md', RELEASE / 'NOTICE.md')
    files = sorted([RELEASE / f'taiga-{mc}-forge-{VERSION}.jar' for mc in ('1.18.2','1.19.2','1.20.1')] + [archive,RELEASE/'taiga-traits.toml'])
    hashes = '\n'.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name for p in files) + '\n'
    (RELEASE / 'SHA256SUMS.txt').write_text(hashes, encoding='ascii')
    with zipfile.ZipFile(archive) as source:
        names = source.namelist()
        for version in ('1.18.2','1.19.2','1.20.1'):
            assert f'taiga_port/forge-{version}/gradle/wrapper/gradle-wrapper.jar' in names
            assert f'taiga_port/forge-{version}/build.gradle' in names
        assert not any('/.deps/' in name or '/build/' in name for name in names)
        for path in ('ARMOR.md','config/armor_materials.json','config/armor_traits.json',
                     'tools/armor_resources.py','tools/armor_platform.py','tools/verify_armor.py','tests/ArmorBalanceTest.java'):
            assert 'taiga_port/'+path in names, path
    print('Packaged 3 mod jars and', len(included), 'corresponding source files.')
    print(hashes)

if __name__ == '__main__': main()
