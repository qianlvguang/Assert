# 审核模板诊断报告：新西兰全黑队 (All Blacks) (`all_blacks`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 345, 346）
- **默认采用版本**: `id=345` (`ip_allblacks`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=265
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `345` | `ip_allblacks` | ✅ | 265 | 0 处 | `active_ip` | `brand_logo_trademark` | `rel` 中的 `Black` 为后缀/队名子串误匹配 |
| `346` | `ip_allblakcs` |  | 1272 | 2 处 | `quarantine_paste_bug` | `sports_collegiate_celebrity, boolean_rule_reverse_elim` | 标题为 ip_allblakcs（拼写误写），示例 JSON reason 混入“是否出现比利时足协相关元素”。；拼写错误：`allblakcs`（应为 allblacks） |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `cross_entity_paste_bug`, `rel_metadata_mismatch`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_00272_ip_allblacks` · `ip_allblacks` · status=`needs_identity_review`
  - `kb_00400_新西兰国家男子橄榄球队_All_Blacks_全黑队_` · `新西兰国家男子橄榄球队（All Blacks / 全黑队）` · status=`needs_identity_review`
  - `kb_08606_ip_allblakcs` · `ip_allblakcs` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/345_ip_allblacks.md`](versions/345_ip_allblacks.md) — `345`, `chars=265` （默认采用）
- [`versions/346_ip_allblakcs.md`](versions/346_ip_allblakcs.md) — `346`, `chars=1272` 
