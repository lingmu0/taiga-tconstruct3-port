"""Emit the deliberately small adapters for Forge and TiC API differences."""
from pathlib import Path
import armor_platform
ROOT = Path(__file__).resolve().parents[1]

COMMON_IMPORTS = '''package com.sosnitzka.taiga;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.core.Direction;
import net.minecraftforge.event.entity.player.PlayerEvent;
import slimeknights.tconstruct.library.modifiers.Modifier;
import slimeknights.tconstruct.library.modifiers.ModifierEntry;
import slimeknights.tconstruct.library.tools.context.*;
import slimeknights.tconstruct.library.tools.nbt.*;
import slimeknights.tconstruct.library.tools.stat.ModifierStatsBuilder;
import slimeknights.tconstruct.library.tools.SlotType;
import java.util.List;
'''

HOOKS = '''import slimeknights.tconstruct.library.modifiers.ModifierHooks;
import slimeknights.tconstruct.library.module.ModuleHookMap;
import slimeknights.tconstruct.library.modifiers.hook.build.*;
import slimeknights.tconstruct.library.modifiers.hook.combat.*;
import slimeknights.tconstruct.library.modifiers.hook.interaction.InventoryTickModifierHook;
import slimeknights.tconstruct.library.modifiers.hook.mining.*;
import slimeknights.tconstruct.library.modifiers.hook.behavior.*;
public final class TaigaModifier extends Modifier implements ToolStatsModifierHook, VolatileDataModifierHook,
    MeleeDamageModifierHook, MeleeHitModifierHook, InventoryTickModifierHook, BlockBreakModifierHook,
    ProcessLootModifierHook, LootingModifierHook, ToolDamageModifierHook, BreakSpeedModifierHook {
  private final Trait trait;
  public TaigaModifier(Trait trait) { this.trait = trait; }
  @Override protected void registerHooks(ModuleHookMap.Builder builder) {
    builder.addHook(this, ModifierHooks.TOOL_STATS, ModifierHooks.VOLATILE_DATA, ModifierHooks.MELEE_DAMAGE,
        ModifierHooks.MELEE_HIT, ModifierHooks.INVENTORY_TICK, ModifierHooks.BLOCK_BREAK, ModifierHooks.PROCESS_LOOT,
        ModifierHooks.WEAPON_LOOTING, ModifierHooks.TOOL_DAMAGE, ModifierHooks.BREAK_SPEED);
  }
  @Override public void addToolStats(IToolContext context, ModifierEntry entry, ModifierStatsBuilder builder) {
    TraitLogic.stats(trait, entry.getLevel(), builder);
  }
  @Override public void addVolatileData(IToolContext context, ModifierEntry entry, @DATA@ data) {
    if (trait == Trait.ARCANE) data.addSlots(SlotType.UPGRADE, TraitTuning.i("tools.arcane.slotsPerLevel") * entry.getLevel());
  }
  @Override public float getMeleeDamage(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float base, float damage) {
    return TraitLogic.damage(trait, tool, entry.getLevel(), context, damage);
  }
  @Override public float beforeMeleeHit(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float damage, float base, float knockback) {
    return TraitLogic.knockback(trait, entry.getLevel(), knockback);
  }
  @Override public void afterMeleeHit(IToolStackView tool, ModifierEntry entry, ToolAttackContext context, float damage) {
    TraitLogic.hit(trait, tool, entry.getLevel(), context);
  }
  @Override public void onInventoryTick(IToolStackView tool, ModifierEntry entry, Level world, LivingEntity holder, int slot, boolean selected, boolean correct, ItemStack stack) {
    TraitLogic.tick(trait, tool, entry.getLevel(), world, holder, correct);
  }
  @Override public void afterBlockBreak(IToolStackView tool, ModifierEntry entry, ToolHarvestContext context) {
    TraitLogic.broken(trait, tool, entry.getLevel(), context);
  }
  @Override public void processLoot(IToolStackView tool, ModifierEntry entry, List<ItemStack> drops, LootContext context) {
    TraitLogic.loot(trait, entry.getLevel(), drops, context);
  }
  @Override public int updateLooting(IToolStackView tool, ModifierEntry entry, LootingContext context, int looting) {
    return looting + (trait == Trait.SLAUGHTERING ? TraitTuning.i("tools.slaughtering.lootingPerLevel") * entry.getLevel() : 0);
  }
  @Override public int onDamageTool(IToolStackView tool, ModifierEntry entry, int amount, LivingEntity holder) {
    return TraitLogic.durability(trait, entry.getLevel(), amount);
  }
  @Override public void onBreakSpeed(IToolStackView tool, ModifierEntry entry, PlayerEvent.BreakSpeed event, Direction side, boolean effective, float multiplier) {
    event.setNewSpeed(TraitLogic.mining(trait, tool, entry.getLevel(), (net.minecraft.world.entity.player.Player)event.getEntity(), event.getNewSpeed(), effective));
  }
}
'''

LEGACY = '''public final class TaigaModifier extends Modifier {
  private final Trait trait;
  public TaigaModifier(Trait trait) { this.trait = trait; }
  @Override public void addToolStats(ToolRebuildContext context, int level, ModifierStatsBuilder builder) { TraitLogic.stats(trait, level, builder); }
  @Override public void addVolatileData(ToolRebuildContext context, int level, ModDataNBT data) {
    if (trait == Trait.ARCANE) data.addSlots(SlotType.UPGRADE, TraitTuning.i("tools.arcane.slotsPerLevel") * level);
  }
  @Override public float getEntityDamage(IToolStackView tool, int level, ToolAttackContext context, float base, float damage) { return TraitLogic.damage(trait, tool, level, context, damage); }
  @Override public float beforeEntityHit(IToolStackView tool, int level, ToolAttackContext context, float damage, float base, float knockback) { return TraitLogic.knockback(trait, level, knockback); }
  @Override public int afterEntityHit(IToolStackView tool, int level, ToolAttackContext context, float damage) { TraitLogic.hit(trait, tool, level, context); return 0; }
  @Override public void onInventoryTick(IToolStackView tool, int level, Level world, LivingEntity holder, int slot, boolean selected, boolean correct, ItemStack stack) { TraitLogic.tick(trait, tool, level, world, holder, correct); }
  @Override public void afterBlockBreak(IToolStackView tool, int level, ToolHarvestContext context) { TraitLogic.broken(trait, tool, level, context); }
  @Override public List<ItemStack> processLoot(IToolStackView tool, int level, List<ItemStack> drops, LootContext context) { TraitLogic.loot(trait, level, drops, context); return drops; }
  @Override public int getLootingValue(IToolStackView tool, int level, LivingEntity holder, Entity target, DamageSource source, int looting) { return looting + (trait == Trait.SLAUGHTERING ? TraitTuning.i("tools.slaughtering.lootingPerLevel") * level : 0); }
  @Override public int onDamageTool(IToolStackView tool, int level, int amount, LivingEntity holder) { return TraitLogic.durability(trait, level, amount); }
  @Override public void onBreakSpeed(IToolStackView tool, int level, PlayerEvent.BreakSpeed event, Direction side, boolean effective, float multiplier) {
    event.setNewSpeed(TraitLogic.mining(trait, tool, level, event.getPlayer(), event.getNewSpeed(), effective));
  }
}
'''

PLATFORM = '''package com.sosnitzka.taiga;
import java.util.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;
import net.minecraftforge.fluids.ForgeFlowingFluid;
@IMPORTS@
public final class Platform {
  private static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(ForgeRegistries.FLUIDS, Taiga.ID);
  private static final Map<String, RegistryObject<FlowingFluid>> SOURCES = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<FlowingFluid>> FLOWING = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<Item>> BUCKETS = new LinkedHashMap<>();
  private static final Map<String, RegistryObject<LiquidBlock>> BLOCKS = new LinkedHashMap<>();
  @FIELDS@
  public static Item.Properties itemProperties() { return new Item.Properties()@ITEM_PROPS@; }
  public static BlockBehaviour.Properties blockProperties() { return @BLOCK_PROPS@; }
  public static Component translate(String key, Object... args) { return @TRANSLATE@; }
  public static void burn(net.minecraft.world.entity.Entity entity) { entity.hurt(@LAVA_DAMAGE@, 4f); }
  public static ItemStack smelt(ItemStack stack, Level world) {
    return world.getRecipeManager().getRecipeFor(RecipeType.SMELTING, new SimpleContainer(stack), world)
        .map(recipe -> { ItemStack out = recipe.@RESULT@.copy(); out.setCount(Math.min(out.getMaxStackSize(), out.getCount() * stack.getCount())); return out; })
        .orElse(ItemStack.EMPTY);
  }
  public static void register(IEventBus bus) {
    for (Catalog.Material material : Catalog.MATERIALS) {
      String name = material.name();
      @TYPE_REGISTER@
      SOURCES.put(name, FLUIDS.register("molten_" + name, () -> new ForgeFlowingFluid.Source(properties(name))));
      FLOWING.put(name, FLUIDS.register("flowing_molten_" + name, () -> new ForgeFlowingFluid.Flowing(properties(name))));
      BUCKETS.put(name, Taiga.ITEMS.register("molten_" + name + "_bucket", () -> new BucketItem(SOURCES.get(name), itemProperties().stacksTo(1).craftRemainder(Items.BUCKET))));
      BLOCKS.put(name, Taiga.BLOCKS.register("molten_" + name, () -> new MoltenBlock(SOURCES.get(name), @LIQUID_PROPS@.noCollission().strength(100).lightLevel(state -> 10).@NO_LOOT@())));
    }
    FLUIDS.register(bus);
    @TYPE_BUS@
    @TAB_BUS@
    @WORLDGEN@
  }
  private static ForgeFlowingFluid.Properties properties(String name) {
    Catalog.Material material = Catalog.find(name);
    return new ForgeFlowingFluid.Properties(@FLUID_PROPS@)
        .bucket(BUCKETS.get(name)).block(BLOCKS.get(name)).tickRate(20).slopeFindDistance(2).levelDecreasePerBlock(2);
  }
  @CLIENT_RENDERING@
}
'''

TYPE_REGISTER = '''TYPES.put(name, TYPES_REGISTER.register("molten_" + name, () -> new FluidType(FluidType.Properties.create().density(2000).viscosity(10000).temperature(material.temperature() + 273).lightLevel(10).sound(net.minecraftforge.common.SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL_LAVA).sound(net.minecraftforge.common.SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY_LAVA)) {
        @Override public void initializeClient(java.util.function.Consumer<IClientFluidTypeExtensions> consumer) {
          consumer.accept(new IClientFluidTypeExtensions() {
            @Override public ResourceLocation getStillTexture() { return new ResourceLocation("minecraft", "block/water_still"); }
            @Override public ResourceLocation getFlowingTexture() { return new ResourceLocation("minecraft", "block/water_flow"); }
            @Override public int getTintColor() { return 0xFF000000 | material.color(); }
          });
        }
      }));'''

def main():
    for mc in ('1.18.2', '1.19.2', '1.20.1'):
        path = ROOT / f'src/platform/{mc}/java/com/sosnitzka/taiga'
        path.mkdir(parents=True, exist_ok=True)
        armor_platform.generate(mc, path)
        modifier = COMMON_IMPORTS + (LEGACY if mc == '1.18.2' else HOOKS.replace('@DATA@', 'ToolDataNBT' if mc == '1.20.1' else 'ModDataNBT'))
        modifier = modifier.replace('  private final Trait trait;', '''  @Override public List<net.minecraft.network.chat.Component> getDescriptionList(int level) {
    return TraitDescriptions.describe("tools."+trait.id, super.getDescriptionList());
  }
  private final Trait trait;''')
        (path / 'TaigaModifier.java').write_text(modifier, encoding='utf-8')
        old = mc == '1.18.2'
        tab = mc == '1.20.1'
        values = {
            'IMPORTS': ('import net.minecraftforge.fluids.FluidAttributes;\nimport net.minecraft.network.chat.TranslatableComponent;'
                        if old else 'import net.minecraftforge.fluids.FluidType;\nimport net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;'),
            'FIELDS': ('private static final DeferredRegister<FluidType> TYPES_REGISTER = DeferredRegister.create(ForgeRegistries.Keys.FLUID_TYPES, Taiga.ID);\nprivate static final Map<String, RegistryObject<FluidType>> TYPES = new LinkedHashMap<>();' if not old else ''),
            'ITEM_PROPS': '' if tab else '.tab(TAB)',
            'BLOCK_PROPS': 'BlockBehaviour.Properties.of()' if tab else 'BlockBehaviour.Properties.of(Material.STONE)',
            'TRANSLATE': 'new TranslatableComponent(key, args)' if old else 'Component.translatable(key, args)',
            'LAVA_DAMAGE': 'entity.damageSources().lava()' if tab else 'net.minecraft.world.damagesource.DamageSource.LAVA',
            'RESULT': 'getResultItem(world.registryAccess())' if tab else 'getResultItem()',
            'TYPE_REGISTER': '' if old else TYPE_REGISTER,
            'TYPE_BUS': '' if old else 'TYPES_REGISTER.register(bus);',
            'TAB_BUS': 'TABS.register(bus);' if tab else '',
            'WORLDGEN': 'NativeWorldgen.register(bus);' if old else '',
            'CLIENT_RENDERING': '''@net.minecraftforge.fml.common.Mod.EventBusSubscriber(modid = Taiga.ID, bus = net.minecraftforge.fml.common.Mod.EventBusSubscriber.Bus.MOD, value = net.minecraftforge.api.distmarker.Dist.CLIENT)
  public static final class ClientRendering {
    @net.minecraftforge.eventbus.api.SubscribeEvent
    public static void setup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
      event.enqueueWork(() -> Taiga.SOLIDS.forEach((name, block) -> {
        if (name.endsWith("_ore")) net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(block.get(), net.minecraft.client.renderer.RenderType.cutoutMipped());
      }));
    }
  }''' if old else '',
            'NO_LOOT': 'noDrops' if old else 'noLootTable',
            'LIQUID_PROPS': 'BlockBehaviour.Properties.of().liquid().replaceable()' if tab else 'BlockBehaviour.Properties.of(Material.LAVA)',
            'FLUID_PROPS': ('SOURCES.get(name), FLOWING.get(name), FluidAttributes.builder(new ResourceLocation("minecraft", "block/water_still"), new ResourceLocation("minecraft", "block/water_flow")).color(0xFF000000 | material.color()).temperature(material.temperature() + 273).density(2000).viscosity(10000).luminosity(10).sound(SoundEvents.BUCKET_FILL_LAVA, SoundEvents.BUCKET_EMPTY_LAVA)' if old else 'TYPES.get(name), SOURCES.get(name), FLOWING.get(name)'),
        }
        if tab:
            values['FIELDS'] += '''
  private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(net.minecraft.core.registries.Registries.CREATIVE_MODE_TAB, Taiga.ID);
  private static final RegistryObject<CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
      .title(Component.translatable("itemGroup.taiga")).icon(() -> new ItemStack(Taiga.block("vibranium_ore")))
      .displayItems((parameters, output) -> Taiga.ITEMS.getEntries().forEach(item -> output.accept(item.get()))).build());
'''
        else:
            values['FIELDS'] += '''
  private static final CreativeModeTab TAB = new CreativeModeTab("taiga") {
    @Override public ItemStack makeIcon() { return new ItemStack(Taiga.block("vibranium_ore")); }
  };
'''
        text = PLATFORM
        for key, value in values.items(): text = text.replace('@' + key + '@', value)
        (path / 'Platform.java').write_text(text, encoding='utf-8')
    print('Generated three platform adapters.')

if __name__ == '__main__': main()
