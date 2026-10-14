package com.sosnitzka.taiga;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.phys.Vec3;
import slimeknights.tconstruct.library.tools.context.ToolAttackContext;
import slimeknights.tconstruct.library.tools.context.ToolHarvestContext;
import slimeknights.tconstruct.library.tools.nbt.IToolStackView;
import slimeknights.tconstruct.library.tools.stat.ModifierStatsBuilder;
import slimeknights.tconstruct.library.tools.stat.ToolStats;

import java.util.List;
import java.util.Random;
import static com.sosnitzka.taiga.TraitTuning.f;
import static com.sosnitzka.taiga.TraitTuning.i;

/** Gameplay shared by all three versions. The platform modifier only adapts hooks. */
public final class TraitLogic {
  private static final Random RANDOM = new Random();
  public static final net.minecraft.resources.ResourceLocation SOULS = Taiga.id("souls");
  public static final net.minecraft.resources.ResourceLocation SOUL_DAMAGE = Taiga.id("soul_damage");
  private static final net.minecraft.resources.ResourceLocation CHAIN = Taiga.id("mining_chain");
  private static final net.minecraft.resources.ResourceLocation LAST_BREAK = Taiga.id("last_break");
  private TraitLogic() {}

  public static void stats(Trait trait, int level, ModifierStatsBuilder builder) {
    switch (trait) {
      case HOLLOW -> {
        ToolStats.DURABILITY.multiply(builder, Math.pow(f("tools.hollow.durabilityMultiplierPerLevel"), level));
        ToolStats.ATTACK_SPEED.multiply(builder, 1 + f("tools.hollow.attackSpeedBonusPerLevel") * level);
      }
      case FRAGILE -> {
        ToolStats.DURABILITY.multiply(builder, Math.pow(f("tools.fragile.durabilityMultiplierPerLevel"), level));
        ToolStats.ATTACK_DAMAGE.add(builder, f("tools.fragile.damagePerLevel") * level);
      }
      case SOFTY -> {
        ToolStats.ATTACK_DAMAGE.multiply(builder, Math.pow(f("tools.softy.damageMultiplierPerLevel"), level));
        ToolStats.MINING_SPEED.multiply(builder, 1 + f("tools.softy.miningBonusPerLevel") * level);
      }
      case SUPERHEAVY -> {
        ToolStats.ATTACK_SPEED.multiply(builder, Math.pow(f("tools.superheavy.attackSpeedMultiplierPerLevel"), level));
        ToolStats.ATTACK_DAMAGE.add(builder, f("tools.superheavy.damagePerLevel") * level);
      }
      case ALIEN -> {
        ToolStats.DURABILITY.multiply(builder, 1 + f("tools.taiga_alien.durabilityBonusPerLevel") * level);
        ToolStats.MINING_SPEED.add(builder, f("tools.taiga_alien.miningSpeedPerLevel") * level);
      }
      default -> {}
    }
  }

  public static float damage(Trait trait, IToolStackView tool, int level, ToolAttackContext context, float damage) {
    LivingEntity attacker = context.getAttacker();
    LivingEntity target = context.getLivingTarget();
    if (target == null) return damage;
    float missing = 1 - attacker.getHealth() / attacker.getMaxHealth();
    return switch (trait) {
      case BERSERK -> damage * (1 + missing * f("tools.berserk.damagePerMissingHealth") * level);
      case HEROIC -> target instanceof Enemy ? damage * (1 + f("tools.heroic.damageBonusPerLevel") * level) : damage;
      case SOULEATER -> damage + Math.min(tool.getPersistentData().getFloat(SOUL_DAMAGE), f("tools.souleater.damageCapPerLevel")) * level;
      case ANALYSING -> damage + Math.min(f("tools.analysing.damageCapPerLevel"), target.getArmorValue() * f("tools.analysing.armorDamageRatio")) * level;
      case CONGENIAL -> attacker.getHealth() >= attacker.getMaxHealth() * f("tools.congenial.minimumHealthRatio") ? damage * (1 + f("tools.congenial.damageBonusPerLevel") * level) : damage;
      case CURVATURE -> target.getType() == net.minecraft.world.entity.EntityType.ENDERMAN ? damage * (1 + f("tools.curvature.damageBonusPerLevel") * level) : damage;
      case GARISHLY -> target.fireImmune() ? damage * (1 + f("tools.garishly.damageBonusPerLevel") * level) : damage;
      case CRUSHING -> target.getHealth() >= target.getMaxHealth() * f("tools.crushing.targetHealthRatio") ? damage * (1 + f("tools.crushing.damageBonusPerLevel") * level) : damage;
      case FRACTURE -> damage * (1 + damageFraction(tool) * f("tools.fracture.damageBonusPerLevel") * level);
      case TANTRUM -> damage * randomMultiplier("tools.tantrum");
      case UNSTABLE -> damage * randomMultiplier("tools.unstable");
      default -> damage;
    };
  }

  public static float knockback(Trait trait, int level, float value) {
    return value + (trait == Trait.WHIRL ? f("tools.whirl.knockbackPerLevel") * level : trait == Trait.RESONANCE ? f("tools.resonance.knockbackPerLevel") * level : 0);
  }

  public static void hit(Trait trait, IToolStackView tool, int level, ToolAttackContext context) {
    LivingEntity target = context.getLivingTarget();
    LivingEntity attacker = context.getAttacker();
    if (target == null || attacker.getCommandSenderWorld().isClientSide || context.isExtraAttack() || !context.isFullyCharged()) return;
    switch (trait) {
      case BLIND -> { if (chance(f("tools.blind.chancePerLevel") * level)) effect(target, MobEffects.BLINDNESS, i("tools.blind.durationTicks"), i("tools.blind.amplifier")); }
      case CATCHER -> effect(target, MobEffects.MOVEMENT_SLOWDOWN, i("tools.catcher.baseTicks") + i("tools.catcher.ticksPerLevel") * level, i("tools.catcher.amplifier"));
      case MELTING -> { if (!target.fireImmune()) target.setSecondsOnFire(i("tools.melting.fireBaseSeconds") + i("tools.melting.fireSecondsPerLevel") * level); }
      case DECAY -> { if (chance(f("tools.decay.chancePerLevel") * level)) effect(target, MobEffects.WITHER, i("tools.decay.durationTicks"), i("tools.decay.amplifier")); }
      case MUTATE -> { if (chance(f("tools.mutate.chancePerLevel") * level)) effect(target, chance(f("tools.mutate.poisonChance")) ? MobEffects.POISON : MobEffects.WEAKNESS, i("tools.mutate.durationTicks"), i("tools.mutate.amplifier")); }
      case CURSED -> { if (chance(f("tools.cursed.chance"))) effect(attacker, MobEffects.WEAKNESS, i("tools.cursed.durationTicks"), i("tools.cursed.amplifier")); }
      case GLIMMER -> effect(target, MobEffects.GLOWING, i("tools.glimmer.glowBaseTicks") + i("tools.glimmer.glowTicksPerLevel") * level, 0);
      case RESONANCE -> effect(attacker, MobEffects.DAMAGE_RESISTANCE, i("tools.resonance.resistanceTicks"), i("tools.resonance.amplifier"));
      case WHIRL -> effect(attacker, MobEffects.MOVEMENT_SPEED, i("tools.whirl.speedTicks"), i("tools.whirl.amplifier"));
      case TANTRUM -> { if (chance(f("tools.tantrum.strengthChance"))) effect(attacker, MobEffects.DAMAGE_BOOST, i("tools.tantrum.strengthTicks"), i("tools.tantrum.amplifier")); }
      default -> {}
    }
  }

  public static float mining(Trait trait, IToolStackView tool, int level, Player player, float speed, boolean effective) {
    if (!effective) return speed;
    int light = player.getCommandSenderWorld().getMaxLocalRawBrightness(player.blockPosition());
    float bonus = switch (trait) {
      case DARK -> light < i("tools.dark.maximumLightExclusive") ? f("tools.dark.miningBonusPerLevel") * level : 0;
      case BRIGHT -> light >= i("tools.bright.minimumLight") ? f("tools.bright.miningBonusPerLevel") * level : 0;
      case FRACTURE -> damageFraction(tool) * f("tools.fracture.miningBonusPerLevel") * level;
      case CASCADE -> {
        long now = player.getCommandSenderWorld().getGameTime();
        int chain = miningChain(tool, now);
        yield Math.min(i("tools.cascade.maximumChain"), chain) * f("tools.cascade.bonusPerChainLevel") * level;
      }
      case CRUMBLING -> f("tools.taiga_crumbling.miningBonusPerLevel") * level;
      case SUPERHEAVY -> -Math.min(f("tools.superheavy.miningPenaltyCap"), f("tools.superheavy.miningPenaltyPerLevel") * level);
      default -> 0;
    };
    return speed * (1 + bonus);
  }

  public static void broken(Trait trait, IToolStackView tool, int level, ToolHarvestContext context) {
    if (!context.isEffective() || !context.canHarvest()) return;
    switch (trait) {
      case CASCADE -> {
        long now = context.getWorld().getGameTime();
        int chain = miningChain(tool, now);
        tool.getPersistentData().putInt(CHAIN, Math.min(i("tools.cascade.maximumChain"), chain + 1));
        tool.getPersistentData().putInt(LAST_BREAK, (int)now);
      }
      case ANALYSING -> { if (chance(f("tools.analysing.miningXpChancePerLevel") * level)) context.getState().getBlock().popExperience(context.getWorld(), context.getPos(), i("tools.analysing.miningXp")); }
      case GLIMMER -> { if (context.getPlayer() != null) effect(context.getPlayer(), MobEffects.NIGHT_VISION, i("tools.glimmer.miningNightVisionTicks"), 0); }
      default -> {}
    }
  }

  public static void tick(Trait trait, IToolStackView tool, int level, Level world, LivingEntity holder, boolean held) {
    if (world.isClientSide || !held) return;
    int interval = trait == Trait.NATUREBOUND ? i("tools.naturebound.intervalTicks") : i("tool_rules.nightVisionCheckTicks");
    if (holder.tickCount % interval != 0) return;
    switch (trait) {
      case NATUREBOUND -> {
        BlockPos below = holder.blockPosition().below();
        if (world.getBlockState(below).is(BlockTags.DIRT) || world.getBlockState(below).is(BlockTags.LOGS)) repair(tool, i("tools.naturebound.repairPerLevel") * level);
      }
      case BRIGHT -> { if (!tool.isBroken() && world.getMaxLocalRawBrightness(holder.blockPosition()) >= i("tools.bright.minimumLight")) effect(holder, MobEffects.NIGHT_VISION, i("tools.bright.nightVisionTicks"), 0); }
      case DARK -> { if (!tool.isBroken() && world.getMaxLocalRawBrightness(holder.blockPosition()) < i("tools.dark.maximumLightExclusive")) effect(holder, MobEffects.NIGHT_VISION, i("tools.dark.nightVisionTicks"), 0); }
      default -> {}
    }
  }

  public static int durability(Trait trait, int level, int amount) {
    if (trait == Trait.FRAGILE && chance(Math.min(f("tools.fragile.extraWearChanceCap"), f("tools.fragile.extraWearChancePerLevel") * level))) return amount + i("tools.fragile.extraWear");
    return amount;
  }

  public static void loot(Trait trait, int level, List<ItemStack> drops, LootContext context) {
    if (trait == Trait.DIFFUSE) {
      drops.removeIf(stack -> chance(f("tools.diffuse.dropLossChance")));
      return;
    }
    for (int i = 0; i < drops.size(); i++) {
      ItemStack stack = drops.get(i);
      if (trait == Trait.MELTING && chance(f("tools.melting.smeltingChancePerLevel") * level)) {
        ItemStack result = Platform.smelt(stack, context.getLevel());
        if (!result.isEmpty()) drops.set(i, result);
      } else if (trait == Trait.PULVERIZING && chance(f("tools.pulverizing.conversionChance"))) {
        if (stack.is(Items.COBBLESTONE) || stack.is(Items.COBBLED_DEEPSLATE)) drops.set(i, new ItemStack(Items.GRAVEL, stack.getCount()));
        else if (stack.is(Items.GRAVEL)) drops.set(i, new ItemStack(Items.SAND, stack.getCount()));
      } else if (trait == Trait.CRUSHING && stack.is(ItemTags.create(new net.minecraft.resources.ResourceLocation("forge", "raw_materials"))) && chance(Math.min(f("tools.crushing.oreChanceCap"), f("tools.crushing.oreChancePerLevel") * level))) {
        stack.grow(Math.min(i("tools.crushing.extraDropsPerLevel") * level, stack.getMaxStackSize() - stack.getCount()));
      }
    }
  }

  public static void repair(IToolStackView tool, int amount) {
    if (amount > 0 && tool.getDamage() > 0) tool.setDamage(Math.max(0, tool.getDamage() - amount));
  }
  private static float damageFraction(IToolStackView tool) {
    return Math.min(1, (float) tool.getDamage() / Math.max(1, tool.getStats().getInt(ToolStats.DURABILITY)));
  }
  private static int miningChain(IToolStackView tool, long now) {
    // Signed subtraction also handles the 32-bit tick counter wrapping.
    int elapsed = (int)now - tool.getPersistentData().getInt(LAST_BREAK);
    return elapsed >= 0 && elapsed <= i("tools.cascade.resetTicks") ? tool.getPersistentData().getInt(CHAIN) : 0;
  }
  private static float randomMultiplier(String group) {
    float minimum = f(group+".minimumDamageMultiplier");
    return minimum + RANDOM.nextFloat() * Math.max(0, f(group+".maximumDamageMultiplier") - minimum);
  }
  private static boolean chance(float value) { return RANDOM.nextFloat() < Math.max(0, Math.min(1, value)); }
  private static void effect(LivingEntity entity, MobEffect effect, int duration, int amplifier) {
    if (duration > 0) entity.addEffect(new MobEffectInstance(effect, duration, amplifier, false, false, true));
  }
}
