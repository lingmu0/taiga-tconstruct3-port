package com.sosnitzka.taiga;
import static com.sosnitzka.taiga.TraitTuning.*;

/** Pure balance rules, also exercised by the non-launch regression checks. */
public final class ArmorBalance {
  private ArmorBalance() {}
  public static int level(int raw) { return Math.max(0, Math.min(i("armor_rules.maximumTotalLevel"), raw)); }
  public static int pieceLevel(int raw) { return Math.max(0, Math.min(i("armor_rules.maximumPieceLevel"), raw)); }
  public static float reduction(int[] levels, boolean melee, boolean fire, boolean projectile, boolean fall,
                                float healthFraction, float random) {
    float amount = 0;
    if (melee) amount += f("armor.bulwark.reductionPerLevel") * level(levels[ArmorTrait.BULWARK.ordinal()]);
    if (fire) amount += f("armor.heat_guard.reductionPerLevel") * level(levels[ArmorTrait.HEAT_GUARD.ordinal()]);
    if (projectile) amount += f("armor.deflection.reductionPerLevel") * level(levels[ArmorTrait.DEFLECTION.ordinal()]);
    if (fall) amount += f("armor.cushion.reductionPerLevel") * level(levels[ArmorTrait.CUSHION.ordinal()]);
    if (healthFraction < f("armor.last_stand.healthThreshold")) amount += f("armor.last_stand.reductionPerLevel") * level(levels[ArmorTrait.LAST_STAND.ordinal()]);
    if (healthFraction >= f("armor.composed.healthThreshold")) amount += f("armor.composed.reductionPerLevel") * level(levels[ArmorTrait.COMPOSED.ordinal()]);
    amount += Math.max(0, Math.min(1, random)) * f("armor.volatile.maximumReductionPerLevel") * level(levels[ArmorTrait.VOLATILE.ordinal()]);
    return Math.min(f("armor_rules.maximumDamageReduction"), amount);
  }
  public static double speed(int light, int anchor) { return Math.max(-1, d("armor.lightweight.speedBonusPerLevel") * level(light) - d("armor.anchor.speedPenaltyPerLevel") * level(anchor)); }
  public static double knockback(int anchor) { return Math.min(1, d("armor.anchor.knockbackPerLevel") * level(anchor)); }
  public static double health(int vitality) { return d("armor.vitality.healthPerLevel") * level(vitality); }
}
