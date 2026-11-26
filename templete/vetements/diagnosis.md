# 审核模板诊断报告：Ip_vetements_exception (`vetements`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 258）
- **默认采用版本**: `id=258` (`Ip_vetements_exception`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +3）；清洗后正文长度 chars=949
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `258` | `Ip_vetements_exception` | ✅ | 949 | 0 处 | `active_ip` | `common_word_disambiguation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 兜底松弛风险（主观逃生舱）：条款含“除非直观可判断 / 合理理解为指向”等模糊兜底，易架空前置特征组合约束。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `fuzzy_ocr_deformation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `weak_anchor_or_escape_hatch`

### 规则与数据构造建议

- 【去除主观逃生舱】替换“除非直观可判断 / 合理理解为指向”等主观逃生短语，将其固化为具体的无色彩轮廓/结构拓扑检验条件。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_00435_VETEMENTS_唯特萌_` · `VETEMENTS（唯特萌）` · status=`needs_identity_review`
  - `kb_05105_Ip_vetements_exception` · `Ip_vetements_exception` · status=`needs_identity_review`
