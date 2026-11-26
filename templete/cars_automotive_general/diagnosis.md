# 审核模板诊断报告：汽车品牌通用侵权与配件豁免 (Cars Automotive) (`cars_automotive_general`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 17, 180, 298）
- **默认采用版本**: `id=298` (`hemier-cars-selfmodel`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=1242
- **导出商品硬编码清理**: 共自动将 5 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `17` | `IP-cars-aurelia-llm-black` |  | 1869 | 2 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, auto_parts_compatibility_obfuscation, boolean_rule_reverse_elim` | 模板实为汽车品牌/配件侵权，并非皮克斯动画《汽车总动员》；JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `180` | `IP_cars prompt` |  | 648 | 2 处 | `active_ip` | `anime_derivative_two_step, auto_parts_compatibility_obfuscation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 模板实为汽车品牌/配件侵权，并非皮克斯动画《汽车总动员》；错别字：`主管涂抹`（应为主观涂抹） |
| `298` | `hemier-cars-selfmodel` | ✅ | 1242 | 1 处 | `active_ip` | `auto_parts_compatibility_obfuscation, boolean_rule_reverse_elim, multi_image_open_set, fuzzy_ocr_deformation` | 模板实为汽车品牌/配件侵权，并非皮克斯动画《汽车总动员》 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `auto_parts_compatibility_obfuscation`, `boolean_rule_reverse_elim`, `common_word_disambiguation`, `fuzzy_ocr_deformation`, `multi_image_open_set`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`, `missing_exclusion_clause`, `rel_metadata_mismatch`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_cars_aurelia_ambig` (歧义待核：皮克斯《赛车总动员 Cars》/ 蓝旗亚 Aurelia / Cars (Pixar) / Lancia Aurelia (Ambiguous)) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_cars_aurelia_ambig.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_00333_IP_cars_aurelia_llm_black` · `IP-cars-aurelia-llm-black` · status=`needs_identity_review`
  - `kb_00334_hemier_cars_selfmodel` · `hemier-cars-selfmodel` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/017_IP-cars-aurelia-llm-black.md`](versions/017_IP-cars-aurelia-llm-black.md) — `17`, `chars=1869` 
- [`versions/180_IP_cars_prompt.md`](versions/180_IP_cars_prompt.md) — `180`, `chars=648` 
- [`versions/298_hemier-cars-selfmodel.md`](versions/298_hemier-cars-selfmodel.md) — `298`, `chars=1242` （默认采用）
