# 审核模板诊断报告：ip-Rilakkuma-prompt (`rilakkuma`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 310）
- **默认采用版本**: `id=310` (`ip-Rilakkuma-prompt`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=384
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `310` | `ip-Rilakkuma-prompt` | ✅ | 384 | 2 处 | `active_ip` | `boolean_rule_reverse_elim` | `rel` 中的 `Kuma` 为局部切词误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_rilakkuma` (轻松小熊 Rilakkuma / Rilakkuma) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_rilakkuma.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_05039_轻松熊_Rilakkuma_リラックマ_` · `轻松熊（Rilakkuma / リラックマ）` · status=`variant_review_required`
  - `kb_00298_ip_Rilakkuma_prompt` · `ip-Rilakkuma-prompt` · status=`needs_identity_review`
