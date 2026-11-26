# 补图规范与 1119 批次落地方案

## 本批核对结果

输入为 `need_standard_images_1119.md` 的「仍需标准图片」章节，解析到 4,668 个唯一实体 ID。输入 SHA256 记录在 `../manifests/standard_images_1119/summary.json`。

原清单以「是否已有标准 SVG」排除，不能用来判断「是否已有可用参考图」。初次盘点仅检查 Assert 的 320 张现有 PNG；后续执行结果见文末。未复核附录排除的 4,024 项，也未扫描 Datawheel 全量资产。

| 建议处理方式 | 条目数 | 核对重点 |
|---|---:|---|
| 招式、特性先判断是否存在固定视觉 | 1,291 | 核对游戏和版本；不得把生成图标成官方标准图 |
| 角色身份与作品版本核对 | 1,087 | 作品、角色、形态、服装和真人／动画版本 |
| 带图鉴编号的宝可梦立绘 | 1,025 | 编号、形态、地区、普通／异色、画风版本 |
| 实体类参考图 | 553 | 品牌、作品 IP、赛事、机构等实际所需图形 |
| 审核模板识别目标核对 | 237 | 原模板检测对象；先补身份再补图 |
| 材质、纹样、工艺等示例集 | 343 | 单张标志不能代表材质或工艺 |
| 指南、集合或规则文档范围核对 | 56 | 纯文本、子实体拆分或例图集合 |
| 人物与作品用途核对 | 41 | 肖像、签名、个人商标、作品分别记录 |
| 其他宝可梦条目身份核对 | 35 | 与图鉴条目合并候选，形态不能误合并 |

这些是依据域和标题的初步路由，不是已经确认的视觉类型。原清单域有噪声，例如 `anime_char` 含灭霸和超人，不能仅凭域名直接抓图。

## 实体、模板、图片分开记录

- `entity_id`：原始知识条目 ID，不改名。同一实体可能有多个知识条目。
- `canonical_entity_id`：核对后确定的稳定实体 ID，建议使用带类型的命名空间，如 `brand:ford`、`pokemon:0001:normal`；不能仅按展示名合并。
- `template_ids`：原始模板 ID 列表。清单里没有的映射保持空，不从名称猜造。
- `asset_id`：按图片原始字节计算 `sha256_<完整哈希>`，同一文件只存一份。
- 映射关系：知识条目／模板 → 标准实体 → 一个或多个已批准图片版本。

名称相同只产生候选。机构与球队、作品标题与角色、珠宝 Pandora 与音乐 Pandora 必须分开。Apple 标志不能代表 Apple Watch 表带外观；联赛标志不能代表参赛球队队徽。Triumph 等多品牌模板必须先核对原模板目标，不能把两种品牌都算正确覆盖。

## 文件与路径

保留当前图片、原 JSONL 和原 manifests。`existing_assets.jsonl` 提供相对 Assert 根目录的真实 `local_path`，并保留 `legacy_local_path` 供迁移核对；本次没有修改旧消费者路径。

新补图片建议使用以下结构；目录按实际入库需要再创建：

```text
assets/standard_images/<asset_kind>/<canonical_slug>/<variant_id>/
  source.svg       # 或原始 PNG/JPEG，保留原始内容和格式
  reference.png    # 经核准的确定性栅格转换
  preview.jpg      # 白底或棋盘格预览，不作为训练原图
manifests/standard_image_assets.jsonl
manifests/standard_image_links.jsonl
```

`canonical_slug`、`variant_id` 使用小写 snake_case，变体中明确年代／型号／形态。原始文件扩展名由文件内容确定，不能把 JPEG 改后缀伪装 PNG。所有 `local_path` 相对 Assert 根目录；消费者通过配置的资源根目录解析，不依赖启动工作目录。

## 来源与图片类型

每张新资源至少记录：`asset_id`、`asset_kind`、`canonical_entity_id`、`variant_id`、`local_path`、`source_page_url`、`download_url`、`publisher`、`fetched_at`、`license`、`sha256`、`width`、`height`、`is_synthetic_image`、`transform_history`、`review_status`、`review_note`。未知信息写 null 或 unknown，不能猜填。

优先找权利方官网、官方品牌资源页、角色设定或赛事／球队资源页；第三方镜像与百科可以作为候选，但要记录真实发布来源与图形版本。来自 Wikimedia 不自动等于官方来源。现有 320 张图片只通过本地完整性检查，语义、版本和授权信息仍待核对。

| 类型 | 可以入选的内容 | 不应替代它的内容 |
|---|---|---|
| 品牌／赛事／球队标 | 官方图形，分别记录字标、图形标、组合标及历史版 | 商品照、博物馆标、专辑封面或相似品牌 |
| 角色／宝可梦 | 官方立绘、设定图，明确作品及形态 | 同人图、模型生成图、另一作品同名角色 |
| 材质／工艺／纹样 | 可追溯实拍或馆藏细节，建议至少 3 个不同样本起步 | 用单个示意图宣称整个类别已标准覆盖 |
| 招式／特性 | 核实存在的官方图标或带版本的游戏画面 | 自行生图后声称官方统一视觉 |
| 指南／规则／集合 | 纯文本，或拆分后绑定子实体例图 | 为凑覆盖率强行绑定一张 Logo |

派生 PNG 使用确定性转换，保持比例、色彩和透明通道。建议 SVG 渲染长边 1,024 像素；原始位图保留原尺寸，长边低于 512 像素标记低分辨率待审，不通过放大或 AI 修复变成“高清标准图”。白底原图保留白底；不自动抠图、重绘、锐化或裁掉构成标识的元素。生成示意图单独记录 `asset_kind=illustration`、`is_synthetic_image=true`，不得进入标准参考图覆盖分母。

## 状态与验收

建议流程：`needs_identity_review → identity_confirmed → source_found → downloaded → file_verified → semantic_reviewed → approved`。名称匹配已有图片时先进入 `reuse_candidate`。无合适来源保留 `source_missing`；确认没有统一视觉则使用 `no_canonical_visual`；歧义使用 `ambiguous`。这些状态均不等于已覆盖。

批准前需确认：文件可完整解码，内容格式与扩展名相符；哈希、尺寸和路径正确；实体、作品／型号／形态与图形版本匹配；图片无意外水印、截断和背景污染；来源、变换记录和审核意见齐全。拼图用于快速筛查，关键图片还要查看原图。

覆盖率分别报告「原始条目映射率」「去重实体批准率」「需要固定视觉的实体覆盖率」。纯文本文档、无统一视觉概念和示例集单独列出；同一图片映射多个条目不等于新增多张图片。

## 本批执行顺序

1. P0：核对 237 条审核模板的目标与原模板 ID，优先消除同名、泛词和类型歧义。
2. 复审 48 条名称匹配的复用候选；初始清单不自动批准条目，后续审核结果见执行统计。
3. P1：核对宝可梦编号及形态，统一多域条目；补具体品牌、赛事和机构参考图。
4. P2：按作品建立角色清单，补角色图；材质／工艺与人物按各自用途补示例集。
5. P3：复核招式／特性和集合文档，决定纯文本、拆分或单独配示意图。

## 生成与复现

在 Assert 根目录执行：

```bash
python3 scripts/build_standard_image_backlog.py \
  --needs ~/Downloads/need_standard_images_1119.md
```

输出在 `manifests/standard_images_1119/`：`backlog.jsonl` 是 4,668 条逐条待办；`existing_assets.jsonl` 是 320 张现有 PNG 的候选索引；`summary.json` 记录输入指纹、路由计数和本次范围。

脚本只读原资源，不下载、不修改原清单，不自动批准或导出训练样本。它会验证章节条数、实体 ID 唯一性、现有资源路径与清单 MD5。生成结果会覆盖同名输出，因此人工审核结果应另存 `manifests/standard_image_links.jsonl`，不要直接编辑生成待办。后续训练导出只使用经审核批准的显式映射，并在导出时验证图片路径。

## 执行补充（2026-11-20）

已加入 `collect_pokemon_references.py` 与 `finalize_standard_image_batch.py`，实际进度见 `../manifests/standard_images_1119/execution_summary.json`。已有 48 条候选经拼图与相关图片复审，37 条按当前标志用途批准，4 条错配拒绝，7 条版本待核。原台账、原图片和原训练 JSONL 保持不变。

宝可梦采用 [PokeAPI/sprites 的 official-artwork 目录](https://github.com/PokeAPI/sprites)，通过固定版本 CSV 同时校对编号、中英文名称与形态。针对原清单的繁简混写与全角字母，仅做有限字符归一化，原始标题不改写。PokeAPI 是镜像发布者，不能填写成权利方直供；图片权利说明按上游 [LICENCE.txt](https://github.com/PokeAPI/sprites/blob/master/LICENCE.txt) 单独记录，不将仓库 CC0 声明套用为图片授权。

原始立绘常为 475×475，保留原尺寸并标记 `native_resolution_below_512`，不放大冒充高清。新图完整解码、哈希、透明通道非空及身份匹配通过后仍为 `identity_verified_pending_visual_review`；抽检拼图不代表全部视觉验收。未通过批准的图片不进入 `approved_references.jsonl`。

本次逐条判断可由显式审核规则重建。`finalize_standard_image_batch.py` 会重写 `standard_image_links.jsonl`，因此后续人工更正须同步修改脚本里的审核规则；不要只手改生成结果。

## 项目独立边界（2026-11-20）

本项目使用自己的 `.venv` 与 `requirements.txt`。标准图采集构建器和视觉属性工具均在 `scripts/` 内，不导入其他项目模块，也不扫描相邻资源目录。原工作区重复补图文件已按哈希归档，只有显式交付的文件包可作为其他项目输入。新体育补充包清单写入 `output/sports_ip_supplement/manifests/`，原始注册表保持不变。
