"""Prepare wrappers and a local Maven mirror of pinned upstream dependencies.

Run from anywhere. Downloads are unmodified upstream artifacts, never bundled
inside the mod. No credentials or global Gradle configuration are needed.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
COMPATIBILITY = json.loads((ROOT / 'config/compatibility.json').read_text(encoding='utf-8'))
VERSIONS = {mc: tuple(v[key] for key in ('forge','tconstruct','mantle','forge_gradle','gradle'))
            for mc,v in COMPATIBILITY['versions'].items()}
EXPECTED = {}

BUILD = '''plugins {
    id 'net.minecraftforge.gradle' version '@FG@'
}
group = 'com.sosnitzka.taiga'
version = '@VERSION@'
base { archivesName = 'taiga-@MC@-forge' }
java {
    toolchain.languageVersion = JavaLanguageVersion.of(17)
    withSourcesJar()
}
minecraft {
    mappings channel: 'official', version: '@MC@'
    runs {
        client { workingDirectory project.file('run'); mods { taiga { source sourceSets.main } } }
        server { workingDirectory project.file('run'); args '--nogui'; mods { taiga { source sourceSets.main } } }
    }
}
sourceSets.main {
    java.srcDirs = ['../src/main/java', '../src/platform/@MC@/java']
    resources.srcDirs = ['../src/generated/@MC@', '../src/main/resources']
}
repositories {
    maven { url = uri('../.deps/maven') }
    maven { url = 'https://dvs1.progwml6.com/files/maven/' }
}
dependencies {
    minecraft 'net.minecraftforge:forge:@MC@-@FORGE@'
    implementation fg.deobf('slimeknights.mantle:Mantle:@MC@-@MANTLE@')
    implementation fg.deobf('slimeknights.tconstruct:TConstruct:@MC@-@TC@')
}
tasks.withType(JavaCompile).configureEach { options.encoding = 'UTF-8'; options.release = 17 }
tasks.named('jar', Jar).configure {
    from('../LICENSE'); from('../NOTICE.md')
    manifest { attributes 'Implementation-Version': project.version, 'Implementation-Title': 'TAIGA Unofficial Port' }
    finalizedBy 'reobfJar'
}
tasks.named('sourcesJar', Jar).configure { from('../LICENSE'); from('../NOTICE.md') }
'''

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def download(task):
    artifact, mc, version, suffix = task
    group = 'tconstruct' if artifact == 'TConstruct' else 'mantle'
    relative = f'slimeknights/{group}/{artifact}/{mc}-{version}/{artifact}-{mc}-{version}{suffix}'
    dest = ROOT / '.deps/maven' / relative
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Environment proxies are not required for this public upstream Maven.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request('https://dvs1.progwml6.com/files/maven/' + relative,
                                         headers={'User-Agent': 'python-requests/2.32.3'})
        with opener.open(request, timeout=180) as response:
            content = response.read()
        dest.write_bytes(content)
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    if relative in EXPECTED and EXPECTED[relative] != digest:
        raise ValueError('Dependency checksum mismatch: ' + relative)
    return {'path': relative, 'sha256': digest}

def main():
    lock = ROOT / 'dependencies.lock.json'
    if lock.exists(): EXPECTED.update({entry['path']: entry['sha256'] for entry in json.loads(lock.read_text())})
    tasks = []
    for mc, (forge, tc, mantle, fg, gradle) in VERSIONS.items():
        target = ROOT / f'forge-{mc}'
        template = WORKSPACE / ('demo' if mc == '1.20.1' else 'blood_magic_mechanical/forge-1.18.2')
        for name in ('gradlew', 'gradlew.bat', 'gradle/wrapper/gradle-wrapper.jar'):
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.copyfile(template / name, dest)
        write(target / 'gradle/wrapper/gradle-wrapper.properties',
              'distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\n'
              f'distributionUrl=https\\://services.gradle.org/distributions/gradle-{gradle}-bin.zip\n'
              'networkTimeout=60000\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\n')
        write(target / 'settings.gradle', "pluginManagement { repositories { maven { url = 'https://maven.minecraftforge.net/' }; gradlePluginPortal(); mavenCentral() } }\nrootProject.name = 'taiga-" + mc + "'\n")
        write(target / 'gradle.properties', 'org.gradle.jvmargs=-Xmx3G\norg.gradle.daemon=false\norg.gradle.workers.max=2\n')
        build = BUILD
        for key, val in {'MC': mc, 'FORGE': forge, 'TC': tc, 'MANTLE': mantle, 'FG': fg,
                         'VERSION': COMPATIBILITY['mod_version']}.items():
            build = build.replace('@' + key + '@', val)
        write(target / 'build.gradle', build)
        for artifact, ver in [('TConstruct', tc), ('Mantle', mantle)]:
            for suffix in ('.pom', '.jar', '-sources.jar'):
                tasks.append((artifact, mc, ver, suffix))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        hashes = list(pool.map(download, tasks))
    write(ROOT / 'dependencies.lock.json', json.dumps(hashes, indent=2) + '\n')
    print('Prepared all three build projects and', len(hashes), 'upstream artifacts.')

if __name__ == '__main__':
    main()
