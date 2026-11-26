# 审核模板诊断报告：ip_brand_alliance_discoverer (`aux_brand_alliance`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 357, 358）
- **默认采用版本**: `id=358` (`ip_brand_alliance_discoverer`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=2098
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `357` | `ip_brand_alliance_auditor` |  | 1913 | 0 处 | `route_auxiliary_non_ip` | `non_ip_auxiliary` | `rel` 中的 `Audi` 为 `audit` 子串误匹配 |
| `358` | `ip_brand_alliance_discoverer` | ✅ | 2098 | 0 处 | `route_auxiliary_non_ip` | `non_ip_auxiliary` | `rel` 中的 `Discover` 为方法名误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `non_ip_auxiliary`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `not_applicable_non_ip_or_test`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/357_ip_brand_alliance_auditor.md`](versions/357_ip_brand_alliance_auditor.md) — `357`, `chars=1913` 
- [`versions/358_ip_brand_alliance_discoverer.md`](versions/358_ip_brand_alliance_discoverer.md) — `358`, `chars=2098` （默认采用）
