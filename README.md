# Brush Cover Pack

一个给 Claude Code 和 Codex 用的 skill：做黑黄笔刷大字风格的视频封面，一次交付 7 个比例，写法符合抖音和小红书的规则。

<p>
  <img src="docs/preview-16x9.jpg" alt="16:9 示例" width="64%">
  <img src="docs/preview-9x16.jpg" alt="9:16 示例" width="22%">
</p>

<sub>示例里的摊主是虚构人物，图片用 skill 自带的 `examples/cover.json` 生成，没有用任何风格参考图。</sub>

## 这种风格

- 左边是黑色斜向笔刷面板，边缘带黄色飞溅
- 面板上四行字：一个黄色小标签，两行白色粗毛笔字（身份、在做什么），一行最大的黄色毛笔字主标题
- 右边是博主本人的暖光写实人像，画面里能看出他在拍视频
- 金色暖光和虚化背景，手机缩略图上也看得清

## 为什么要单独做成 skill

用 AI 出这种封面，难的不是画得好不好看，而是这几件容易出错、出错就要返工的事：

- **限流**：标题写「月入XX万」，或者画面里有 YouTube 图标，抖音和小红书会判作品"不适合推荐"。主标题要改用可核实的增长数据，比如「改版后播放涨34倍」。
- **编造细节**：为了显得在拍视频，AI 会随手画一个手持云台。但博主实际可能只用一台吸在驾驶台上的小相机。器材要照拆解报告里的真实情况画。
- **绿眼睛**：截帧里防蓝光镜片的绿色反光，会被画成绿色的眼睛。
- **裁切**：直接把横版裁成竖版，会切掉字和脸，所以每个比例都要单独重新构图。
- **措辞**：描述真人博主要用中性词，不贴「农村」「出租屋」这类标签。

这些规则都写进了 SKILL.md 和提示词模板，脚本负责重复性的步骤。

## 交付内容

| 用途 | 比例 | 上传 JPG |
| --- | --- | --- |
| YouTube | 16:9 | 1280×720 |
| 抖音横版 | 4:3 | 1440×1080 |
| 视频号主页 | 3:4 | 1080×1440 |
| 竖屏 | 9:16 | 1080×1920 |
| 方图 | 1:1 | 1080×1080 |
| Instagram | 4:5 | 1080×1350 |
| 公众号 | 21:9 | 1260×540 |

每个比例还会保留一张高清 PNG。另外附带 `社媒标题.txt`（抖音、小红书、视频号、B站、公众号、YouTube 的标题、话题和简介）和 `制作说明.txt`。

## 前置条件

- **Codex CLI，并开启图像生成**：出图靠 Codex 内置的 imagegen，走 ChatGPT 订阅额度。macOS 上 ChatGPT.app 自带一份，脚本会自动找到；也可以用 `CODEX_BIN` 指定路径。
- **Python 3 + Pillow**：用于生成任务文件和导出 JPG。
- **numpy**：只有 `fix_green_eyes.py` 需要。
- **zsh + macOS 的 `date`**：`run.sh` 用它们计算额度重置时间。在其他系统上可以手动按顺序执行两个任务文件。

## 安装

```bash
git clone https://github.com/superchaospc/brush-cover-pack.git ~/.claude/skills/brush-cover-pack
```

要让 Codex 也能自动触发，做一个软链接即可，两边用的是同一种 skill 格式：

```bash
ln -s ~/.claude/skills/brush-cover-pack ~/.codex/skills/brush-cover-pack
```

## 使用

直接说就行，skill 会自己触发：

- 「按 Paul 那种风格给这个频道拆解做封面，所有比例都要。」
- 「封面别写月入多少了，发抖音会被限流，改成播放增长。」
- 「人物换一张他的照片，器材按报告里写的画。」
- 「眼睛太绿了，改黑一点。」

## 也可以手动跑

```bash
S=~/.claude/skills/brush-cover-pack
python3 $S/scripts/make_tasks.py my-cover.json           # 生成任务文件
zsh $S/scripts/run.sh ~/my-cover-work ~/Desktop/my-cover  # 先出 16:9，再出其余比例
python3 $S/scripts/export.py ~/Desktop/my-cover           # 导出上传尺寸的 JPG
```

配置字段参照 [`examples/cover.json`](examples/cover.json)：

| 字段 | 说明 |
| --- | --- |
| `work_dir` / `out_dir` | 任务文件和日志放在哪，成品放在哪 |
| `texts` | `label`、`line1`、`line2`、`headline` 四行字 |
| `breaks` | 允许在哪里换行 |
| `identity_refs` | 博主本人的截帧，第一张最重要；留空则画虚构人物 |
| `style_refs` | 风格参考图，可以留空 |
| `subject` / `scene` | 人物外貌和场景 |
| `filming` | 他真实的拍摄器材和机位 |
| `prop` | 小道具，默认是只显示上涨曲线的手机 |
| `ratios` | 只出部分比例时填，默认是全部 6 个 |
| `base_image` / `change` | 在已通过的 16:9 上局部修改（改字、换器材） |
| `extra_rules` | 这一套额外的要求 |

## 文件

```
SKILL.md                      规则和流程（agent 读这个）
templates/master.md           16:9 母版提示词
templates/edit-master.md      在母版上局部修改的提示词
templates/ratios.md           其余比例的提示词
templates/ratio-specs.md      每个比例的版式坐标
scripts/make_tasks.py         配置 → 任务文件
scripts/run.sh                委派 codex exec，撞额度自动等待
scripts/export.py             导出上传 JPG，比例不对就拒绝
scripts/fix_green_eyes.py     只修眼镜区域的绿色偏色
references/social-titles.md   社媒标题的写法和模板
examples/cover.json           示例配置（虚构人物）
```

## License

MIT
