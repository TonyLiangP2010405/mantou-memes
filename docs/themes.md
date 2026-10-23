# 表情选题调研

调研日期：2026-10-23。范围为 GitHub 模板生态、哔哩哔哩创作者/素材平台、抖音创作者内容、LINE 官方及创作者商店。用于建立选题池，不代表全网穷尽、热度排名或授权取得；搜索摘要没有用于推导播放量或流行趋势。

## 技术依据

- [上游 README](https://github.com/MemeCrafters/meme-generator)：明确支持独立外部表情仓库。
- [模板注册与外部加载器](https://github.com/MemeCrafters/meme-generator/blob/main/meme_generator/manager.py)：`add_meme`、`load_memes`，支持目录中的 Python 包。
- [上游输入、输出协议](https://github.com/MemeCrafters/meme-generator/blob/main/meme_generator/meme.py)：接收图片字节/路径，模板得到 `BuildImage`，返回 `BytesIO`。
- [官方额外模板库](https://github.com/MemeCrafters/meme-generator-contrib)、[meme_emoji](https://github.com/anyliew/meme_emoji)、[tudou-meme](https://github.com/LRZ9712/tudou-meme)：验证独立库这一交付方式与现有生态一致。本项目没有复制这些库的素材。

## 场景来源

下列内容用于理解表情的使用场景；标题与主题由作者/平台公开发布。模板的文案和绘制由本项目实现，来源原图不在仓库中。

| 来源 | 可借鉴的使用场景 | 转化方式 |
|---|---|---|
| [B站：这些表情包在演我打工的精神状态](https://www.bilibili.com/video/BV16h4y1V7je/) | 打工、精神状态、自嘲 | 工牌、精神工资条、电量 |
| [B站：以为在喊收到，实际阴阳怪气](https://www.bilibili.com/video/BV1BqwDeqEeH/) | 收到、被动回复、表面配合 | 群聊小票、已读乱回 |
| [抖音创作者：表情包演我精神状态](https://www.douyin.com/video/7686713809831112015) | 吐槽、抬杠、发疯 | 红温 GIF、满头问号 |
| [LINE 创作者商店：打工人精神状态五·已读乱回](https://store.line.me/stickershop/product/30924901/zh-Hant) | 不知道怎么回、闲聊回复 | 已读乱回小票、加载中 |
| [LINE 创作者商店：水豚滚滚的日常生活](https://store.line.me/stickershop/product/1179565/zh-Hant) | 水豚、松弛、日常陪伴 | 几何绘制的泡汤水豚 |
| [LINE 台湾官方：猫狗大战篇](https://line-tw-official.weblog.to/archives/1007881247.html) | 动物、惊讶、幸运、搞笑 | 头像结合猫耳、探头 |
| [B站官方素材酷](https://cool.bilibili.com/video) | 红温、擦汗、可爱、应援、爱心、夸夸 | 红温、双人应援、夸夸奖状 |
| [游戏官方B站：挑战给路人发抽象表情包](https://www.bilibili.com/video/BV1Wuuj6CE26/) | 游戏群聊、抽象互动 | 双头像对决、围观吃瓜 |

## 首批已实现：20 个

| 分类 | 模板 | 输入 | 输出 |
|---|---|---|---|
| 情绪 | 社交电量、本人已下线、满头问号 | 单头像 | PNG |
| 动态情绪 | 正在红温、脑子加载中 | 单头像 | 8 帧循环 GIF |
| 打工与摆烂 | 摸鱼工牌 | 单头像 | PNG |
| 打工与摆烂 | 精神工资条、今日摆烂计划 | 文字 | PNG |
| 群聊回复 | 已读乱回小票 | 文字 | PNG |
| 夸夸与抽象 | 夸夸奖状、头上长草 | 单头像 | PNG |
| 动物 | 水豚泡汤、猫猫探头 | 单头像 | PNG |
| 馒头与桃子 | 蒸笼认领、今日桃气 | 单头像 | PNG |
| 双人互动 | 双人应援、给你充电、菜鸡对决 | 双头像 | PNG |
| 生活 | 吃瓜席位、关机睡觉 | 单头像 | PNG |

## 后续候选：未实现

以下是从使用场景延伸的选题，不表示已有成品或经过热度验证。保留在文档中，避免把未实现功能写进目录。

- 群聊反应：收到但没完全收到、偷偷窥屏、前排搬凳子、散会、撤回失败、礼貌微笑。
- 打工学习：周一开机失败、周五下班冲刺、会议分身、DDL追赶、交作业、考试锦鲤。
- 情绪抽象：CPU烧了、情绪稳定但裂开、灵魂出窍、暂停一下、回血、重启人生。
- 动物治愈：狗狗摇尾巴、猫猫伸爪、企鹅排队、海豹鼓掌、仓鼠囤粮、水豚发呆。
- 游戏互动：队友救一下、操作失误复盘、胜利合影、败者采访、欧气借用、抽卡保底。
- 关系互动：贴贴、隔空击掌、给你递奶茶、接住好运、生日应援、谢谢老板。
- 馒头专属：蒸笼躲猫猫、桃气补给、闹别扭待哄、好感升级、偏爱认证、出锅警告。

## 取舍

首批优先让头像/文字真实参与生成，保证没有图片素材下载依赖，适配转盘自动提供的输入。带复杂真人/影视抠图、指定角色底图、三张以上图片、强制额外参数的方案保留到有明确素材和交互需求时再实现。
