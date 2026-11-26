# 审核模板诊断报告：UGG Australia (`ugg`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 234, 235）
- **默认采用版本**: `id=235` (`IP_ugg_patent`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +3）；清洗后正文长度 chars=2498
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `234` | `IP_ugg` |  | 2496 | 1 处 | `active_ip` | `design_patent_trade_dress, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `235` | `IP_ugg_patent` | ✅ | 2498 | 0 处 | `active_ip` | `design_patent_trade_dress, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `design_patent_trade_dress`, `fuzzy_ocr_deformation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_ugg` (UGG 雪地靴品牌 / UGG) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_ugg.png`

## 5. 同族版本文件索引

- [`versions/234_IP_ugg.md`](versions/234_IP_ugg.md) — `234`, `chars=2496` 
- [`versions/235_IP_ugg_patent.md`](versions/235_IP_ugg_patent.md) — `235`, `chars=2498` （默认采用）
