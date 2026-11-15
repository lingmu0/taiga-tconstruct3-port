# Changelog

## 2.0.0-port.6

- Give all 37 tool and 18 armor traits configured colors, using original TAIGA colors for the legacy traits.
- Reduce overworld meteor generation attempts from one in 64 eligible chunks to one in 256; existing chunks are unchanged.
- Add optional Mekanism enrichment chamber and crusher recipes, and Thermal Expansion pulverizer recipes. TAIGA ore blocks produce two dust; ingots produce one dust; two tiberium or dilithium crystals produce one dust.
- Apply recipes to all TAIGA ores, including deepslate variants, and retain the existing Forge, Tinkers' Construct and Mantle requirements.

Validation: all three Forge builds and generated-resource checks. These changes have not been tested in a running game or with the optional mods installed.

## 2.0.0-port.5

- Add `taiga-traits.toml`: 126 runtime numeric settings for all 37 tool traits and 18 armor traits, including damage, chances, durations, cooldowns, durability, slots and stacking limits.
- Use Forge SERVER configuration, isolated per world and synchronized when clients connect.
- Rebuild existing carried/equipped tools and armor after a configuration change without clearing material choices, installed modifiers or Soul Eater progress.
- Show current configured values in detailed descriptions for customized traits.
- Keep the existing lower Forge, Tinkers' Construct and Mantle requirements for all three Minecraft versions.
- Move the old common Soul Eater cap and teleport cooldown settings into the new trait configuration. See CONFIGURATION.md.

Validation: all three Forge builds, resource/schema and packaged-resource checks, trait-setting coverage, armor crafting/repair integration and plain-JDK balance/configuration tests. Minecraft has not been launched for in-game verification.

## 2.0.0-port.4

- Design armor properties for 30 TAIGA tool materials and add 18 dedicated armor traits.
- Integrate native plating and maille on 1.19.2 and 1.20.1.
- Add 30 fixed-material modifiable armor sets on 1.18.2, including crafting and repair.

## 2.0.0-port.3

- Modernize ore host textures and add deepslate vibranium/dilithium ores.
- Localize fluid types and compact custom mining-tier names.
- Restore eezo generation replacing overworld bedrock.
