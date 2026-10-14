package com.sosnitzka.taiga;
import java.util.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;
import net.minecraftforge.fluids.ForgeFlowingFluid;
import net.minecraftforge.fluids.FluidAttributes;
import net.minecraft.network.chat.TranslatableComponent;
public final class Platform {
  private static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(ForgeRegistries.FLUIDS, Taiga.ID);
  private static final Map<String, RegistryObject<FlowingFluid>> SOURCES = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<FlowingFluid>> FLOWING = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<Item>> BUCKETS = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<LiquidBlock>> BLOCKS = new LinkedHashMap<>();
  
  private static final CreativeModeTab TAB = new CreativeModeTab("taiga") {
    @Override public ItemStack makeIcon() { return new ItemStack(Taiga.block("vibranium_ore")); }
  };

  public static Item.Properties itemProperties() { return new Item.Properties().tab(TAB); }
  public static BlockBehaviour.Properties blockProperties() { return BlockBehaviour.Properties.of(Material.STONE); }
  public static Component translate(String key, Object... args) { return new TranslatableComponent(key, args); }
  public static void burn(net.minecraft.world.entity.Entity entity) { entity.hurt(net.minecraft.world.damagesource.DamageSource.LAVA, 4f); }
  public static ItemStack smelt(ItemStack stack, Level world) {
    return world.getRecipeManager().getRecipeFor(RecipeType.SMELTING, new SimpleContainer(stack), world)
        .map(recipe -> { ItemStack out = recipe.getResultItem().copy(); out.setCount(Math.min(out.getMaxStackSize(), out.getCount() * stack.getCount())); return out; })
        .orElse(ItemStack.EMPTY);
  }
  public static void register(IEventBus bus) {
    for (Catalog.Material material : Catalog.MATERIALS) {
      String name = material.name();
      
      SOURCES.put(name, FLUIDS.register("molten_" + name, () -> new ForgeFlowingFluid.Source(properties(name))));
      FLOWING.put(name, FLUIDS.register("flowing_molten_" + name, () -> new ForgeFlowingFluid.Flowing(properties(name))));
      BUCKETS.put(name, Taiga.ITEMS.register("molten_" + name + "_bucket", () -> new BucketItem(SOURCES.get(name), itemProperties().stacksTo(1).craftRemainder(Items.BUCKET))));
      BLOCKS.put(name, Taiga.BLOCKS.register("molten_" + name, () -> new MoltenBlock(SOURCES.get(name), BlockBehaviour.Properties.of(Material.LAVA).noCollission().strength(100).lightLevel(state -> 10).noDrops())));
    }
    FLUIDS.register(bus);
    
    
    NativeWorldgen.register(bus);
  }
  private static ForgeFlowingFluid.Properties properties(String name) {
    Catalog.Material material = Catalog.find(name);
    return new ForgeFlowingFluid.Properties(SOURCES.get(name), FLOWING.get(name), FluidAttributes.builder(new ResourceLocation("minecraft", "block/water_still"), new ResourceLocation("minecraft", "block/water_flow")).color(0xFF000000 | material.color()).temperature(material.temperature() + 273).density(2000).viscosity(10000).luminosity(10).sound(SoundEvents.BUCKET_FILL_LAVA, SoundEvents.BUCKET_EMPTY_LAVA))
        .bucket(BUCKETS.get(name)).block(BLOCKS.get(name)).tickRate(20).slopeFindDistance(2).levelDecreasePerBlock(2);
  }
  @net.minecraftforge.fml.common.Mod.EventBusSubscriber(modid = Taiga.ID, bus = net.minecraftforge.fml.common.Mod.EventBusSubscriber.Bus.MOD, value = net.minecraftforge.api.distmarker.Dist.CLIENT)
  public static final class ClientRendering {
    @net.minecraftforge.eventbus.api.SubscribeEvent
    public static void setup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
      event.enqueueWork(() -> Taiga.SOLIDS.forEach((name, block) -> {
        if (name.endsWith("_ore")) net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(block.get(), net.minecraft.client.renderer.RenderType.cutoutMipped());
      }));
    }
  }
}
