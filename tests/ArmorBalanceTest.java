import com.sosnitzka.taiga.ArmorBalance;
import com.sosnitzka.taiga.ArmorTrait;
import java.util.Arrays;
import java.util.Map;
import com.sosnitzka.taiga.TraitTuning;

/** Runs on a plain JDK, without loading Minecraft, Forge or any game registries. */
public final class ArmorBalanceTest {
  private static int checks;
  private static void near(double expected, double actual) {
    if (Math.abs(expected-actual) > 0.000001) throw new AssertionError(expected+" != "+actual);
    checks++;
  }
  private static int[] loadout(ArmorTrait trait, int level) {
    int[] levels = new int[ArmorTrait.values().length];
    levels[trait.ordinal()] = level;
    return levels;
  }
  private static float hit(int[] levels, boolean melee, boolean fire, boolean projectile, boolean fall, float health, float random) {
    return ArmorBalance.reduction(levels,melee,fire,projectile,fall,health,random);
  }
  public static void main(String[] args) {
    int[] empty = new int[ArmorTrait.values().length];
    near(0, hit(empty,true,true,true,true,0.1f,1));
    // Four normal pieces and artificially excessive levels share the same cap.
    for (int level : new int[]{4,8,100,Integer.MAX_VALUE}) {
      near(0.12, hit(loadout(ArmorTrait.BULWARK,level),true,false,false,false,0.5f,0));
      near(0.16, hit(loadout(ArmorTrait.HEAT_GUARD,level),false,true,false,false,0.5f,0));
      near(0.16, hit(loadout(ArmorTrait.DEFLECTION,level),false,false,true,false,0.5f,0));
      near(0.24, hit(loadout(ArmorTrait.CUSHION,level),false,false,false,true,0.5f,0));
      near(0.08, ArmorBalance.speed(level,0));
      near(-0.04, ArmorBalance.speed(0,level));
      near(0.16, ArmorBalance.knockback(level));
      near(4, ArmorBalance.health(level));
      near(2, ArmorBalance.pieceLevel(level));
    }
    // Wrong damage types confer no protection; thresholds are intentionally strict.
    near(0, hit(loadout(ArmorTrait.BULWARK,4),false,true,true,true,0.5f,0));
    near(0, hit(loadout(ArmorTrait.HEAT_GUARD,4),true,false,false,false,0.5f,0));
    near(0, hit(loadout(ArmorTrait.LAST_STAND,4),true,false,false,false,0.4f,0));
    near(0.12, hit(loadout(ArmorTrait.LAST_STAND,4),true,false,false,false,0.399f,0));
    near(0.12, hit(loadout(ArmorTrait.COMPOSED,4),true,false,false,false,0.9f,0));
    near(0, hit(loadout(ArmorTrait.COMPOSED,4),true,false,false,false,0.899f,0));
    near(0, hit(loadout(ArmorTrait.VOLATILE,4),true,false,false,false,1,0));
    near(0.06, hit(loadout(ArmorTrait.VOLATILE,4),true,false,false,false,1,0.5f));
    near(0.12, hit(loadout(ArmorTrait.VOLATILE,4),true,false,false,false,1,1));
    // A mixed set adds bonuses once; no per-piece exponential attribute stacking.
    near(0.02, ArmorBalance.speed(2,2));
    near(0, ArmorBalance.speed(0,0));
    near(0, ArmorBalance.health(0));
    // All combinations stay bounded even with malformed negative levels or RNG input.
    for (int level = -2; level <= 10; level++) {
      int[] all = new int[ArmorTrait.values().length];
      Arrays.fill(all,level);
      for (int flags = 0; flags < 16; flags++) {
        for (float health : new float[]{0.1f,0.4f,0.8f,0.9f,1}) {
          for (float random : new float[]{-1,0,0.5f,1,2}) {
            float reduction = hit(all,(flags&1)!=0,(flags&2)!=0,(flags&4)!=0,(flags&8)!=0,health,random);
            if (reduction < 0 || reduction > 0.300001f) throw new AssertionError("Unbounded reduction: "+reduction);
            checks++;
          }
        }
      }
    }
    int[] all = new int[ArmorTrait.values().length];
    Arrays.fill(all,4);
    near(0.30, hit(all,true,true,true,true,0.2f,1));
    String originalFingerprint = TraitTuning.fingerprint();
    // A non-default config must affect the actual calculation, not only the file.
    TraitTuning.apply(Map.of("armor_rules.maximumTotalLevel",2,"armor_rules.maximumDamageReduction",0.10,
        "armor.bulwark.reductionPerLevel",0.08,"armor.lightweight.speedBonusPerLevel",0.05,
        "armor.vitality.healthPerLevel",3.0,"armor_rules.maximumPieceLevel",1));
    near(0.10, hit(loadout(ArmorTrait.BULWARK,4),true,false,false,false,0.5f,0));
    near(0.10, ArmorBalance.speed(4,0));
    near(6, ArmorBalance.health(4));
    near(1, ArmorBalance.pieceLevel(4));
    if (originalFingerprint.equals(TraitTuning.fingerprint())) throw new AssertionError("Config fingerprint did not change");
    String configured = TraitTuning.fingerprint();
    // Invalid edits are rejected atomically, retaining the last valid snapshot.
    for (Map<String,Number> invalid : java.util.List.<Map<String,Number>>of(
        Map.of("armor_rules.maximumTotalLevel",0),Map.of("armor_rules.maximumTotalLevel",2.5),
        Map.of("armor_rules.maximumDamageReduction",Double.NaN),Map.of("armor.nonexistent",1))) {
      boolean rejected = false;
      try { TraitTuning.apply(invalid); } catch (IllegalArgumentException expected) { rejected = true; }
      if (!rejected || !configured.equals(TraitTuning.fingerprint())) throw new AssertionError("Invalid edit changed live config");
      checks++;
    }
    TraitTuning.reset();
    if (!originalFingerprint.equals(TraitTuning.fingerprint())) throw new AssertionError("World unload did not restore defaults");
    near(0.12, hit(loadout(ArmorTrait.BULWARK,4),true,false,false,false,0.5f,0));
    System.out.println("Armor balance: "+checks+" scenario and bound checks passed (no game launched).");
  }
}
