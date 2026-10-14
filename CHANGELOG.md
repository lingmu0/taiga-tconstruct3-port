# Changelog

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
