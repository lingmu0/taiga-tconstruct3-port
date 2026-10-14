package com.sosnitzka.taiga;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Small, chunk-contained deposits; no runtime meteor strikes or terrain explosions. */
public final class DepositFeature extends Feature<NoneFeatureConfiguration> {
  private final boolean end;
  public DepositFeature(boolean end) {
    super(NoneFeatureConfiguration.CODEC);
    this.end = end;
  }
  @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
    if (!TaigaConfig.WORLDGEN.get()) return false;
    WorldGenLevel level = context.level();
    BlockPos origin = context.origin();
    int x = (origin.getX() & ~15) + 8;
    int z = (origin.getZ() & ~15) + 8;
    int surface = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z);
    if (surface <= level.getMinBuildHeight() + 12 || surface >= level.getMaxBuildHeight() - 8) return false;
    if (!level.getFluidState(new BlockPos(x, surface - 1, z)).isEmpty()) return false;
    int radius = end ? 3 : 3 + context.random().nextInt(3);
    BlockPos center = new BlockPos(x, surface - (end ? 4 : 1), z);
    if (end && !level.getBlockState(center).is(Blocks.END_STONE)) return false;
    BlockState shell = Taiga.block(end ? "obsidiorite_block" : "meteorite_block").defaultBlockState();
    BlockState core = Taiga.block(end ? "uru_ore" : "duranite_ore").defaultBlockState();
    boolean changed = false;
    for (int dx = -radius; dx <= radius; dx++) for (int dy = -radius; dy <= radius; dy++) for (int dz = -radius; dz <= radius; dz++) {
      int dist = dx * dx + dy * dy + dz * dz;
      if (dist > radius * radius) continue;
      BlockPos pos = center.offset(dx, dy, dz);
      BlockState old = level.getBlockState(pos);
      if (old.is(Blocks.BEDROCK) || old.hasBlockEntity() || !old.getFluidState().isEmpty()) continue;
      if (end && !old.is(Blocks.END_STONE)) continue;
      level.setBlock(pos, dist <= 2 ? core : shell, 2);
      changed = true;
    }
    return changed;
  }
}
