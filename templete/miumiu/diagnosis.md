# 审核模板诊断报告：ip-miumiu (`miumiu`)

## 1. 同族与版本选择概览

- **同族成员数**: 5 个独立版本（来源记录 ID: 322）
- **默认采用版本**: `id=322` (`ip-miumiu`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1338
- **导出商品硬编码清理**: 共自动将 5 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `322::1` | `ip-miumiu` | ✅ | 1338 | 1 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `322::2` | `ip_miumiu_1` |  | 139 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `322::3` | `ip_miumiu_2` |  | 101 | 0 处 | `active_ip` | `subject_host_isolation` | 判据过于笼统（清洗后 101 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |
| `322::4` | `ip_miumiu_mianshen` |  | 459 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `322::5` | `ip_miumiu_background` |  | 1040 | 4 处 | `active_ip` | `subject_host_isolation, fuzzy_ocr_deformation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `underspecified_rubric`

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【规则补全】当前主模板仅一句宽泛提问，类间边界完全未定义；建议先补充正例必需锚点清单与常见误召回排除条款，再进入训练或线上评测。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_05113_ip_miumiu` · `ip-miumiu` · status=`needs_identity_review`
  - `kb_00442_缪缪_Miu_Miu_` · `缪缪（Miu Miu）` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/322_ip-miumiu.md`](versions/322_ip-miumiu.md) — `322::1`, `chars=1338` （默认采用）
- [`versions/322_ip_miumiu_1.md`](versions/322_ip_miumiu_1.md) — `322::2`, `chars=139` 
- [`versions/322_ip_miumiu_2.md`](versions/322_ip_miumiu_2.md) — `322::3`, `chars=101` 
- [`versions/322_ip_miumiu_mianshen.md`](versions/322_ip_miumiu_mianshen.md) — `322::4`, `chars=459` 
- [`versions/322_ip_miumiu_background.md`](versions/322_ip_miumiu_background.md) — `322::5`, `chars=1040` 
