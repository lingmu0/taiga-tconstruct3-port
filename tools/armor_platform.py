"""Generate the few Forge/Tinkers armor API differences at the existing baselines."""
MODIFIER_IMPORTS = '''package com.sosnitzka.taiga;
import net.minecraft.world.item.ArmorItem;
import slimeknights.tconstruct.library.modifiers.Modifier;
import slimeknights.tconstruct.library.modifiers.ModifierEntry;
import slimeknights.tconstruct.library.tools.context.ToolRebuildContext;
import slimeknights.tconstruct.library.tools.nbt.*;
import slimeknights.tconstruct.library.tools.stat.ModifierStatsBuilder;
import slimeknights.tconstruct.library.tools.stat.ToolStats;
import slimeknights.tconstruct.library.tools.SlotType;
'''
LEGACY_MODIFIER = '''public final class ArmorModifier extends Modifier {
  public final ArmorTrait trait;
  public ArmorModifier(ArmorTrait trait) { this.trait = trait; }
  @Override public void addToolStats(ToolRebuildContext context, int level, ModifierStatsBuilder builder) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.REINFORCED)
      ToolStats.DURABILITY.multiply(builder, 1 + 0.1f * ArmorBalance.pieceLevel(level));
  }
  @Override public void addVolatileData(ToolRebuildContext context, int level, ModDataNBT data) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.ARCANE)
      data.addSlots(SlotType.UPGRADE, ArmorBalance.pieceLevel(level));
  }
}
'''
MODERN_MODIFIER = '''import slimeknights.tconstruct.library.modifiers.ModifierHooks;
import slimeknights.tconstruct.library.module.ModuleHookMap;
import slimeknights.tconstruct.library.modifiers.hook.build.ToolStatsModifierHook;
import slimeknights.tconstruct.library.modifiers.hook.build.VolatileDataModifierHook;
public final class ArmorModifier extends Modifier implements ToolStatsModifierHook, VolatileDataModifierHook {
  public final ArmorTrait trait;
  public ArmorModifier(ArmorTrait trait) { this.trait = trait; }
  @Override protected void registerHooks(ModuleHookMap.Builder builder) {
    builder.addHook(this, ModifierHooks.TOOL_STATS, ModifierHooks.VOLATILE_DATA);
  }
  @Override public void addToolStats(IToolContext context, ModifierEntry entry, ModifierStatsBuilder builder) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.REINFORCED)
      ToolStats.DURABILITY.multiply(builder, 1 + 0.1f * ArmorBalance.pieceLevel(entry.getLevel()));
  }
  @Override public void addVolatileData(IToolContext context, ModifierEntry entry, @DATA@ data) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.ARCANE)
      data.addSlots(SlotType.UPGRADE, ArmorBalance.pieceLevel(entry.getLevel()));
  }
}
'''
PLATFORM = '''package com.sosnitzka.taiga;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
public final class ArmorPlatform {
  private ArmorPlatform() {}
  public static void registerConfigEvents(net.minecraftforge.eventbus.api.IEventBus bus) { @CONFIG_EVENTS@ }
  public static void registerEvents() {
    net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(
        (net.minecraftforge.event.entity.living.LivingEvent.@TICK@ event) -> {
          TraitStatRefresh.tick((LivingEntity) event.getEntity());
          ArmorEvents.tick((LivingEntity) event.getEntity());
        });
  }
  public static void registerItems() { @ITEMS@ }
  public static boolean isFire(DamageSource source) { return @FIRE@; }
  public static boolean isProjectile(DamageSource source) { return @PROJECTILE@; }
  public static boolean isFall(DamageSource source) { return @FALL@; }
  public static boolean bypassesProtection(DamageSource source) { return @BYPASS@; }
  public static boolean isMelee(DamageSource source) {
    return source.getEntity() instanceof LivingEntity && source.getDirectEntity() == source.getEntity()
        && !isFire(source) && !isProjectile(source) && !bypassesProtection(source) && !(@EXPLOSION@) && !(@THORNS_TEST@);
  }
  public static DamageSource thorns(LivingEntity wearer) { return @THORNS@; }
}
'''
ITEMS = '''
    for (ArmorCatalog.Material entry : ArmorCatalog.MATERIALS) {
      slimeknights.tconstruct.library.tools.definition.ModifiableArmorMaterial material =
          slimeknights.tconstruct.library.tools.definition.ModifiableArmorMaterial.builder(Taiga.id(entry.name()))
            .set(builder -> builder.noParts()).setSoundEvent(net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_IRON).build();
      for (slimeknights.tconstruct.tools.item.ArmorSlotType slot : slimeknights.tconstruct.tools.item.ArmorSlotType.values()) {
        Taiga.ITEMS.register(entry.name()+"_"+slot.getSerializedName(), () -> new LegacyArmorItem(material, slot, entry.color()));
      }
    }
'''

def generate(mc, path):
    old = mc == '1.18.2'
    modern_damage = mc == '1.20.1'
    modifier = MODIFIER_IMPORTS + (LEGACY_MODIFIER if old else MODERN_MODIFIER.replace('@DATA@', 'ToolDataNBT' if modern_damage else 'ModDataNBT'))
    modifier = modifier.replace('  public final ArmorTrait trait;', '''  @Override public java.util.List<net.minecraft.network.chat.Component> getDescriptionList(int level) {
    return TraitDescriptions.describe("armor."+trait.id.substring("armor_".length()), super.getDescriptionList());
  }
  public final ArmorTrait trait;''')
    modifier = modifier.replace('0.1f * ArmorBalance.pieceLevel', 'TraitTuning.f("armor.reinforced.durabilityBonusPerLevel") * ArmorBalance.pieceLevel')
    modifier = modifier.replace('data.addSlots(SlotType.UPGRADE, ArmorBalance.pieceLevel', 'data.addSlots(SlotType.UPGRADE, TraitTuning.i("armor.arcane.slotsPerLevel") * ArmorBalance.pieceLevel')
    (path / 'ArmorModifier.java').write_text(modifier, encoding='utf-8')
    values = {'TICK':'LivingUpdateEvent' if old else 'LivingTickEvent','ITEMS':ITEMS if old else '',
              'CONFIG_EVENTS':'bus.addListener((net.minecraftforge.fml.event.config.ModConfigEvent.Unloading event) -> { if (event.getConfig().getSpec() == TraitConfig.SPEC) TraitTuning.reset(); });' if modern_damage else '',
              'FIRE':'source.is(net.minecraft.tags.DamageTypeTags.IS_FIRE)' if modern_damage else 'source.isFire()',
              'PROJECTILE':'source.is(net.minecraft.tags.DamageTypeTags.IS_PROJECTILE)' if modern_damage else 'source.isProjectile()',
              'FALL':'source.is(net.minecraft.tags.DamageTypeTags.IS_FALL)' if modern_damage else 'source == DamageSource.FALL',
              'BYPASS':'source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY) || source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_ENCHANTMENTS)' if modern_damage else 'source.isBypassInvul() || source.isBypassMagic()',
              'EXPLOSION':'source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION)' if modern_damage else 'source.isExplosion()',
              'THORNS_TEST':'source.is(net.minecraft.world.damagesource.DamageTypes.THORNS)' if modern_damage else 'source.getMsgId().equals("thorns")',
              'THORNS':'wearer.damageSources().thorns(wearer)' if modern_damage else 'DamageSource.thorns(wearer)'}
    platform = PLATFORM
    for key, value in values.items(): platform = platform.replace('@'+key+'@', value)
    (path / 'ArmorPlatform.java').write_text(platform, encoding='utf-8')
