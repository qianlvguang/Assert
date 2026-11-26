# 审核模板诊断报告：杜克大学 (Duke University) (`duke_university`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 378, 379, 380）
- **默认采用版本**: `id=380` (`ip_duke_excepmtion`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +3）；清洗后正文长度 chars=1027
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `378` | `ip_duke` |  | 422 | 0 处 | `active_ip` | `subject_host_isolation, sports_collegiate_celebrity, fuzzy_ocr_deformation` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `379` | `ip_duke universityu` |  | 462 | 0 处 | `active_ip` | `sports_collegiate_celebrity, boolean_rule_reverse_elim` | 拼写错误：`universityu`（应为 university） |
| `380` | `ip_duke_excepmtion` | ✅ | 1027 | 0 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 拼写错误：`excepmtion`（应为 exception）；兜底松弛风险（主观逃生舱）：条款含“除非直观可判断 / 合理理解为指向”等模糊兜底，易架空前置特征组合约束。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `fuzzy_ocr_deformation`, `sports_collegiate_celebrity`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `typo_or_logic_defect`, `weak_anchor_or_escape_hatch`

### 规则与数据构造建议

- 【去除主观逃生舱】替换“除非直观可判断 / 合理理解为指向”等主观逃生短语，将其固化为具体的无色彩轮廓/结构拓扑检验条件。
- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (4 条展示)**:
  - `kb_07686_ip_duke` · `ip_duke` · status=`needs_identity_review`
  - `kb_07687_ip_duke_excepmtion` · `ip_duke_excepmtion` · status=`needs_identity_review`
  - `kb_00208_杜克大学_Duke_University_` · `杜克大学（Duke University）` · status=`needs_identity_review`
  - `kb_07688_ip_duke_universityu` · `ip_duke universityu` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/378_ip_duke.md`](versions/378_ip_duke.md) — `378`, `chars=422` 
- [`versions/379_ip_duke_universityu.md`](versions/379_ip_duke_universityu.md) — `379`, `chars=462` 
- [`versions/380_ip_duke_excepmtion.md`](versions/380_ip_duke_excepmtion.md) — `380`, `chars=1027` （默认采用）
