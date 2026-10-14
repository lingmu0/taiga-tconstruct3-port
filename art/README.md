# port.3 矿石素材

使用内置 `image_gen` 工具制作，模式为透明背景编辑，参考本项目保留的原版 TAIGA 矿石纹理。8 张原稿位于 `art/source/`，完整提示词和参考路径见 [prompts.json](prompts.json)。泰伯利亚条目记录的是本次编辑规格，其余条目保存调用时的原始提示词。

游戏使用的最终文件位于 `src/main/resources/assets/taiga/textures/block/ore_overlay/`：`tiberium.png`、`prometheum.png`、`valyrium.png`、`karmesine.png`、`jauxum.png`、`ovium.png`、`vibranium.png`、`dilithium.png`。原稿用最近邻采样缩至 16×16 RGBA，保留生成的透明通道；不进行平滑、补画或重新着色。振金和双锂在普通矿石与深层矿石之间共享同一矿粒层。

矿石模型引用现代 Minecraft 的下界岩、安山岩、花岗岩、闪长岩、石头或深板岩底纹。三个版本共用矿粒，1.18.2 通过客户端渲染层注册，1.19.2／1.20.1 通过模型的 `render_type` 启用 `cutout_mipped`。

可选素材处理（需要 Pillow，正常编译无需安装）：

```powershell
python tools/prepare_ore_art.py
python tools/preview_ores.py '<本机 Minecraft client.jar 路径>'
```

第二条命令把本机原版纹理与矿粒按模型方式渲染到 `build/qa/ore-comparison.png`，供纹理检查；它不是游戏截图。预览文件和原版底纹不进入发布包。素材原稿和最终 PNG 均包含在对应源码包中。
