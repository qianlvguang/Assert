# 审核模板诊断报告：通用多模态商品/广告风险评估 (`risk_evaluation`)

## 1. 同族与版本选择概览

- **同族成员数**: 4 个独立版本（来源记录 ID: 440, 441, 442, 443）
- **默认采用版本**: `id=443` (`risk_ip_adds_evaluation_gemini`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=3124
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `440` | `risk_adds_evaluation` |  | 1952 | 0 处 | `active_ip` | `anime_derivative_two_step, design_patent_trade_dress, sports_collegiate_celebrity, multi_image_open_set, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `441` | `risk_goods_evaluation` |  | 963 | 0 处 | `active_ip` | `anime_derivative_two_step, design_patent_trade_dress, multi_image_open_set` | 无明显模板缺陷 |
| `442` | `risk_ip_adds_evaluation` |  | 2461 | 0 处 | `active_ip` | `anime_derivative_two_step, design_patent_trade_dress, sports_collegiate_celebrity, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 角色设定段落重复粘贴了两遍。 |
| `443` | `risk_ip_adds_evaluation_gemini` | ✅ | 3124 | 0 处 | `active_ip` | `anime_derivative_two_step, design_patent_trade_dress, sports_collegiate_celebrity, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | `rel` 中的 `Mini` 来自 `gemini` 或误绑；角色设定段落重复粘贴了两遍。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `boolean_rule_reverse_elim`, `design_patent_trade_dress`, `fuzzy_ocr_deformation`, `multi_image_open_set`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `duplicate_role_header`, `rel_metadata_mismatch`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (4 条展示)**:
  - `kb_08656_risk_adds_evaluation` · `risk_adds_evaluation` · status=`needs_identity_review`
  - `kb_08600_risk_goods_evaluation` · `risk_goods_evaluation` · status=`needs_identity_review`
  - `kb_08657_risk_ip_adds_evaluation` · `risk_ip_adds_evaluation` · status=`needs_identity_review`
  - `kb_00307_risk_ip_adds_evaluation_gemini` · `risk_ip_adds_evaluation_gemini` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/440_risk_adds_evaluation.md`](versions/440_risk_adds_evaluation.md) — `440`, `chars=1952` 
- [`versions/441_risk_goods_evaluation.md`](versions/441_risk_goods_evaluation.md) — `441`, `chars=963` 
- [`versions/442_risk_ip_adds_evaluation.md`](versions/442_risk_ip_adds_evaluation.md) — `442`, `chars=2461` 
- [`versions/443_risk_ip_adds_evaluation_gemini.md`](versions/443_risk_ip_adds_evaluation_gemini.md) — `443`, `chars=3124` （默认采用）
