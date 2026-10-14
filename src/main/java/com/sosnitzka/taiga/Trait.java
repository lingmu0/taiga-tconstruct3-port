package com.sosnitzka.taiga;

public enum Trait {
  ANALYSING("analysing"), ARCANE("arcane"), BERSERK("berserk"), BLIND("blind"), BRIGHT("bright"),
  CASCADE("cascade"), CATCHER("catcher"), CONGENIAL("congenial"), CRUSHING("crushing"), CURSED("cursed"),
  CURVATURE("curvature"), DARK("dark"), DECAY("decay"), DIFFUSE("diffuse"), DISSOLVING("dissolving"),
  FRACTURE("fracture"), FRAGILE("fragile"), GARISHLY("garishly"), GLIMMER("glimmer"), HEROIC("heroic"),
  HOLLOW("hollow"), MELTING("melting"), MUTATE("mutate"), NATUREBOUND("naturebound"), PORTED("ported"),
  PULVERIZING("pulverizing"), RESONANCE("resonance"), REVIVING("reviving"), SLAUGHTERING("slaughtering"),
  SOFTY("softy"), SOULEATER("souleater"), SUPERHEAVY("superheavy"), TANTRUM("tantrum"), UNSTABLE("unstable"),
  WHIRL("whirl"), ALIEN("taiga_alien"), CRUMBLING("taiga_crumbling");
  public final String id;
  Trait(String id) { this.id = id; }
}
