# 广域审核模板（36 族 / Track A）系统化学习路线图：衔接 CPT-SFT v3.0 与 Pro / Flash-Next 演进

> **定位与边界**：本文档基于 [`manifests/template_taxonomy_requirements.json`](../manifests/template_taxonomy_requirements.json) 对全量 **352 审核模板同族**（533 拆包版本）的客观划分，针对 **36 族广域识别模板 (`broad_domain`: A1–A4)** 制定可落地的能力习得与训练路线，并直接对齐 `CPT-SFT` 现有 **Lite → Flash (v3.0) → Pro → Qwen3.8-Flash-Next** 训练与评测基础设施（严格保持只读对齐，不跨仓修改）。

---

## 一、为什么广域模板必须与特定实体模板分轨训练？

| 维度 | 特定产品/IP/品牌模板 (`entity_specific`, 307 族 / 87.2%) | 广域识别模板 (`broad_domain`, 36 族 / 10.2%) | 隔离模板 (`quarantined_excluded`, 9 族 / 2.6%) |
|---|---|---|---|
| **核心瓶颈** | 长尾实体的“见过没有”（视觉先验与版本/形态映射缺失） | **判决机制与边界泛化**（宿主隔离、闭集名单服从、多图聚合、以图覆文、防二创与原创区分、证据不足拒判） | 错贴 Bug（4 族）与测试垃圾（5 族），混入训练直接污染梯度 |
| **主导解法** | **Assert / Wiki 标准参考图 + 多载体 CPT 视觉锚定** + `rule_grounded_audit_sft` | **机制先导的多源视觉对照 CPT (`v2` + `v6_edit_pairs`) + 结构化条款 SFT + RAG 证据绑定 + Pro/OPD 纠偏** | 硬隔离 (`fix_template_prompt_bug`, `requires_weight_update=false`) |
| **主要风险** | 实体认不出、同名歧义（如 `Triumph` 内衣 vs 摩托） | **表面关键词抢答**、把手机/模特宿主当售卖主体、超名单越权判侵权、对原创艺术/普通画风高误杀 | 训练噪声与错误归因 |

---

## 二、36 族广域模板能力拆解与 CPT-SFT 通道精准路由

### A1 跨域开放集商标 / IP / 宿主隔离识别（10 族）
覆盖：`brand_gemini_general`, `brand_goods_consistent_multi_img`, `cluster_gemini`, `general_ip_model_nxy`, `general_rihe`, `infringement_detection`, `logo_similar_judge`, `risk_evaluation`, `riskdata_iplogo_brand_gemini`, `tro_anly`

- **提取的共性审核需求**：
  1. **售卖主体锁定与宿主隔离**（`general_rihe`, `brand_gemini_general`）：必须区分真正售卖的商品与手机本体、GamePad 宿主、展示模特身上的穿戴物或背景道具；
  2. **材质与工艺一致性**（`brand_gemini_general`, `general_rihe`）：Logo/图案必须在纹理、走线、反光、形变透视上自然附着于售卖品材质，过滤 P 图/透出误判；
  3. **多图与动态名单约束**（`brand_goods_consistent_multi_img`）：给定 `#BRAND_LIST#` 与主图/轮播图/SKU 图，跨图去重并逐项核验列表边界；
  4. **图搜外部证据穿透**（`cluster_gemini`）：融合商品图与谷歌以图搜图候选 URL 列表，做权利方归因而非只看表面视觉。
- **CPT-SFT 对应通道**：
  - **CPT / 视觉主通道**：`Datawheel` + `Assert` 混合多品牌锚定（`2,260` 统一规范资产） + 线 B `build_v6_edit_pairs.py`（`v6_1` `1.73M` + 净 `v7` `2.44M` 编辑前后对）专门负责**宿主替换、背景无关 Logo 注入、局部涂抹反规避**；
  - **SFT 规则绑定**：`rule_grounded_audit_sft` 产出「同图更换售卖宿主/涂抹关键区域 → 结论翻转」对抗三元组。

### A2 垂直品类 / 多实体列表联合审核（14 族）
覆盖：
- **闭集多品牌/多联盟（须严守名单边界）**：`cars_automotive_general`（雪佛兰/现代/大众/KTM/斯柯达）、`counterfeit_watch`（限定奢侈名表名单，明确排除 Apple/Samsung/华为/小米）、`hemier_league`（MLB + NHL）、`kpop`（Red Velvet/TREASURE/EXO/BABYMONSTER/DAY6/SEVENTEEN/TWICE）
- **垂直开放集/品类边界（高同质与版权风险）**：`artist`、`band_music_general`、`merchtraffic`、`sports_ball_general`、`sport_star`、`spainish_celebrity`、`counterfeit_jerseys`（去 Logo 纯配色/版型抄袭）、`household`、`infringementcards`（卡牌 vs 卡套/卡册/贴纸豁免）、`nin1_game_console`（N合1 游戏机 vs 俄罗斯方块机/早教机/电子宠物豁免）

- **提取的共性审核需求**：
  1. **闭集防越界 (`Closed-Set Boundary`)**：输入含非名单大牌（如 `Omega` 出现于不含 Omega 的版本或 `Apple Watch` 出现在名表模板），必须严格按模板名单判 `false`；
  2. **功能/品类前置豁免门 (`Category & Compatibility Gate`)**：`infringementcards` Step 1 先剔除卡套/卡膜/相册/卡 binder；`nin1_game_console` Step 1 先剔除 Tetris Brick Game / Tamagotchi；`cars_automotive_general` 区分配件适配词（`suitable for`）与车标本体侵权；
  3. **无 Logo 装潢与结构判定**（`counterfeit_jerseys`）：故意遮罩 Logo 后仅凭球衣条纹布局与配色判抄袭，需同载体强负例对照；
  4. **高幻觉域必须配 RAG / 保守拒判**（`artist`, `spainish_celebrity`, `sport_star`）：不允许模型靠裸权重硬背全球所有插画师或西班牙国籍公众人物，缺失可核验出处时必须输出“证据不足/不强判”。

### A3 双图对比防二创 / 规避机制（1 族）
覆盖：`twizler`
- **审核需求**：输入「敏感母本图 vs 待审风险图」，判断后者是否通过 AI 二创、裁剪、镜像、拼贴或风格重绘规避审核。
- **CPT-SFT 对应通道**：直接复用生图 v2 `ch_v2_derivative_pair` / `ch_v2_cf_pair` 与线 B `ch_v6_edit_cf_pair`，构造「同主体结构保留（true） vs 同构图不同独立实体（false）」双图 Pairwise 训练与评测切片。

### A4 非视觉商品辅助治理与法务合规流（11 族）
覆盖：
- **多模态文档/截图型（2 族）**：`aux_invoices`（进货发票地址/税号/商品匹配防伪核验）、`aux_crawlplatform_anti_risk`（网页截图反爬状态识别）
- **纯文本/法务/关联/反馈运维型（9 族）**：`aux_black_word_risk_reviewer`（Temu 文案跨类商标风险）、`aux_brand_alliance`、`aux_brand_collab`、`aux_identifying_fake_brands`、`aux_logos_review_verification_text`（联邦法院 JudgmentReport 结构化解析）、`aux_tro_brandname_alignment`、`aux_tro_brandname_rec`、`aux_tro_warning_case_process`（12 类 TRO 诉讼节点）、`aux_audit_feedback_optimizer`
- **关键约束**：`A4` 属于**辅助工作流而非核心视觉 IP 识别**。依据 `CPT-SFT` v3.0 配比铁律（CPT 中 QA/纯文散文占比严格 **`<= 15%`**，零 raw ChatML），`A4` **绝不占满 CPT 主视觉桶**，而应按 `--sft-mixed-budget` 配额进入 SFT 阶段，同时 `aux_audit_feedback_optimizer` 应直接接入 Pro 阶段 `error_cluster_miner.py` 做线上错例归因。

---

## 三、结合当前与后续 `CPT-SFT` 的五阶段学习路线图

### Stage 0：数据卫生与族级防泄漏门控（已完成基础，即时可接）
1. **输入对齐**：将本仓库产出的 `manifests/template_taxonomy_requirements.jsonl` 与清洗后的 461 模板注入 `CPT-SFT/training/flash/template_rule_registry.py`（当前已实现 10 大认知原型映射，建议同步增补 `broad_domain` `A1–A4` 分层标签）。
2. **铁律隔离**：
   - `Q1/Q2`（9 族）与含错贴分支的版本永久列入 `template_family_exclusion_map.json` 隔离区，Pro 阶段命中时开具 `fix_template_prompt_bug`；
   - `canonical_store.py` 锁定 `sch_v04` 为 Strict OOD 验证集、丢弃 `trial100` 与 `b010b_withdrawn`；
   - 严格执行 **`doc_family_overlap == 0`** 与 **`sft_overlap == 0`**，防止同一模板或同一商品图在 CPT 与 SFT/OOD 间绕回泄漏。

### Stage 1（现役 Phase A）：Lite 15% 快速机制验证（27B `checkpoint-2257` 底座）
- **目标**：以最低算力确认「广域机制在双模 SFT 下不掉点、Think-ON/OFF 规则激活有效」。
- **广域锚点切片**：优先从 `A1–A3` 抽取 4 类代表性机制样本接入 `slice_flash_to_lite.py`（维持 15% 整家族切片 + `MBS=1/GBS=4/MAX_LENGTH=8192` + 四墙加固后的双模 SFT `49,036 / 2,578`）：
  1. `brand_gemini_general` / `general_rihe`（测**宿主隔离与材质一致性**）；
  2. `sports_ball_general` / `counterfeit_watch`（测**闭集名单遵守与地名消歧**）；
  3. `infringementcards` / `nin1_game_console`（测**Step 1 品类前置豁免门**）；
  4. `twizler`（测**双图 AI 二创抗规避**）。
- **准出门槛**：Think-ON 与 Think-OFF 宏 ACC 同步上升；Host-Isolation 对偶翻转正确率显著高于基线，无 7-step 或格式退化。

### Stage 2（现役 Phase B）：Flash v3.0 全量骨干构建（`share-1` + `template_rule_v05`）
在单阶段 **30 / 35 / 15 / 20 WSD Mid-Training**（30% 域文档+多图 / 35% 真实图库 / 15% CF+干扰对比 / 20% 去 `<think>` 百科散文与回放，严控 `synth <= 25%`、`qa_prose <= 15%`、`doc_text_repeat == 1`）与统一双模 SFT 中，按能力模块系统化供给：

| 广域目标能力 | CPT Mid-Training 供给（学本体与视觉先验） | 统一双模 SFT 供给（学规则求值与输出契约） |
|---|---|---|
| **1. 宿主隔离与材质检验 (`A1`)** | 线 B `v6_1` (`1.73M`) + 净 `v7` (`2.44M`) 生成「手机壳本体印标 vs 手机本体Logo透出 / 模特配饰标 / 无关背景水印」像素对照 (`ch_v6_edit_cf_pair`) | `rule_grounded_audit_sft` 对偶三元组：同一主体换宿主不翻错，Logo 从主体移至背景道具则翻 `res=false` |
| **2. 以图覆文与 OCR 抗变形 (`A1/A2`)** | 真实带噪网图 + 局部裁切/旋转/涂抹扰动对；强负例专配「标题堆砌大牌词但商品实图无标」样本 | `single_clause_flip_negative`：刻意制造标题含品牌词 + 图片净白，强制模型输出 `false` 并引用“仅以可见商品主体为准” |
| **3. 闭集与前置豁免 (`A2`)** | 按垂直领域打包多图共现文档（汽车多标、NBA/MLB/NHL 队徽、奢侈表盘细节、卡牌 vs 卡套实物区别） | 在 Prompt 中动态替换/删减闭集名单，训练“名单内 true / 名单外哪怕识别出大牌也必须 false”的指令跟随 |
| **4. 二创与无Logo装潢 (`A2/A3`)** | 动漫/球衣同载体 4 分桶（25% 原图、25% 可核验二创、30% 同风格原创强负例、20% 证据不足）+ `ch_v2_derivative_pair` | 训练两步门控 CoT：先剥离画风/配色共性，再核验特征组合；缺关键辨识组合时退回证据不足 |
| **5. 工具/RAG证据核验 (`A1/A2/A4`)** | 从 `cluster_gemini` 与 Wiki/Assert 索引构造「待审图 + Top-K 召回（含正确/近邻混淆/空结果）→ 证据引用与可支撑结论」图文原文 | 训练三种证据状态响应：`直接命中`、`存在混淆近邻需排除`、`空召回/证据不足禁止强猜`，并绑定 `A4` 预算 SFT |

- **SFT 格式与 Think 配比**：遵循 Flash `7:3` Think-ON / Clean-Direct 配比与 `Clean Direct Twins >= 80%`，保持 `339/352` 族所需的标准 `json_res_reason` 格式合法率，同时兼容 `A4`（如 `aux_tro_warning_case_process`、`aux_logos_review_verification_text`）的复杂多字段结构。

### Stage 3（后续 Phase C）：Pro 闭环演化、DPO 与 OPD（待 Flash 验收后启动）
1. **错误簇自动分诊（优先零成本修索引/路由，后动权重）**：
   - 将 `aux_audit_feedback_optimizer` 产出的线上错例与 `error_cluster_miner.py` 联动：
     - `missing_index_evidence`（如新版画师/小众西班牙球星/新增表款缺失）→ 先向 `Assert` / RAG 索引补图与别名，**固定权重重测 Recall**；
     - `disposition_mapping_drift` → 先修模板布尔逻辑或路由版本；
     - `style_collision_false_positive` / `insufficient_forced_judgment` → 进入 **50% 新缺口 / 30% 旧已验收锚点 / 20% 历史回放** 增量 CPT + 异模板 SFT，并受 `iteration_ledger.json` 单调账本约束 (`sft_overlap == 0`)。
2. **4 项同源增强 (`enhance_flash_to_pro.py`) 对广域模板的专项收益**：
   - **WiSE-FT 安全阀** (`0.8*CPT + 0.2*Base`)：防止过度拟合垂直 IP 规则导致通用 OCR、常识推理（如识别 `Apple Watch` vs 奢侈表）掉点 `> 2.0pp`；
   - **50,669 净学生 DPO/KTO 偏好对**：重点压制三大广域顽疾——**关键词抢答（标题诱饵正→拒）**、**证据不足强判（盲猜艺术家/二创）**、**超名单越权判侵权**；
   - **OPD (`Think-ON → Think-OFF` 上下文蒸馏)**：线上大批广域审核（如 `risk_evaluation`, `brand_goods_consistent_multi_img`）要求低延迟无思考直出 JSON；通过 `pro_opd_bsd_seeds.jsonl` 对齐 `Think-OFF` logits，将 `think_on_off_gap_pp` 压至 `<= 8.0pp` 内；
   - **Montessori 影响力筛选**：剔除高损失/矛盾推理的伪 CoT 轨迹，避免广域多步骤指令学偏。

### Stage 4（算力与底座代际迁移）：`Qwen3.8-Flash-Next`（180B/6B MoE + 51B PLE）
- **零返工切换**：直接复用本路线图产出的同一套 `ms_swift_jsonl_v3`（`midtrain_train.jsonl` + `sft_unified_train.jsonl`）。
- **MoE 能力匹配点**：`Qwen3.8-Flash-Next`（`TP2/EP4/PP2 + PLE_CPU_OFFLOAD=1 + LoRA-only + share-1`）在广域任务上具有天然优势——多专家天然分化承担 **A1 视觉精细取证**、**A2 领域专家规则** 与 **A4 法务长文本推理**，且 `6B` 激活参数兼顾线上审核吞吐。建议按 `MODEL_FAMILY=qwen38_flash_next` 先跑 Lite 15% LoRA 验证，再全量接管 Flash 与 Pro。

---

## 四、广域模板专属评测切片与毕业门槛（Evaluation Gates）

除整体模板等权宏 ACC（首轮业务目标 **净增益 >= +2.0 pp** 且配对 95% CI 下界 > 0）外，广域模板必须在密封测试中单列以下 6 个切片门槛：

| 评测切片 | 对应模板家族 | 核心度量指标 | 通过建议门槛 |
|---|---|---|---|
| **1. 宿主隔离与透出对偶集** | `brand_gemini_general`, `general_rihe`, `samsung_phonecase` | 成对变换翻转率（同一标在主体=true、移至宿主/背景=false 两边全对比例） | 较基线提升 >= +5 pp |
| **2. 标题诱饵与图文冲突集** | `brand_goods_consistent_multi_img`, `riskdata_iplogo_brand_gemini` | 标题含大牌词但图片干净无标的误杀率 (FPR) | FPR 显著下降且召回不劣化 |
| **3. 闭集与前置豁免集** | `counterfeit_watch`, `cars_automotive_general`, `infringementcards`, `nin1_game_console` | 名单外大牌零误报率 + 豁免配件/砖头机正确放行率 | 名单泄露率 <= 2% |
| **4. 原创防误杀与证据不足拒判** | `artist`, `counterfeit_jerseys`, `sports_ball_general`, `spainish_celebrity` | 原创合规误罚率 & 缺检索证据时的合规拒判率 | 误罚率下降、盲猜强判率 <= 5% |
| **5. 双图 AI 二创抗规避** | `twizler` | 正负双图对判别准确率 / AUC | 成对准确率 >= 85% |
| **6. 线上协议与双模一致性** | 全量 36 族（尤其 `risk_evaluation`, `A4`） | JSON 合法解析率 & `Think-ON vs Think-OFF` 差距 | JSON 合法率 >= 99.5%；Gap <= 8.0 pp |
