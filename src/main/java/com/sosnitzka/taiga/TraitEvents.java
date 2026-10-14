package com.sosnitzka.taiga;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingExperienceDropEvent;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import slimeknights.tconstruct.common.TinkerTags;
import slimeknights.tconstruct.library.modifiers.ModifierId;
import slimeknights.tconstruct.library.tools.nbt.ToolStack;
import slimeknights.tconstruct.library.tools.stat.ToolStats;

import java.util.Random;
import static com.sosnitzka.taiga.TraitTuning.f;
import static com.sosnitzka.taiga.TraitTuning.i;

public final class TraitEvents {
  private static final Random RANDOM = new Random();
  private static final String TELEPORT_TIME = "taiga:next_teleport";
  private static ToolStack held(Player player) {
    ItemStack stack = player.getMainHandItem();
    if (!stack.is(TinkerTags.Items.MODIFIABLE)) return null;
    ToolStack tool = ToolStack.from(stack);
    return tool.isBroken() ? null : tool;
  }
  private static int level(ToolStack tool, Trait trait) { return tool.getModifierLevel(new ModifierId(Taiga.ID, trait.id)); }

  @SubscribeEvent public void onDeath(LivingDeathEvent event) {
    if (!(event.getSource().getEntity() instanceof ServerPlayer player)
        || event.getSource().getDirectEntity() != player || !(event.getEntity() instanceof Enemy)) return;
    ToolStack tool = held(player);
    if (tool == null) return;
    int souls = level(tool, Trait.SOULEATER);
    if (souls > 0) {
      int count = tool.getPersistentData().getInt(TraitLogic.SOULS);
      tool.getPersistentData().putInt(TraitLogic.SOULS, count == Integer.MAX_VALUE ? count : count + 1);
      float bonus = tool.getPersistentData().getFloat(TraitLogic.SOUL_DAMAGE);
      float increase = Math.min(f("tools.souleater.gainPerKillCap"), ((LivingEntity) event.getEntity()).getMaxHealth() / f("tools.souleater.healthDivisor"));
      tool.getPersistentData().putFloat(TraitLogic.SOUL_DAMAGE, Math.min(f("tools.souleater.damageCapPerLevel"), bonus + increase));
    }
    int reviving = level(tool, Trait.REVIVING);
    if (reviving > 0) {
      player.heal(f("tools.reviving.healPerLevel") * reviving);
      TraitLogic.repair(tool, Math.max(i("tools.reviving.minimumRepair"), (int)(tool.getStats().getInt(ToolStats.DURABILITY) * f("tools.reviving.repairRatioPerLevel"))) * reviving);
    }
  }

  @SubscribeEvent public void onExperience(LivingExperienceDropEvent event) {
    Player player = event.getAttackingPlayer();
    if (player == null || player.getCommandSenderWorld().isClientSide) return;
    ToolStack tool = held(player);
    if (tool == null) return;
    int xp = event.getDroppedExperience();
    if (level(tool, Trait.DIFFUSE) > 0) xp = Math.round(xp * f("tools.diffuse.experienceMultiplier"));
    if (level(tool, Trait.DISSOLVING) > 0) xp = (int)Math.min(i("tools.dissolving.experienceCap"), (long)xp * RANDOM.nextInt(i("tools.dissolving.maximumMultiplier") + 1));
    event.setDroppedExperience(xp);
  }

  @SubscribeEvent public void onUse(PlayerInteractEvent.RightClickItem event) {
    Player player = (Player) event.getEntity();
    if (!player.isShiftKeyDown() || event.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND) return;
    ToolStack tool = held(player);
    if (tool == null || level(tool, Trait.PORTED) == 0) return;
    // Both sides cancel only the intended activation, keeping regular tool use available.
    event.setCanceled(true);
    event.setCancellationResult(InteractionResult.SUCCESS);
    Level world = player.getCommandSenderWorld();
    if (world.isClientSide || !(player instanceof ServerPlayer serverPlayer)) return;
    long now = world.getGameTime();
    if (now < player.getPersistentData().getLong(TELEPORT_TIME)) return;
    Vec3 direction = player.getLookAngle();
    for (int distance = i("tools.ported.distance"); distance >= 2; distance--) {
      Vec3 point = player.position().add(direction.scale(distance));
      BlockPos pos = new BlockPos((int)Math.floor(point.x), (int)Math.floor(point.y), (int)Math.floor(point.z));
      if (!world.hasChunkAt(pos) || !world.getWorldBorder().isWithinBounds(pos)
          || pos.getY() < world.getMinBuildHeight() || pos.getY() + 2 >= world.getMaxBuildHeight()) continue;
      if (!world.getBlockState(pos.below()).isFaceSturdy(world, pos.below(), net.minecraft.core.Direction.UP)
          || !world.getFluidState(pos).isEmpty() || !world.getFluidState(pos.above()).isEmpty()) continue;
      Vec3 destination = new Vec3(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5);
      if (!world.noCollision(player, player.getBoundingBox().move(destination.subtract(player.position())))) continue;
      serverPlayer.connection.teleport(destination.x, destination.y, destination.z, player.getYRot(), player.getXRot());
      player.fallDistance = 0;
      player.getPersistentData().putLong(TELEPORT_TIME, now + i("tools.ported.cooldownTicks"));
      if (!player.getAbilities().instabuild) tool.setDamage(Math.min(tool.getStats().getInt(ToolStats.DURABILITY), tool.getDamage() + i("tools.ported.durabilityCost")));
      break;
    }
  }

  @SubscribeEvent public void tooltip(ItemTooltipEvent event) {
    ItemStack stack = event.getItemStack();
    if (!stack.is(TinkerTags.Items.MODIFIABLE)) return;
    ToolStack tool = ToolStack.from(stack);
    if (level(tool, Trait.SOULEATER) > 0) {
      event.getToolTip().add(Platform.translate("tooltip.taiga.souls", tool.getPersistentData().getInt(TraitLogic.SOULS),
          String.format(java.util.Locale.ROOT, "%.2f", tool.getPersistentData().getFloat(TraitLogic.SOUL_DAMAGE))));
    }
  }
}
