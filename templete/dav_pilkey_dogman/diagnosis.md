# 审核模板诊断报告：神探狗狗 (Dav Pilkey / Dog Man) (`dav_pilkey_dogman`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 74, 186, 190）
- **默认采用版本**: `id=74` (`IP_DavPilkey_dogman`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=908
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `74` | `IP_DavPilkey_dogman` | ✅ | 908 | 0 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `186` | `IP_davpilkey_test` |  | 908 | 1 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `190` | `IP_detectivedpg` |  | 129 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `brand_logo_trademark`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_dav_pilkey` (Dav Pilkey（神探狗狗 / 内裤超人） / Dav Pilkey (Dog Man / Captain Underpants)) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_dav_pilkey.png`

## 5. 同族版本文件索引

- [`versions/074_IP_DavPilkey_dogman.md`](versions/074_IP_DavPilkey_dogman.md) — `74`, `chars=908` （默认采用）
- [`versions/186_IP_davpilkey_test.md`](versions/186_IP_davpilkey_test.md) — `186`, `chars=908` 
- [`versions/190_IP_detectivedpg.md`](versions/190_IP_detectivedpg.md) — `190`, `chars=129` 
