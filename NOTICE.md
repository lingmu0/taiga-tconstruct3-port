# TAIGA — unofficial Forge / Tinkers' Construct 3 port

Original TAIGA by Zkaface, IdleGandalf / randomtz and contributors:
https://somegit.dev/TAIGA/TAIGA
Upstream revision: 4ba49b23a3683146e0164a55df0a11f4dfc1abf5.

Original code, material values, alloy recipes and textures are licensed under
GNU GPL version 3. The full license is included in LICENSE.
This modified version is also distributed under GPL-3.0-only.

Port modifications, dated 2026-10-12: Forge 1.18.2, 1.19.2 and 1.20.1
registration and world generation; Tinkers' Construct 3 materials, fluid recipes,
rendering and modifier implementations; trait redesigns documented in TRAITS.md.
This is an independent unofficial port, not an original-author release.

Compatibility update, dated 2026-10-14 (2.0.0-port.2): lower minimum
Tinkers' Construct and Mantle versions; rebuild against older Forge versions;
centralize build and runtime dependency constraints in config/compatibility.json.

Visual and content fixes, dated 2026-10-14 (2.0.0-port.3): new transparent
mineral overlays for modern vanilla stone hosts; deepslate vibranium and
dilithium ores; localized fluid types and compact custom harvest-tier labels;
restore eezo generation in overworld bedrock. New mineral art was generated
with the built-in image_gen tool using original TAIGA ore art as references,
then downscaled with nearest-neighbor sampling. Prompts and source images
are included under art/. Minecraft host textures are referenced by resource
location and are not copied into this distribution.

Armor extension, dated 2026-10-14 (2.0.0-port.4): original armor balance
designs for 30 TAIGA materials and 18 armor-specific modifiers; native plate
and maille integration on 1.19.2/1.20.1; 120 fixed-material modifiable armor
items, crafting and repair integration on 1.18.2. Armor effects include bounded
damage reduction, retaliation with recursion protection, removable attributes,
conditional repair and utility effects. Designs are documented in ARMOR.md.
Legacy armor references vanilla iron armor textures and tints them at render
time; those vanilla textures are not included. Material render-info palettes
and field naming now also match the minimum supported Tinkers versions.

Configurable traits, dated 2026-10-14 (2.0.0-port.5): 126 numeric settings
covering all tool and armor traits; Forge world-specific SERVER configuration;
validated atomic tuning snapshots; automatic stat rebuilds for carried items;
current-value descriptions for customized traits. The corresponding source
includes the complete configuration template, generator and regression checks.

Tinkers' Construct and Mantle are separate, required dependencies. Their binaries
are not included in the TAIGA mod or the corresponding-source distribution.
