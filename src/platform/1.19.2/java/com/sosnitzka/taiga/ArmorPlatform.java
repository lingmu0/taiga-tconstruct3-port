package com.sosnitzka.taiga;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
public final class ArmorPlatform {
  private ArmorPlatform() {}
  public static void registerConfigEvents(net.minecraftforge.eventbus.api.IEventBus bus) {  }
  public static void registerEvents() {
    net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(
        (net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent event) -> {
          TraitStatRefresh.tick((LivingEntity) event.getEntity());
          ArmorEvents.tick((LivingEntity) event.getEntity());
        });
  }
  public static void registerItems() {  }
  public static boolean isFire(DamageSource source) { return source.isFire(); }
  public static boolean isProjectile(DamageSource source) { return source.isProjectile(); }
  public static boolean isFall(DamageSource source) { return source == DamageSource.FALL; }
  public static boolean bypassesProtection(DamageSource source) { return source.isBypassInvul() || source.isBypassMagic(); }
  public static boolean isMelee(DamageSource source) {
    return source.getEntity() instanceof LivingEntity && source.getDirectEntity() == source.getEntity()
        && !isFire(source) && !isProjectile(source) && !bypassesProtection(source) && !(source.isExplosion()) && !(source.getMsgId().equals("thorns"));
  }
  public static DamageSource thorns(LivingEntity wearer) { return DamageSource.thorns(wearer); }
}
