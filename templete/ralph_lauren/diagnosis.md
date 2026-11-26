# 审核模板诊断报告：拉夫劳伦 (Ralph Lauren) (`ralph_lauren`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 327, 328）
- **默认采用版本**: `id=328` (`ip-ralphlauren2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=2009
- **导出商品硬编码清理**: 共自动将 7 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `327` | `ip-ralphlauren` |  | 269 | 6 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `328` | `ip-ralphlauren2` | ✅ | 2009 | 1 处 | `active_ip` | `subject_host_isolation, design_patent_trade_dress, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `design_patent_trade_dress`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_00077_拉夫劳伦_Ralph_Lauren_` (`brand:ralph_lauren`) → `['sch96_ip_supplement/brands/ip_ralph_lauren.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_ralph_lauren` (拉夫劳伦 Ralph Lauren / Ralph Lauren) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_ralph_lauren.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_05078_ip_ralphlauren` · `ip-ralphlauren` · status=`needs_identity_review`
  - `kb_05079_ip_ralphlauren2` · `ip-ralphlauren2` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/327_ip-ralphlauren.md`](versions/327_ip-ralphlauren.md) — `327`, `chars=269` 
- [`versions/328_ip-ralphlauren2.md`](versions/328_ip-ralphlauren2.md) — `328`, `chars=2009` （默认采用）
