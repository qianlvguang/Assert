# 审核模板诊断报告：ip_godzilla_3 (`godzilla`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 387）
- **默认采用版本**: `id=387` (`ip_godzilla_3`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1338
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `387::1` | `ip_godzilla` |  | 1203 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `387::2` | `ip_godzilla_2` |  | 1203 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `387::3` | `ip_godzilla_3` | ✅ | 1338 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `brand_logo_trademark`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_03752_哥斯拉_Godzilla_` (`franchise:godzilla`) → `['sch96_ip_supplement/anime_games_entertainment/ip_godzilla.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_godzilla` (哥斯拉 Godzilla / Godzilla) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_godzilla.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_03753_ip_godzilla` · `ip_godzilla` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/387_ip_godzilla.md`](versions/387_ip_godzilla.md) — `387::1`, `chars=1203` 
- [`versions/387_ip_godzilla_2.md`](versions/387_ip_godzilla_2.md) — `387::2`, `chars=1203` 
- [`versions/387_ip_godzilla_3.md`](versions/387_ip_godzilla_3.md) — `387::3`, `chars=1338` （默认采用）
