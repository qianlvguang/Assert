# 审核模板诊断报告：西班牙皇家足协 (RFEF) (`rfef`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 256, 412）
- **默认采用版本**: `id=256` (`Ip_REFE_exception`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +3）；清洗后正文长度 chars=1595
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `256` | `Ip_REFE_exception` | ✅ | 1595 | 0 处 | `active_ip` | `sports_collegiate_celebrity, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `412` | `ip_rfef` |  | 472 | 1 处 | `active_ip` | `sports_collegiate_celebrity, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `fuzzy_ocr_deformation`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_08659_Ip_REFE_exception` · `Ip_REFE_exception` · status=`needs_identity_review`
  - `kb_07690_ip_rfef` · `ip_rfef` · status=`needs_identity_review`
  - `kb_04995_西班牙皇家足球协会_RFEF_` · `西班牙皇家足球协会（RFEF）` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/256_Ip_REFE_exception.md`](versions/256_Ip_REFE_exception.md) — `256`, `chars=1595` （默认采用）
- [`versions/412_ip_rfef.md`](versions/412_ip_rfef.md) — `412`, `chars=472` 
