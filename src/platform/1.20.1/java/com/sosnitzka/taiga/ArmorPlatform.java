package com.sosnitzka.taiga;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
public final class ArmorPlatform {
  private ArmorPlatform() {}
  public static void registerConfigEvents(net.minecraftforge.eventbus.api.IEventBus bus) { bus.addListener((net.minecraftforge.fml.event.config.ModConfigEvent.Unloading event) -> { if (event.getConfig().getSpec() == TraitConfig.SPEC) TraitTuning.reset(); }); }
  public static void registerEvents() {
    net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(
        (net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent event) -> {
          TraitStatRefresh.tick((LivingEntity) event.getEntity());
          ArmorEvents.tick((LivingEntity) event.getEntity());
        });
  }
  public static void registerItems() {  }
  public static boolean isFire(DamageSource source) { return source.is(net.minecraft.tags.DamageTypeTags.IS_FIRE); }
  public static boolean isProjectile(DamageSource source) { return source.is(net.minecraft.tags.DamageTypeTags.IS_PROJECTILE); }
  public static boolean isFall(DamageSource source) { return source.is(net.minecraft.tags.DamageTypeTags.IS_FALL); }
  public static boolean bypassesProtection(DamageSource source) { return source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY) || source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_ENCHANTMENTS); }
  public static boolean isMelee(DamageSource source) {
    return source.getEntity() instanceof LivingEntity && source.getDirectEntity() == source.getEntity()
        && !isFire(source) && !isProjectile(source) && !bypassesProtection(source) && !(source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION)) && !(source.is(net.minecraft.world.damagesource.DamageTypes.THORNS));
  }
  public static DamageSource thorns(LivingEntity wearer) { return wearer.damageSources().thorns(wearer); }
}
