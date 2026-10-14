package com.sosnitzka.taiga;

/** Armor-specific effects: kept separate from weapon and mining traits. */
public enum ArmorTrait {
  BULWARK("bulwark"), HEAT_GUARD("heat_guard"), DEFLECTION("deflection"), ANCHOR("anchor"),
  LIGHTWEIGHT("lightweight"), CUSHION("cushion"), LAST_STAND("last_stand"), REACTIVE("reactive"),
  VENOM("venom"), RADIANT("radiant"), NATURAL("natural"), RENEWAL("renewal"), AQUATIC("aquatic"),
  VITALITY("vitality"), REINFORCED("reinforced"), VOLATILE("volatile"), ARCANE("arcane"), COMPOSED("composed");
  public final String id;
  ArmorTrait(String id) { this.id = "armor_" + id; }
}
