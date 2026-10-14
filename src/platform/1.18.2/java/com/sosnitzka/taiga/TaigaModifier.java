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
public final class TaigaModifier extends Modifier {
  @Override public List<net.minecraft.network.chat.Component> getDescriptionList(int level) {
    return TraitDescriptions.describe("tools."+trait.id, super.getDescriptionList());
  }
  private final Trait trait;
  public TaigaModifier(Trait trait) { this.trait = trait; }
  @Override public void addToolStats(ToolRebuildContext context, int level, ModifierStatsBuilder builder) { TraitLogic.stats(trait, level, builder); }
  @Override public void addVolatileData(ToolRebuildContext context, int level, ModDataNBT data) {
    if (trait == Trait.ARCANE) data.addSlots(SlotType.UPGRADE, TraitTuning.i("tools.arcane.slotsPerLevel") * level);
  }
  @Override public float getEntityDamage(IToolStackView tool, int level, ToolAttackContext context, float base, float damage) { return TraitLogic.damage(trait, tool, level, context, damage); }
  @Override public float beforeEntityHit(IToolStackView tool, int level, ToolAttackContext context, float damage, float base, float knockback) { return TraitLogic.knockback(trait, level, knockback); }
  @Override public int afterEntityHit(IToolStackView tool, int level, ToolAttackContext context, float damage) { TraitLogic.hit(trait, tool, level, context); return 0; }
  @Override public void onInventoryTick(IToolStackView tool, int level, Level world, LivingEntity holder, int slot, boolean selected, boolean correct, ItemStack stack) { TraitLogic.tick(trait, tool, level, world, holder, correct); }
  @Override public void afterBlockBreak(IToolStackView tool, int level, ToolHarvestContext context) { TraitLogic.broken(trait, tool, level, context); }
  @Override public List<ItemStack> processLoot(IToolStackView tool, int level, List<ItemStack> drops, LootContext context) { TraitLogic.loot(trait, level, drops, context); return drops; }
  @Override public int getLootingValue(IToolStackView tool, int level, LivingEntity holder, Entity target, DamageSource source, int looting) { return looting + (trait == Trait.SLAUGHTERING ? TraitTuning.i("tools.slaughtering.lootingPerLevel") * level : 0); }
  @Override public int onDamageTool(IToolStackView tool, int level, int amount, LivingEntity holder) { return TraitLogic.durability(trait, level, amount); }
  @Override public void onBreakSpeed(IToolStackView tool, int level, PlayerEvent.BreakSpeed event, Direction side, boolean effective, float multiplier) {
    event.setNewSpeed(TraitLogic.mining(trait, tool, level, event.getPlayer(), event.getNewSpeed(), effective));
  }
}
