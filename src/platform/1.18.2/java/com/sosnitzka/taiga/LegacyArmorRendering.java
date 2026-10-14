package com.sosnitzka.taiga;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.Model;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.IItemRenderProperties;
import net.minecraftforge.client.event.ColorHandlerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Code-based tinting of referenced vanilla armor; contains no copied textures. */
@Mod.EventBusSubscriber(modid = Taiga.ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class LegacyArmorRendering {
  private static final TintedModel MODEL = new TintedModel();
  private LegacyArmorRendering() {}
  @SubscribeEvent public static void colors(ColorHandlerEvent.Item event) {
    Taiga.ITEMS.getEntries().forEach(entry -> {
      if (entry.get() instanceof LegacyArmorItem)
        event.getItemColors().register((stack, tint) -> ((LegacyArmorItem)stack.getItem()).color, entry.get());
    });
  }
  public static IItemRenderProperties properties() {
    return new IItemRenderProperties() {
      @Override public Model getBaseArmorModel(LivingEntity entity, ItemStack stack, EquipmentSlot slot, HumanoidModel<?> original) {
        MODEL.base = original;
        MODEL.color = ((LegacyArmorItem) stack.getItem()).color;
        return MODEL;
      }
    };
  }
  private static final class TintedModel extends Model {
    private HumanoidModel<?> base;
    private int color;
    private TintedModel() { super(RenderType::entityCutoutNoCull); }
    @Override public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int light, int overlay, float red, float green, float blue, float alpha) {
      if (base != null) base.renderToBuffer(pose, buffer, light, overlay,
          red * ((color >> 16) & 255) / 255f, green * ((color >> 8) & 255) / 255f, blue * (color & 255) / 255f, alpha);
    }
  }
}
