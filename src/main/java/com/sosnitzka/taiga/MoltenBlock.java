package com.sosnitzka.taiga;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FlowingFluid;

/** Retains the original molten fluids' heat hazard on both Forge fluid APIs. */
public final class MoltenBlock extends LiquidBlock {
  public MoltenBlock(Supplier<? extends FlowingFluid> fluid, Properties properties) { super(fluid, properties); }
  @Override public void entityInside(BlockState state, Level world, BlockPos pos, Entity entity) {
    super.entityInside(state, world, pos, entity);
    if (!world.isClientSide && entity.isAlive() && !entity.fireImmune()) {
      entity.setSecondsOnFire(8);
      if (entity.tickCount % 10 == 0) Platform.burn(entity);
    }
  }
}
