# 审核模板诊断报告：亚利桑那大学 (University of Arizona) (`arizona_university`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 335, 349）
- **默认采用版本**: `id=335` (`ip_Arizona`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1124
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `335` | `ip_Arizona` | ✅ | 1124 | 0 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 兜底松弛风险（主观逃生舱）：条款含“除非直观可判断 / 合理理解为指向”等模糊兜底，易架空前置特征组合约束。 |
| `349` | `ip_arizona university` |  | 498 | 0 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `weak_anchor_or_escape_hatch`

### 规则与数据构造建议

- 【去除主观逃生舱】替换“除非直观可判断 / 合理理解为指向”等主观逃生短语，将其固化为具体的无色彩轮廓/结构拓扑检验条件。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_07664_ip_Arizona` · `ip_Arizona` · status=`needs_identity_review`
  - `kb_07665_ip_arizona_university` · `ip_arizona university` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/335_ip_Arizona.md`](versions/335_ip_Arizona.md) — `335`, `chars=1124` （默认采用）
- [`versions/349_ip_arizona_university.md`](versions/349_ip_arizona_university.md) — `349`, `chars=498` 
