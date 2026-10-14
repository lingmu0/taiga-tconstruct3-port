package com.sosnitzka.taiga;

import net.minecraft.network.chat.Component;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Show live values for customized traits rather than a stale default-number tooltip. */
public final class TraitDescriptions {
  private TraitDescriptions() {}
  public static List<Component> describe(String section, List<Component> defaults) {
    boolean armor = section.startsWith("armor.");
    if (!TraitTuning.custom(section) && !(armor && TraitTuning.custom("armor_rules"))) return defaults;
    List<Component> result = new ArrayList<>();
    if (!defaults.isEmpty()) result.add(defaults.get(0));
    result.add(Platform.translate("tooltip.taiga.configured_trait"));
    for (TraitDefaults.Entry entry : TraitDefaults.ENTRIES) {
      if (entry.key().startsWith(section+".") || (armor && entry.key().startsWith("armor_rules."))) {
        double value = TraitTuning.d(entry.key());
        String display = entry.integer() ? Integer.toString((int)value) : String.format(Locale.ROOT,"%.4f",value).replaceAll("0+$", "").replaceAll("\\.$", "");
        result.add(Platform.translate("config.taiga."+entry.key(), display));
      }
    }
    return result;
  }
}
