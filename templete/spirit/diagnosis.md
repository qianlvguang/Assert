# 审核模板诊断报告：IP_SPIRIT_IMG (`spirit`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 145）
- **默认采用版本**: `id=145` (`IP_SPIRIT_IMG`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=218
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `145` | `IP_SPIRIT_IMG` | ✅ | 218 | 0 处 | `active_ip` | `brand_logo_trademark` | `rel` 过于泛化，未绑定 DreamWorks《小马王 Spirit》 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `brand_logo_trademark`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_spirit_ambig` (歧义待核：梦工厂《小马王 Spirit》/ Spirit Halloween / Spirit: Stallion of the Cimarron / Spirit Halloween (Ambiguous)) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_spirit_ambig.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00204_spirit` · `spirit` · status=`needs_identity_review`
