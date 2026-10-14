# 词条数值配置

`taiga-traits.toml` 提供 126 项设置，覆盖 37 个工具词条和 18 个盔甲词条的效果数值。默认值保持 port.4 的平衡设计。

## 使用

- 新建世界之前，把随发布包提供的 `taiga-traits.toml` 放进 Minecraft 实例的 `defaultconfigs/`。
- 已有单人世界：修改 `saves/<世界名>/serverconfig/taiga-traits.toml`。
- 专用服务器：修改 `<世界目录>/serverconfig/taiga-traits.toml`，默认世界目录为 `world/`。

首次加载世界时，Forge 自动生成这个服务端配置，并在玩家连接时同步给客户端。修改后重启世界或服务器，确保所有客户端收到一致数值。文件监控也会重新加载合法修改；在线客户端需要重新连接才能保证配置提示与服务端一致。

已有工具及盔甲在进入实体背包或装备栏后自动检查配置版本，最迟一秒内重新计算耐久和槽位。箱子里的装备在取出后更新；不清除噬魂成长或已经安装的强化。降低槽位可能使装备的已用槽位超过新上限，需在工匠站调整强化。

`config/taiga-common.toml` 现在保留特殊矿床开关。旧版 `soulEaterDamageCap` 与 `teleportCooldown` 的自定义值需分别迁移到新文件的 `tools.souleater.damageCapPerLevel` 与 `tools.ported.cooldownTicks`。

## 示例

```toml
[tools.souleater]
damageCapPerLevel = 10.0
gainPerKillCap = 0.1
healthDivisor = 400.0

[tools.ported]
distance = 8
durabilityCost = 30
cooldownTicks = 400

[armor_rules]
maximumTotalLevel = 4
maximumPieceLevel = 2
maximumDamageReduction = 0.2

[armor.reactive]
damagePerLevel = 0.25
cooldownTicks = 40
```

上例把噬魂上限降为每级 10 点，传送冷却改为 20 秒，TAIGA 额外盔甲减伤上限改为 20%，反伤改为每级 0.25 点且冷却 2 秒。

## 单位与范围

- 概率和比例用小数：`0.15` 为 15%，`1.0` 为 100%。
- `Ticks` 为游戏刻，20 刻通常为 1 秒；`Seconds` 为秒。
- 生命和伤害数值以半颗心为单位：`2.0` 为一颗心。
- 效果 `amplifier = 0` 为 I 级，`1` 为 II 级。
- 比例增量和乘数不同：`damageBonusPerLevel = 0.2` 表示每级额外 20%；`durabilityMultiplierPerLevel = 0.8` 表示每级乘 80%。

模板中每一项都带中文注释和合法范围。范围外的值由 Forge 纠正；运行时快照拒绝非法数值并保留上一次有效配置。概率计算限制在 0～100%，移动速度不会因惩罚变为负数，击退抗性不会超过 100%。

全部盔甲穿戴效果的叠加上限由 `armor_rules` 控制。单件坚固、符文槽、光合按 `maximumPieceLevel` 计算；其余总等级按 `maximumTotalLevel` 计算。反伤仍有循环保护，任何配置下都不会互相无限反伤。

自定义词条在装备的详细说明中显示当前配置数值。匠魂宝典及本文以默认设计为参考；完整默认值见 [config/taiga-traits.toml](config/taiga-traits.toml)。材料基础属性和词条绑定仍通过数据包控制，不属于本次数值 TOML。
