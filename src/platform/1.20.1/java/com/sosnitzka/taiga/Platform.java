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
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
public final class Platform {
  private static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(ForgeRegistries.FLUIDS, Taiga.ID);
  private static final Map<String, RegistryObject<FlowingFluid>> SOURCES = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<FlowingFluid>> FLOWING = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<Item>> BUCKETS = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<LiquidBlock>> BLOCKS = new LinkedHashMap<>();
  private static final DeferredRegister<FluidType> TYPES_REGISTER = DeferredRegister.create(ForgeRegistries.Keys.FLUID_TYPES, Taiga.ID);
private static final Map<String, RegistryObject<FluidType>> TYPES = new LinkedHashMap<>();
  private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(net.minecraft.core.registries.Registries.CREATIVE_MODE_TAB, Taiga.ID);
  private static final RegistryObject<CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
      .title(Component.translatable("itemGroup.taiga")).icon(() -> new ItemStack(Taiga.block("vibranium_ore")))
      .displayItems((parameters, output) -> Taiga.ITEMS.getEntries().forEach(item -> output.accept(item.get()))).build());

  public static Item.Properties itemProperties() { return new Item.Properties(); }
  public static BlockBehaviour.Properties blockProperties() { return BlockBehaviour.Properties.of(); }
  public static Component translate(String key, Object... args) { return Component.translatable(key, args); }
  public static void burn(net.minecraft.world.entity.Entity entity) { entity.hurt(entity.damageSources().lava(), 4f); }
  public static ItemStack smelt(ItemStack stack, Level world) {
    return world.getRecipeManager().getRecipeFor(RecipeType.SMELTING, new SimpleContainer(stack), world)
        .map(recipe -> { ItemStack out = recipe.getResultItem(world.registryAccess()).copy(); out.setCount(Math.min(out.getMaxStackSize(), out.getCount() * stack.getCount())); return out; })
        .orElse(ItemStack.EMPTY);
  }
  public static void register(IEventBus bus) {
    for (Catalog.Material material : Catalog.MATERIALS) {
      String name = material.name();
      TYPES.put(name, TYPES_REGISTER.register("molten_" + name, () -> new FluidType(FluidType.Properties.create().density(2000).viscosity(10000).temperature(material.temperature() + 273).lightLevel(10).sound(net.minecraftforge.common.SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL_LAVA).sound(net.minecraftforge.common.SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY_LAVA)) {
        @Override public void initializeClient(java.util.function.Consumer<IClientFluidTypeExtensions> consumer) {
          consumer.accept(new IClientFluidTypeExtensions() {
            @Override public ResourceLocation getStillTexture() { return new ResourceLocation("minecraft", "block/water_still"); }
            @Override public ResourceLocation getFlowingTexture() { return new ResourceLocation("minecraft", "block/water_flow"); }
            @Override public int getTintColor() { return 0xFF000000 | material.color(); }
          });
        }
      }));
      SOURCES.put(name, FLUIDS.register("molten_" + name, () -> new ForgeFlowingFluid.Source(properties(name))));
      FLOWING.put(name, FLUIDS.register("flowing_molten_" + name, () -> new ForgeFlowingFluid.Flowing(properties(name))));
      BUCKETS.put(name, Taiga.ITEMS.register("molten_" + name + "_bucket", () -> new BucketItem(SOURCES.get(name), itemProperties().stacksTo(1).craftRemainder(Items.BUCKET))));
      BLOCKS.put(name, Taiga.BLOCKS.register("molten_" + name, () -> new MoltenBlock(SOURCES.get(name), BlockBehaviour.Properties.of().liquid().replaceable().noCollission().strength(100).lightLevel(state -> 10).noLootTable())));
    }
    FLUIDS.register(bus);
    TYPES_REGISTER.register(bus);
    TABS.register(bus);
    
  }
  private static ForgeFlowingFluid.Properties properties(String name) {
    Catalog.Material material = Catalog.find(name);
    return new ForgeFlowingFluid.Properties(TYPES.get(name), SOURCES.get(name), FLOWING.get(name))
        .bucket(BUCKETS.get(name)).block(BLOCKS.get(name)).tickRate(20).slopeFindDistance(2).levelDecreasePerBlock(2);
  }
  
}
