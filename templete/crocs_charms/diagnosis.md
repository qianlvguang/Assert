# 审核模板诊断报告：洞洞鞋及鞋花配件 (Crocs Charms) (`crocs_charms`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 184, 185）
- **默认采用版本**: `id=185` (`IP_crocs_charms2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=1039
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `184::1` | `IP_crocscharms` |  | 262 | 0 处 | `active_ip` | `brand_logo_trademark` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `184::2` | `IP_crocs_charms` |  | 1009 | 1 处 | `active_ip` | `fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `185` | `IP_crocs_charms2` | ✅ | 1039 | 1 处 | `active_ip` | `boolean_rule_reverse_elim, multi_image_open_set, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `fuzzy_ocr_deformation`, `multi_image_open_set`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/184_IP_crocscharms.md`](versions/184_IP_crocscharms.md) — `184::1`, `chars=262` 
- [`versions/184_IP_crocs_charms.md`](versions/184_IP_crocs_charms.md) — `184::2`, `chars=1009` 
- [`versions/185_IP_crocs_charms2.md`](versions/185_IP_crocs_charms2.md) — `185`, `chars=1039` （默认采用）
