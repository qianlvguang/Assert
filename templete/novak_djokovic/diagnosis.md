# 审核模板诊断报告：NOVAK DJOKOVICselfmodel (`novak_djokovic`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 266）
- **默认采用版本**: `id=266` (`NOVAK DJOKOVICselfmodel`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=441
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `266` | `NOVAK DJOKOVICselfmodel` | ✅ | 441 | 0 处 | `active_ip` | `subject_host_isolation, sports_collegiate_celebrity, fuzzy_ocr_deformation` | `rel` 中的 `FMOD` 疑似来自模板名/方法名 `selfmodel` 误匹配；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `fuzzy_ocr_deformation`, `sports_collegiate_celebrity`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `rel_metadata_mismatch`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_novak_djokovic` (诺瓦克·德约科维奇 Novak Djokovic / Novak Djokovic) · fetch_ok=`True` · `assets/sch96_ip_supplement/music_celebrity_sports/ip_novak_djokovic.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_08673_诺瓦克_德约科维奇_Novak_Djokovic_` · `诺瓦克·德约科维奇（Novak Djokovic）` · status=`needs_identity_review`
  - `kb_00279_NOVAK_DJOKOVICselfmodel` · `NOVAK DJOKOVICselfmodel` · status=`needs_identity_review`
