package com.sosnitzka.taiga;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEquipmentChangeEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import slimeknights.tconstruct.common.TinkerTags;
import slimeknights.tconstruct.library.modifiers.ModifierEntry;
import slimeknights.tconstruct.library.tools.helper.ToolDamageUtil;
import slimeknights.tconstruct.library.tools.nbt.ToolStack;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import static com.sosnitzka.taiga.TraitTuning.f;
import static com.sosnitzka.taiga.TraitTuning.i;

/** Server-authoritative armor effects. Only intact armor in its proper slot counts. */
public final class ArmorEvents {
  private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
  private static final UUID SPEED = UUID.fromString("86a4d7da-fd1e-4f33-a0e9-5a88faf8f8c4");
  private static final UUID ANCHOR = UUID.fromString("5d671828-c708-4b7a-94c8-f9a536ba4b81");
  private static final UUID HEALTH = UUID.fromString("d89a8d83-e2ba-40c6-9cf2-c33d1deaa9f1");
  private static final ThreadLocal<Boolean> REFLECTING = ThreadLocal.withInitial(() -> false);

  private record Worn(ToolStack tool, int natural) {}
  private record Loadout(int[] levels, List<Worn> worn) {
    int level(ArmorTrait trait) { return ArmorBalance.level(levels[trait.ordinal()]); }
  }

  private static Loadout collect(LivingEntity wearer) {
    int[] levels = new int[ArmorTrait.values().length];
    List<Worn> worn = new ArrayList<>();
    for (EquipmentSlot slot : SLOTS) {
      ItemStack stack = wearer.getItemBySlot(slot);
      if (!(stack.getItem() instanceof ArmorItem) || Mob.getEquipmentSlotForItem(stack) != slot
          || !stack.is(TinkerTags.Items.MODIFIABLE)) continue;
      TraitStatRefresh.refresh(stack,wearer.getCommandSenderWorld());
      ToolStack tool = ToolStack.from(stack);
      if (tool.isBroken()) continue;
      int natural = 0;
      for (ModifierEntry entry : tool.getModifierList()) {
        if (entry.getModifier() instanceof ArmorModifier modifier) {
          int level = ArmorBalance.level(entry.getLevel());
          levels[modifier.trait.ordinal()] += level;
          if (modifier.trait == ArmorTrait.NATURAL) natural += level;
        }
      }
      if (natural > 0) worn.add(new Worn(tool, ArmorBalance.pieceLevel(natural)));
    }
    return new Loadout(levels, worn);
  }

  private static void attribute(LivingEntity wearer, Attribute attribute, UUID id, double amount, AttributeModifier.Operation operation) {
    AttributeInstance instance = wearer.getAttribute(attribute);
    if (instance == null) return;
    AttributeModifier previous = instance.getModifier(id);
    if (previous != null && previous.getAmount() == amount && previous.getOperation() == operation) return;
    if (previous != null) instance.removeModifier(id);
    if (amount != 0) instance.addTransientModifier(new AttributeModifier(id, "TAIGA worn armor", amount, operation));
  }

  private static void attributes(LivingEntity wearer, Loadout loadout) {
    attribute(wearer, Attributes.MOVEMENT_SPEED, SPEED,
        ArmorBalance.speed(loadout.level(ArmorTrait.LIGHTWEIGHT), loadout.level(ArmorTrait.ANCHOR)), AttributeModifier.Operation.MULTIPLY_BASE);
    attribute(wearer, Attributes.KNOCKBACK_RESISTANCE, ANCHOR,
        ArmorBalance.knockback(loadout.level(ArmorTrait.ANCHOR)), AttributeModifier.Operation.ADDITION);
    attribute(wearer, Attributes.MAX_HEALTH, HEALTH,
        ArmorBalance.health(loadout.level(ArmorTrait.VITALITY)), AttributeModifier.Operation.ADDITION);
    if (wearer.getHealth() > wearer.getMaxHealth()) wearer.setHealth(wearer.getMaxHealth());
  }

  @SubscribeEvent public void equipment(LivingEquipmentChangeEvent event) {
    LivingEntity wearer = (LivingEntity) event.getEntity();
    if (!wearer.getCommandSenderWorld().isClientSide) attributes(wearer, collect(wearer));
  }

  /** Called by the small platform adapter because Forge renamed LivingUpdateEvent. */
  public static void tick(LivingEntity wearer) {
    Level world = wearer.getCommandSenderWorld();
    if (world.isClientSide || !wearer.isAlive() || wearer.tickCount % 20 != 0) return;
    Loadout loadout = collect(wearer);
    // Re-evaluate broken armor and datapack/NBT changes, without accumulating attributes.
    attributes(wearer, loadout);
    if (loadout.level(ArmorTrait.RADIANT) > 0 && i("armor.radiant.nightVisionTicks") > 0)
      wearer.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, i("armor.radiant.nightVisionTicks"), 0, true, false));
    int aquatic = loadout.level(ArmorTrait.AQUATIC);
    if (aquatic > 0 && wearer.isUnderWater())
      wearer.setAirSupply(Math.min(wearer.getMaxAirSupply(), wearer.getAirSupply() + i("armor.aquatic.airPerLevelPerSecond") * aquatic));
    if (!loadout.worn().isEmpty() && ready(wearer, "natural") && world.dimensionType().hasSkyLight() && world.isDay() && !world.isRainingAt(wearer.blockPosition())
        && world.canSeeSky(wearer.blockPosition().above())) {
      cooldown(wearer, "natural", i("armor.natural.intervalTicks"));
      for (Worn piece : loadout.worn()) ToolDamageUtil.repair(piece.tool(), i("armor.natural.repairPerLevel") * piece.natural());
    }
  }

  private static boolean ready(LivingEntity wearer, String key) {
    return wearer.getCommandSenderWorld().getGameTime() >= wearer.getPersistentData().getLong("taiga:armor_" + key);
  }
  private static void cooldown(LivingEntity wearer, String key, int ticks) {
    wearer.getPersistentData().putLong("taiga:armor_" + key, wearer.getCommandSenderWorld().getGameTime() + ticks);
  }

  @SubscribeEvent(priority = EventPriority.LOWEST)
  public void damage(LivingDamageEvent event) {
    LivingEntity wearer = (LivingEntity) event.getEntity();
    DamageSource source = event.getSource();
    if (wearer.getCommandSenderWorld().isClientSide || event.getAmount() <= 0 || ArmorPlatform.bypassesProtection(source)) return;
    Loadout loadout = collect(wearer);
    attributes(wearer, loadout);
    boolean melee = ArmorPlatform.isMelee(source);
    float random = loadout.level(ArmorTrait.VOLATILE) > 0 ? wearer.getRandom().nextFloat() : 0;
    float reduction = ArmorBalance.reduction(loadout.levels(), melee, ArmorPlatform.isFire(source),
        ArmorPlatform.isProjectile(source), ArmorPlatform.isFall(source), wearer.getHealth() / wearer.getMaxHealth(), random);
    event.setAmount(event.getAmount() * (1 - reduction));
    if (!melee || REFLECTING.get() || !(source.getEntity() instanceof LivingEntity attacker) || attacker == wearer) return;
    int reactive = loadout.level(ArmorTrait.REACTIVE);
    if (reactive > 0 && ready(wearer, "reactive")) {
      cooldown(wearer, "reactive", i("armor.reactive.cooldownTicks"));
      REFLECTING.set(true);
      try { attacker.hurt(ArmorPlatform.thorns(wearer), f("armor.reactive.damagePerLevel") * reactive); }
      finally { REFLECTING.set(false); }
    }
    int venom = loadout.level(ArmorTrait.VENOM);
    if (venom > 0 && i("armor.venom.durationTicks") > 0 && ready(wearer, "venom") && wearer.getRandom().nextFloat() < Math.min(1, f("armor.venom.chancePerLevel") * venom)) {
      cooldown(wearer, "venom", i("armor.venom.cooldownTicks"));
      attacker.addEffect(new MobEffectInstance(MobEffects.POISON, i("armor.venom.durationTicks"), i("armor.venom.amplifier")));
    }
  }

  @SubscribeEvent(priority = EventPriority.LOWEST)
  public void kill(LivingDeathEvent event) {
    if (REFLECTING.get() || !(event.getEntity() instanceof Enemy) || !ArmorPlatform.isMelee(event.getSource())
        || !(event.getSource().getEntity() instanceof LivingEntity killer) || !killer.isAlive()
        || killer.getCommandSenderWorld().isClientSide || killer.getHealth() >= killer.getMaxHealth()) return;
    int level = collect(killer).level(ArmorTrait.RENEWAL);
    if (level > 0 && ready(killer, "renewal")) {
      cooldown(killer, "renewal", i("armor.renewal.cooldownTicks"));
      killer.heal(f("armor.renewal.healPerLevel") * level);
    }
  }
}
