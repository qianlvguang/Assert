# 审核模板诊断报告：俄克拉荷马大学 (University of Oklahoma) (`oklahoma_university`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 408, 421）
- **默认采用版本**: `id=421` (`ip_universityofoklahomo`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1218
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `408` | `ip_oklahoma` |  | 185 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `421` | `ip_universityofoklahomo` | ✅ | 1218 | 1 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 拼写错误：`oklahomo`（应为 oklahoma） |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_07671_ip_oklahoma` · `ip_oklahoma` · status=`needs_identity_review`
  - `kb_07673_ip_universityofoklahomo` · `ip_universityofoklahomo` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/408_ip_oklahoma.md`](versions/408_ip_oklahoma.md) — `408`, `chars=185` 
- [`versions/421_ip_universityofoklahomo.md`](versions/421_ip_universityofoklahomo.md) — `421`, `chars=1218` （默认采用）
