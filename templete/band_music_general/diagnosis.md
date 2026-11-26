# 审核模板诊断报告：通用乐队/歌手召回 (Band) (`band_music_general`)

## 1. 同族与版本选择概览

- **同族成员数**: 4 个独立版本（来源记录 ID: 4, 5）
- **默认采用版本**: `id=4` (`ip_band_v2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=123
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `4::1` | `Band` |  | 28 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 判据过于笼统（清洗后 28 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |
| `4::2` | `ip_band` |  | 74 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 判据过于笼统（清洗后 74 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |
| `4::3` | `ip_band_v2` | ✅ | 123 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `5` | `Band2` |  | 74 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 判据过于笼统（清洗后 74 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `underspecified_rubric`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。
- 【规则补全】当前主模板仅一句宽泛提问，类间边界完全未定义；建议先补充正例必需锚点清单与常见误召回排除条款，再进入训练或线上评测。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_07640_Band` · `Band` · status=`needs_identity_review`
  - `kb_07639_Band2` · `Band2` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/004_Band.md`](versions/004_Band.md) — `4::1`, `chars=28` 
- [`versions/004_ip_band.md`](versions/004_ip_band.md) — `4::2`, `chars=74` 
- [`versions/004_ip_band_v2.md`](versions/004_ip_band_v2.md) — `4::3`, `chars=123` （默认采用）
- [`versions/005_Band2.md`](versions/005_Band2.md) — `5`, `chars=74` 
