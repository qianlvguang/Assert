# 审核模板诊断报告：爱马仕 (Hermès) (`hermes`)

## 1. 同族与版本选择概览

- **同族成员数**: 6 个独立版本（来源记录 ID: 86, 89, 90, 91, 92, 93）
- **默认采用版本**: `id=90` (`IP_Hermes_Giftbox`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=757
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `86` | `IP_HERMES_bag_keywords` |  | 378 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `89` | `IP_Hermes_Bag` |  | 237 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `90` | `IP_Hermes_Giftbox` | ✅ | 757 | 1 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `91` | `IP_Hermes_Hlogo` |  | 350 | 0 处 | `active_ip` | `common_word_disambiguation` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `92` | `IP_Hermes_Hlogo_keyproducts` |  | 400 | 1 处 | `active_ip` | `common_word_disambiguation, fuzzy_ocr_deformation` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `93` | `IP_Hermes_Keyword` |  | 468 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `brand_logo_trademark`, `common_word_disambiguation`, `fuzzy_ocr_deformation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/086_IP_HERMES_bag_keywords.md`](versions/086_IP_HERMES_bag_keywords.md) — `86`, `chars=378` 
- [`versions/089_IP_Hermes_Bag.md`](versions/089_IP_Hermes_Bag.md) — `89`, `chars=237` 
- [`versions/090_IP_Hermes_Giftbox.md`](versions/090_IP_Hermes_Giftbox.md) — `90`, `chars=757` （默认采用）
- [`versions/091_IP_Hermes_Hlogo.md`](versions/091_IP_Hermes_Hlogo.md) — `91`, `chars=350` 
- [`versions/092_IP_Hermes_Hlogo_keyproducts.md`](versions/092_IP_Hermes_Hlogo_keyproducts.md) — `92`, `chars=400` 
- [`versions/093_IP_Hermes_Keyword.md`](versions/093_IP_Hermes_Keyword.md) — `93`, `chars=468` 
