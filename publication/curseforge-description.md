# TAIGA — Tinkers' Alloying Addon: Unofficial Forge Port

An independent **GPLv3 port of the original Tinkers' Alloying Addon (TAIGA)** for Minecraft **1.18.2, 1.19.2 and 1.20.1**, using **Forge and Tinkers' Construct 3**.

Original TAIGA by Zkaface, IdleGandalf / randomtz and contributors. This project is an unofficial continuation and is not a release by the original authors.

## Features

- 30 Tinkers' tool materials, with support for heads, handles, bindings, bow limbs and grips.
- 37 adapted tool traits, including bounded Soul Eater growth, conditional repairs, teleportation and mining effects.
- Armor designs for all 30 tool materials, plus 18 dedicated armor traits covering defense, retaliation, mobility, utility and recovery.
- 39 molten fluids and buckets, 37 solid material families and 28 alloy recipes.
- 17 ore blocks, including deepslate vibranium and dilithium, meteorite deposits and End deposits.
- Modern vanilla host textures for stone, deepslate, andesite, granite, diorite and netherrack ores.
- English and Simplified Chinese translations.
- **126 configurable trait values** in the world-specific `serverconfig/taiga-traits.toml`. Copy the supplied template to `defaultconfigs/` before creating new worlds. See the configuration guide in the source repository.

## Armor behavior by Minecraft version

**1.19.2 / 1.20.1:** materials integrate with Tinkers' native armor plating and maille. Mix materials through the normal Tinkers' armor workflow.

**1.18.2:** the supported Tinkers' version uses fixed-material armor. This port adds 30 modifiable armor sets (120 pieces), crafted using the corresponding material's ingots and chains. Upgrade and repair them in the Tinkers' workstations.

## Requirements

| Minecraft | Forge build baseline | Minimum Tinkers' Construct | Minimum Mantle |
|---|---|---|---|
| 1.18.2 | 40.1.92 | 3.6.4.113 | 1.9.42 |
| 1.19.2 | 43.3.0 | 3.8.2.37 | 1.10.35 |
| 1.20.1 | 47.1.3 | 3.9.2.37 | 1.11.43 |

Install the matching Minecraft-version file on both client and server. Tinkers' Construct and Mantle are required and are not bundled. Use Java 17. Install only one TAIGA mod in an instance; this port retains the `taiga` mod ID.

The mod's own Forge loader range starts at the corresponding major version. Dependencies still enforce their own Forge requirements. Supported Tinkers' ranges are `[3.6.4.113,3.8)`, `[3.8.2.37,3.9)`, and `[3.9.2.37,3.13)` respectively.

## Source and license

- [Public source repository](https://github.com/lingmu0/taiga-tconstruct3-port)
- [Matching source archives and configuration template](https://github.com/lingmu0/taiga-tconstruct3-port/releases)
- [Original TAIGA source](https://somegit.dev/TAIGA/TAIGA)
- License: **GPL-3.0-only**. Original author notices and the license are retained. Modpacks and third-party downloads are permitted under the license.

This initial public build is a **beta**. All three versions pass compilation, resource checks and non-launch logic tests; in-game visuals, combat interactions and multiplayer have not yet been verified. Ore-generation changes apply to newly generated chunks.
