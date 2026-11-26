# 审核模板诊断报告：tro_brandname_alignment_gemini (`aux_tro_brandname_alignment`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 455, 456）
- **默认采用版本**: `id=455` (`tro_brandname_alignment_gemini`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1158
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `455` | `tro_brandname_alignment_gemini` | ✅ | 1158 | 0 处 | `route_auxiliary_non_ip` | `non_ip_auxiliary` | `rel` 中的 `Mini` 来自 `gemini` 或误绑 |
| `456` | `tro_brandname_alignment_gemini_similar_goods_scene` |  | 1152 | 0 处 | `route_auxiliary_non_ip` | `non_ip_auxiliary` | `rel` 中的 `Argo` 为无关误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `non_ip_auxiliary`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `not_applicable_non_ip_or_test`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/455_tro_brandname_alignment_gemini.md`](versions/455_tro_brandname_alignment_gemini.md) — `455`, `chars=1158` （默认采用）
- [`versions/456_tro_brandname_alignment_gemini_similar_goods_scene.md`](versions/456_tro_brandname_alignment_gemini_similar_goods_scene.md) — `456`, `chars=1152` 
