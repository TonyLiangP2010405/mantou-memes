# mantou-memes

适用于 [MemeCrafters/meme-generator](https://github.com/MemeCrafters/meme-generator) **0.1.14 / 0.1.x** 的独立表情模板库。现有 **1620 个模板：921 个 PNG、699 个循环 GIF**。

最新增加 **500 个双人、多人模板：434 个循环 GIF、66 个 PNG**，其中 **379 个双人、121 个三至十人模板**。编号 **`mantou_group_001`–`mantou_group_500`**，关键词 **馒头同框001–馒头同框500**。仅换头像，不接受文字输入；动图按每个保留帧记录角色位置。插件中双人依次使用 bot 与触发者头像，多人的其余角色从本群好感榜随机补齐，排除重复成员。两个主要角色优先使用 bot 与触发者，榜单人数不足时跳过该模板。[查看本批 500 个](GROUPS_CATALOG.md) · [对齐与去重复核](docs/groups-review.md)。

上一批增加 **500 个单头像模板：62 个真实循环 GIF、438 个 PNG**，覆盖 52 个图集。编号 **`mantou_action_501`–`mantou_action_1000`**，关键词 **馒头动作501–馒头动作1000**。仅换头像，不接受文字输入。企鹅、动漫、猫狗、影视与手势等素材经过居中原图/换头像对照复核；动图按全部保留帧检查，修正了探头猫桌沿、狗狗栏杆、巴哥犬双眼以及卡通头部定位。[查看本批 500 个](ACTIONS_2_CATALOG.md) · [本批复核记录](docs/actions-next-review.md)。

此前新增 **500 个单头像模板：194 个循环 GIF、306 个 PNG**，来自 45 个公开图集。人物、萌娃、熊猫、猫狗、武侠、影视与手势等素材逐张筛选、裁切并校准，动图按保留帧分别定位，卡通头部使用轮廓蒙版。**这一批只接受 1 张头像，不接受文字输入，不绘制昵称或文案。** [查看新增 500 个](ACTIONS_CATALOG.md) · [本批对齐复核](docs/actions-review.md)。

此前新增的 **100 个换头像模板：98 个单头像、2 个双头像**。60 个熊猫头、25 个白色小人、15 个猫猫底图逐张裁切、清理旧字幕并校准头像区域，保留原图动作和背景，其中 7 个为 GIF。**这一批不接受文字输入，不绘制昵称或文案。** [查看新增 100 个](DUEL_CATALOG.md) · [查看逐图来源](ASSET_SOURCES.md)。此前 20 个绘制模板继续保留。

模板会真正替换输入头像或文字，不是只能转发的成品图库。通过上游公开的 `add_meme` 注册、`load_memes` 加载；无需 fork 或修改生成器。所有键名带 `mantou_` 前缀，避免和现有库撞名。

![模板总览](previews/overview.jpg)

完整动图和单张预览：[CATALOG.md](CATALOG.md)，提供 81 页总览。选题来源与范围：[主题调研](docs/themes.md)。

GitHub 的源码 ZIP 不包含预览图库，减少插件首次下载的体积；运行所需的代码、字体和底图完整保留。在线仓库可查看全部预览，`git clone` 也会取得完整图库。

2026-10-24 对新增 100 个模板完成了一轮逐图复核，重新校准 87 个模板的头像坐标，并为 23 个模板添加手势、帽子或道具的前景遮挡区域；修正旋转时出现的白色三角。对照图和检查范围见 [头像对齐复核](docs/alignment-review.md)。

## 使用

需要 Python 3.9+，使用 Python 版 `meme-generator`，不是 `meme-generator-rs`。

Linux 上的上游 Skia 还需要系统图形运行库。例如 Debian / Ubuntu：

```bash
sudo apt-get update
sudo apt-get install -y libegl1 libgl1
```

```bash
git clone https://github.com/TonyLiangP2010405/mantou-memes.git
cd mantou-memes
python -m pip install -r requirements.txt
```

Python 中使用（从项目根目录运行）：

```python
from pathlib import Path
from meme_generator import get_meme, load_memes

load_memes(Path("memes").resolve())

# 单头像模板；也可传图片字节或 BytesIO。
result = get_meme("mantou_battery")(images=[Path("avatar.png")])
Path("result.png").write_bytes(result.getvalue())

# 双头像模板：第一张在左，第二张在右。
result = get_meme("mantou_charge")(images=[Path("bot.png"), Path("friend.png")])
Path("charge.png").write_bytes(result.getvalue())

# 多人同框：示例需 10 张不同头像；具体数量可查模板参数或目录。
result = get_meme("mantou_group_001")(images=[Path(f"avatar-{i}.png") for i in range(10)])
Path("group.gif").write_bytes(result.getvalue())

# 动图：mantou_overheat / mantou_loading。
result = get_meme("mantou_loading")(images=[Path("avatar.png")])
Path("loading.gif").write_bytes(result.getvalue())

# 第一批 500 个动作模板：只传参与者头像。
result = get_meme("mantou_action_001")(images=[Path("avatar.png")])
Path("action.gif").write_bytes(result.getvalue())

# 此前新增的网络底图换头像模板：只传图片，不需要文字。
result = get_meme("mantou_duel_006")(images=[Path("avatar.png")])
Path("duel.png").write_bytes(result.getvalue())

# 新增双头像模板：左右两人分别替换。
result = get_meme("mantou_duel_045")(images=[Path("bot.png"), Path("friend.png")])
Path("duel_pair.png").write_bytes(result.getvalue())
```

也可以在上游生成器的 `config.toml` 中，把本仓库 **`memes` 目录的绝对路径**加入 `[meme].meme_dirs`；保留你已有的其他目录。

```toml
[meme]
meme_dirs = ["/path/to/mantou-memes/memes"]
```

关键词、参数数量、标签见 [模板目录](CATALOG.md)。通过机器人命令调用需要机器人端的 memes 插件支持，模板库本身不注册 NoneBot 命令。

## 馒头好感度插件

配套的 [nonebot-plugin-mantou-affection](https://github.com/TonyLiangP2010405/nonebot-plugin-mantou-affection) 可以通过外部仓库加载器下载本库的 `memes/` 目录。插件 0.25.0+ 的转盘可使用全部 1620 个模板：

- 纯文字：参与者群昵称。
- 单头像：参与者头像。
- 双头像：机器人头像在左，参与者头像在右。
- 多头像：两个主要角色先用机器人与触发者，其余从本群好感榜随机补齐不同成员；榜单人数不足时跳过对应模板。
- 仍遵循插件的表情确认、免确认白名单、屏蔽词和失败提示。

本库包含完整中文字体、程序绘制代码和已裁切的网络底图，本库自身加载后不需要额外下载字体或背景图。头像输入仍由调用方提供，插件获取 QQ 头像需要网络。上游内置模板的资源下载机制与本库独立。

此前两批各 500 个单头像模板均使用参与者头像；此前 100 个换头像模板中，98 个使用参与者头像，2 个依次使用机器人和参与者头像。网络底图的裁切成品已随库提供，生成时不访问素材来源网站。

插件 0.25.0+ 启动时发现缓存缺少 `mantou_groups` 模块，会自动更新一次；已含新模块的完整缓存继续复用。旧版插件可升级，或停止机器人后删除本插件数据目录下的 **`meme_repos/mantou-memes/`** 再启动。直接使用本库的用户执行 `git pull` 后重启调用方即可。

## 开发与验证

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check .
python tools/generate_previews.py
```

测试通过**真实的上游 `load_memes` 和 `Meme.__call__`**检查注册及输出，覆盖全部模板的 PNG/GIF 解码、长昵称、透明/极小/纵向/JPEG 输入、双头像顺序和非法参数。测试与预览脚本使用临时配置，不会加载用户的第三方模板，也不发起网络请求。

程序绘制的模板在 `memes/mantou/__init__.py` 中维护；换头像模板在 `memes/mantou_duel/templates.json`、`memes/mantou_actions/templates.json` 、`memes/mantou_actions_next/templates.json` 和 `memes/mantou_groups/templates.json` 中维护，包含原图固定提交链接、SHA256、裁切矩形、旧字幕清理区域、头像嵌入矩形及旋转角度。动态头像会随对应帧的位置和角度变化。需要重建裁切素材时，显式运行 `python tools/prepare_duel_assets.py --cache-dir /path/to/cache`，该开发工具才会下载原图；运行时不下载。GIF 超过 16 帧时采样并合并帧时长，单帧 GIF 按静态图处理。

新 500 个模板逐个经过真实后端出图检查，另验证源图及底图 SHA256 去重、逐帧坐标与轮廓边界、实际人脸特征点覆盖、轮廓遮挡和文字拒绝；头像格式变体在共享渲染器的 PNG/GIF 代表模板上检查。

测试逐个验证此前 100 个模板的头像替换位置、双头像顺序、逐帧位置及文字参数拒绝行为，并检查底图去重。另用独立于头像框的原图眼睛、嘴巴与道具像素坐标，检查典型偏位回归及旋转边缘。坐标测试不能代替视觉复核，改动头像位置后还应查看完整预览及 GIF 全部帧。换头像模板接受的头像数量以各模板的固定输入数为准（1–10 张），每个模板保持 512×512，不需要额外文字参数。首批保留模板的原有输入规则保持不变。

## 许可与来源

代码、程序绘制的模板构图、示例头像及本项目新增文案采用 [MIT](LICENSE)。第一批 20 个为程序绘制；此前 1100 个使用 [ChineseBQB](https://github.com/zhaoolee/ChineseBQB) 公开图集；本批 500 个另结合多个公开动漫 GIF 与表情图集制作，底图与其衍生预览的相应权利仍归原作者，具体来源与范围见 [ASSET_SOURCES.md](ASSET_SOURCES.md)，不将第三方图像标记为本项目原创或 MIT 素材。使用者传入的头像归其相应权利人所有。

随库字体 [Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc) 由 Google Fonts 提供，单独遵循 [SIL Open Font License 1.1](memes/mantou/OFL.txt)。原始字体未修改，SHA256：`a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da`。完整字体约 17 MiB，保留字库以支持用户自定义中文昵称。
