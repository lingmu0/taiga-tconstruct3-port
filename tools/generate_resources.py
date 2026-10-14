"""Generate complete version-specific datapacks from reviewed, standalone tables."""
from pathlib import Path
from collections import defaultdict
import copy
import json
import armor_resources
import generate_trait_config

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = json.loads((ROOT / 'config/materials.json').read_text())
ALLOYS = json.loads((ROOT / 'config/alloys.json').read_text())
ORES = json.loads((ROOT / 'config/worldgen.json').read_text())
TRAITS = json.loads((ROOT / 'config/traits.json').read_text(encoding='utf-8'))
COMPATIBILITY = json.loads((ROOT / 'config/compatibility.json').read_text(encoding='utf-8'))
ORE_APPEARANCE = json.loads((ROOT / 'config/ore_appearance.json').read_text(encoding='utf-8'))

def ore_result(ore, host):
    prefix = 'deepslate_' if host == 'minecraft:deepslate' and ORE_APPEARANCE.get(ore['name'], {}).get('deepslate') else ''
    return prefix + ore['name'] + '_ore'

def layered_ore_model(host, mineral, old):
    directions = ('down','up','north','south','west','east')
    model = {
        'parent':'minecraft:block/block',
        'textures':{'base':'minecraft:block/'+host, 'overlay':'taiga:block/ore_overlay/'+mineral, 'particle':'minecraft:block/'+host},
        'elements':[
            {'from':[0,0,0], 'to':[16,16,16], 'faces':{face:{'uv':[0,0,16,16],'texture':'#base','cullface':face} for face in directions}},
            {'from':[-0.001,-0.001,-0.001], 'to':[16.001,16.001,16.001], 'faces':{face:{'uv':[0,0,16,16],'texture':'#overlay','cullface':face} for face in directions}}
        ]
    }
    if not old: model['render_type'] = 'minecraft:cutout_mipped'
    return model

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')

def tiers(tier):
    return {'minecraft:stone': 1, 'minecraft:iron': 2, 'minecraft:diamond': 3,
            'minecraft:netherite': 4, 'taiga:duranite': 5, 'taiga:valyrium': 6, 'taiga:vibranium': 7}[tier]

def loot(block):
    return {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'entries': [{'type': 'minecraft:item', 'name': 'taiga:' + block}],
            'conditions': [{'condition': 'minecraft:survives_explosion'}]}]}

def generate(mc):
    root = ROOT / f'src/generated/{mc}'
    old = mc == '1.18.2'
    compatibility = COMPATIBILITY['versions'][mc]
    tconstruct, mantle, forge, pack = (compatibility[key] for key in ('tconstruct','mantle','loader','pack_format'))
    text(root / 'META-INF/mods.toml', f'''modLoader="javafml"
loaderVersion="[{forge},)"
license="GPL-3.0-only"
[[mods]]
modId="taiga"
version="{COMPATIBILITY['mod_version']}"
displayName="TAIGA - Tinkers Alloying Addon (Unofficial Port)"
logoFile="taiga.png"
authors="Zkaface, IdleGandalf / randomtz, TAIGA contributors; unofficial port contributors"
description=''' + "'''" + '''Ores, alloys and adapted material traits for Tinkers' Construct 3. Independent GPLv3 port.''' + "'''" + f'''
[[dependencies.taiga]]
modId="forge"
mandatory=true
versionRange="[{forge},)"
ordering="NONE"
side="BOTH"
[[dependencies.taiga]]
modId="minecraft"
mandatory=true
versionRange="[{mc}]"
ordering="NONE"
side="BOTH"
[[dependencies.taiga]]
modId="mantle"
mandatory=true
versionRange="[{mantle},)"
ordering="AFTER"
side="BOTH"
[[dependencies.taiga]]
modId="tconstruct"
mandatory=true
versionRange="[{tconstruct},{compatibility['tconstruct_max']})"
ordering="AFTER"
side="BOTH"
''')
    write(root / 'pack.mcmeta', {'pack': {'pack_format': pack, 'description': 'TAIGA Forge / Tinkers Construct 3 port'}})
    tags = defaultdict(list)
    names = {lang: json.loads((ROOT / f'config/names_{lang}.json').read_text(encoding='utf-8')) for lang in ('en_us','zh_cn')}
    langs = {lang: {'itemGroup.taiga': 'TAIGA', 'tooltip.taiga.souls': 'Souls: %s | Bonus damage: %s' if lang == 'en_us' else '灵魂：%s | 额外伤害：%s'} for lang in names}
    data = root / 'data/taiga'
    assets = root / 'assets/taiga'
    # Keep tier labels short enough for the book's 81-pixel stat columns.
    for tier_name, tier_level in (('duranite',5),('valyrium',6),('vibranium',7)):
        for lang in langs:
            langs[lang]['stat.tconstruct.harvest_tier.taiga.'+tier_name] = str(tier_level)+('级' if lang == 'zh_cn' else '')
    write(assets / 'mantle/colors.json', {'harvest_tier.taiga':{'duranite':'#527A8B','valyrium':'#A84444','vibranium':'#347D73'}})
    def recipe(path, obj): write(data / f'recipes/{path}.json', obj)
    def model(name, texture): write(assets / f'models/item/{name}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': texture}})
    for material in MATERIALS:
        name, color, temperature = material['name'], material['color'], material['temperature']
        fluid = 'taiga:molten_' + name
        for lang in langs:
            display = names[lang].get(name, name.title())
            langs[lang]['fluid.taiga.molten_' + name] = ('Molten ' + display) if lang == 'en_us' else '熔融' + display
            langs[lang]['fluid_type.taiga.molten_' + name] = langs[lang]['fluid.taiga.molten_' + name]
            langs[lang]['fluid.taiga.flowing_molten_' + name] = langs[lang]['fluid.taiga.molten_' + name]
            langs[lang]['block.taiga.molten_' + name] = langs[lang]['fluid.taiga.molten_' + name]
            langs[lang]['item.taiga.molten_' + name + '_bucket'] = ('Molten ' + display + ' Bucket') if lang == 'en_us' else '熔融' + display + '桶'
            langs[lang]['material.taiga.' + name] = display
        write(data / f'tags/fluids/molten_{name}.json', {'replace': False, 'values': [fluid, 'taiga:flowing_molten_' + name]})
        tags[f'forge/tags/fluids/molten_{name}'].extend([fluid, 'taiga:flowing_molten_' + name])
        write(assets / f'blockstates/molten_{name}.json', {'variants': {'': {'model': 'taiga:block/fluid'}}})
        write(assets / f'models/item/molten_{name}_bucket.json', {'parent': 'forge:item/bucket_drip', 'fluid': fluid, 'loader': 'forge:bucket' if old else 'tconstruct:fluid_container', 'flip_gas': False})
        if name in ('magma','nitronite'): continue
        blocks = [name + '_block'] + ([name + '_ore'] if material['ore'] else [])
        if ORE_APPEARANCE.get(name,{}).get('deepslate'): blocks.append('deepslate_'+name+'_ore')
        if name in ('meteorite','obsidiorite'): blocks.append(name + 'cobble_block')
        for block in blocks:
            ore = block.endswith('_ore')
            deepslate = block.startswith('deepslate_')
            texture_name = block.removeprefix('deepslate_').removesuffix('_block').removesuffix('_ore')
            texture = f'taiga:block/{"ore" if ore else "block"}/{texture_name}'
            assert (ROOT / f'src/main/resources/assets/taiga/textures/{texture.split(":")[1]}.png').is_file(), texture
            write(assets / f'blockstates/{block}.json', {'variants': {'': {'model': 'taiga:block/' + block}}})
            if ore and name in ORE_APPEARANCE:
                host = 'deepslate' if deepslate else ORE_APPEARANCE[name]['host']
                write(assets / f'models/block/{block}.json', layered_ore_model(host, name, old))
            else:
                write(assets / f'models/block/{block}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': texture}})
            write(assets / f'models/item/{block}.json', {'parent': 'taiga:block/' + block})
            table = loot(block)
            if name in ('meteorite','obsidiorite') and block == name + '_block':
                table['pools'][0]['entries'] = [{'type': 'minecraft:alternatives', 'children': [
                    {'type':'minecraft:item','name':'taiga:'+block,'conditions':[{'condition':'minecraft:match_tool','predicate':{'enchantments':[{'enchantment':'minecraft:silk_touch','levels':{'min':1}}]}}]},
                    {'type':'minecraft:item','name':f'taiga:{name}cobble_block'}]}]
            if ore and name in ('tiberium','dilithium'):
                table['pools'][0]['entries'] = [{'type': 'minecraft:alternatives', 'children': [
                    {'type': 'minecraft:item', 'name': 'taiga:' + block,
                     'conditions': [{'condition': 'minecraft:match_tool', 'predicate': {'enchantments': [{'enchantment':'minecraft:silk_touch','levels':{'min':1}}]}}]},
                    {'type': 'minecraft:item', 'name': 'taiga:' + name + '_crystal', 'functions': [
                        {'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':2,'max':4}},
                        {'function':'minecraft:apply_bonus','enchantment':'minecraft:fortune','formula':'minecraft:ore_drops'}]}]}]
            write(data / f'loot_tables/blocks/{block}.json', table)
            tags['minecraft/tags/blocks/mineable/pickaxe'].append('taiga:' + block)
            tier = material['ore_tier'] if ore else (material['tool']['tier'] if material['tool'] else 'minecraft:diamond')
            if name == 'meteorite' and not ore: tier = 'minecraft:netherite'
            if name == 'obsidiorite' and not ore: tier = 'taiga:duranite'
            if tiers(tier) >= 3: tags['minecraft/tags/blocks/needs_diamond_tool'].append('taiga:' + block)
            elif tiers(tier) == 2: tags['minecraft/tags/blocks/needs_iron_tool'].append('taiga:' + block)
            elif tiers(tier) == 1: tags['minecraft/tags/blocks/needs_stone_tool'].append('taiga:' + block)
            if tiers(tier) >= 4: tags['forge/tags/blocks/needs_netherite_tool'].append('taiga:' + block)
            if tier.startswith('taiga:'): tags[f'taiga/tags/blocks/needs_{tier.split(":")[1]}_tool'].append('taiga:' + block)
            if ore:
                tags[f'forge/tags/items/ores/{name}'].append('taiga:' + block)
                tags['forge/tags/items/ores'].append('taiga:' + block)
                tags[f'forge/tags/blocks/ores/{name}'].append('taiga:' + block)
                tags['forge/tags/blocks/ores'].append('taiga:' + block)
                if name in ('vibranium','dilithium'):
                    tags[f'forge/tags/items/ores_in_ground/{"deepslate" if deepslate else "stone"}'].append('taiga:'+block)
                    tags[f'forge/tags/blocks/ores_in_ground/{"deepslate" if deepslate else "stone"}'].append('taiga:'+block)
                if deepslate:
                    recipe('melting/'+block, {'type':'tconstruct:ore_melting','ingredient':{'item':'taiga:'+block},'result':{'fluid':fluid,'amount':180},'temperature':temperature,'time':150,'rate':'metal'})
                    if name != 'dilithium':
                        for kind,cooking in [('smelting',200),('blasting',100)]:
                            recipe(kind+'/'+block, {'type':'minecraft:'+kind,'ingredient':{'item':'taiga:'+block},'result':'taiga:'+name+'_ingot','experience':0.7,'cookingtime':cooking})
            elif 'cobble' not in block:
                tags[f'forge/tags/items/storage_blocks/{name}'].append('taiga:' + block)
                tags['forge/tags/items/storage_blocks'].append('taiga:' + block)
                tags[f'forge/tags/blocks/storage_blocks/{name}'].append('taiga:' + block)
            for lang in langs:
                display = names[lang].get(name, name.title())
                suffix = (' Ore' if ore else ' Cobblestone' if 'cobble' in block else ' Block') if lang == 'en_us' else ('矿石' if ore else '圆石' if 'cobble' in block else '块')
                prefix = ('Deepslate ' if lang == 'en_us' else '深层') if deepslate else ''
                langs[lang]['block.taiga.' + block] = prefix + display + suffix
        for form, amount in [('ingot',90),('nugget',10),('dust',90)]:
            item = name + '_' + form
            texture = f'taiga:item/{form}/{name}'
            assert (ROOT / f'src/main/resources/assets/taiga/textures/item/{form}/{name}.png').is_file(), texture
            model(item, texture)
            tags[f'forge/tags/items/{form}s/{name}'].append('taiga:' + item)
            tags[f'forge/tags/items/{form}s'].append('taiga:' + item)
            recipe(f'melting/{item}', {'type':'tconstruct:melting','ingredient':{'tag':f'forge:{form}s/{name}'},
                'result':{'fluid':fluid,'amount':amount},'temperature':temperature,'time':60 if form != 'nugget' else 20})
            for lang in langs:
                display = names[lang].get(name, name.title())
                langs[lang]['item.taiga.' + item] = display + ((' ' + form.title()) if lang == 'en_us' else {'ingot':'锭','nugget':'粒','dust':'粉'}[form])
        recipe(f'melting/{name}_block', {'type':'tconstruct:melting','ingredient':{'item':f'taiga:{name}_block'},'result':{'fluid':fluid,'amount':810},'temperature':temperature,'time':180})
        if material['ore']:
            recipe(f'melting/{name}_ore', {'type':'tconstruct:ore_melting','ingredient':{'item':f'taiga:{name}_ore'},'result':{'fluid':fluid,'amount':180},'temperature':temperature,'time':120,'rate':'metal'})
        for form, amount, cast, cooling in [('ingot',90,'ingot',60),('nugget',10,'nugget',20),('block',810,None,180)]:
            casting = {'type': 'tconstruct:casting_basin' if cast is None else 'tconstruct:casting_table',
                'fluid': {'fluid':fluid,'amount':amount}, 'result':{'item':f'taiga:{name}_{form}'}, 'cooling_time':cooling}
            if cast: casting['cast'] = {'tag':f'tconstruct:casts/multi_use/{cast}'}
            recipe(f'casting/{name}_{form}', casting)
            if cast:
                casting = copy.deepcopy(casting)
                casting['cast'] = {'tag':f'tconstruct:casts/single_use/{cast}'}
                casting['cast_consumed'] = True
                recipe(f'casting/{name}_{form}_sand', casting)
        # Four distinct IDs prevent the two ingot recipes overwriting each other.
        for legacy in ('block','ingot','nugget'):
            (data / f'recipes/crafting/{name}_{legacy}.json').unlink(missing_ok=True)
        for large, small in [('block','ingot'),('ingot','nugget')]:
            ingredient = {'item':f'taiga:{name}_{small}'}
            recipe(f'crafting/{name}_{large}_from_{small}', {'type':'minecraft:crafting_shaped','pattern':['###','###','###'],'key':{'#':ingredient},'result':{'item':f'taiga:{name}_{large}'}})
            recipe(f'crafting/{name}_{small}_from_{large}', {'type':'minecraft:crafting_shapeless','ingredients':[{'item':f'taiga:{name}_{large}'}],'result':{'item':f'taiga:{name}_{small}','count':9}})
        for smelt_form in ['dust'] + (['ore'] if material['ore'] and name not in ('tiberium','dilithium') else []):
            for kind, cooking in [('smelting',200),('blasting',100)]:
                recipe(f'{kind}/{name}_{smelt_form}', {'type':'minecraft:' + kind,'ingredient':{'item':f'taiga:{name}_{smelt_form}'},'result':f'taiga:{name}_ingot','experience':0.7,'cookingtime':cooking})
        tool = material['tool']
        if tool is None: continue
        mid = 'taiga:' + name
        write(data / f'tinkering/materials/definition/{name}.json', {'craftable':name in ('basalt','tiberium','terrax','eezo','triberium'),'tier':max(2, tiers(tool['tier'])),'sortOrder':10,'hidden':False})
        if old:
            stats = {'tconstruct:head': {'durability':tool['durability'],'miningSpeed':tool['speed'],'attack':tool['attack'],'harvestTier':tool['tier']},
                'tconstruct:handle':{'durability':tool['handle'],'attackSpeed':1.0,'miningSpeed':1.0,'attackDamage':1.0},'tconstruct:extra':{}}
            stats['tconstruct:limb'] = {'durability':tool['durability'],'drawSpeed':round(tool['bow']['draw']-1,3),'velocity':round(tool['bow']['range']-1,3),'accuracy':0.0}
            stats['tconstruct:grip'] = {'durability':tool['handle'],'accuracy':0.0,'meleeAttack':tool['attack']}
        else:
            stats = {'tconstruct:head': {'durability':tool['durability'],'mining_speed':tool['speed'],'melee_attack':tool['attack'],'mining_tier':tool['tier']},
                'tconstruct:handle': {'durability':round(tool['handle'] - 1, 3),'mining_speed':0.0,'melee_speed':0.0,'melee_damage':0.0},'tconstruct:binding':{}}
            stats['tconstruct:limb'] = {'durability':tool['durability'],'draw_speed':round(tool['bow']['draw']-1,3),'velocity':round(tool['bow']['range']-1,3),'accuracy':0.0}
            stats['tconstruct:grip'] = {'durability':round(tool['handle']-1,3),'accuracy':0.0,'melee_damage':tool['attack']}
        armor_resources.add_stats(name, stats, old)
        write(data / f'tinkering/materials/stats/{name}.json', {'stats':stats})
        traits = copy.deepcopy(material['traits'])
        for stat in traits['perStat']:
            traits['perStat'][stat] = traits['default'] + traits['perStat'][stat]
        armor_resources.add_traits(name, traits, old)
        write(data / f'tinkering/materials/traits/{name}.json', traits)
        # All minimum supported TiC versions accept the array palette. Newer
        # 1.20.1 versions additionally accept compact objects, but 3.9.2 does not.
        palette = []
        for grey in [0,63,102,140,178,216,255]:
            c = ''.join(f'{min(255,round(int(color[i:i+2],16) * grey/216)):02X}' for i in (0,2,4))
            palette.append({'grey':grey,'color':'FF' + c})
        supported_key = 'supported_stats' if mc == '1.20.1' else 'supportedStats'
        generator = {'transformer':{'type':'tconstruct:recolor_sprite','color_mapping':{'type':'tconstruct:grey_to_color','palette':palette}},
                     supported_key: list(stats) + ['tconstruct:repair_kit']}
        if not old: generator[supported_key] += ['tconstruct:armor_plating','tconstruct:armor_maille']
        write(assets / f'tinkering/materials/{name}.json', {'color':('' if old else 'FF')+color,'fallbacks':['metal'],'generator':generator})
        for form, value, needed in [('ingot',1,1),('nugget',1,9),('block',9,1)]:
            recipe(f'materials/{name}_{form}', {'type':'tconstruct:material','ingredient':{'item':f'taiga:{name}_{form}'},'material':mid,'value':value,'needed':needed})
        recipe(f'materials/{name}_casting', {'type':'tconstruct:material_fluid','fluid':{'fluid':fluid,'amount':90},'output':mid,'temperature':temperature})
        recipe(f'materials/{name}_melting', {'type':'tconstruct:material_melting','input':mid,'result':{'fluid':fluid,'amount':90},'temperature':temperature})
    for name in ('tiberium','dilithium'):
        crystal = name + '_crystal'
        model(crystal, 'taiga:item/crystal/' + name)
        recipe('melting/' + crystal, {'type':'tconstruct:melting','ingredient':{'item':'taiga:' + crystal},'result':{'fluid':'taiga:molten_'+name,'amount':45},'temperature':500 if name == 'tiberium' else 1500,'time':40})
        for lang in langs: langs[lang]['item.taiga.' + crystal] = names[lang].get(name,name.title()) + (' Crystal' if lang == 'en_us' else '水晶')
    for name, vanilla in [('basalt','basalt'),('magma','magma_block')]:
        recipe('melting/vanilla_' + name, {'type':'tconstruct:melting','ingredient':{'item':'minecraft:' + vanilla},'result':{'fluid':'taiga:molten_'+name,'amount':90 if name == 'basalt' else 180},'temperature':550 if name == 'basalt' else 1000,'time':80})
    for name in ('meteorite','obsidiorite'):
        recipe('melting/' + name + '_cobble', {'type':'tconstruct:melting','ingredient':{'item':f'taiga:{name}cobble_block'},'result':{'fluid':'taiga:molten_'+name,'amount':810},'temperature':950 if name == 'meteorite' else 1050,'time':180})
        recipe('smelting/' + name + '_cobble', {'type':'minecraft:smelting','ingredient':{'item':f'taiga:{name}cobble_block'},'result':f'taiga:{name}_block','experience':0.1,'cookingtime':200})
    for index, alloy in enumerate(ALLOYS):
        # Fixed alloying heat is independent of the fluid's display temperature.
        recipe(f'alloy/{index:02d}_{alloy["result"]["fluid"].split("molten_")[1]}', {'type':'tconstruct:alloy','inputs':alloy['inputs'],'result':alloy['result'],'temperature':1000 if 'nitronite' in alloy['result']['fluid'] else min(1000, max(next((m['temperature'] for m in MATERIALS if 'taiga:molten_'+m['name'] == f['fluid']),800) for f in alloy['inputs']))})
    for name, amount, duration, temperature in [('magma',50,100,1600),('nitronite',100,500,2000),('dilithium',50,100,1700)]:
        recipe('fuel/' + name, {'type':'tconstruct:melting_fuel','fluid':{'fluid':'taiga:molten_'+name,'amount':amount},'duration':duration,'temperature':temperature,'rate':10})
    armor_resources.generate(root, langs, tags, write)
    for key, entries in tags.items(): write(root / ('data/' + key + '.json'), {'replace':False,'values':sorted(set(entries))})
    for lang in langs:
        langs[lang]['tooltip.taiga.configured_trait'] = 'Custom server values (replace the default description):' if lang == 'en_us' else '此词条已调整，当前服务端数值：'
        for entry in json.loads((ROOT / 'config/trait_defaults.json').read_text(encoding='utf-8')):
            label = entry['key'].split('.')[-1] if lang == 'en_us' else entry['comment']
            langs[lang]['config.taiga.'+entry['key']] = label+': %s'
        for trait, values in TRAITS.items():
            langs[lang]['modifier.taiga.'+trait] = values[0 if lang == 'en_us' else 1]
            langs[lang]['modifier.taiga.'+trait+'.description'] = values[2 if lang == 'en_us' else 3]
            langs[lang]['modifier.taiga.'+trait+'.flavor'] = values[0 if lang == 'en_us' else 1]
        write(assets / f'lang/{lang}.json', langs[lang])
    for ore in ORES:
        name = ore['name'] + '_ore'
        targets = [{'target':{'predicate_type':'minecraft:block_match','block':block},'state':{'Name':'taiga:'+ore_result(ore,block)}} for block in ore['targets']]
        write(data / f'worldgen/configured_feature/{name}.json', {'type':'minecraft:ore','config':{'size':ore['size'],'discard_chance_on_air_exposure':0,'targets':targets}})
        write(data / f'worldgen/placed_feature/{name}.json', {'feature':'taiga:'+name,'placement':[
            {'type':'minecraft:count','count':ore['count']},{'type':'minecraft:in_square'},
            {'type':'minecraft:height_range','height':{'type':'minecraft:uniform','min_inclusive':{'absolute':ore['min']},'max_inclusive':{'absolute':ore['max']}}},
            {'type':'minecraft:biome'}]})
    for special, chance in [('meteor',64),('end_deposit',32)]:
        write(data / f'worldgen/configured_feature/{special}.json', {'type':'taiga:'+special,'config':{}})
        write(data / f'worldgen/placed_feature/{special}.json', {'feature':'taiga:'+special,'placement':[
            {'type':'minecraft:rarity_filter','chance':chance},{'type':'minecraft:in_square'},
            {'type':'minecraft:heightmap','heightmap':'WORLD_SURFACE_WG'},{'type':'minecraft:biome'}]})
    if not old:
        for dimension in ('overworld','nether','end'):
            features = ['taiga:'+o['name']+'_ore' for o in ORES if o['dimension'] == dimension]
            features += ['taiga:meteor'] if dimension == 'overworld' else ['taiga:end_deposit'] if dimension == 'end' else []
            write(data / f'forge/biome_modifier/{dimension}_ores.json', {'type':'forge:add_features','biomes':'#minecraft:is_'+dimension,'features':features,'step':'underground_ores'})
    print(mc, 'generated', len(list(root.rglob('*.json'))), 'JSON resources.')

def native_worldgen():
    lines = []
    for ore in ORES:
        targets = ', '.join('OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.' + block.split(':')[1].upper() + '), Taiga.block("'+ore_result(ore,block)+'").defaultBlockState())' for block in ore['targets'])
        lines.append('    add("'+ore['name']+'_ore", "'+ore['dimension']+'", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of('+targets+'), '+str(ore['size'])+')), List.of(CountPlacement.of('+str(ore['count'])+'), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute('+str(ore['min'])+'), VerticalAnchor.absolute('+str(ore['max'])+')), BiomeFilter.biome()));')
    source = '''package com.sosnitzka.taiga;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.data.BuiltinRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.feature.*;
import net.minecraft.world.level.levelgen.feature.configurations.*;
import net.minecraft.world.level.levelgen.placement.*;
import net.minecraft.world.level.levelgen.structure.templatesystem.BlockMatchTest;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.world.BiomeLoadingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
/** 1.18.2 predates Forge biome modifiers. Register builtins and inject through its biome event. */
public final class NativeWorldgen {
  private static final Map<String, List<Holder<PlacedFeature>>> BY_DIMENSION = new HashMap<>();
  public static void register(IEventBus bus) {
    bus.addListener((FMLCommonSetupEvent event) -> event.enqueueWork(NativeWorldgen::bootstrap));
    MinecraftForge.EVENT_BUS.addListener(NativeWorldgen::biome);
  }
  private static void add(String id, String dimension, ConfiguredFeature<?, ?> configured, List<PlacementModifier> placements) {
    Registry.register(BuiltinRegistries.CONFIGURED_FEATURE, Taiga.id(id), configured);
    Holder<ConfiguredFeature<?, ?>> holder = BuiltinRegistries.CONFIGURED_FEATURE.getHolderOrThrow(ResourceKey.create(Registry.CONFIGURED_FEATURE_REGISTRY, Taiga.id(id)));
    PlacedFeature placed = new PlacedFeature(holder, placements);
    Registry.register(BuiltinRegistries.PLACED_FEATURE, Taiga.id(id), placed);
    BY_DIMENSION.computeIfAbsent(dimension, key -> new ArrayList<>()).add(BuiltinRegistries.PLACED_FEATURE.getHolderOrThrow(ResourceKey.create(Registry.PLACED_FEATURE_REGISTRY, Taiga.id(id))));
  }
  private static void bootstrap() {
@ORES@
    add("meteor", "overworld", new ConfiguredFeature<>(Taiga.deposit("meteor"), NoneFeatureConfiguration.INSTANCE), List.of(RarityFilter.onAverageOnceEvery(64), InSquarePlacement.spread(), HeightmapPlacement.onHeightmap(Heightmap.Types.WORLD_SURFACE_WG), BiomeFilter.biome()));
    add("end_deposit", "end", new ConfiguredFeature<>(Taiga.deposit("end_deposit"), NoneFeatureConfiguration.INSTANCE), List.of(RarityFilter.onAverageOnceEvery(32), InSquarePlacement.spread(), HeightmapPlacement.onHeightmap(Heightmap.Types.WORLD_SURFACE_WG), BiomeFilter.biome()));
  }
  private static void biome(BiomeLoadingEvent event) {
    String dimension = event.getCategory() == Biome.BiomeCategory.NETHER ? "nether" : event.getCategory() == Biome.BiomeCategory.THEEND ? "end" : "overworld";
    for (Holder<PlacedFeature> feature : BY_DIMENSION.getOrDefault(dimension, List.of())) event.getGeneration().addFeature(GenerationStep.Decoration.UNDERGROUND_ORES, feature);
  }
}
'''.replace('@ORES@', '\n'.join(lines))
    text(ROOT / 'src/platform/1.18.2/java/com/sosnitzka/taiga/NativeWorldgen.java', source)

def main():
    generate_trait_config.main()
    catalog = '''package com.sosnitzka.taiga;
/** Generated from config/materials.json; original TAIGA values are preserved in that table. */
public final class Catalog {
  public record Material(String name, int color, int temperature, boolean ore, boolean deepslate) {}
  public static final Material[] MATERIALS = {
'''
    catalog += ',\n'.join('    new Material("'+m['name']+'", 0x'+m['color']+', '+str(m['temperature'])+', '+str(m['ore']).lower()+', '+str(bool(ORE_APPEARANCE.get(m['name'],{}).get('deepslate'))).lower()+')' for m in MATERIALS)
    catalog += '\n  };\n  public static Material find(String name) { for (Material material : MATERIALS) if (material.name().equals(name)) return material; throw new IllegalArgumentException(name); }\n  private Catalog() {}\n}\n'
    text(ROOT / 'src/main/java/com/sosnitzka/taiga/Catalog.java', catalog)
    for mc in ('1.18.2','1.19.2','1.20.1'): generate(mc)
    native_worldgen()
    armor_resources.generate_catalog_and_docs(text)
    docs = '# 匠魂 3 特性适配\n\n37 个特性均有实现，保留原版材料与部件的对应关系。数值与以下说明同步生成。\n\n| 特性 | 名称 | 当前效果 |\n|---|---|---|\n'
    docs += '\n'.join('| '+key+' | '+v[1]+' | '+v[3]+' |' for key,v in TRAITS.items())
    docs += '\n\n主要重设计：奥术使用升级槽；噬魂只通过直接近战击杀敌对怪物积累并受上限限制；复苏改为治疗和修复；传送改为潜行右键且检查落点。旋流、共振、解析、碾压等已替换旧事件效果。特性中的近战命中效果要求满蓄力，附加攻击不会再次触发。\n\n挖掘等级 5/6/7 通过 Forge TierSortingRegistry 保留。普罗米修姆矿石降低至下界合金等级，以开放普罗米修姆（5级）→核素（6级）→太阳金属（7级）的正常生存进阶。阿迪特配方输入替换为匠魂 3 的黑色金属 Hepatizon。\n'
    docs += '\n上述为默认数值。port.5 起，全部词条效果数值可修改世界的 `serverconfig/taiga-traits.toml`，无需重新编译。见 [CONFIGURATION.md](CONFIGURATION.md)。\n'
    text(ROOT / 'TRAITS.md', docs)

if __name__ == '__main__': main()
