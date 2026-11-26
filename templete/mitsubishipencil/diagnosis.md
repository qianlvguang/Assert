# 审核模板诊断报告：IP_mitsubishipencil_prompt (`mitsubishipencil`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 214）
- **默认采用版本**: `id=214` (`IP_mitsubishipencil_prompt`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=451
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `214::1` | `IP_mitsubishipencil` |  | 451 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `214::2` | `IP_mitsubishipencil_prompt` | ✅ | 451 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/214_IP_mitsubishipencil.md`](versions/214_IP_mitsubishipencil.md) — `214::1`, `chars=451` 
- [`versions/214_IP_mitsubishipencil_prompt.md`](versions/214_IP_mitsubishipencil_prompt.md) — `214::2`, `chars=451` （默认采用）
