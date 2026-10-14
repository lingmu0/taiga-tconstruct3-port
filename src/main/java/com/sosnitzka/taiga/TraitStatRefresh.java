package com.sosnitzka.taiga;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import slimeknights.tconstruct.common.TinkerTags;
import slimeknights.tconstruct.library.tools.nbt.ToolStack;

/** Rebuild persisted durability and slots once after a synced config change. */
public final class TraitStatRefresh {
  private static final String KEY = "taiga:trait_config";
  private TraitStatRefresh() {}
  public static void refresh(ItemStack stack, Level world) {
    if (world.isClientSide || stack.isEmpty() || !stack.is(TinkerTags.Items.MODIFIABLE)) return;
    String fingerprint = TraitTuning.fingerprint();
    if (!fingerprint.equals(stack.getOrCreateTag().getString(KEY))) {
      ToolStack.from(stack).rebuildStats();
      stack.getOrCreateTag().putString(KEY,fingerprint);
    }
  }
  public static void tick(LivingEntity entity) {
    Level world = entity.getCommandSenderWorld();
    if (world.isClientSide || entity.tickCount % 20 != 0) return;
    for (ItemStack stack : entity.getAllSlots()) refresh(stack,world);
    if (entity instanceof Player player) for (ItemStack stack : player.getInventory().items) refresh(stack,world);
  }
}
