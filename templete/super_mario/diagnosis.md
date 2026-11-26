# 审核模板诊断报告：超级马里奥 (Super Mario) (`super_mario`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 148, 272）
- **默认采用版本**: `id=148` (`IP_SUPERMARIO_HIGHACCURACY`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +3）；清洗后正文长度 chars=818
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `148::1` | `supermario` |  | 1079 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `148::2` | `IP_SUPERMARIO_HIGHACCURACY` | ✅ | 818 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `272` | `SUPERMARIO_WORD` |  | 193 | 1 处 | `active_ip` | `brand_logo_trademark` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `fuzzy_ocr_deformation`, `image_title_conflict`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_super_mario` (超级马力欧 Super Mario / Super Mario) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_super_mario.png`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_04917_supermario` · `supermario` · status=`needs_identity_review`
  - `kb_04918_SUPERMARIO_WORD` · `SUPERMARIO_WORD` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/148_supermario.md`](versions/148_supermario.md) — `148::1`, `chars=1079` 
- [`versions/148_IP_SUPERMARIO_HIGHACCURACY.md`](versions/148_IP_SUPERMARIO_HIGHACCURACY.md) — `148::2`, `chars=818` （默认采用）
- [`versions/272_SUPERMARIO_WORD.md`](versions/272_SUPERMARIO_WORD.md) — `272`, `chars=193` 
