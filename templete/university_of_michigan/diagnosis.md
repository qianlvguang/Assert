# 审核模板诊断报告：密歇根大学 (University of Michigan) (`university_of_michigan`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 394, 395, 396）
- **默认采用版本**: `id=396` (`ip_michiganv3`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v3；清洗后正文长度 chars=1102
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `394` | `ip_michigan` |  | 1048 | 0 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 错别字：`间断一句话`（应为简短一句话） |
| `395` | `ip_michiganV2` |  | 170 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 错别字：`密歇嘎大学`（应为密歇根大学）；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `396` | `ip_michiganv3` | ✅ | 1102 | 0 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, fuzzy_ocr_deformation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `fuzzy_ocr_deformation`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_07668_ip_michigan` · `ip_michigan` · status=`needs_identity_review`
  - `kb_07670_ip_michiganV2` · `ip_michiganV2` · status=`needs_identity_review`
  - `kb_07669_ip_michiganv3` · `ip_michiganv3` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/394_ip_michigan.md`](versions/394_ip_michigan.md) — `394`, `chars=1048` 
- [`versions/395_ip_michiganV2.md`](versions/395_ip_michiganV2.md) — `395`, `chars=170` 
- [`versions/396_ip_michiganv3.md`](versions/396_ip_michiganv3.md) — `396`, `chars=1102` （默认采用）
