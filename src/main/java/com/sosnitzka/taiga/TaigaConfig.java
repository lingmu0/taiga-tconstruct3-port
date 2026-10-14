package com.sosnitzka.taiga;

import net.minecraftforge.common.ForgeConfigSpec;

public final class TaigaConfig {
  public static final ForgeConfigSpec SPEC;
  public static final ForgeConfigSpec.BooleanValue WORLDGEN;
  static {
    ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
    WORLDGEN = builder.comment("Enable meteorite and End deposit generation. Ore placement is configurable through datapacks.")
        .define("specialDeposits", true);
    SPEC = builder.build();
  }
  private TaigaConfig() {}
}
