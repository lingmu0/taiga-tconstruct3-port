"""Texture roots provided by the required Tinkers' Construct mod."""

ROCK_FLUIDS = ('basalt', 'magma', 'meteorite', 'obsidiorite')


def texture_roots(mc):
    if mc == '1.18.2':
        return {'metal': 'tconstruct:block/fluid/molten', 'rock': 'tconstruct:block/fluid/stone'}
    return {'metal': 'tconstruct:fluid/molten', 'rock': 'tconstruct:fluid/molten/stone'}
