# 审核模板诊断报告：迪奥 (Dior) (`dior`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 68, 69）
- **默认采用版本**: `id=69` (`IP_DIOR_TRADEMARK`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=874
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `68` | `IP_DIOR_Oblique` |  | 212 | 0 处 | `active_ip` | `subject_host_isolation, design_patent_trade_dress` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `69` | `IP_DIOR_TRADEMARK` | ✅ | 874 | 0 处 | `active_ip` | `subject_host_isolation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `design_patent_trade_dress`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/068_IP_DIOR_Oblique.md`](versions/068_IP_DIOR_Oblique.md) — `68`, `chars=212` 
- [`versions/069_IP_DIOR_TRADEMARK.md`](versions/069_IP_DIOR_TRADEMARK.md) — `69`, `chars=874` （默认采用）
