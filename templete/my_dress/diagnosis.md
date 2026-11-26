# 审核模板诊断报告：ip-my dress-llm-black (`my_dress`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 323）
- **默认采用版本**: `id=323` (`ip-my dress-llm-black`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1027
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `323::1` | `ip-my dress-llm-black` | ✅ | 1027 | 1 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | `rel` 中的 `Black` 为后缀/队名子串误匹配 |
| `323::2` | `ip-my dress-llm-black_coarse_recall` |  | 967 | 1 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | `rel` 中的 `Black` 为后缀/队名子串误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `boolean_rule_reverse_elim`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_my_dress_up_darling` (更衣人偶坠入爱河 My Dress-Up Darling / My Dress-Up Darling) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_my_dress_up_darling.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00271_ip_my_dress_llm_black` · `ip-my dress-llm-black` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/323_ip-my_dress-llm-black.md`](versions/323_ip-my_dress-llm-black.md) — `323::1`, `chars=1027` （默认采用）
- [`versions/323_ip-my_dress-llm-black_coarse_recall.md`](versions/323_ip-my_dress-llm-black_coarse_recall.md) — `323::2`, `chars=967` 
