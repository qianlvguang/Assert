# 审核模板诊断报告：迈克尔·杰克逊 (Michael Jackson) (`michael_jackson`)

## 1. 同族与版本选择概览

- **同族成员数**: 4 个独立版本（来源记录 ID: 111, 112）
- **默认采用版本**: `id=112` (`IP_MICHAELJACKSON_MJ_V2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=511
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `111::1` | `michaeljackson` |  | 86 | 0 处 | `active_ip` | `brand_logo_trademark` | 判据过于笼统（清洗后 86 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |
| `111::2` | `IP_MICHAELJACKSON` |  | 422 | 0 处 | `active_ip` | `common_word_disambiguation` | 无明显模板缺陷 |
| `112::1` | `IP_MICHAELJACKSON_MJ` |  | 313 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `112::2` | `IP_MICHAELJACKSON_MJ_V2` | ✅ | 511 | 1 处 | `active_ip` | `common_word_disambiguation, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `common_word_disambiguation`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `underspecified_rubric`

### 规则与数据构造建议

- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。
- 【规则补全】当前主模板仅一句宽泛提问，类间边界完全未定义；建议先补充正例必需锚点清单与常见误召回排除条款，再进入训练或线上评测。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_08629_michaeljackson` · `michaeljackson` · status=`needs_identity_review`
  - `kb_00401_迈克尔_杰克逊_Michael_Jackson_` · `迈克尔·杰克逊 (Michael Jackson)` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/111_michaeljackson.md`](versions/111_michaeljackson.md) — `111::1`, `chars=86` 
- [`versions/111_IP_MICHAELJACKSON.md`](versions/111_IP_MICHAELJACKSON.md) — `111::2`, `chars=422` 
- [`versions/112_IP_MICHAELJACKSON_MJ.md`](versions/112_IP_MICHAELJACKSON_MJ.md) — `112::1`, `chars=313` 
- [`versions/112_IP_MICHAELJACKSON_MJ_V2.md`](versions/112_IP_MICHAELJACKSON_MJ_V2.md) — `112::2`, `chars=511` （默认采用）
