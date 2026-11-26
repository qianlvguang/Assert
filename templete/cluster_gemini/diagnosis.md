# 审核模板诊断报告：通用聚类品牌/山寨/独立站审查 (Gemini) (`cluster_gemini`)

## 1. 同族与版本选择概览

- **同族成员数**: 4 个独立版本（来源记录 ID: 372, 373, 374, 375）
- **默认采用版本**: `id=375` (`ip_cluster_gemini_grounding`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=3074
- **导出商品硬编码清理**: 共自动将 4 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `372` | `ip_cluster_gemini` |  | 2462 | 1 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, sports_collegiate_celebrity, multi_image_open_set, fuzzy_ocr_deformation` | `rel` 中的 `Mini` 来自 `gemini` 或误绑 |
| `373` | `ip_cluster_gemini_crop` |  | 1789 | 1 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, image_title_conflict, sports_collegiate_celebrity, multi_image_open_set, fuzzy_ocr_deformation` | `rel` 中的 `Mini` 来自 `gemini` 或误绑 |
| `374` | `ip_cluster_gemini_crop_copycat` |  | 2204 | 1 处 | `active_ip` | `subject_host_isolation, image_title_conflict, auto_parts_compatibility_obfuscation, design_patent_trade_dress, sports_collegiate_celebrity, multi_image_open_set, fuzzy_ocr_deformation` | `rel` 中的 `Mini` 来自 `gemini` 或误绑 |
| `375` | `ip_cluster_gemini_grounding` | ✅ | 3074 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, multi_image_open_set` | `rel` 中的 `Mini` 来自 `gemini` 或误绑 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `auto_parts_compatibility_obfuscation`, `common_word_disambiguation`, `design_patent_trade_dress`, `fuzzy_ocr_deformation`, `image_title_conflict`, `multi_image_open_set`, `sports_collegiate_celebrity`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。
- 【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (4 条展示)**:
  - `kb_00303_ip_cluster_gemini` · `ip_cluster_gemini` · status=`needs_identity_review`
  - `kb_00304_ip_cluster_gemini_crop` · `ip_cluster_gemini_crop` · status=`needs_identity_review`
  - `kb_00305_ip_cluster_gemini_crop_copycat` · `ip_cluster_gemini_crop_copycat` · status=`needs_identity_review`
  - `kb_00306_ip_cluster_gemini_grounding` · `ip_cluster_gemini_grounding` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/372_ip_cluster_gemini.md`](versions/372_ip_cluster_gemini.md) — `372`, `chars=2462` 
- [`versions/373_ip_cluster_gemini_crop.md`](versions/373_ip_cluster_gemini_crop.md) — `373`, `chars=1789` 
- [`versions/374_ip_cluster_gemini_crop_copycat.md`](versions/374_ip_cluster_gemini_crop_copycat.md) — `374`, `chars=2204` 
- [`versions/375_ip_cluster_gemini_grounding.md`](versions/375_ip_cluster_gemini_grounding.md) — `375`, `chars=3074` （默认采用）
