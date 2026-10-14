package com.sosnitzka.taiga;
import net.minecraft.world.item.ArmorItem;
import slimeknights.tconstruct.library.modifiers.Modifier;
import slimeknights.tconstruct.library.modifiers.ModifierEntry;
import slimeknights.tconstruct.library.tools.context.ToolRebuildContext;
import slimeknights.tconstruct.library.tools.nbt.*;
import slimeknights.tconstruct.library.tools.stat.ModifierStatsBuilder;
import slimeknights.tconstruct.library.tools.stat.ToolStats;
import slimeknights.tconstruct.library.tools.SlotType;
public final class ArmorModifier extends Modifier {
  @Override public java.util.List<net.minecraft.network.chat.Component> getDescriptionList(int level) {
    return TraitDescriptions.describe("armor."+trait.id.substring("armor_".length()), super.getDescriptionList());
  }
  public final ArmorTrait trait;
  public ArmorModifier(ArmorTrait trait) { this.trait = trait; }
  @Override public void addToolStats(ToolRebuildContext context, int level, ModifierStatsBuilder builder) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.REINFORCED)
      ToolStats.DURABILITY.multiply(builder, 1 + TraitTuning.f("armor.reinforced.durabilityBonusPerLevel") * ArmorBalance.pieceLevel(level));
  }
  @Override public void addVolatileData(ToolRebuildContext context, int level, ModDataNBT data) {
    if (context.getItem() instanceof ArmorItem && trait == ArmorTrait.ARCANE)
      data.addSlots(SlotType.UPGRADE, TraitTuning.i("armor.arcane.slotsPerLevel") * ArmorBalance.pieceLevel(level));
  }
}
