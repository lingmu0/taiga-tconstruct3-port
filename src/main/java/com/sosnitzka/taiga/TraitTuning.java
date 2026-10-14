package com.sosnitzka.taiga;

import java.util.LinkedHashMap;
import java.util.Map;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;

/** Atomic configuration snapshots keep gameplay and plain-JDK tests on the same rules. */
public final class TraitTuning {
  private static final Map<String, Double> DEFAULTS = defaults();
  private record Snapshot(Map<String, Double> values, String fingerprint) {}
  private static final Snapshot DEFAULT_SNAPSHOT = snapshot(DEFAULTS);
  private static volatile Snapshot current = DEFAULT_SNAPSHOT;
  private TraitTuning() {}
  private static Map<String, Double> defaults() {
    Map<String, Double> map = new LinkedHashMap<>();
    for (TraitDefaults.Entry entry : TraitDefaults.ENTRIES) {
      if (map.put(entry.key(), entry.value()) != null) throw new IllegalStateException("Duplicate trait key: "+entry.key());
    }
    return Map.copyOf(map);
  }
  public static double d(String key) {
    Double value = current.values().get(key);
    if (value == null) throw new IllegalArgumentException("Unknown trait setting: "+key);
    return value;
  }
  public static float f(String key) { return (float)d(key); }
  public static int i(String key) { return (int)d(key); }
  public static boolean custom(String prefix) {
    Map<String, Double> values = current.values();
    for (String key : DEFAULTS.keySet())
      if (key.startsWith(prefix+".") && !DEFAULTS.get(key).equals(values.get(key))) return true;
    return false;
  }
  public static String fingerprint() { return current.fingerprint(); }
  private static Snapshot snapshot(Map<String, Double> values) {
    StringBuilder text = new StringBuilder();
    for (TraitDefaults.Entry entry : TraitDefaults.ENTRIES) text.append(entry.key()).append('=').append(values.get(entry.key())).append('\n');
    try { return new Snapshot(Map.copyOf(values), HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.toString().getBytes(StandardCharsets.UTF_8)))); }
    catch (NoSuchAlgorithmException exception) { throw new IllegalStateException(exception); }
  }
  public static void reset() { current = DEFAULT_SNAPSHOT; }
  public static void apply(Map<String, ? extends Number> overrides) {
    Map<String, Double> updated = new LinkedHashMap<>(DEFAULTS);
    for (String key : overrides.keySet()) if (!DEFAULTS.containsKey(key)) throw new IllegalArgumentException("Unknown trait setting: "+key);
    for (TraitDefaults.Entry entry : TraitDefaults.ENTRIES) {
      Number number = overrides.get(entry.key());
      if (number == null) continue;
      double value = number.doubleValue();
      if (!Double.isFinite(value) || value < entry.minimum() || value > entry.maximum() || (entry.integer() && value != Math.rint(value)))
        throw new IllegalArgumentException("Invalid trait value: "+entry.key());
      updated.put(entry.key(), value);
    }
    current = snapshot(updated);
  }
}
