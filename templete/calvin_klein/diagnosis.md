# 审核模板诊断报告：Calvin Klein (CK) (`calvin_klein`)

## 1. 同族与版本选择概览

- **同族成员数**: 12 个独立版本（来源记录 ID: 55, 56, 62, 284, 285, 286, 287, 288, 368）
- **默认采用版本**: `id=55` (`IP_CALVIN_v2`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=355
- **导出商品硬编码清理**: 共自动将 5 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `55::1` | `IP_CALVIN` |  | 296 | 1 处 | `active_ip` | `subject_host_isolation, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `55::2` | `IP_CALVIN_v2` | ✅ | 355 | 1 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `56` | `IP_CALVINKLEIN` |  | 532 | 2 处 | `active_ip` | `subject_host_isolation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `62` | `IP_CalvinKlein_cklogo` |  | 263 | 0 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `284::1` | `cklogo` |  | 180 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `284::2` | `ck_logo` |  | 374 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |
| `284::3` | `ck_logo_background` |  | 411 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |
| `285` | `ck_logo1` |  | 409 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |
| `286` | `ck_logodetect` |  | 411 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |
| `287` | `ck_perfume` |  | 296 | 1 处 | `active_ip` | `subject_host_isolation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `288` | `ck_word` |  | 430 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |
| `368` | `ip_calvin_special` |  | 258 | 0 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `fuzzy_ocr_deformation`, `image_title_conflict`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (7 条展示)**:
  - `kb_00150_卡尔文_克莱恩_Calvin_Klein_` · `卡尔文·克莱恩（Calvin Klein）` · status=`needs_identity_review`
  - `kb_05092_ip_calvin_special` · `ip_calvin_special` · status=`needs_identity_review`
  - `kb_05093_cklogo` · `cklogo` · status=`needs_identity_review`
  - `kb_05094_ck_logo1` · `ck_logo1` · status=`needs_identity_review`
  - `kb_05095_ck_logodetect` · `ck_logodetect` · status=`needs_identity_review`
  - `kb_05090_ck_perfume` · `ck_perfume` · status=`needs_identity_review`
  - `kb_05091_ck_word` · `ck_word` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/055_IP_CALVIN.md`](versions/055_IP_CALVIN.md) — `55::1`, `chars=296` 
- [`versions/055_IP_CALVIN_v2.md`](versions/055_IP_CALVIN_v2.md) — `55::2`, `chars=355` （默认采用）
- [`versions/056_IP_CALVINKLEIN.md`](versions/056_IP_CALVINKLEIN.md) — `56`, `chars=532` 
- [`versions/062_IP_CalvinKlein_cklogo.md`](versions/062_IP_CalvinKlein_cklogo.md) — `62`, `chars=263` 
- [`versions/284_cklogo.md`](versions/284_cklogo.md) — `284::1`, `chars=180` 
- [`versions/284_ck_logo.md`](versions/284_ck_logo.md) — `284::2`, `chars=374` 
- [`versions/284_ck_logo_background.md`](versions/284_ck_logo_background.md) — `284::3`, `chars=411` 
- [`versions/285_ck_logo1.md`](versions/285_ck_logo1.md) — `285`, `chars=409` 
- [`versions/286_ck_logodetect.md`](versions/286_ck_logodetect.md) — `286`, `chars=411` 
- [`versions/287_ck_perfume.md`](versions/287_ck_perfume.md) — `287`, `chars=296` 
- [`versions/288_ck_word.md`](versions/288_ck_word.md) — `288`, `chars=430` 
- [`versions/368_ip_calvin_special.md`](versions/368_ip_calvin_special.md) — `368`, `chars=258` 
