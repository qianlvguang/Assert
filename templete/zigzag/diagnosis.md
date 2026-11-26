# 审核模板诊断报告：IP_zigzag (`zigzag`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 242）
- **默认采用版本**: `id=242` (`IP_zigzag`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=114
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `242` | `IP_zigzag` | ✅ | 114 | 0 处 | `active_ip` | `brand_logo_trademark` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `brand_logo_trademark`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_00248_Zig_Zag_吉格扎格_捷格扎格_` (`brand:zig_zag`) → `['sch96_ip_supplement/brands/ip_zig_zag.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_zig_zag` (Zig-Zag 品牌标识 / Zig-Zag) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_zig_zag.png`
