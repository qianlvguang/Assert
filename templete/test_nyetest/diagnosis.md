# 审核模板诊断报告：NyeTestCertKeywords (`test_nyetest`)

## 1. 同族与版本选择概览

- **同族成员数**: 6 个独立版本（来源记录 ID: 267, 268, 269, 270, 271）
- **默认采用版本**: `id=269` (`NyeTestCertKeywords`)
- **版本判定置信度**: `medium`
- **版本选择理由**: 存在阻塞缺陷（quarantine_test_junk）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=3134
- **导出商品硬编码清理**: 共自动将 4 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `267::1` | `NyeTest` |  | 135 | 1 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `267::2` | `NyeTest_coarse_recall` |  | 127 | 1 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `268` | `NyeTestCert` |  | 124 | 1 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `269` | `NyeTestCertKeywords` | ✅ | 3134 | 0 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim, multi_image_open_set` | 无明显模板缺陷 |
| `270` | `NyeTestCustomTemplate` |  | 126 | 1 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `271` | `NyeTestParam` |  | 130 | 0 处 | `quarantine_test_junk` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `multi_image_open_set`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `blocked_hygiene`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `not_applicable_non_ip_or_test`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/267_NyeTest.md`](versions/267_NyeTest.md) — `267::1`, `chars=135` 
- [`versions/267_NyeTest_coarse_recall.md`](versions/267_NyeTest_coarse_recall.md) — `267::2`, `chars=127` 
- [`versions/268_NyeTestCert.md`](versions/268_NyeTestCert.md) — `268`, `chars=124` 
- [`versions/269_NyeTestCertKeywords.md`](versions/269_NyeTestCertKeywords.md) — `269`, `chars=3134` （默认采用）
- [`versions/270_NyeTestCustomTemplate.md`](versions/270_NyeTestCustomTemplate.md) — `270`, `chars=126` 
- [`versions/271_NyeTestParam.md`](versions/271_NyeTestParam.md) — `271`, `chars=130` 
