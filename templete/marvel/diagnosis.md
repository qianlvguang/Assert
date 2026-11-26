# 审核模板诊断报告：漫威角色 (Marvel) (`marvel`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 107, 108）
- **默认采用版本**: `id=107` (`IP_MARVELCHARACTER`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=258
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `107` | `IP_MARVELCHARACTER` | ✅ | 258 | 0 处 | `active_ip` | `anime_derivative_two_step` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `108::1` | `IP_marvel` |  | 91 | 0 处 | `quarantine_paste_bug` | `brand_logo_trademark` | 子版本 IP_marvel 正文误写为“是否包含迪士尼元素的信息”（同记录另一版本 IP_MARVEL_IMAGE 正常）。 |
| `108::2` | `IP_MARVEL_IMAGE` |  | 160 | 0 处 | `active_ip` | `anime_derivative_two_step` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `brand_logo_trademark`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `cross_entity_paste_bug`, `missing_exclusion_clause`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/107_IP_MARVELCHARACTER.md`](versions/107_IP_MARVELCHARACTER.md) — `107`, `chars=258` （默认采用）
- [`versions/108_IP_marvel.md`](versions/108_IP_marvel.md) — `108::1`, `chars=91` 
- [`versions/108_IP_MARVEL_IMAGE.md`](versions/108_IP_MARVEL_IMAGE.md) — `108::2`, `chars=160` 
