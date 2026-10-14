"""Armor material integration and the fixed-material 1.18.2 compatibility sets."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = json.loads((ROOT / 'config/armor_materials.json').read_text(encoding='utf-8'))
TRAITS = json.loads((ROOT / 'config/armor_traits.json').read_text(encoding='utf-8'))
SLOTS = ('helmet','chestplate','leggings','boots')
FACTORS = (11,16,15,13)
TAGS = ('helmets','chestplate','leggings','boots')
PATTERNS = (['mmm','ccc'],['m m','mmm','cmc'],['mmm','m m','c c'],['m m','m m'])

def modifier(trait): return {'name':'taiga:armor_'+trait, 'level':1}

def add_stats(name, stats, old):
    if old: return
    armor = MATERIALS[name]
    for index, slot in enumerate(SLOTS):
        stats['tconstruct:plating_'+slot] = {
            'durability':armor['durability_factor']*FACTORS[index],
            'armor':armor['armor'][index], 'toughness':armor['toughness'],
            'knockback_resistance':armor['knockback_resistance']}
    stats['tconstruct:maille'] = {}

def add_traits(name, traits, old):
    if old: return
    armor = MATERIALS[name]
    # Explicit armor overrides prevent weapon traits leaking onto worn pieces.
    traits['perStat']['tconstruct:armor'] = [modifier(armor['plating'])]
    traits['perStat']['tconstruct:maille'] = [modifier(armor['maille'])]

def generate(root, langs, tags, write):
    for language, lang in langs.items():
        offset = 0 if language == 'en_us' else 1
        for trait, values in TRAITS.items():
            key = 'modifier.taiga.armor_'+trait
            lang[key] = values[offset]
            lang[key+'.description'] = values[offset+2]
            lang[key+'.flavor'] = values[offset]
    if root.name != '1.18.2': return
    for name, armor in MATERIALS.items():
        repair_items = []
        for index, slot in enumerate(SLOTS):
            item = name+'_'+slot
            repair_items.append({'item':'taiga:'+item})
            # Vanilla art is referenced and tinted by the legacy client adapter.
            write(root / f'assets/taiga/models/item/{item}.json', {
                'parent':'minecraft:item/generated', 'textures':{'layer0':'minecraft:item/iron_'+slot}})
            for language, lang in langs.items():
                material_name = lang['material.taiga.'+name]
                suffix = (' Helmet',' Chestplate',' Leggings',' Boots')[index] if language == 'en_us' else ('头盔','胸甲','护腿','靴子')[index]
                lang['item.taiga.'+item] = material_name+suffix
            write(root / f'data/taiga/tinkering/tool_definitions/{item}.json', {
                'stats':{'base':{
                    'tconstruct:durability':armor['durability_factor']*FACTORS[index],
                    'tconstruct:armor':armor['armor'][index],
                    'tconstruct:armor_toughness':armor['toughness'],
                    'tconstruct:knockback_resistance':armor['knockback_resistance']},
                    'multipliers':{'tconstruct:attack_damage':0.4}},
                'slots':{'upgrades':2,'defense':3,'abilities':1},
                'traits':[modifier(armor['plating']),modifier(armor['maille'])]})
            key = {'m':{'item':'taiga:'+name+'_ingot'}}
            if index != 3: key['c'] = {'item':'minecraft:chain'}
            write(root / f'data/taiga/recipes/armor/building/{item}.json', {
                'type':'minecraft:crafting_shaped','pattern':PATTERNS[index],
                'key':key,'result':{'item':'taiga:'+item}})
            tags['tconstruct/tags/items/modifiable/armor/'+TAGS[index]].append('taiga:'+item)
            tags['tconstruct/tags/items/modifiable/durability'].append('taiga:'+item)
            tags['forge/tags/items/armors'].append('taiga:'+item)
            tags['forge/tags/items/armors/'+('chestplates' if index == 1 else TAGS[index])].append('taiga:'+item)
        for kind, serializer in (('station','specialized_station_repair'),('repair_kit','specialized_repair_kit')):
            write(root / f'data/taiga/recipes/armor/repair/{name}_{kind}.json', {
                'type':'tconstruct:'+serializer,'tool':repair_items,'repair_material':'taiga:'+name})
        recipes = ['taiga:armor/building/'+name+'_'+slot for slot in SLOTS]
        write(root / f'data/taiga/advancements/recipes/armor/{name}.json', {
            'parent':'minecraft:recipes/root',
            'criteria':{'has_material':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':['taiga:'+name+'_ingot']}]}},
                        'has_recipe':{'trigger':'minecraft:recipe_unlocked','conditions':{'recipe':recipes[0]}}},
            'requirements':[['has_material','has_recipe']], 'rewards':{'recipes':recipes}})

def generate_catalog_and_docs(write_text):
    names = json.loads((ROOT / 'config/names_zh_cn.json').read_text(encoding='utf-8'))
    originals = json.loads((ROOT / 'config/materials.json').read_text(encoding='utf-8'))
    colors = {m['name']:m['color'] for m in originals}
    assert set(MATERIALS) == {m['name'] for m in originals if m['tool']}
    source = 'package com.sosnitzka.taiga;\n/** Generated from config/armor_materials.json. */\npublic final class ArmorCatalog {\n'
    source += '  public record Material(String name, int color) {}\n  public static final Material[] MATERIALS = {\n'
    source += ',\n'.join('    new Material("'+name+'", 0x'+colors[name]+')' for name in MATERIALS)
    source += '\n  };\n  private ArmorCatalog() {}\n}\n'
    write_text(ROOT / 'src/main/java/com/sosnitzka/taiga/ArmorCatalog.java', source)
    docs = '''# TAIGA 盔甲材料与词条（port.4）

30 种现有匠魂材料拥有盔甲设计。配方辅助材料与仅流体材料不额外变成盔甲材料。

## 制作与版本差异

- **1.19.2／1.20.1**：在匠魂原有流程中制作对应材质的头盔板、胸甲板、护腿板、靴子板及锁甲，再组装板甲；盔甲板和锁甲可以混搭，分别贡献下表中的词条。部件的浇铸、组装、替换和修复沿用匠魂原生配方。材料数据和词条会显示在匠魂的盔甲材料书页中。
- **1.18.2**：当前最低匠魂没有材料化盔甲板系统，因此提供 30 套、共 120 件固定材质的匠魂可强化盔甲，使用对应材料锭和锁链在工作台制作。头盔消耗 3 锭、3 锁链，胸甲消耗 6 锭、2 锁链，护腿消耗 5 锭、2 锁链，靴子消耗 4 锭。每件同时获得该材料的板材及锁甲词条，初始为 2 升级槽、3 防御槽和 1 能力槽；在工匠站使用同材质修复材料或修复工具包修复。固定材质套装不支持更换板材或锁甲。图标及穿戴外观引用铁甲纹理并按材料染色。

保留 port.3 的最低 Forge、匠魂和 Mantle 要求，不增加盔甲附属前置。安装后原有工具属性与词条不变。

## 数值

数值顺序均为 **头盔／胸甲／护腿／靴子**。耐久列为部件基础值，尚未计算坚固词条或其他强化。韧性与击退抗性按单件列出；整套相加。防御基础总和最多 16，为匠魂的钻石等强化留出空间。

| 材料 | 基础耐久（头／胸／腿／靴） | 防御（头／胸／腿／靴） | 单件韧性 | 单件击退抗性 | 盔甲板词条 | 锁甲词条 |
|---|---|---|---|---|---|---|
'''
    for name, armor in MATERIALS.items():
        docs += '| '+names[name]+' | '+'／'.join(str(armor['durability_factor']*factor) for factor in FACTORS)+' | '+'／'.join(map(str,armor['armor']))+' | '+str(armor['toughness'])+' | '+f'{armor["knockback_resistance"]:.0%}'+' | '+TRAITS[armor['plating']][1]+' | '+TRAITS[armor['maille']][1]+' |\n'
    docs += '''
## 词条规则

只有穿在对应装备栏、尚未损坏的匠魂盔甲才计入穿戴效果，手持和背包中的盔甲不计入。穿戴效果按四个部位累加，同一词条最多计 4 级；坚固、符文槽按单件最多计 2 级，光合按单件修复，辉光不叠加。不同 TAIGA 减伤词条相加后最多额外降低 30% 的护甲结算后伤害；绕过无敌或魔法保护的伤害不受这些减伤影响。反伤使用共享冷却和重入保护，不能循环反伤，也不会触发生息。

生命、速度和击退抗性使用可移除的临时属性；脱下后移除，增加生命上限不会直接补满生命。损坏或数据变更最迟在下一次每秒检查时同步这些属性。

| 词条 | 效果 |
|---|---|
'''
    for values in TRAITS.values(): docs += '| '+values[1]+' | '+values[3]+' |\n'
    docs += '''
上表为默认设计。port.5 起，词条效果数值可直接修改世界的 `serverconfig/taiga-traits.toml`，无需重新编译，详见 [CONFIGURATION.md](CONFIGURATION.md)。材料基础属性和词条绑定的配置源为 `config/armor_materials.json` 与 `config/armor_traits.json`，仍可通过生成资源或数据包调整。

接口参考：[匠魂材料属性](https://slimeknights.github.io/docs/json/stat-types/)、[匠魂盔甲模型](https://slimeknights.github.io/docs/json/armor-models/)。实际实现针对三个版本记录的最低依赖源码与 JAR 校验。
'''
    write_text(ROOT / 'ARMOR.md', docs)
