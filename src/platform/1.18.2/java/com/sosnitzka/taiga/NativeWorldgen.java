package com.sosnitzka.taiga;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.data.BuiltinRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.feature.*;
import net.minecraft.world.level.levelgen.feature.configurations.*;
import net.minecraft.world.level.levelgen.placement.*;
import net.minecraft.world.level.levelgen.structure.templatesystem.BlockMatchTest;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.world.BiomeLoadingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
/** 1.18.2 predates Forge biome modifiers. Register builtins and inject through its biome event. */
public final class NativeWorldgen {
  private static final Map<String, List<Holder<PlacedFeature>>> BY_DIMENSION = new HashMap<>();
  public static void register(IEventBus bus) {
    bus.addListener((FMLCommonSetupEvent event) -> event.enqueueWork(NativeWorldgen::bootstrap));
    MinecraftForge.EVENT_BUS.addListener(NativeWorldgen::biome);
  }
  private static void add(String id, String dimension, ConfiguredFeature<?, ?> configured, List<PlacementModifier> placements) {
    Registry.register(BuiltinRegistries.CONFIGURED_FEATURE, Taiga.id(id), configured);
    Holder<ConfiguredFeature<?, ?>> holder = BuiltinRegistries.CONFIGURED_FEATURE.getHolderOrThrow(ResourceKey.create(Registry.CONFIGURED_FEATURE_REGISTRY, Taiga.id(id)));
    PlacedFeature placed = new PlacedFeature(holder, placements);
    Registry.register(BuiltinRegistries.PLACED_FEATURE, Taiga.id(id), placed);
    BY_DIMENSION.computeIfAbsent(dimension, key -> new ArrayList<>()).add(BuiltinRegistries.PLACED_FEATURE.getHolderOrThrow(ResourceKey.create(Registry.PLACED_FEATURE_REGISTRY, Taiga.id(id))));
  }
  private static void bootstrap() {
    add("tiberium_ore", "nether", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.NETHERRACK), Taiga.block("tiberium_ore").defaultBlockState())), 14)), List.of(CountPlacement.of(12), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(32), VerticalAnchor.absolute(128)), BiomeFilter.biome()));
    add("prometheum_ore", "nether", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.NETHERRACK), Taiga.block("prometheum_ore").defaultBlockState())), 4)), List.of(CountPlacement.of(3), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(8), VerticalAnchor.absolute(40)), BiomeFilter.biome()));
    add("valyrium_ore", "nether", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.NETHERRACK), Taiga.block("valyrium_ore").defaultBlockState())), 3)), List.of(CountPlacement.of(2), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(96)), BiomeFilter.biome()));
    add("osram_ore", "nether", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.LAVA), Taiga.block("osram_ore").defaultBlockState())), 4)), List.of(CountPlacement.of(5), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(32)), BiomeFilter.biome()));
    add("karmesine_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.ANDESITE), Taiga.block("karmesine_ore").defaultBlockState())), 8)), List.of(CountPlacement.of(8), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(80)), BiomeFilter.biome()));
    add("ovium_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.DIORITE), Taiga.block("ovium_ore").defaultBlockState())), 8)), List.of(CountPlacement.of(8), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(80)), BiomeFilter.biome()));
    add("jauxum_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.GRANITE), Taiga.block("jauxum_ore").defaultBlockState())), 8)), List.of(CountPlacement.of(8), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(80)), BiomeFilter.biome()));
    add("eezo_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.BEDROCK), Taiga.block("eezo_ore").defaultBlockState())), 5)), List.of(CountPlacement.of(6), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(-64), VerticalAnchor.absolute(-60)), BiomeFilter.biome()));
    add("vibranium_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.STONE), Taiga.block("vibranium_ore").defaultBlockState()), OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.DEEPSLATE), Taiga.block("deepslate_vibranium_ore").defaultBlockState())), 3)), List.of(CountPlacement.of(1), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(-32), VerticalAnchor.absolute(32)), BiomeFilter.biome()));
    add("dilithium_ore", "overworld", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.STONE), Taiga.block("dilithium_ore").defaultBlockState()), OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.DEEPSLATE), Taiga.block("deepslate_dilithium_ore").defaultBlockState())), 6)), List.of(CountPlacement.of(3), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(-48), VerticalAnchor.absolute(48)), BiomeFilter.biome()));
    add("aurorium_ore", "end", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.END_STONE), Taiga.block("aurorium_ore").defaultBlockState())), 4)), List.of(CountPlacement.of(3), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(16), VerticalAnchor.absolute(64)), BiomeFilter.biome()));
    add("palladium_ore", "end", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.END_STONE), Taiga.block("palladium_ore").defaultBlockState())), 4)), List.of(CountPlacement.of(3), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(32), VerticalAnchor.absolute(80)), BiomeFilter.biome()));
    add("abyssum_ore", "end", new ConfiguredFeature<>(Feature.ORE, new OreConfiguration(List.of(OreConfiguration.target(new BlockMatchTest(net.minecraft.world.level.block.Blocks.END_STONE), Taiga.block("abyssum_ore").defaultBlockState())), 4)), List.of(CountPlacement.of(5), InSquarePlacement.spread(), HeightRangePlacement.uniform(VerticalAnchor.absolute(0), VerticalAnchor.absolute(64)), BiomeFilter.biome()));
    add("meteor", "overworld", new ConfiguredFeature<>(Taiga.deposit("meteor"), NoneFeatureConfiguration.INSTANCE), List.of(RarityFilter.onAverageOnceEvery(64), InSquarePlacement.spread(), HeightmapPlacement.onHeightmap(Heightmap.Types.WORLD_SURFACE_WG), BiomeFilter.biome()));
    add("end_deposit", "end", new ConfiguredFeature<>(Taiga.deposit("end_deposit"), NoneFeatureConfiguration.INSTANCE), List.of(RarityFilter.onAverageOnceEvery(32), InSquarePlacement.spread(), HeightmapPlacement.onHeightmap(Heightmap.Types.WORLD_SURFACE_WG), BiomeFilter.biome()));
  }
  private static void biome(BiomeLoadingEvent event) {
    String dimension = event.getCategory() == Biome.BiomeCategory.NETHER ? "nether" : event.getCategory() == Biome.BiomeCategory.THEEND ? "end" : "overworld";
    for (Holder<PlacedFeature> feature : BY_DIMENSION.getOrDefault(dimension, List.of())) event.getGeneration().addFeature(GenerationStep.Decoration.UNDERGROUND_ORES, feature);
  }
}
