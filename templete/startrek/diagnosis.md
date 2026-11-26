# 审核模板诊断报告：ip_startrek (`startrek`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 417）
- **默认采用版本**: `id=417` (`ip_startrek`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=628
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `417` | `ip_startrek` | ✅ | 628 | 0 处 | `active_ip` | `sports_collegiate_celebrity, boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_04940_星际迷航_Star_Trek_` (`franchise:star_trek`) → `['sch96_ip_supplement/anime_games_entertainment/ip_star_trek.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_star_trek` (星际迷航 Star Trek / Star Trek) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_star_trek.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00321_ip_startrek` · `ip_startrek` · status=`needs_identity_review`
