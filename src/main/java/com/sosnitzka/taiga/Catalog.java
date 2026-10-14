package com.sosnitzka.taiga;
/** Generated from config/materials.json; original TAIGA values are preserved in that table. */
public final class Catalog {
  public record Material(String name, int color, int temperature, boolean ore, boolean deepslate) {}
  public static final Material[] MATERIALS = {
    new Material("basalt", 0xE4DDC3, 550, false, false),
    new Material("tiberium", 0xD4FF00, 500, true, false),
    new Material("aurorium", 0xEFAE94, 750, true, false),
    new Material("prometheum", 0x372C49, 850, true, false),
    new Material("duranite", 0xACDDEB, 1400, true, false),
    new Material("valyrium", 0xE85C31, 1500, true, false),
    new Material("vibranium", 0xBAD2D9, 1500, true, true),
    new Material("karmesine", 0xEB484A, 750, true, false),
    new Material("jauxum", 0x68C663, 750, true, false),
    new Material("ovium", 0x7D77C3, 750, true, false),
    new Material("terrax", 0xA5978E, 850, false, false),
    new Material("palladium", 0xEE8736, 690, true, false),
    new Material("uru", 0xBFB9F0, 1200, true, false),
    new Material("osram", 0xFFBC90, 800, true, false),
    new Material("abyssum", 0x21BCC2, 700, true, false),
    new Material("eezo", 0x58798A, 500, true, false),
    new Material("triberium", 0x66F136, 550, false, false),
    new Material("fractum", 0xD2C583, 750, false, false),
    new Material("violium", 0xBFB0E2, 850, false, false),
    new Material("proxii", 0xCEFDE1, 750, false, false),
    new Material("tritonite", 0x8EDEFF, 550, false, false),
    new Material("ignitz", 0xFF284B, 950, false, false),
    new Material("imperomite", 0x7FEFA0, 900, false, false),
    new Material("solarium", 0xFEF864, 1500, false, false),
    new Material("nihilite", 0x6645BA, 580, false, false),
    new Material("adamant", 0xFF8EFE, 1500, false, false),
    new Material("dyonite", 0xFFBD3F, 660, false, false),
    new Material("nucleum", 0xE6FF40, 500, false, false),
    new Material("lumix", 0xF9F3CC, 500, false, false),
    new Material("seismum", 0xECBCA8, 720, false, false),
    new Material("astrium", 0x8F385F, 680, false, false),
    new Material("niob", 0x7398B9, 550, false, false),
    new Material("yrdeen", 0x8F385F, 710, false, false),
    new Material("iox", 0x99323C, 900, false, false),
    new Material("meteorite", 0x374F3D, 950, false, false),
    new Material("obsidiorite", 0x224853, 1050, false, false),
    new Material("magma", 0xFFC000, 1500, false, false),
    new Material("nitronite", 0xCCFF00, 1500, false, false),
    new Material("dilithium", 0x79AEA6, 1500, true, true)
  };
  public static Material find(String name) { for (Material material : MATERIALS) if (material.name().equals(name)) return material; throw new IllegalArgumentException(name); }
  private Catalog() {}
}
