package com.sosnitzka.taiga;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraftforge.common.ForgeTier;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.TierSortingRegistry;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import slimeknights.tconstruct.library.modifiers.util.ModifierDeferredRegister;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Mod(Taiga.ID)
public final class Taiga {
  public static final String ID = "taiga";
  public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, ID);
  public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, ID);
  public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(ForgeRegistries.FEATURES, ID);
  public static final ModifierDeferredRegister MODIFIERS = ModifierDeferredRegister.create(ID);
  public static final Map<String, RegistryObject<Block>> SOLIDS = new LinkedHashMap<>();

  static {
    for (Catalog.Material material : Catalog.MATERIALS) {
      String name = material.name();
      if (!name.equals("magma") && !name.equals("nitronite")) {
        solid(name + "_block", material);
        if (material.ore()) solid(name + "_ore", material);
        if (material.deepslate()) solid("deepslate_" + name + "_ore", material);
        for (String form : List.of("ingot", "nugget", "dust")) {
          ITEMS.register(name + "_" + form, () -> new Item(Platform.itemProperties()));
        }
      }
    }
    solid("meteoritecobble_block", Catalog.find("meteorite"));
    solid("obsidioritecobble_block", Catalog.find("obsidiorite"));
    ITEMS.register("tiberium_crystal", () -> new Item(Platform.itemProperties()));
    ITEMS.register("dilithium_crystal", () -> new Item(Platform.itemProperties()));
    for (Trait trait : Trait.values()) MODIFIERS.register(trait.id, () -> new TaigaModifier(trait));
    for (ArmorTrait trait : ArmorTrait.values()) MODIFIERS.register(trait.id, () -> new ArmorModifier(trait));
    ArmorPlatform.registerItems();
    FEATURES.register("meteor", () -> new DepositFeature(false));
    FEATURES.register("end_deposit", () -> new DepositFeature(true));
  }

  public Taiga() {
    IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
    BLOCKS.register(bus);
    ITEMS.register(bus);
    FEATURES.register(bus);
    MODIFIERS.register(bus);
    Platform.register(bus);
    ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, TaigaConfig.SPEC);
    ModLoadingContext.get().registerConfig(ModConfig.Type.SERVER, TraitConfig.SPEC, "taiga-traits.toml");
    TraitConfig.register(bus);
    MinecraftForge.EVENT_BUS.register(new TraitEvents());
    MinecraftForge.EVENT_BUS.register(new ArmorEvents());
    ArmorPlatform.registerEvents();
    registerTiers();
  }

  private static void solid(String name, Catalog.Material material) {
    RegistryObject<Block> block = BLOCKS.register(name, () -> new Block(Platform.blockProperties()
        .strength(name.startsWith("deepslate_") ? 9f : name.contains("ore") ? 6f : 5f, 12f)
        .sound(name.startsWith("deepslate_") ? net.minecraft.world.level.block.SoundType.DEEPSLATE : net.minecraft.world.level.block.SoundType.STONE)
        .requiresCorrectToolForDrops()
        .lightLevel(state -> material.name().equals("lumix") ? 12 : material.name().equals("tiberium") ? 6 : 0)));
    SOLIDS.put(name, block);
    ITEMS.register(name, () -> new BlockItem(block.get(), Platform.itemProperties()));
  }

  private static void registerTiers() {
    Object previous = Tiers.NETHERITE;
    for (String name : List.of("duranite", "valyrium", "vibranium")) {
      ResourceLocation id = id(name);
      ForgeTier tier = new ForgeTier(name.equals("duranite") ? 5 : name.equals("valyrium") ? 6 : 7,
          1500, 6, 3, 15, BlockTags.create(id("needs_" + name + "_tool")), Ingredient::of);
      TierSortingRegistry.registerTier(tier, id, List.of(previous), List.of());
      previous = id;
    }
  }

  public static ResourceLocation id(String path) { return new ResourceLocation(ID, path); }
  public static Block block(String name) { return SOLIDS.get(name).get(); }
  public static DepositFeature deposit(String name) { return (DepositFeature) ForgeRegistries.FEATURES.getValue(id(name)); }
}
