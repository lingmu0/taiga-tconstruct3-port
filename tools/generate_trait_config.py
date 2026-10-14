"""One source of truth for runtime tuning defaults, Forge ranges and TOML templates."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
 'tools.analysing': [('armorDamageRatio',.1,0,10,'护甲值转换为额外伤害的比例'),('damageCapPerLevel',5.,0,1000,'每级额外伤害上限'),('miningXpChancePerLevel',.1,0,1,'每级采矿经验触发概率'),('miningXp',1,0,1000,'触发时额外经验')],
 'tools.arcane':[('slotsPerLevel',1,0,10,'每级增加的升级槽')],
 'tools.berserk':[('damagePerMissingHealth',.4,0,10,'每级在生命完全损失时的伤害倍率增量')],
 'tools.blind':[('chancePerLevel',.15,0,1,'每级致盲概率'),('durationTicks',60,0,72000,'致盲时间（刻）'),('amplifier',0,0,10,'效果等级，0为I')],
 'tools.bright':[('minimumLight',12,0,15,'光明触发最低亮度'),('miningBonusPerLevel',.2,0,10,'每级挖掘速度增量'),('nightVisionTicks',240,0,72000,'夜视时间（刻）')],
 'tools.cascade':[('maximumChain',10,1,1000,'采掘连锁层数上限'),('bonusPerChainLevel',.03,0,10,'每层连锁每级的速度增量'),('resetTicks',60,0,72000,'连锁重置间隔（刻）')],
 'tools.catcher':[('baseTicks',40,0,72000,'缓慢基础时间（刻）'),('ticksPerLevel',20,0,72000,'每级追加时间（刻）'),('amplifier',1,0,10,'缓慢效果等级，0为I')],
 'tools.congenial':[('minimumHealthRatio',.9,0,1,'和谐触发最低生命比例'),('damageBonusPerLevel',.15,0,10,'每级伤害倍率增量')],
 'tools.crushing':[('targetHealthRatio',.8,0,1,'碾压伤害触发最低目标生命比例'),('damageBonusPerLevel',.2,0,10,'每级伤害倍率增量'),('oreChancePerLevel',.1,0,1,'每级原矿增产概率'),('oreChanceCap',.5,0,1,'原矿增产概率上限'),('extraDropsPerLevel',1,0,64,'每级追加原矿数')],
 'tools.cursed':[('chance',.05,0,1,'诅咒触发概率'),('durationTicks',60,0,72000,'虚弱时间（刻）'),('amplifier',0,0,10,'虚弱等级，0为I')],
 'tools.curvature':[('damageBonusPerLevel',.3,0,10,'每级对末影人的伤害倍率增量')],
 'tools.dark':[('maximumLightExclusive',8,0,16,'黑暗触发亮度上限，不含本值'),('miningBonusPerLevel',.2,0,10,'每级挖掘速度增量'),('nightVisionTicks',240,0,72000,'夜视时间（刻）')],
 'tools.decay':[('chancePerLevel',.15,0,1,'每级凋零触发概率'),('durationTicks',60,0,72000,'凋零时间（刻）'),('amplifier',0,0,10,'凋零等级，0为I')],
 'tools.diffuse':[('experienceMultiplier',1.5,0,100,'生物经验倍率'),('dropLossChance',.35,0,1,'每组掉落物消失概率')],
 'tools.dissolving':[('maximumMultiplier',4,0,100,'经验随机整数倍率上限（下限为0）'),('experienceCap',10000,0,1000000,'单次经验上限')],
 'tools.fracture':[('damageBonusPerLevel',.2,0,10,'完全磨损时每级伤害倍率增量'),('miningBonusPerLevel',.25,0,10,'完全磨损时每级挖掘速度增量')],
 'tools.fragile':[('durabilityMultiplierPerLevel',.85,.01,10,'每级耐久乘数'),('damagePerLevel',1.,0,1000,'每级额外伤害'),('extraWearChancePerLevel',.15,0,1,'每级额外磨损概率'),('extraWearChanceCap',.5,0,1,'额外磨损概率上限'),('extraWear',1,0,1000,'额外磨损耐久')],
 'tools.garishly':[('damageBonusPerLevel',.2,0,10,'每级对免疫火焰目标的伤害倍率增量')],
 'tools.glimmer':[('glowBaseTicks',80,0,72000,'发光基础时间（刻）'),('glowTicksPerLevel',20,0,72000,'每级发光追加时间（刻）'),('miningNightVisionTicks',240,0,72000,'采矿夜视时间（刻）')],
 'tools.heroic':[('damageBonusPerLevel',.15,0,10,'每级对敌对生物的伤害倍率增量')],
 'tools.hollow':[('durabilityMultiplierPerLevel',.8,.01,10,'每级耐久乘数'),('attackSpeedBonusPerLevel',.15,0,10,'每级攻速增量')],
 'tools.melting':[('fireBaseSeconds',2,0,3600,'点燃基础时间（秒）'),('fireSecondsPerLevel',1,0,3600,'每级追加点燃时间（秒）'),('smeltingChancePerLevel',.2,0,1,'每级熔炼掉落概率')],
 'tools.mutate':[('chancePerLevel',.2,0,1,'每级突变概率'),('poisonChance',.5,0,1,'触发时选中中毒而非虚弱的概率'),('durationTicks',80,0,72000,'效果时间（刻）'),('amplifier',0,0,10,'效果等级，0为I')],
 'tools.naturebound':[('repairPerLevel',1,0,1000,'每级每次修复耐久'),('intervalTicks',40,1,72000,'修复检查间隔（刻）')],
 'tools.ported':[('distance',10,2,64,'传送最大距离（格）'),('durabilityCost',20,0,10000,'传送耐久消耗'),('cooldownTicks',200,0,72000,'传送冷却（刻）')],
 'tools.pulverizing':[('conversionChance',1.,0,1,'每组掉落转为下一种矿物的概率')],
 'tools.resonance':[('knockbackPerLevel',.15,0,10,'每级击退增量'),('resistanceTicks',40,0,72000,'抗性提升时间（刻）'),('amplifier',0,0,10,'抗性等级，0为I')],
 'tools.reviving':[('healPerLevel',2.,0,1000,'每级击杀恢复生命'),('repairRatioPerLevel',.01,0,1,'每级击杀修复最大耐久比例'),('minimumRepair',1,0,1000,'每级最低修复耐久')],
 'tools.slaughtering':[('lootingPerLevel',1,0,10,'每级额外抢夺等级')],
 'tools.softy':[('damageMultiplierPerLevel',.9,0,10,'每级伤害乘数'),('miningBonusPerLevel',.1,0,10,'每级挖掘速度增量')],
 'tools.souleater':[('damageCapPerLevel',20.,0,1000,'每级永久伤害上限'),('gainPerKillCap',.25,0,1000,'每次击杀伤害成长上限'),('healthDivisor',400.,.01,1000000,'敌人最大生命除以此值作为成长量')],
 'tools.superheavy':[('damagePerLevel',1.5,0,1000,'每级额外伤害'),('attackSpeedMultiplierPerLevel',.85,.01,10,'每级攻速乘数'),('miningPenaltyPerLevel',.1,0,1,'每级采掘速度惩罚'),('miningPenaltyCap',.4,0,1,'采掘速度惩罚上限')],
 'tools.tantrum':[('minimumDamageMultiplier',.85,0,100,'伤害随机倍率下限'),('maximumDamageMultiplier',1.35,0,100,'伤害随机倍率上限，低于下限时按下限处理'),('strengthChance',.15,0,1,'力量触发概率'),('strengthTicks',40,0,72000,'力量时间（刻）'),('amplifier',0,0,10,'力量等级，0为I')],
 'tools.unstable':[('minimumDamageMultiplier',.75,0,100,'伤害随机倍率下限'),('maximumDamageMultiplier',1.25,0,100,'伤害随机倍率上限，低于下限时按下限处理')],
 'tools.whirl':[('knockbackPerLevel',.25,0,10,'每级击退增量'),('speedTicks',40,0,72000,'速度效果时间（刻）'),('amplifier',0,0,10,'速度等级，0为I')],
 'tools.taiga_alien':[('durabilityBonusPerLevel',.1,0,10,'每级耐久倍率增量'),('miningSpeedPerLevel',.5,0,100,'每级额外采掘速度')],
 'tools.taiga_crumbling':[('miningBonusPerLevel',.15,0,10,'每级采掘速度增量')],
 'tool_rules':[('nightVisionCheckTicks',40,1,72000,'光明和黑暗夜视检查间隔（刻）')],
 'armor_rules':[('maximumTotalLevel',4,1,64,'全身穿戴效果的同词条等级上限'),('maximumPieceLevel',2,1,64,'单件坚固、符文槽和光合的等级上限'),('maximumDamageReduction',.3,0,1,'TAIGA盔甲额外减伤合计上限')],
 'armor.bulwark':[('reductionPerLevel',.03,0,1,'每总等级近战减伤')],
 'armor.heat_guard':[('reductionPerLevel',.04,0,1,'每总等级火焰和熔岩减伤')],
 'armor.deflection':[('reductionPerLevel',.04,0,1,'每总等级弹射物减伤')],
 'armor.anchor':[('knockbackPerLevel',.04,0,1,'每总等级击退抗性增量'),('speedPenaltyPerLevel',.01,0,1,'每总等级移动速度惩罚')],
 'armor.lightweight':[('speedBonusPerLevel',.02,0,10,'每总等级移动速度增量')],
 'armor.cushion':[('reductionPerLevel',.06,0,1,'每总等级摔落减伤')],
 'armor.last_stand':[('healthThreshold',.4,0,1,'生命比例低于此值触发'),('reductionPerLevel',.03,0,1,'每总等级减伤')],
 'armor.reactive':[('damagePerLevel',.5,0,1000,'每总等级反伤'),('cooldownTicks',20,0,72000,'反伤共享冷却（刻）')],
 'armor.venom':[('chancePerLevel',.15,0,1,'每总等级中毒触发概率'),('cooldownTicks',80,0,72000,'毒棘共享冷却（刻）'),('durationTicks',60,0,72000,'中毒时间（刻）'),('amplifier',0,0,10,'中毒等级，0为I')],
 'armor.radiant':[('nightVisionTicks',220,0,72000,'夜视时间（刻），每秒刷新')],
 'armor.natural':[('repairPerLevel',1,0,1000,'每级每次修复本件耐久'),('intervalTicks',100,20,72000,'修复间隔（刻），每秒检查，向上取整到检查时机')],
 'armor.renewal':[('healPerLevel',.5,0,1000,'每总等级击杀恢复生命'),('cooldownTicks',100,0,72000,'生息共享冷却（刻）')],
 'armor.aquatic':[('airPerLevelPerSecond',4,0,300,'每总等级每秒补回氧气')],
 'armor.vitality':[('healthPerLevel',1.,0,1000,'每总等级生命上限增量')],
 'armor.reinforced':[('durabilityBonusPerLevel',.1,0,10,'单件每级耐久增量')],
 'armor.volatile':[('maximumReductionPerLevel',.03,0,1,'每总等级随机减伤上限')],
 'armor.arcane':[('slotsPerLevel',1,0,10,'单件每级增加升级槽')],
 'armor.composed':[('healthThreshold',.9,0,1,'生命比例达到此值触发'),('reductionPerLevel',.03,0,1,'每总等级减伤')]
}

def main():
    entries = []
    toml = '# TAIGA runtime trait tuning / 词条运行时配置\n# Copy to defaultconfigs/taiga-traits.toml before creating a world, or edit <world>/serverconfig/taiga-traits.toml.\n# Server config is synchronized to clients. 20 ticks = 1 second; 1 health = half a heart.\n# 工具耐久/槽位等重建属性修改后请重启世界；服务端配置自动同步客户端。\n\n'
    for group, fields in GROUPS.items():
        toml += '['+group+']\n'
        for key, default, minimum, maximum, comment in fields:
            entries.append({'key':group+'.'+key,'default':default,'minimum':minimum,'maximum':maximum,'integer':isinstance(default,int),'comment':comment})
            toml += '# '+comment+' / Range: '+str(minimum)+' ~ '+str(maximum)+'\n'+key+' = '+str(default)+'\n'
        toml += '\n'
    (ROOT / 'config/trait_defaults.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT / 'config/taiga-traits.toml').write_text(toml,encoding='utf-8')
    source = '''package com.sosnitzka.taiga;
/** Generated from tools/generate_trait_config.py; no Minecraft classes needed. */
public final class TraitDefaults {
  public record Entry(String key, double value, double minimum, double maximum, boolean integer, String comment) {}
  public static final Entry[] ENTRIES = {
'''
    source += ',\n'.join('    new Entry('+json.dumps(e['key'])+', '+str(float(e['default']))+', '+str(float(e['minimum']))+', '+str(float(e['maximum']))+', '+str(e['integer']).lower()+', '+json.dumps(e['comment'],ensure_ascii=False)+')' for e in entries)
    source += '\n  };\n  private TraitDefaults() {}\n}\n'
    (ROOT / 'src/main/java/com/sosnitzka/taiga/TraitDefaults.java').write_text(source,encoding='utf-8')
    print('Generated',len(entries),'runtime trait settings and config/taiga-traits.toml.')

if __name__ == '__main__': main()
