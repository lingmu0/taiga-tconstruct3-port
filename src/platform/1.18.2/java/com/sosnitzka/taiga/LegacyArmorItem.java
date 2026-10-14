package com.sosnitzka.taiga;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.IItemRenderProperties;
import slimeknights.tconstruct.library.tools.definition.ModifiableArmorMaterial;
import slimeknights.tconstruct.library.tools.item.ModifiableArmorItem;
import slimeknights.tconstruct.tools.item.ArmorSlotType;

import java.util.function.Consumer;

/** Fixed-material Tinkers armor for the pre-material-plating API in 1.18.2. */
public final class LegacyArmorItem extends ModifiableArmorItem {
  public final int color;
  public LegacyArmorItem(ModifiableArmorMaterial material, ArmorSlotType slot, int color) {
    super(material, slot, Platform.itemProperties().stacksTo(1));
    this.color = color;
  }
  @Override public String getArmorTexture(ItemStack stack, Entity entity, EquipmentSlot slot, String type) {
    return "minecraft:textures/models/armor/iron_layer_"+(slot == EquipmentSlot.LEGS ? "2" : "1")+".png";
  }
  @Override public void initializeClient(Consumer<IItemRenderProperties> consumer) {
    // Item construction invokes this before fields initialize: read color from the stack later.
    consumer.accept(LegacyArmorRendering.properties());
  }
}
