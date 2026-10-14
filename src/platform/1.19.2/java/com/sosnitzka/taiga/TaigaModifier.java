package com.sosnitzka.taiga;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.core.Direction;
import net.minecraftforge.event.entity.player.PlayerEvent;
import slimeknights.tconstruct.library.modifiers.Modifier;
import slimeknights.tconstruct.library.modifiers.ModifierEntry;
import slimeknights.tconstruct.library.tools.context.*;
import slimeknights.tconstruct.library.tools.nbt.*;
import slimeknights.tconstruct.library.tools.stat.ModifierStatsBuilder;
import slimeknights.tconstruct.library.tools.SlotType;
import java.util.List;
import slimeknights.tconstruct.library.modifiers.ModifierHooks;
import slimeknights.tconstruct.library.module.ModuleHookMap;
import slimeknights.tconstruct.library.modifiers.hook.build.*;
import slimeknights.tconstruct.library.modifiers.hook.combat.*;
import slimeknights.tconstruct.library.modifiers.hook.interaction.InventoryTickModifierHook;
import slimeknights.tconstruct.library.modifiers.hook.mining.*;
import slimeknights.tconstruct.library.modifiers.hook.behavior.*;
public final class TaigaModifier extends Modifier implements ToolStatsModifierHook, VolatileDataModifierHook,
    MeleeDamageModifierHook, MeleeHitModifierHook, InventoryTickModifierHook, BlockBreakModifierHook,
    ProcessLootModifierHook, LootingModifierHook, ToolDamageModifierHook, BreakSpeedModifierHook {
  @Override public List<net.minecraft.network.chat.Component> getDescriptionList(int level) {
    return TraitDescriptions.describe("tools."+trait.id, super.getDescriptionList());
  }
  private final Trait trait;
  public TaigaModifier(Trait trait) { this.trait = trait; }
  @Override protected void registerHooks(ModuleHookMap.Builder builder) {
    builder.addHook(this, ModifierHooks.TOOL_STATS, ModifierHooks.VOLATILE_DATA, ModifierHooks.MELEE_DAMAGE,
        ModifierHooks.MELEE_HIT, ModifierHooks.INVENTORY_TICK, ModifierHooks.BLOCK_BREAK, ModifierHooks.PROCESS_LOOT,
        ModifierHooks.WEAPON_LOOTING, ModifierHooks.TOOL_DAMAGE, ModifierHooks.BREAK_SPEED);
  }
  @Override public void addToolStats(IToolContext context, ModifierEntry entry, ModifierStatsBuilder builder) {
    TraitLogic.stats(trait, entry.getLevel(), builder);
  }
  @Override public void addVolatileData(IToolContext context, ModifierEntry entry, ModDataNBT data) {
    if (trait == Trait.ARCANE) data.addSlots(SlotType.UPGRADE, TraitTuning.i("tools.arcane.slotsPerLevel") * entry.getLevel());
  }
  @Override public float getMeleeDamage(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float base, float damage) {
    return TraitLogic.damage(trait, tool, entry.getLevel(), context, damage);
  }
  @Override public float beforeMeleeHit(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float damage, float base, float knockback) {
    return TraitLogic.knockback(trait, entry.getLevel(), knockback);
  }
  @Override public void afterMeleeHit(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float damage) {
    TraitLogic.hit(trait, tool, entry.getLevel(), context);
  }
  @Override public void onInventoryTick(IToolStackView tool, ModifierEntry entry, Level world, LivingEntity holder, int slot, boolean selected, boolean correct, ItemStack stack) {
    TraitLogic.tick(trait, tool, entry.getLevel(), world, holder, correct);
  }
  @Override public void afterBlockBreak(IToolStackView tool, ModifierEntry entry, ToolHarvestContext context) {
    TraitLogic.broken(trait, tool, entry.getLevel(), context);
  }
  @Override public void processLoot(IToolStackView tool, ModifierEntry entry, List<ItemStack> drops, LootContext context) {
    TraitLogic.loot(trait, entry.getLevel(), drops, context);
  }
  @Override public int updateLooting(IToolStackView tool, ModifierEntry entry, LootingContext context, int looting) {
    return looting + (trait == Trait.SLAUGHTERING ? TraitTuning.i("tools.slaughtering.lootingPerLevel") * entry.getLevel() : 0);
  }
  @Override public int onDamageTool(IToolStackView tool, ModifierEntry entry, int amount, LivingEntity holder) {
    return TraitLogic.durability(trait, entry.getLevel(), amount);
  }
  @Override public void onBreakSpeed(IToolStackView tool, ModifierEntry entry, PlayerEvent.BreakSpeed event, Direction side, boolean effective, float multiplier) {
    event.setNewSpeed(TraitLogic.mining(trait, tool, entry.getLevel(), (net.minecraft.world.entity.player.Player)event.getEntity(), event.getNewSpeed(), effective));
  }
}
