package com.sosnitzka.taiga;

import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.config.ModConfigEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import java.util.LinkedHashMap;
import java.util.Map;

/** SERVER config: Forge handles world isolation, persistence and client synchronization. */
public final class TraitConfig {
  public static final ForgeConfigSpec SPEC;
  private static final Map<String, ForgeConfigSpec.ConfigValue<? extends Number>> VALUES = new LinkedHashMap<>();
  static {
    ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
    for (TraitDefaults.Entry entry : TraitDefaults.ENTRIES) {
      builder.comment(entry.comment());
      VALUES.put(entry.key(), entry.integer()
          ? builder.defineInRange(entry.key(), (int)entry.value(), (int)entry.minimum(), (int)entry.maximum())
          : builder.defineInRange(entry.key(), entry.value(), entry.minimum(), entry.maximum()));
    }
    SPEC = builder.build();
  }
  private TraitConfig() {}
  public static void register(IEventBus bus) {
    bus.addListener((ModConfigEvent.Loading event) -> refresh(event.getConfig()));
    bus.addListener((ModConfigEvent.Reloading event) -> refresh(event.getConfig()));
    ArmorPlatform.registerConfigEvents(bus);
    net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(
        (net.minecraftforge.event.server.ServerStoppedEvent event) -> TraitTuning.reset());
  }
  private static void refresh(ModConfig config) {
    if (config.getSpec() != SPEC) return;
    Map<String, Number> values = new LinkedHashMap<>();
    VALUES.forEach((key,value) -> values.put(key,value.get()));
    TraitTuning.apply(values);
  }
}
