"""Generate optional Mekanism and Thermal processing recipes.

The ore recipes use individual TAIGA blocks, rather than global ore tags, so
they cannot accidentally replace another mod's recipes for similarly named ores.
"""


def generate(recipe, materials, ore_appearance):
    def machine(kind, name, source, output, *, input_count=1, output_count=1):
        item = {'item': 'taiga:' + source}
        result = {'item': 'taiga:' + output}
        if output_count != 1:
            result['count'] = output_count
        if kind == 'thermal':
            if input_count != 1:
                item['count'] = input_count
            data = {'type': 'thermal:pulverizer', 'ingredient': item, 'result': [result]}
            modid = 'thermal_expansion'
        else:
            ingredient = {'ingredient': item}
            if input_count != 1:
                ingredient['amount'] = input_count
            data = {'type': 'mekanism:' + kind, 'input': ingredient, 'output': result}
            modid = 'mekanism'
        data['conditions'] = [{'type': 'forge:mod_loaded', 'modid': modid}]
        recipe(f'compat/{modid}/{kind}/{name}', data)

    for material in materials:
        name = material['name']
        if name in ('magma', 'nitronite'):
            continue
        # A single ingot and a single dust each melt into 90 mB.
        for kind in ('crushing', 'thermal'):
            machine(kind, name + '_ingot', name + '_ingot', name + '_dust')
        if material['ore']:
            ores = [name + '_ore']
            if ore_appearance.get(name, {}).get('deepslate'):
                ores.append('deepslate_' + name + '_ore')
            for ore in ores:
                for kind in ('enriching', 'crushing', 'thermal'):
                    machine(kind, ore, ore, name + '_dust', output_count=2)
    # Crystals normally drop without Silk Touch and melt into 45 mB each.
    for name in ('tiberium', 'dilithium'):
        for kind in ('crushing', 'thermal'):
            machine(kind, name + '_crystal', name + '_crystal', name + '_dust', input_count=2)
