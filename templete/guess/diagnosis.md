# 审核模板诊断报告：GUESS (`guess`)

## 1. 同族与版本选择概览

- **同族成员数**: 4 个独立版本（来源记录 ID: 201, 295, 296）
- **默认采用版本**: `id=201` (`IP_guess_penalty`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=961
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `201` | `IP_guess_penalty` | ✅ | 961 | 0 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `295::1` | `guess_test` |  | 238 | 0 处 | `active_ip` | `brand_logo_trademark` | 缺字错漏：`的信。`（应为的信息） |
| `295::2` | `guess_prompt` |  | 515 | 0 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `296` | `guessprompt` |  | 108 | 0 处 | `quarantine_paste_bug` | `multi_image_open_set` | 标题为 guessprompt，正文却是通用未限定 IP 字典模板（未出现 GUESS）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `brand_logo_trademark`, `common_word_disambiguation`, `fuzzy_ocr_deformation`, `multi_image_open_set`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`, `cross_entity_paste_bug`, `missing_exclusion_clause`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_00189_盖尔斯_GUESS_` (`brand:guess`) → `['sch96_ip_supplement/brands/ip_guess.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_guess` (GUESS 时装品牌 / GUESS) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_guess.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_05099_guessprompt` · `guessprompt` · status=`needs_identity_review`
  - `kb_05098_guess_test` · `guess_test` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/201_IP_guess_penalty.md`](versions/201_IP_guess_penalty.md) — `201`, `chars=961` （默认采用）
- [`versions/295_guess_test.md`](versions/295_guess_test.md) — `295::1`, `chars=238` 
- [`versions/295_guess_prompt.md`](versions/295_guess_prompt.md) — `295::2`, `chars=515` 
- [`versions/296_guessprompt.md`](versions/296_guessprompt.md) — `296`, `chars=108` 
