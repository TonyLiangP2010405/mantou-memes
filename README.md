# mantou-memes

适用于 [MemeCrafters/meme-generator](https://github.com/MemeCrafters/meme-generator) **0.1.14 / 0.1.x** 的独立表情模板库。现有 **120 个模板：111 个 PNG、9 个循环 GIF**。

最新新增 **100 个网络梗图裁切模板**：60 个熊猫头、25 个白色小人、15 个猫猫，使用昵称生成反问、嫌弃、阴阳、回怼和围观文案，其中 7 个保留原图动作。底图逐张选择并记录裁切区域，[查看新增 100 个](DUEL_CATALOG.md) · [查看逐图来源](ASSET_SOURCES.md)。此前 20 个原创绘制模板继续保留。

模板会真正替换输入头像或文字，不是只能转发的成品图库。通过上游公开的 `add_meme` 注册、`load_memes` 加载；无需 fork 或修改生成器。所有键名带 `mantou_` 前缀，避免和现有库撞名。

![模板总览](previews/overview.jpg)

完整动图和单张预览：[CATALOG.md](CATALOG.md)，提供 6 页总览。选题来源与范围：[主题调研](docs/themes.md)。

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

# 纯文字模板。
result = get_meme("mantou_receipt")(texts=["群友昵称"])
Path("receipt.png").write_bytes(result.getvalue())

# 双头像模板：第一张在左，第二张在右。
result = get_meme("mantou_charge")(images=[Path("bot.png"), Path("friend.png")])
Path("charge.png").write_bytes(result.getvalue())

# 动图：mantou_overheat / mantou_loading。
result = get_meme("mantou_loading")(images=[Path("avatar.png")])
Path("loading.gif").write_bytes(result.getvalue())

# 网络底图回怼模板：输入昵称，生成带该昵称的回怼文案。
result = get_meme("mantou_duel_006")(texts=["群友昵称"])
Path("duel.png").write_bytes(result.getvalue())
```

也可以在上游生成器的 `config.toml` 中，把本仓库 **`memes` 目录的绝对路径**加入 `[meme].meme_dirs`；保留你已有的其他目录。

```toml
[meme]
meme_dirs = ["/path/to/mantou-memes/memes"]
```

关键词、参数数量、标签见 [模板目录](CATALOG.md)。通过机器人命令调用需要机器人端的 memes 插件支持，模板库本身不注册 NoneBot 命令。

## 馒头好感度插件

配套的 [nonebot-plugin-mantou-affection](https://github.com/TonyLiangP2010405/nonebot-plugin-mantou-affection) 可以通过外部仓库加载器下载本库的 `memes/` 目录。转盘原有规则可直接使用全部 120 个模板：

- 纯文字：参与者群昵称。
- 单头像：参与者头像。
- 双头像：机器人头像在左，参与者头像在右。
- 仍遵循插件的表情确认、免确认白名单、屏蔽词和失败提示。

本库包含完整中文字体、程序绘制代码和已裁切的网络底图，本库自身加载后不需要额外下载字体或背景图。头像输入仍由调用方提供，插件获取 QQ 头像需要网络。上游内置模板的资源下载机制与本库独立。

新增 100 个模板使用昵称配文；之前的单头像、双头像模板保持原有输入方式。网络底图的裁切成品已随库提供，生成时不访问素材来源网站。

如果插件此前已缓存旧版模板库，先停止机器人，删除本插件数据目录下的 **`meme_repos/mantou-memes/`** 缓存目录，然后启动机器人，加载器会重新下载当前仓库。直接使用本库的用户执行 `git pull` 后重启调用方即可。

## 开发与验证

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check .
python tools/generate_previews.py
```

测试通过**真实的上游 `load_memes` 和 `Meme.__call__`**检查注册及输出，覆盖全部模板的 PNG/GIF 解码、长昵称、透明/极小/纵向/JPEG 输入、双头像顺序和非法参数。测试与预览脚本使用临时配置，不会加载用户的第三方模板，也不发起网络请求。

程序绘制的模板在 `memes/mantou/__init__.py` 中维护；网络底图模板在 `memes/mantou_duel/templates.json` 中维护，包含原图固定提交链接、SHA256、像素裁切矩形和配文。需要重建裁切素材时，显式运行 `python tools/prepare_duel_assets.py --cache-dir /path/to/cache`，该开发工具才会下载原图；运行时不下载。GIF 超过 16 帧时采样并合并帧时长，单帧 GIF 按静态图处理。

测试逐个验证新增 100 个模板的昵称替换，并对底图内容本身去重，防止用一张底图改文案凑数量。每个模板保持 512×512，输入限制为 1 段文字、1 张头像或 2 张头像之一，不需要强制附加参数。字体不支持的字符（例如部分彩色 emoji）可能显示为缺字框，常用简体中文、拉丁字母和数字可用。

## 许可与来源

代码、程序绘制的模板构图、示例头像及本项目新增文案采用 [MIT](LICENSE)。第一批 20 个为程序绘制；第二批 100 个使用 [ChineseBQB](https://github.com/zhaoolee/ChineseBQB) 公开图集中的不同网络梗图裁切制作，底图与其衍生预览的相应权利仍归原作者，具体来源与范围见 [ASSET_SOURCES.md](ASSET_SOURCES.md)，不将第三方图像标记为本项目原创或 MIT 素材。使用者传入的头像归其相应权利人所有。

随库字体 [Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc) 由 Google Fonts 提供，单独遵循 [SIL Open Font License 1.1](memes/mantou/OFL.txt)。原始字体未修改，SHA256：`a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da`。完整字体约 17 MiB，保留字库以支持用户自定义中文昵称。
