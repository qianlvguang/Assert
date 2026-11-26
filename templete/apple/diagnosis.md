# 审核模板诊断报告：苹果 (Apple 产品/标识/配件) (`apple`)

## 1. 同族与版本选择概览

- **同族成员数**: 6 个独立版本（来源记录 ID: 34, 35, 36, 37, 38, 245）
- **默认采用版本**: `id=38` (`IP_APPLE_WATCHBAND`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1263
- **导出商品硬编码清理**: 共自动将 4 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `34` | `IP_APPLE_COMBOPACK` |  | 329 | 0 处 | `active_ip` | `auto_parts_compatibility_obfuscation` | 无明显模板缺陷 |
| `35` | `IP_APPLE_IMG` |  | 253 | 1 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `36` | `IP_APPLE_LOGO` |  | 646 | 2 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `37` | `IP_APPLE_WATCH` |  | 347 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `38` | `IP_APPLE_WATCHBAND` | ✅ | 1263 | 1 处 | `active_ip` | `fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `245` | `IP组-apple lightning头-商品判断` |  | 141 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `auto_parts_compatibility_obfuscation`, `brand_logo_trademark`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_apple_watch` (苹果 / Apple Watch / Apple / Apple Watch) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_apple_watch.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_00001_Apple` · `Apple` · status=`needs_identity_review`
  - `kb_00391_IP组_apple_lightning头_商品判断` · `IP组-apple lightning头-商品判断` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/034_IP_APPLE_COMBOPACK.md`](versions/034_IP_APPLE_COMBOPACK.md) — `34`, `chars=329` 
- [`versions/035_IP_APPLE_IMG.md`](versions/035_IP_APPLE_IMG.md) — `35`, `chars=253` 
- [`versions/036_IP_APPLE_LOGO.md`](versions/036_IP_APPLE_LOGO.md) — `36`, `chars=646` 
- [`versions/037_IP_APPLE_WATCH.md`](versions/037_IP_APPLE_WATCH.md) — `37`, `chars=347` 
- [`versions/038_IP_APPLE_WATCHBAND.md`](versions/038_IP_APPLE_WATCHBAND.md) — `38`, `chars=1263` （默认采用）
- [`versions/245_IP组-apple_lightning头-商品判断.md`](versions/245_IP组-apple_lightning头-商品判断.md) — `245`, `chars=141` 
