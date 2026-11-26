# Assert 审核模板整理与诊断总库 (`templete/`) — 461 原始记录 / 全量完整版

> 生成时间：2026-11-25T07:47:01.397226+00:00 · 原始记录：**461** 条 → 拆包独立版本：**533** 个 · 归并同族目录：**352** 个 · 导出硬编码清理：**327** 处（涉及 212 条原始记录） · 可视化审核画廊：[`review_dashboard.html`](review_dashboard.html)

## 1. 全量清理与归并规则

- **导出残留自动清洗**：原始导出文件在部分模板中混入了运行时注入的商品标题、`p_spec_name` 规格 JSON 及商品属性数组；脚本已在 [`audit_prompts_461_full_cleaned.jsonl`](../manifests/audit_prompts_461_full_cleaned.jsonl) 中将其统一还原为 `#GOODS_TEXT_INFO#` / `#GOODS_PROPERTIES#` / `#GOODS_SPEC#` / `#GOODS_CONTEXT#` / `#BRAND_LIST#`，且**不再计为模板自身缺陷**。
- **内联多版本完整拆包**：将 54 条包含 `**同一对象的 N 个版本**` 的合并记录拆包为各自独立的完整模板正文（共 **535** 个独立版本），按同审核对象归并至 **352** 个同族目录，严格隔离同名撞车（如 `dc_comics` vs `dc_shoes`、`university_of_michigan` vs `michigan_state`）。
- **默认最新版本优先**：按「健康可用 > 非 `test/ceshi/copy` 分支 > 显式版本号 > 生产专项/日期后缀 > 清洗后正文长度」自动选出默认主模板写入 `latest_template.md`。

## 2. 全库汇总统计

### 2.1 模板处置分布（535 个独立版本逐条统计）

| 处置状态 | 数量 | 说明 |
|---|---:|---|
| `active_ip` | 499 | 有效 IP 审核模板（含全量规则文本） |
| `route_auxiliary_non_ip` | 15 | 非具体商品视觉 IP 的辅助/法务/反爬/品牌关联模板 |
| `quarantine_paste_bug` | 8 | 存在跨实体错贴 Bug（标题与正文目标冲突，必须隔离修复） |
| `quarantine_test_junk` | 10 | 测试垃圾模板（`5678`、`NyeTest*`、`test111`、`lingjinglan_test`、`IPgeneraltest`） |
| `needs_body_completion` | 1 | 空壳占位模板（如 `397 ip_molson_mianshen`） |

### 2.2 模板自身缺陷与类间边界隐患（已排除导出硬编码干扰）

| 缺陷/隐患类型 | 命中版本数 | 典型表现 |
|---|---:|---|
| `broken_json_schema` | 132 | `jason`、`ture`/`treue`、`default形式`、缺引号/全角冒号/圆括号等输出契约损坏 |
| `missing_exclusion_clause` | 116 | 高风险域/二创模板缺少宿主隔离、通用属性排除或证据不足判 false 的边界条款 |
| `rel_metadata_mismatch` | 66 | 关联实体字段 `rel` 存在机械子串误绑（如 `FMOD`、`Mini`、`Audi`、`Lion Air`、`Poly`、`艾莎` 等） |
| `typo_or_logic_defect` | 20 | 拼写错误、前后题号矛盾（如 `IP_RATT`）、或把 OR 误写成 ALL-AND（如 `molson_mianshen2~4`） |
| `underspecified_rubric` | 17 | 正文字数过短（<110字），只有泛问句而无判据锚点或排除条件 |
| `cross_entity_paste_bug` | 8 | 跨实体复制粘贴错误（标题与正文检查目标完全不一致） |
| `style_only_trigger_risk` | 5 | 允许仅凭“符合作品独特艺术风格/画风二创”触发，易将同画风原创 OC 误判 |
| `empty_placeholder_variable` | 4 | 变量槽位空缺（如 `根据 来判断`、`商户标题（）`） |
| `weak_anchor_or_escape_hatch` | 4 | 含“除非直观可判断 / 合理理解为指向”等模糊逃生舱，易架空前置特征约束 |
| `duplicate_role_header` | 2 | 角色设定段落重复粘贴 |
| `empty_or_trivial_body` | 1 | 实质无规则正文 |

### 2.3 类间混淆风险 & Assert 参考图对齐统计（按 352 个同族）

- **类间风险等级分布**: `high` = **171** · `medium` = **92** · `low` = **84** · `blocked_hygiene` = **5**
- **Assert 标准参考图对齐**: `approved_in_assert` = **26** · `supplement_asset_available_pending_approval` = **46** · `backlog_needs_review` = **213** · `no_assert_match` = **51** · `not_applicable_non_ip_or_test` = **16**

## 3. 跨实体错贴 Bug（必修清单）

| 版本键 | 模板标题 | 同族目录 | 错贴诊断 |
|---|---|---|---|
| `7` | `Deutsches Rotes Kreuz e.V` | [`deutsches_rotes_kreuz/`](deutsches_rotes_kreuz/diagnosis.md) | 标题为德国红十字会 (Deutsches Rotes Kreuz e.V)，正文却写“管控瑞士红十字会Logo / Swiss Red Cross”。 |
| `108::1` | `IP_marvel` | [`marvel/`](marvel/diagnosis.md) | 子版本 IP_marvel 正文误写为“是否包含迪士尼元素的信息”（同记录另一版本 IP_MARVEL_IMAGE 正常）。 |
| `179` | `IP_brand` | [`brand/`](brand/diagnosis.md) | 标题为泛用名 IP_brand，正文硬编码限定单一品牌 adidas。 |
| `231` | `IP_tintin` | [`tintin/`](tintin/diagnosis.md) | 《丁丁历险记》模板正文混入“是否符合rusty判断的核心特征”（复制粘贴残留）。；JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `248` | `IP组-nike-关键词召回识别` | [`nike/`](nike/diagnosis.md) | 标题为 IP组-nike-关键词召回识别，正文却是通用未限定 IP 字典模板。 |
| `296` | `guessprompt` | [`guess/`](guess/diagnosis.md) | 标题为 guessprompt，正文却是通用未限定 IP 字典模板（未出现 GUESS）。 |
| `346` | `ip_allblakcs` | [`all_blacks/`](all_blacks/diagnosis.md) | 标题为 ip_allblakcs（拼写误写），示例 JSON reason 混入“是否出现比利时足协相关元素”。；拼写错误：`allblakcs`（应为 allblacks） |
| `415` | `ip_southcarolina` | [`southcarolina/`](southcarolina/diagnosis.md) | 标题与细则面向南卡罗来纳大学 (South Carolina)，但括注误写为南加州大学 (University of Southern California)。 |

## 4. 全部同族目录索引（共 352 个子目录）

| 同族目录 | 审核对象 | 版本数 | 默认主版本 | 类间风险 | Assert 状态 | 文档 |
|---|---|---:|---|---|---|---|
| `511` | IP_511_1103_V2 | 2 | `27::2` `IP_511_1103_V2` | `medium` | `no_assert_match` | [主模板](511/latest_template.md) · [诊断](511/diagnosis.md) |
| `abba` | ip-abba | 1 | `312` `ip-abba` | `medium` | `backlog_needs_review` | [主模板](abba/latest_template.md) · [诊断](abba/diagnosis.md) |
| `acdcllm` | ip_acdcllm | 1 | `343` `ip_acdcllm` | `medium` | `backlog_needs_review` | [主模板](acdcllm/latest_template.md) · [诊断](acdcllm/diagnosis.md) |
| `adanola` | ip-ADANOLA | 1 | `301` `ip-ADANOLA` | `high` | `backlog_needs_review` | [主模板](adanola/latest_template.md) · [诊断](adanola/diagnosis.md) |
| `adventuretime` | IP_ADVENTURETIME_db_01 | 3 | `28::3` `IP_ADVENTURETIME_db_01` | `high` | `approved_in_assert` | [主模板](adventuretime/latest_template.md) · [诊断](adventuretime/diagnosis.md) |
| `agv` | IP_AGV | 1 | `29` `IP_AGV` | `medium` | `no_assert_match` | [主模板](agv/latest_template.md) · [诊断](agv/diagnosis.md) |
| `ajsnifty` | IP_AJSNIFTY_ALLRULE | 1 | `30` `IP_AJSNIFTY_ALLRULE` | `high` | `no_assert_match` | [主模板](ajsnifty/latest_template.md) · [诊断](ajsnifty/diagnosis.md) |
| `alabama` | ip_alabama | 1 | `344` `ip_alabama` | `medium` | `backlog_needs_review` | [主模板](alabama/latest_template.md) · [诊断](alabama/diagnosis.md) |
| `alemannia_aachen` | ip_Alemannia Aachen | 1 | `334` `ip_Alemannia Aachen` | `medium` | `backlog_needs_review` | [主模板](alemannia_aachen/latest_template.md) · [诊断](alemannia_aachen/diagnosis.md) |
| `alexandermcqueen` | IP_alexandermcqueen | 1 | `173` `IP_alexandermcqueen` | `medium` | `backlog_needs_review` | [主模板](alexandermcqueen/latest_template.md) · [诊断](alexandermcqueen/diagnosis.md) |
| `all_blacks` | 新西兰全黑队 (All Blacks) | 2 | `345` `ip_allblacks` | `low` | `backlog_needs_review` | [主模板](all_blacks/latest_template.md) · [诊断](all_blacks/diagnosis.md) |
| `ami` | IP_AMI_V1 | 1 | `32` `IP_AMI_V1` | `medium` | `no_assert_match` | [主模板](ami/latest_template.md) · [诊断](ami/diagnosis.md) |
| `amiri` | IP_AMIRI_ALLRULE | 1 | `31` `IP_AMIRI_ALLRULE` | `high` | `backlog_needs_review` | [主模板](amiri/latest_template.md) · [诊断](amiri/diagnosis.md) |
| `amongus` | IP-amongus | 1 | `16` `IP-amongus` | `low` | `backlog_needs_review` | [主模板](amongus/latest_template.md) · [诊断](amongus/diagnosis.md) |
| `angry_birds` | ip_angry birds | 1 | `347` `ip_angry birds` | `low` | `backlog_needs_review` | [主模板](angry_birds/latest_template.md) · [诊断](angry_birds/diagnosis.md) |
| `annabelle` | IP_ANNABELLE | 1 | `33` `IP_ANNABELLE` | `high` | `backlog_needs_review` | [主模板](annabelle/latest_template.md) · [诊断](annabelle/diagnosis.md) |
| `anpanman` | 面包超人 (Anpanman) | 3 | `274` `anpanman1` | `high` | `backlog_needs_review` | [主模板](anpanman/latest_template.md) · [诊断](anpanman/diagnosis.md) |
| `apf` | ip_apf | 1 | `348` `ip_apf` | `medium` | `no_assert_match` | [主模板](apf/latest_template.md) · [诊断](apf/diagnosis.md) |
| `apple` | 苹果 (Apple 产品/标识/配件) | 6 | `38` `IP_APPLE_WATCHBAND` | `medium` | `supplement_asset_available_pending_approval` | [主模板](apple/latest_template.md) · [诊断](apple/diagnosis.md) |
| `arizona_university` | 亚利桑那大学 (University of Arizona) | 2 | `335` `ip_Arizona` | `high` | `backlog_needs_review` | [主模板](arizona_university/latest_template.md) · [诊断](arizona_university/diagnosis.md) |
| `artist` | ip_artist | 1 | `350` `ip_artist` | `high` | `backlog_needs_review` | [主模板](artist/latest_template.md) · [诊断](artist/diagnosis.md) |
| `asmodee` | asmodee | 1 | `275` `asmodee` | `low` | `backlog_needs_review` | [主模板](asmodee/latest_template.md) · [诊断](asmodee/diagnosis.md) |
| `atari` | IP_atari | 1 | `175` `IP_atari` | `high` | `supplement_asset_available_pending_approval` | [主模板](atari/latest_template.md) · [诊断](atari/diagnosis.md) |
| `attack_on_titan` | IP_ATTACK_ON_TITAN | 1 | `39` `IP_ATTACK_ON_TITAN` | `high` | `backlog_needs_review` | [主模板](attack_on_titan/latest_template.md) · [诊断](attack_on_titan/diagnosis.md) |
| `audi` | 奥迪 (Audi) | 3 | `2` `AUDIselfmodel` | `high` | `supplement_asset_available_pending_approval` | [主模板](audi/latest_template.md) · [诊断](audi/diagnosis.md) |
| `aux_audit_feedback_optimizer` | ip_audit_feedback_optimizer | 1 | `352` `ip_audit_feedback_optimizer` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_audit_feedback_optimizer/latest_template.md) · [诊断](aux_audit_feedback_optimizer/diagnosis.md) |
| `aux_black_word_risk_reviewer` | black_word_risk_reviewer | 1 | `277` `black_word_risk_reviewer` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_black_word_risk_reviewer/latest_template.md) · [诊断](aux_black_word_risk_reviewer/diagnosis.md) |
| `aux_brand_alliance` | ip_brand_alliance_discoverer | 2 | `358` `ip_brand_alliance_discoverer` | `high` | `not_applicable_non_ip_or_test` | [主模板](aux_brand_alliance/latest_template.md) · [诊断](aux_brand_alliance/diagnosis.md) |
| `aux_brand_collab` | ip_brand_collab_auditor | 3 | `359` `ip_brand_collab_auditor` | `high` | `not_applicable_non_ip_or_test` | [主模板](aux_brand_collab/latest_template.md) · [诊断](aux_brand_collab/diagnosis.md) |
| `aux_crawlplatform_anti_risk` | crawlplatform_anti_risk | 1 | `292` `crawlplatform_anti_risk` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_crawlplatform_anti_risk/latest_template.md) · [诊断](aux_crawlplatform_anti_risk/diagnosis.md) |
| `aux_identifying_fake_brands` | Identifying_fake_brands | 1 | `254` `Identifying_fake_brands` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_identifying_fake_brands/latest_template.md) · [诊断](aux_identifying_fake_brands/diagnosis.md) |
| `aux_invoices` | Invoices | 1 | `255` `Invoices` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_invoices/latest_template.md) · [诊断](aux_invoices/diagnosis.md) |
| `aux_logos_review_verification_text` | logos_review_verification_text | 1 | `432` `logos_review_verification_text` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_logos_review_verification_text/latest_template.md) · [诊断](aux_logos_review_verification_text/diagnosis.md) |
| `aux_tro_brandname_alignment` | tro_brandname_alignment_gemini | 2 | `455` `tro_brandname_alignment_gemini` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_tro_brandname_alignment/latest_template.md) · [诊断](aux_tro_brandname_alignment/diagnosis.md) |
| `aux_tro_brandname_rec` | tro_brandname_rec_gemini | 1 | `457` `tro_brandname_rec_gemini` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_tro_brandname_rec/latest_template.md) · [诊断](aux_tro_brandname_rec/diagnosis.md) |
| `aux_tro_warning_case_process` | tro_warning_case_process_dome | 1 | `458` `tro_warning_case_process_dome` | `low` | `not_applicable_non_ip_or_test` | [主模板](aux_tro_warning_case_process/latest_template.md) · [诊断](aux_tro_warning_case_process/diagnosis.md) |
| `badcutebunny` | ip_badcutebunny | 1 | `353` `ip_badcutebunny` | `high` | `backlog_needs_review` | [主模板](badcutebunny/latest_template.md) · [诊断](badcutebunny/diagnosis.md) |
| `balenciaga_1103trademark` | IP_BALENCIAGA_1103TRADEMARK | 1 | `40` `IP_BALENCIAGA_1103TRADEMARK` | `high` | `backlog_needs_review` | [主模板](balenciaga_1103trademark/latest_template.md) · [诊断](balenciaga_1103trademark/diagnosis.md) |
| `balmain` | ip_balmain | 1 | `355` `ip_balmain` | `medium` | `approved_in_assert` | [主模板](balmain/latest_template.md) · [诊断](balmain/diagnosis.md) |
| `banana_republic` | Banana Republic | 2 | `49` `IP_BananaRepublic_Trademark` | `high` | `backlog_needs_review` | [主模板](banana_republic/latest_template.md) · [诊断](banana_republic/diagnosis.md) |
| `band_music_general` | 通用乐队/歌手召回 (Band) | 4 | `4::3` `ip_band_v2` | `high` | `backlog_needs_review` | [主模板](band_music_general/latest_template.md) · [诊断](band_music_general/diagnosis.md) |
| `bebe` | IP_BEBE_V2 | 2 | `41::2` `IP_BEBE_V2` | `low` | `backlog_needs_review` | [主模板](bebe/latest_template.md) · [诊断](bebe/diagnosis.md) |
| `beck_s` | IP_Beck's | 1 | `50` `IP_Beck's` | `high` | `backlog_needs_review` | [主模板](beck_s/latest_template.md) · [诊断](beck_s/diagnosis.md) |
| `bench` | IP_BENCH_0409 | 1 | `42` `IP_BENCH_0409` | `low` | `backlog_needs_review` | [主模板](bench/latest_template.md) · [诊断](bench/diagnosis.md) |
| `benchmade` | IP_benchmade | 2 | `177::1` `IP_benchmade` | `low` | `backlog_needs_review` | [主模板](benchmade/latest_template.md) · [诊断](benchmade/diagnosis.md) |
| `bensonboone` | bensonboone | 1 | `276` `bensonboone` | `medium` | `backlog_needs_review` | [主模板](bensonboone/latest_template.md) · [诊断](bensonboone/diagnosis.md) |
| `bentley` | ip_bentley_prompt | 1 | `356` `ip_bentley_prompt` | `medium` | `backlog_needs_review` | [主模板](bentley/latest_template.md) · [诊断](bentley/diagnosis.md) |
| `berserk` | IP_BERSERK_strategy | 2 | `43::2` `IP_BERSERK_strategy` | `high` | `backlog_needs_review` | [主模板](berserk/latest_template.md) · [诊断](berserk/diagnosis.md) |
| `beyonce` | IP_beyonce_strategy | 2 | `44::2` `IP_beyonce_strategy` | `high` | `supplement_asset_available_pending_approval` | [主模板](beyonce/latest_template.md) · [诊断](beyonce/diagnosis.md) |
| `bigfoot` | IP_BIGFOOT_V5 | 5 | `45::5` `IP_BIGFOOT_V5` | `low` | `backlog_needs_review` | [主模板](bigfoot/latest_template.md) · [诊断](bigfoot/diagnosis.md) |
| `billionaire_boys_club` | Billionaire Boys Club | 2 | `47` `IP_BILLIONAIREBOYSCLUB1103` | `medium` | `no_assert_match` | [主模板](billionaire_boys_club/latest_template.md) · [诊断](billionaire_boys_club/diagnosis.md) |
| `bleach` | 死神/境·界 (BLEACH) | 2 | `279` `bleachtoy50gmv` | `high` | `approved_in_assert` | [主模板](bleach/latest_template.md) · [诊断](bleach/diagnosis.md) |
| `bmw` | IP_bmw | 1 | `178` `IP_bmw` | `high` | `supplement_asset_available_pending_approval` | [主模板](bmw/latest_template.md) · [诊断](bmw/diagnosis.md) |
| `bp` | IP_BP | 1 | `48` `IP_BP` | `medium` | `no_assert_match` | [主模板](bp/latest_template.md) · [诊断](bp/diagnosis.md) |
| `brand` | IP_brand | 1 | `179` `IP_brand` | `medium` | `no_assert_match` | [主模板](brand/latest_template.md) · [诊断](brand/diagnosis.md) |
| `brand_gemini_general` | 通用品牌宿主隔离审核 (Gemini) | 3 | `362` `ip_brand_gemini_general` | `high` | `backlog_needs_review` | [主模板](brand_gemini_general/latest_template.md) · [诊断](brand_gemini_general/diagnosis.md) |
| `brand_goods_consistent_multi_img` | 多图商品品牌一致性审核 | 3 | `366` `ip_brand_goods_consistent_multi_imgV2` | `high` | `backlog_needs_review` | [主模板](brand_goods_consistent_multi_img/latest_template.md) · [诊断](brand_goods_consistent_multi_img/diagnosis.md) |
| `brawl_stars` | 荒野乱斗 (Brawl Stars) | 3 | `280` `brawlstarsselfmodel` | `high` | `backlog_needs_review` | [主模板](brawl_stars/latest_template.md) · [诊断](brawl_stars/diagnosis.md) |
| `budweiser` | IP_Budweiser | 1 | `52` `IP_Budweiser` | `high` | `approved_in_assert` | [主模板](budweiser/latest_template.md) · [诊断](budweiser/diagnosis.md) |
| `buick` | ip_buick_prompt | 1 | `367` `ip_buick_prompt` | `medium` | `backlog_needs_review` | [主模板](buick/latest_template.md) · [诊断](buick/diagnosis.md) |
| `burberry` | IP_Burberry | 1 | `53` `IP_Burberry` | `high` | `backlog_needs_review` | [主模板](burberry/latest_template.md) · [诊断](burberry/diagnosis.md) |
| `butterfly` | IP_Butterfly | 1 | `54` `IP_Butterfly` | `low` | `backlog_needs_review` | [主模板](butterfly/latest_template.md) · [诊断](butterfly/diagnosis.md) |
| `calvin_klein` | Calvin Klein (CK) | 12 | `55::2` `IP_CALVIN_v2` | `medium` | `backlog_needs_review` | [主模板](calvin_klein/latest_template.md) · [诊断](calvin_klein/diagnosis.md) |
| `cars_automotive_general` | 汽车品牌通用侵权与配件豁免 (Cars Automotive) | 3 | `298` `hemier-cars-selfmodel` | `high` | `supplement_asset_available_pending_approval` | [主模板](cars_automotive_general/latest_template.md) · [诊断](cars_automotive_general/diagnosis.md) |
| `cbf` | ip-cbf | 1 | `315` `ip-cbf` | `medium` | `no_assert_match` | [主模板](cbf/latest_template.md) · [诊断](cbf/diagnosis.md) |
| `celine` | ip_celine | 1 | `369` `ip_celine` | `high` | `backlog_needs_review` | [主模板](celine/latest_template.md) · [诊断](celine/diagnosis.md) |
| `chainsawman` | chainsawman | 1 | `281` `chainsawman` | `high` | `supplement_asset_available_pending_approval` | [主模板](chainsawman/latest_template.md) · [诊断](chainsawman/diagnosis.md) |
| `champion` | Champion | 2 | `282` `champion1103test0511` | `medium` | `approved_in_assert` | [主模板](champion/latest_template.md) · [诊断](champion/diagnosis.md) |
| `chanel_cc` | IP_CHANEL_CC | 1 | `57` `IP_CHANEL_CC` | `medium` | `backlog_needs_review` | [主模板](chanel_cc/latest_template.md) · [诊断](chanel_cc/diagnosis.md) |
| `chevrolet` | chevrolet | 2 | `283::1` `chevrolet` | `high` | `backlog_needs_review` | [主模板](chevrolet/latest_template.md) · [诊断](chevrolet/diagnosis.md) |
| `chloe` | IP_CHLOE | 1 | `58` `IP_CHLOE` | `high` | `backlog_needs_review` | [主模板](chloe/latest_template.md) · [诊断](chloe/diagnosis.md) |
| `clash_royale` | ip_clash royale | 1 | `371` `ip_clash royale` | `low` | `backlog_needs_review` | [主模板](clash_royale/latest_template.md) · [诊断](clash_royale/diagnosis.md) |
| `cluster_gemini` | 通用聚类品牌/山寨/独立站审查 (Gemini) | 4 | `375` `ip_cluster_gemini_grounding` | `high` | `backlog_needs_review` | [主模板](cluster_gemini/latest_template.md) · [诊断](cluster_gemini/diagnosis.md) |
| `cobra` | IP_COBRA | 2 | `18::2` `IP_COBRA` | `high` | `backlog_needs_review` | [主模板](cobra/latest_template.md) · [诊断](cobra/diagnosis.md) |
| `cohiba` | cohibaselfmodel | 1 | `289` `cohibaselfmodel` | `high` | `backlog_needs_review` | [主模板](cohiba/latest_template.md) · [诊断](cohiba/diagnosis.md) |
| `converseallstar` | converseallstar | 1 | `290` `converseallstar` | `low` | `backlog_needs_review` | [主模板](converseallstar/latest_template.md) · [诊断](converseallstar/diagnosis.md) |
| `cookie_run` | ip-cookie run-prompt | 1 | `316` `ip-cookie run-prompt` | `low` | `backlog_needs_review` | [主模板](cookie_run/latest_template.md) · [诊断](cookie_run/diagnosis.md) |
| `cookies` | IP_COOKIES | 2 | `59::1` `IP_COOKIES` | `high` | `backlog_needs_review` | [主模板](cookies/latest_template.md) · [诊断](cookies/diagnosis.md) |
| `coraline` | IP_CORALINE | 1 | `60` `IP_CORALINE` | `low` | `no_assert_match` | [主模板](coraline/latest_template.md) · [诊断](coraline/diagnosis.md) |
| `corona` | IP_corona | 1 | `181` `IP_corona` | `high` | `backlog_needs_review` | [主模板](corona/latest_template.md) · [诊断](corona/diagnosis.md) |
| `costadelmar_costa` | IP_costadelmar_COSTA | 1 | `182` `IP_costadelmar_COSTA` | `medium` | `supplement_asset_available_pending_approval` | [主模板](costadelmar_costa/latest_template.md) · [诊断](costadelmar_costa/diagnosis.md) |
| `counterfeit_jerseys` | IP-Counterfeit Jerseys | 1 | `8` `IP-Counterfeit Jerseys` | `medium` | `backlog_needs_review` | [主模板](counterfeit_jerseys/latest_template.md) · [诊断](counterfeit_jerseys/diagnosis.md) |
| `counterfeit_watch` | 奢侈手表多品牌侵权治理 | 2 | `9` `IP-Counterfeit Watch` | `high` | `backlog_needs_review` | [主模板](counterfeit_watch/latest_template.md) · [诊断](counterfeit_watch/diagnosis.md) |
| `courtneymorgenstern` | IP_CourtneyMorgenstern | 1 | `63` `IP_CourtneyMorgenstern` | `high` | `backlog_needs_review` | [主模板](courtneymorgenstern/latest_template.md) · [诊断](courtneymorgenstern/diagnosis.md) |
| `covernat` | covernat_prompt | 1 | `291` `covernat_prompt` | `medium` | `backlog_needs_review` | [主模板](covernat/latest_template.md) · [诊断](covernat/diagnosis.md) |
| `cowboybebop` | IP_COWBOYBEBOP | 1 | `61` `IP_COWBOYBEBOP` | `high` | `backlog_needs_review` | [主模板](cowboybebop/latest_template.md) · [诊断](cowboybebop/diagnosis.md) |
| `crayonshinchan` | IP_crayonshinchan | 1 | `183` `IP_crayonshinchan` | `high` | `no_assert_match` | [主模板](crayonshinchan/latest_template.md) · [诊断](crayonshinchan/diagnosis.md) |
| `crocs_charms` | 洞洞鞋及鞋花配件 (Crocs Charms) | 3 | `185` `IP_crocs_charms2` | `medium` | `no_assert_match` | [主模板](crocs_charms/latest_template.md) · [诊断](crocs_charms/diagnosis.md) |
| `cucu` | ip-Cucu-prompt | 1 | `302` `ip-Cucu-prompt` | `high` | `backlog_needs_review` | [主模板](cucu/latest_template.md) · [诊断](cucu/diagnosis.md) |
| `cwt_legging` | ip_cwt legging | 1 | `377` `ip_cwt legging` | `low` | `backlog_needs_review` | [主模板](cwt_legging/latest_template.md) · [诊断](cwt_legging/diagnosis.md) |
| `daddario` | IP_DADDARIO | 1 | `64` `IP_DADDARIO` | `high` | `backlog_needs_review` | [主模板](daddario/latest_template.md) · [诊断](daddario/diagnosis.md) |
| `dandys_world` | Dandy's World | 2 | `72` `IP_DandysWorld` | `high` | `backlog_needs_review` | [主模板](dandys_world/latest_template.md) · [诊断](dandys_world/diagnosis.md) |
| `dav_pilkey_dogman` | 神探狗狗 (Dav Pilkey / Dog Man) | 3 | `74` `IP_DavPilkey_dogman` | `high` | `supplement_asset_available_pending_approval` | [主模板](dav_pilkey_dogman/latest_template.md) · [诊断](dav_pilkey_dogman/diagnosis.md) |
| `dc_comics` | DC 漫画 (DC Comics) | 3 | `66` `IP_DCCOMICS_HIGHACCURACY` | `high` | `approved_in_assert` | [主模板](dc_comics/latest_template.md) · [诊断](dc_comics/diagnosis.md) |
| `dc_shoes` | DC Shoes | 1 | `67` `IP_DCShoes` | `medium` | `no_assert_match` | [主模板](dc_shoes/latest_template.md) · [诊断](dc_shoes/diagnosis.md) |
| `demon_slayer` | 鬼灭之刃 (Demon Slayer) | 6 | `188` `IP_demonslayer_huawen` | `high` | `supplement_asset_available_pending_approval` | [主模板](demon_slayer/latest_template.md) · [诊断](demon_slayer/diagnosis.md) |
| `deutsches_rotes_kreuz` | 德国红十字会 / 错贴瑞士红十字会模板 | 1 | `7` `Deutsches Rotes Kreuz e.V` | `high` | `backlog_needs_review` | [主模板](deutsches_rotes_kreuz/latest_template.md) · [诊断](deutsches_rotes_kreuz/diagnosis.md) |
| `dior` | 迪奥 (Dior) | 2 | `69` `IP_DIOR_TRADEMARK` | `high` | `no_assert_match` | [主模板](dior/latest_template.md) · [诊断](dior/diagnosis.md) |
| `disney` | 迪士尼 (Disney) | 1 | `246` `IP组-disney-召回识别` | `low` | `supplement_asset_available_pending_approval` | [主模板](disney/latest_template.md) · [诊断](disney/diagnosis.md) |
| `dodge` | IP_dodge_llm | 1 | `191` `IP_dodge_llm` | `high` | `backlog_needs_review` | [主模板](dodge/latest_template.md) · [诊断](dodge/diagnosis.md) |
| `dominos` | IP_DOMINOS | 1 | `70` `IP_DOMINOS` | `low` | `approved_in_assert` | [主模板](dominos/latest_template.md) · [诊断](dominos/diagnosis.md) |
| `doubleendedhandtool` | IP_doubleendedhandtool | 1 | `192` `IP_doubleendedhandtool` | `high` | `backlog_needs_review` | [主模板](doubleendedhandtool/latest_template.md) · [诊断](doubleendedhandtool/diagnosis.md) |
| `dragonball` | ip_dragonball | 2 | `317::2` `ip_dragonball` | `high` | `supplement_asset_available_pending_approval` | [主模板](dragonball/latest_template.md) · [诊断](dragonball/diagnosis.md) |
| `dsquared2` | DSQUARED2selfmodel | 1 | `6` `DSQUARED2selfmodel` | `medium` | `backlog_needs_review` | [主模板](dsquared2/latest_template.md) · [诊断](dsquared2/diagnosis.md) |
| `duke_university` | 杜克大学 (Duke University) | 3 | `380` `ip_duke_excepmtion` | `high` | `backlog_needs_review` | [主模板](duke_university/latest_template.md) · [诊断](duke_university/diagnosis.md) |
| `dune` | IP_DUNE | 1 | `71` `IP_DUNE` | `high` | `backlog_needs_review` | [主模板](dune/latest_template.md) · [诊断](dune/diagnosis.md) |
| `ecco` | ip_ecco | 1 | `381` `ip_ecco` | `low` | `backlog_needs_review` | [主模板](ecco/latest_template.md) · [诊断](ecco/diagnosis.md) |
| `elvis` | IP_elvis | 1 | `193` `IP_elvis` | `high` | `no_assert_match` | [主模板](elvis/latest_template.md) · [诊断](elvis/diagnosis.md) |
| `et` | IP_ET | 1 | `75` `IP_ET` | `high` | `no_assert_match` | [主模板](et/latest_template.md) · [诊断](et/diagnosis.md) |
| `evelknievel` | IP_evelknievel | 1 | `194` `IP_evelknievel` | `low` | `supplement_asset_available_pending_approval` | [主模板](evelknievel/latest_template.md) · [诊断](evelknievel/diagnosis.md) |
| `fallout` | IP_FALLOUT | 1 | `76` `IP_FALLOUT` | `low` | `approved_in_assert` | [主模板](fallout/latest_template.md) · [诊断](fallout/diagnosis.md) |
| `fender` | IP_fender | 1 | `195` `IP_fender` | `high` | `backlog_needs_review` | [主模板](fender/latest_template.md) · [诊断](fender/diagnosis.md) |
| `ferrari` | ip_Ferrari | 1 | `336` `ip_Ferrari` | `medium` | `backlog_needs_review` | [主模板](ferrari/latest_template.md) · [诊断](ferrari/diagnosis.md) |
| `florida` | ip_florida | 1 | `382` `ip_florida` | `medium` | `backlog_needs_review` | [主模板](florida/latest_template.md) · [诊断](florida/diagnosis.md) |
| `ford` | 福特汽车 (Ford) | 5 | `385` `ip_ford_mat` | `high` | `supplement_asset_available_pending_approval` | [主模板](ford/latest_template.md) · [诊断](ford/diagnosis.md) |
| `forza` | IP_FORZA | 1 | `77` `IP_FORZA` | `low` | `backlog_needs_review` | [主模板](forza/latest_template.md) · [诊断](forza/diagnosis.md) |
| `friends` | 老友记 (Friends) | 1 | `247` `IP组-friends-图像识别` | `low` | `approved_in_assert` | [主模板](friends/latest_template.md) · [诊断](friends/diagnosis.md) |
| `gant` | IP_GANT | 1 | `78` `IP_GANT` | `low` | `backlog_needs_review` | [主模板](gant/latest_template.md) · [诊断](gant/diagnosis.md) |
| `gap` | IP_gap_prompt | 1 | `196` `IP_gap_prompt` | `high` | `no_assert_match` | [主模板](gap/latest_template.md) · [诊断](gap/diagnosis.md) |
| `general_ip_model_nxy` | general_IP_Model_nxy | 1 | `293` `general_IP_Model_nxy` | `high` | `backlog_needs_review` | [主模板](general_ip_model_nxy/latest_template.md) · [诊断](general_ip_model_nxy/diagnosis.md) |
| `general_rihe` | ip_general_rihe | 1 | `386` `ip_general_rihe` | `high` | `backlog_needs_review` | [主模板](general_rihe/latest_template.md) · [诊断](general_rihe/diagnosis.md) |
| `genies_perfume_atomizer` | IP_genies | 1 | `197` `IP_genies` | `high` | `backlog_needs_review` | [主模板](genies_perfume_atomizer/latest_template.md) · [诊断](genies_perfume_atomizer/diagnosis.md) |
| `glassangelofficial` | glassangelofficial | 1 | `294` `glassangelofficial` | `low` | `backlog_needs_review` | [主模板](glassangelofficial/latest_template.md) · [诊断](glassangelofficial/diagnosis.md) |
| `godzilla` | ip_godzilla_3 | 3 | `387::3` `ip_godzilla_3` | `low` | `approved_in_assert` | [主模板](godzilla/latest_template.md) · [诊断](godzilla/diagnosis.md) |
| `goodyear` | IP_goodyear | 1 | `198` `IP_goodyear` | `medium` | `backlog_needs_review` | [主模板](goodyear/latest_template.md) · [诊断](goodyear/diagnosis.md) |
| `goorinbros` | IP_Goorinbros | 1 | `82` `IP_Goorinbros` | `low` | `backlog_needs_review` | [主模板](goorinbros/latest_template.md) · [诊断](goorinbros/diagnosis.md) |
| `gopro_logoauto` | IP_gopro_logoauto | 1 | `199` `IP_gopro_logoauto` | `high` | `no_assert_match` | [主模板](gopro_logoauto/latest_template.md) · [诊断](gopro_logoauto/diagnosis.md) |
| `gorillaglue` | IP_gorillaglue | 1 | `200` `IP_gorillaglue` | `medium` | `backlog_needs_review` | [主模板](gorillaglue/latest_template.md) · [诊断](gorillaglue/diagnosis.md) |
| `greenday` | IP_GREENDAY_OCR | 1 | `79` `IP_GREENDAY_OCR` | `medium` | `backlog_needs_review` | [主模板](greenday/latest_template.md) · [诊断](greenday/diagnosis.md) |
| `guess` | GUESS | 4 | `201` `IP_guess_penalty` | `high` | `approved_in_assert` | [主模板](guess/latest_template.md) · [诊断](guess/diagnosis.md) |
| `guinness` | IP_GUINNESS | 1 | `80` `IP_GUINNESS` | `high` | `backlog_needs_review` | [主模板](guinness/latest_template.md) · [诊断](guinness/diagnosis.md) |
| `gulf` | ip_gulf | 1 | `388` `ip_gulf` | `low` | `approved_in_assert` | [主模板](gulf/latest_template.md) · [诊断](gulf/diagnosis.md) |
| `gunsnroses` | IP_gunsnroses_strategy | 2 | `81::2` `IP_gunsnroses_strategy` | `high` | `approved_in_assert` | [主模板](gunsnroses/latest_template.md) · [诊断](gunsnroses/diagnosis.md) |
| `haribotitle` | haribotitle | 1 | `297` `haribotitle` | `low` | `backlog_needs_review` | [主模板](haribotitle/latest_template.md) · [诊断](haribotitle/diagnosis.md) |
| `harrypotter` | IP-HarryPotter | 3 | `10::1` `IP-HarryPotter` | `low` | `backlog_needs_review` | [主模板](harrypotter/latest_template.md) · [诊断](harrypotter/diagnosis.md) |
| `hatsune_miku` | 初音未来 (Hatsune Miku) | 5 | `84::4` `IP_HATSUNEMIKU_V4` | `high` | `supplement_asset_available_pending_approval` | [主模板](hatsune_miku/latest_template.md) · [诊断](hatsune_miku/diagnosis.md) |
| `hells_angles_motorcycle` | IP_HELLS_ANGLES_MOTORCYCLE | 1 | `85` `IP_HELLS_ANGLES_MOTORCYCLE` | `low` | `no_assert_match` | [主模板](hells_angles_motorcycle/latest_template.md) · [诊断](hells_angles_motorcycle/diagnosis.md) |
| `hemier_league` | hemier-league-selfmodel | 1 | `299` `hemier-league-selfmodel` | `medium` | `supplement_asset_available_pending_approval` | [主模板](hemier_league/latest_template.md) · [诊断](hemier_league/diagnosis.md) |
| `hendrickmotorsports` | IP_Hendrickmotorsports | 1 | `88` `IP_Hendrickmotorsports` | `medium` | `backlog_needs_review` | [主模板](hendrickmotorsports/latest_template.md) · [诊断](hendrickmotorsports/diagnosis.md) |
| `hermes` | 爱马仕 (Hermès) | 6 | `90` `IP_Hermes_Giftbox` | `high` | `no_assert_match` | [主模板](hermes/latest_template.md) · [诊断](hermes/diagnosis.md) |
| `higuchi_yuko` | 樋口裕子 (Higuchi Yuko) | 2 | `318` `ip-higuchiyoko strict ver` | `high` | `backlog_needs_review` | [主模板](higuchi_yuko/latest_template.md) · [诊断](higuchi_yuko/diagnosis.md) |
| `hilton` | IP_Hilton | 1 | `94` `IP_Hilton` | `medium` | `no_assert_match` | [主模板](hilton/latest_template.md) · [诊断](hilton/diagnosis.md) |
| `hollister` | hollister | 1 | `300` `hollister` | `low` | `backlog_needs_review` | [主模板](hollister/latest_template.md) · [诊断](hollister/diagnosis.md) |
| `honda` | IP_honda | 1 | `202` `IP_honda` | `high` | `no_assert_match` | [主模板](honda/latest_template.md) · [诊断](honda/diagnosis.md) |
| `hotstuff` | IP_HOTSTUFF_IMG | 1 | `87` `IP_HOTSTUFF_IMG` | `low` | `no_assert_match` | [主模板](hotstuff/latest_template.md) · [诊断](hotstuff/diagnosis.md) |
| `household` | IP_Household | 1 | `95` `IP_Household` | `low` | `no_assert_match` | [主模板](household/latest_template.md) · [诊断](household/diagnosis.md) |
| `infringement_detection` | IP_Infringement_Detection | 1 | `96` `IP_Infringement_Detection` | `high` | `no_assert_match` | [主模板](infringement_detection/latest_template.md) · [诊断](infringement_detection/diagnosis.md) |
| `infringementcards` | ip_infringementcards | 1 | `389` `ip_infringementcards` | `high` | `backlog_needs_review` | [主模板](infringementcards/latest_template.md) · [诊断](infringementcards/diagnosis.md) |
| `itmovie` | itmovie | 1 | `427` `itmovie` | `low` | `backlog_needs_review` | [主模板](itmovie/latest_template.md) · [诊断](itmovie/diagnosis.md) |
| `jeep` | ip_jeep | 1 | `390` `ip_jeep` | `high` | `backlog_needs_review` | [主模板](jeep/latest_template.md) · [诊断](jeep/diagnosis.md) |
| `jenny_urquhart` | ip-Jenny Urquhart-prompt | 1 | `303` `ip-Jenny Urquhart-prompt` | `medium` | `backlog_needs_review` | [主模板](jenny_urquhart/latest_template.md) · [诊断](jenny_urquhart/diagnosis.md) |
| `jiaxiangye` | IP_JIAXIANGYE | 1 | `97` `IP_JIAXIANGYE` | `high` | `backlog_needs_review` | [主模板](jiaxiangye/latest_template.md) · [诊断](jiaxiangye/diagnosis.md) |
| `jim_beam` | IP_Jim_Beam | 1 | `99` `IP_Jim_Beam` | `medium` | `backlog_needs_review` | [主模板](jim_beam/latest_template.md) · [诊断](jim_beam/diagnosis.md) |
| `juicewrld` | IP-juicewrld | 1 | `19` `IP-juicewrld` | `low` | `backlog_needs_review` | [主模板](juicewrld/latest_template.md) · [诊断](juicewrld/diagnosis.md) |
| `jujutsukaisen` | IP_JUJUTSUKAISEN | 1 | `98` `IP_JUJUTSUKAISEN` | `high` | `approved_in_assert` | [主模板](jujutsukaisen/latest_template.md) · [诊断](jujutsukaisen/diagnosis.md) |
| `juliusk9` | JULIUSK9 | 1 | `259` `JULIUSK9` | `high` | `approved_in_assert` | [主模板](juliusk9/latest_template.md) · [诊断](juliusk9/diagnosis.md) |
| `junjiito` | IP_junjiIto | 1 | `203` `IP_junjiIto` | `high` | `backlog_needs_review` | [主模板](junjiito/latest_template.md) · [诊断](junjiito/diagnosis.md) |
| `kaffe` | ip-KAFFE-prompt | 1 | `304` `ip-KAFFE-prompt` | `low` | `backlog_needs_review` | [主模板](kaffe/latest_template.md) · [诊断](kaffe/diagnosis.md) |
| `kimesranch` | IP_kimesranch | 1 | `204` `IP_kimesranch` | `low` | `backlog_needs_review` | [主模板](kimesranch/latest_template.md) · [诊断](kimesranch/diagnosis.md) |
| `kirby` | kirby | 1 | `428` `kirby` | `low` | `backlog_needs_review` | [主模板](kirby/latest_template.md) · [诊断](kirby/diagnosis.md) |
| `kith` | KITH_llm | 1 | `260` `KITH_llm` | `high` | `backlog_needs_review` | [主模板](kith/latest_template.md) · [诊断](kith/diagnosis.md) |
| `kpop` | ip-kpop | 1 | `320` `ip-kpop` | `medium` | `backlog_needs_review` | [主模板](kpop/latest_template.md) · [诊断](kpop/diagnosis.md) |
| `ktm` | KTM_prompt | 1 | `261` `KTM_prompt` | `medium` | `backlog_needs_review` | [主模板](ktm/latest_template.md) · [诊断](ktm/diagnosis.md) |
| `lacoste` | IP_lacoste | 1 | `205` `IP_lacoste` | `high` | `backlog_needs_review` | [主模板](lacoste/latest_template.md) · [诊断](lacoste/diagnosis.md) |
| `ledzeppelin` | IP_LEDZEPPELIN | 1 | `100` `IP_LEDZEPPELIN` | `medium` | `backlog_needs_review` | [主模板](ledzeppelin/latest_template.md) · [诊断](ledzeppelin/diagnosis.md) |
| `legorelated` | ip_legorelated | 1 | `391` `ip_legorelated` | `low` | `backlog_needs_review` | [主模板](legorelated/latest_template.md) · [诊断](legorelated/diagnosis.md) |
| `libertyuniversity` | IP_LibertyUniversity | 1 | `102` `IP_LibertyUniversity` | `medium` | `backlog_needs_review` | [主模板](libertyuniversity/latest_template.md) · [诊断](libertyuniversity/diagnosis.md) |
| `lindseyferrell` | IP_lindseyferrell | 1 | `206` `IP_lindseyferrell` | `high` | `backlog_needs_review` | [主模板](lindseyferrell/latest_template.md) · [诊断](lindseyferrell/diagnosis.md) |
| `lionel_messi` | IP-Lionel Messi | 1 | `11` `IP-Lionel Messi` | `high` | `backlog_needs_review` | [主模板](lionel_messi/latest_template.md) · [诊断](lionel_messi/diagnosis.md) |
| `loewe` | 罗意威 (Loewe) | 2 | `103` `IP_Loewe_logo` | `high` | `approved_in_assert` | [主模板](loewe/latest_template.md) · [诊断](loewe/diagnosis.md) |
| `logo_similar_judge` | logo_similar_judge | 1 | `431` `logo_similar_judge` | `high` | `backlog_needs_review` | [主模板](logo_similar_judge/latest_template.md) · [诊断](logo_similar_judge/diagnosis.md) |
| `louisvuitton` | IP_louisvuitton | 1 | `207` `IP_louisvuitton` | `medium` | `approved_in_assert` | [主模板](louisvuitton/latest_template.md) · [诊断](louisvuitton/diagnosis.md) |
| `lupinthethird` | IP_lupinthethird | 1 | `208` `IP_lupinthethird` | `high` | `backlog_needs_review` | [主模板](lupinthethird/latest_template.md) · [诊断](lupinthethird/diagnosis.md) |
| `maison_margiela` | 马丁·马吉拉 (Maison Margiela) | 3 | `114` `IP_MM_SEAM LOGO` | `high` | `backlog_needs_review` | [主模板](maison_margiela/latest_template.md) · [诊断](maison_margiela/diagnosis.md) |
| `mandms` | IP_mandms | 1 | `209` `IP_mandms` | `high` | `supplement_asset_available_pending_approval` | [主模板](mandms/latest_template.md) · [诊断](mandms/diagnosis.md) |
| `maradona` | 马拉多纳 (Diego Maradona) | 2 | `306` `ip-Maradona` | `high` | `backlog_needs_review` | [主模板](maradona/latest_template.md) · [诊断](maradona/diagnosis.md) |
| `marcon` | ip_marcon | 1 | `392` `ip_marcon` | `low` | `backlog_needs_review` | [主模板](marcon/latest_template.md) · [诊断](marcon/diagnosis.md) |
| `marilyn_monroe` | 玛丽莲·梦露 (Marilyn Monroe) | 2 | `106` `IP_MARILYNMONROE_MARILYN` | `medium` | `backlog_needs_review` | [主模板](marilyn_monroe/latest_template.md) · [诊断](marilyn_monroe/diagnosis.md) |
| `marshall` | IP_marshall | 1 | `211` `IP_marshall` | `high` | `backlog_needs_review` | [主模板](marshall/latest_template.md) · [诊断](marshall/diagnosis.md) |
| `marvel` | 漫威角色 (Marvel) | 3 | `107` `IP_MARVELCHARACTER` | `high` | `no_assert_match` | [主模板](marvel/latest_template.md) · [诊断](marvel/diagnosis.md) |
| `maryland` | ip_maryland | 1 | `393` `ip_maryland` | `medium` | `backlog_needs_review` | [主模板](maryland/latest_template.md) · [诊断](maryland/diagnosis.md) |
| `mastermind` | MASTERMIND | 1 | `262` `MASTERMIND` | `low` | `backlog_needs_review` | [主模板](mastermind/latest_template.md) · [诊断](mastermind/diagnosis.md) |
| `mcdonald` | McDonald | 1 | `263` `McDonald` | `low` | `backlog_needs_review` | [主模板](mcdonald/latest_template.md) · [诊断](mcdonald/diagnosis.md) |
| `mcm` | IP_MCM | 1 | `109` `IP_MCM` | `high` | `no_assert_match` | [主模板](mcm/latest_template.md) · [诊断](mcm/diagnosis.md) |
| `mega` | IP_MEGA | 1 | `110` `IP_MEGA` | `low` | `no_assert_match` | [主模板](mega/latest_template.md) · [诊断](mega/diagnosis.md) |
| `megaman` | IP_megaman | 2 | `20::2` `IP_megaman` | `high` | `backlog_needs_review` | [主模板](megaman/latest_template.md) · [诊断](megaman/diagnosis.md) |
| `meitanteikonan` | IP_meitanteikonan | 1 | `212` `IP_meitanteikonan` | `high` | `no_assert_match` | [主模板](meitanteikonan/latest_template.md) · [诊断](meitanteikonan/diagnosis.md) |
| `men_of_mayhem` | ip-MEN OF MAYHEM-prompt | 1 | `305` `ip-MEN OF MAYHEM-prompt` | `low` | `backlog_needs_review` | [主模板](men_of_mayhem/latest_template.md) · [诊断](men_of_mayhem/diagnosis.md) |
| `mercedes_benz` | IP_Mercedes_benz | 1 | `118` `IP_Mercedes_benz` | `high` | `backlog_needs_review` | [主模板](mercedes_benz/latest_template.md) · [诊断](mercedes_benz/diagnosis.md) |
| `merchtraffic` | MerchTraffic | 1 | `264` `MerchTraffic` | `high` | `backlog_needs_review` | [主模板](merchtraffic/latest_template.md) · [诊断](merchtraffic/diagnosis.md) |
| `metallica` | IP_metallica_Strategy | 3 | `213::3` `IP_metallica_Strategy` | `high` | `supplement_asset_available_pending_approval` | [主模板](metallica/latest_template.md) · [诊断](metallica/diagnosis.md) |
| `michael_jackson` | 迈克尔·杰克逊 (Michael Jackson) | 4 | `112::2` `IP_MICHAELJACKSON_MJ_V2` | `high` | `backlog_needs_review` | [主模板](michael_jackson/latest_template.md) · [诊断](michael_jackson/diagnosis.md) |
| `michigan_state` | 密歇根州立大学斯巴达人队 (Michigan State) | 1 | `433` `michiganstate` | `medium` | `backlog_needs_review` | [主模板](michigan_state/latest_template.md) · [诊断](michigan_state/diagnosis.md) |
| `miffyrabbit` | IP_MIFFYRABBIT_HIGHACCURACY | 1 | `113` `IP_MIFFYRABBIT_HIGHACCURACY` | `medium` | `supplement_asset_available_pending_approval` | [主模板](miffyrabbit/latest_template.md) · [诊断](miffyrabbit/diagnosis.md) |
| `milwaukeetool` | ip-milwaukeetool | 1 | `321` `ip-milwaukeetool` | `low` | `backlog_needs_review` | [主模板](milwaukeetool/latest_template.md) · [诊断](milwaukeetool/diagnosis.md) |
| `minions` | IP_Minions | 1 | `119` `IP_Minions` | `high` | `backlog_needs_review` | [主模板](minions/latest_template.md) · [诊断](minions/diagnosis.md) |
| `mitsubishipencil` | IP_mitsubishipencil_prompt | 2 | `214::2` `IP_mitsubishipencil_prompt` | `medium` | `no_assert_match` | [主模板](mitsubishipencil/latest_template.md) · [诊断](mitsubishipencil/diagnosis.md) |
| `miumiu` | ip-miumiu | 5 | `322::1` `ip-miumiu` | `high` | `backlog_needs_review` | [主模板](miumiu/latest_template.md) · [诊断](miumiu/diagnosis.md) |
| `molson_coors` | 莫尔森库尔斯啤酒 (Molson Coors / Miller) | 5 | `400` `ip_molson_mianshen4` | `medium` | `backlog_needs_review` | [主模板](molson_coors/latest_template.md) · [诊断](molson_coors/diagnosis.md) |
| `monchhichi` | ip_monchhichi | 1 | `401` `ip_monchhichi` | `medium` | `backlog_needs_review` | [主模板](monchhichi/latest_template.md) · [诊断](monchhichi/diagnosis.md) |
| `money_heist_la_casa_de_papel` | 纸钞屋 / 西班牙影视 (La Casa De Papel) | 1 | `416` `ip_spian drama` | `medium` | `backlog_needs_review` | [主模板](money_heist_la_casa_de_papel/latest_template.md) · [诊断](money_heist_la_casa_de_papel/diagnosis.md) |
| `monopoly` | 大富翁 (Monopoly) | 2 | `333` `ip-大富翁` | `high` | `backlog_needs_review` | [主模板](monopoly/latest_template.md) · [诊断](monopoly/diagnosis.md) |
| `monsterenergy` | monsterenergy | 1 | `434` `monsterenergy` | `medium` | `backlog_needs_review` | [主模板](monsterenergy/latest_template.md) · [诊断](monsterenergy/diagnosis.md) |
| `monsterhigh` | IP_MonsterHigh | 1 | `120` `IP_MonsterHigh` | `high` | `no_assert_match` | [主模板](monsterhigh/latest_template.md) · [诊断](monsterhigh/diagnosis.md) |
| `moschino` | IP-moschino | 1 | `21` `IP-moschino` | `low` | `backlog_needs_review` | [主模板](moschino/latest_template.md) · [诊断](moschino/diagnosis.md) |
| `mr_men_little_miss` | 奇先生妙小姐 (Mr. Men Little Miss) | 2 | `430` `littlemissselfmodel` | `high` | `backlog_needs_review` | [主模板](mr_men_little_miss/latest_template.md) · [诊断](mr_men_little_miss/diagnosis.md) |
| `muhammad_ali` | 穆罕默德·阿里 (Muhammad Ali) | 7 | `116::2` `IP_MUHAMMADALI_ALI_V2` | `high` | `backlog_needs_review` | [主模板](muhammad_ali/latest_template.md) · [诊断](muhammad_ali/diagnosis.md) |
| `my_dress` | ip-my dress-llm-black | 2 | `323::1` `ip-my dress-llm-black` | `high` | `supplement_asset_available_pending_approval` | [主模板](my_dress/latest_template.md) · [诊断](my_dress/diagnosis.md) |
| `my_hero_academia` | 我的英雄学院 (My Hero Academia) | 2 | `215` `IP_myheroacademia2` | `high` | `supplement_asset_available_pending_approval` | [主模板](my_hero_academia/latest_template.md) · [诊断](my_hero_academia/diagnosis.md) |
| `naruto` | IP_NARUTO | 2 | `121::1` `IP_NARUTO` | `high` | `backlog_needs_review` | [主模板](naruto/latest_template.md) · [诊断](naruto/diagnosis.md) |
| `nba` | NBA 美职篮 | 2 | `122` `IP_NBA Positive` | `high` | `supplement_asset_available_pending_approval` | [主模板](nba/latest_template.md) · [诊断](nba/diagnosis.md) |
| `nebraska` | nebraska | 1 | `436` `nebraska` | `medium` | `backlog_needs_review` | [主模板](nebraska/latest_template.md) · [诊断](nebraska/diagnosis.md) |
| `new_holland` | ip-NEW HOLLAND | 1 | `307` `ip-NEW HOLLAND` | `medium` | `supplement_asset_available_pending_approval` | [主模板](new_holland/latest_template.md) · [诊断](new_holland/diagnosis.md) |
| `newbalance` | IP_NEWBALANCE | 2 | `123::1` `IP_NEWBALANCE` | `low` | `no_assert_match` | [主模板](newbalance/latest_template.md) · [诊断](newbalance/diagnosis.md) |
| `neymar` | ip-Neymar | 1 | `308` `ip-Neymar` | `high` | `backlog_needs_review` | [主模板](neymar/latest_template.md) · [诊断](neymar/diagnosis.md) |
| `nhl` | NHL 北美职业冰球联盟 | 2 | `265` `NHLselfmodel` | `high` | `supplement_asset_available_pending_approval` | [主模板](nhl/latest_template.md) · [诊断](nhl/diagnosis.md) |
| `nike` | 耐克 (Nike) | 2 | `125` `IP_Nikelogo_strategy_prompt` | `medium` | `backlog_needs_review` | [主模板](nike/latest_template.md) · [诊断](nike/diagnosis.md) |
| `nike_jordan` | 乔丹 (Nike Jordan) | 1 | `216` `IP_nikejordan_accuracyimprove` | `medium` | `no_assert_match` | [主模板](nike_jordan/latest_template.md) · [诊断](nike_jordan/diagnosis.md) |
| `nin1_game_console` | N-in-1 怀旧游戏机/内置游戏 | 3 | `404` `ip_nin1new` | `low` | `backlog_needs_review` | [主模板](nin1_game_console/latest_template.md) · [诊断](nin1_game_console/diagnosis.md) |
| `ninewest` | IP_NINEWEST | 1 | `124` `IP_NINEWEST` | `low` | `backlog_needs_review` | [主模板](ninewest/latest_template.md) · [诊断](ninewest/diagnosis.md) |
| `nirvana` | 涅槃乐队 (Nirvana) | 2 | `406` `ip_nirvana2` | `high` | `supplement_asset_available_pending_approval` | [主模板](nirvana/latest_template.md) · [诊断](nirvana/diagnosis.md) |
| `novak_djokovic` | NOVAK DJOKOVICselfmodel | 1 | `266` `NOVAK DJOKOVICselfmodel` | `medium` | `supplement_asset_available_pending_approval` | [主模板](novak_djokovic/latest_template.md) · [诊断](novak_djokovic/diagnosis.md) |
| `oakley` | 欧克利 (Oakley) | 3 | `126` `IP_OAKLEY_Ologo` | `high` | `backlog_needs_review` | [主模板](oakley/latest_template.md) · [诊断](oakley/diagnosis.md) |
| `ohayou_spank` | IP-ohayou spank | 1 | `22` `IP-ohayou spank` | `high` | `supplement_asset_available_pending_approval` | [主模板](ohayou_spank/latest_template.md) · [诊断](ohayou_spank/diagnosis.md) |
| `ohio` | ip_ohio | 1 | `407` `ip_ohio` | `medium` | `backlog_needs_review` | [主模板](ohio/latest_template.md) · [诊断](ohio/diagnosis.md) |
| `oklahoma_university` | 俄克拉荷马大学 (University of Oklahoma) | 2 | `421` `ip_universityofoklahomo` | `high` | `backlog_needs_review` | [主模板](oklahoma_university/latest_template.md) · [诊断](oklahoma_university/diagnosis.md) |
| `olympic` | IP_OLYMPIC_strategy | 2 | `127::2` `IP_OLYMPIC_strategy` | `medium` | `no_assert_match` | [主模板](olympic/latest_template.md) · [诊断](olympic/diagnosis.md) |
| `one_direction` | ip-One Direction-prompt | 1 | `309` `ip-One Direction-prompt` | `medium` | `backlog_needs_review` | [主模板](one_direction/latest_template.md) · [诊断](one_direction/diagnosis.md) |
| `one_piece` | 海贼王 (One Piece) | 2 | `409` `ip_onepiece2` | `high` | `supplement_asset_available_pending_approval` | [主模板](one_piece/latest_template.md) · [诊断](one_piece/diagnosis.md) |
| `oregon` | oregon | 1 | `439` `oregon` | `medium` | `backlog_needs_review` | [主模板](oregon/latest_template.md) · [诊断](oregon/diagnosis.md) |
| `oster` | IP_OSTER | 1 | `128` `IP_OSTER` | `low` | `backlog_needs_review` | [主模板](oster/latest_template.md) · [诊断](oster/diagnosis.md) |
| `pandorobo` | ip-pandorobo | 1 | `325` `ip-pandorobo` | `high` | `backlog_needs_review` | [主模板](pandorobo/latest_template.md) · [诊断](pandorobo/diagnosis.md) |
| `panini_0325quanliang` | IP_panini_0325quanliang | 1 | `217` `IP_panini_0325quanliang` | `high` | `no_assert_match` | [主模板](panini_0325quanliang/latest_template.md) · [诊断](panini_0325quanliang/diagnosis.md) |
| `parkerbabyco` | IP_parkerbabyco | 1 | `218` `IP_parkerbabyco` | `high` | `backlog_needs_review` | [主模板](parkerbabyco/latest_template.md) · [诊断](parkerbabyco/diagnosis.md) |
| `patagonia` | IP_patagonia | 1 | `219` `IP_patagonia` | `medium` | `backlog_needs_review` | [主模板](patagonia/latest_template.md) · [诊断](patagonia/diagnosis.md) |
| `paw_patrol` | 汪汪队立大功 (PAW Patrol) | 2 | `130` `IP_PAWPATROL_badge` | `high` | `supplement_asset_available_pending_approval` | [主模板](paw_patrol/latest_template.md) · [诊断](paw_patrol/diagnosis.md) |
| `peanuts` | IP_PEANUTS_background | 2 | `131::2` `IP_PEANUTS_background` | `high` | `approved_in_assert` | [主模板](peanuts/latest_template.md) · [诊断](peanuts/diagnosis.md) |
| `pepsi` | 百事可乐 (Pepsi) | 1 | `249` `IP组-pepsi-图像识别` | `medium` | `backlog_needs_review` | [主模板](pepsi/latest_template.md) · [诊断](pepsi/diagnosis.md) |
| `pickulsgizmo` | IP_PICKULSGIZMO | 1 | `132` `IP_PICKULSGIZMO` | `low` | `no_assert_match` | [主模板](pickulsgizmo/latest_template.md) · [诊断](pickulsgizmo/diagnosis.md) |
| `pikmin` | 皮克敏 (Pikmin) | 2 | `411` `ip_pikmin3` | `high` | `backlog_needs_review` | [主模板](pikmin/latest_template.md) · [诊断](pikmin/diagnosis.md) |
| `pinkpanther` | IP_PINKPANTHER | 1 | `133` `IP_PINKPANTHER` | `high` | `backlog_needs_review` | [主模板](pinkpanther/latest_template.md) · [诊断](pinkpanther/diagnosis.md) |
| `pitbull` | ip-pitbull | 1 | `326` `ip-pitbull` | `low` | `backlog_needs_review` | [主模板](pitbull/latest_template.md) · [诊断](pitbull/diagnosis.md) |
| `plexaderm` | IP_Plexaderm_tradename | 1 | `137` `IP_Plexaderm_tradename` | `medium` | `no_assert_match` | [主模板](plexaderm/latest_template.md) · [诊断](plexaderm/diagnosis.md) |
| `pokemon` | 宝可梦 (Pokémon) | 1 | `250` `IP组-pokemon-图像识别` | `low` | `backlog_needs_review` | [主模板](pokemon/latest_template.md) · [诊断](pokemon/diagnosis.md) |
| `postyaustin` | IP_postyaustin_V1 | 1 | `220` `IP_postyaustin_V1` | `medium` | `no_assert_match` | [主模板](postyaustin/latest_template.md) · [诊断](postyaustin/diagnosis.md) |
| `prada` | IP_PRADA | 1 | `134` `IP_PRADA` | `medium` | `backlog_needs_review` | [主模板](prada/latest_template.md) · [诊断](prada/diagnosis.md) |
| `purina` | IP_PURINA | 1 | `135` `IP_PURINA` | `medium` | `backlog_needs_review` | [主模板](purina/latest_template.md) · [诊断](purina/diagnosis.md) |
| `purple_innovation` | IP_PURPLE_INNOVATION | 1 | `136` `IP_PURPLE_INNOVATION` | `high` | `backlog_needs_review` | [主模板](purple_innovation/latest_template.md) · [诊断](purple_innovation/diagnosis.md) |
| `purplebrand` | ip_PURPLEBRAND | 1 | `339` `ip_PURPLEBRAND` | `high` | `backlog_needs_review` | [主模板](purplebrand/latest_template.md) · [诊断](purplebrand/diagnosis.md) |
| `rabanne_bag` | ip_Rabanne bag | 1 | `341` `ip_Rabanne bag` | `high` | `backlog_needs_review` | [主模板](rabanne_bag/latest_template.md) · [诊断](rabanne_bag/diagnosis.md) |
| `ralph_lauren` | 拉夫劳伦 (Ralph Lauren) | 2 | `328` `ip-ralphlauren2` | `high` | `approved_in_assert` | [主模板](ralph_lauren/latest_template.md) · [诊断](ralph_lauren/diagnosis.md) |
| `ratt` | IP_RATT | 1 | `138` `IP_RATT` | `medium` | `backlog_needs_review` | [主模板](ratt/latest_template.md) · [诊断](ratt/diagnosis.md) |
| `rbfa` | ip_RBFA | 1 | `340` `ip_RBFA` | `medium` | `backlog_needs_review` | [主模板](rbfa/latest_template.md) · [诊断](rbfa/diagnosis.md) |
| `rezero` | Re:从零开始的异世界生活 (Re:Zero) | 1 | `221` `IP_rezero` | `high` | `supplement_asset_available_pending_approval` | [主模板](rezero/latest_template.md) · [诊断](rezero/diagnosis.md) |
| `rfef` | 西班牙皇家足协 (RFEF) | 2 | `256` `Ip_REFE_exception` | `medium` | `backlog_needs_review` | [主模板](rfef/latest_template.md) · [诊断](rfef/diagnosis.md) |
| `rickandmorty` | IP_RICKANDMORTY_1 | 2 | `139::2` `IP_RICKANDMORTY_1` | `low` | `backlog_needs_review` | [主模板](rickandmorty/latest_template.md) · [诊断](rickandmorty/diagnosis.md) |
| `rilakkuma` | ip-Rilakkuma-prompt | 1 | `310` `ip-Rilakkuma-prompt` | `low` | `supplement_asset_available_pending_approval` | [主模板](rilakkuma/latest_template.md) · [诊断](rilakkuma/diagnosis.md) |
| `risk_evaluation` | 通用多模态商品/广告风险评估 | 4 | `443` `risk_ip_adds_evaluation_gemini` | `high` | `backlog_needs_review` | [主模板](risk_evaluation/latest_template.md) · [诊断](risk_evaluation/diagnosis.md) |
| `riskdata_iplogo_brand_gemini` | riskdata_iplogo_brand_gemini | 1 | `444` `riskdata_iplogo_brand_gemini` | `high` | `backlog_needs_review` | [主模板](riskdata_iplogo_brand_gemini/latest_template.md) · [诊断](riskdata_iplogo_brand_gemini/diagnosis.md) |
| `rockybalboa` | IP_ROCKYBALBOA_IMG | 1 | `140` `IP_ROCKYBALBOA_IMG` | `low` | `backlog_needs_review` | [主模板](rockybalboa/latest_template.md) · [诊断](rockybalboa/diagnosis.md) |
| `rundmc` | IP_RUNDMC_IMG | 1 | `141` `IP_RUNDMC_IMG` | `low` | `backlog_needs_review` | [主模板](rundmc/latest_template.md) · [诊断](rundmc/diagnosis.md) |
| `rusty` | IP_rusty | 1 | `222` `IP_rusty` | `high` | `no_assert_match` | [主模板](rusty/latest_template.md) · [诊断](rusty/diagnosis.md) |
| `samsung_phonecase` | ip_samsung_phonecase | 1 | `413` `ip_samsung_phonecase` | `medium` | `backlog_needs_review` | [主模板](samsung_phonecase/latest_template.md) · [诊断](samsung_phonecase/diagnosis.md) |
| `sandmaennchen` | 沙人 (Unser Sandmännchen) | 1 | `311` `ip-Sandmännchen-prompt` | `low` | `backlog_needs_review` | [主模板](sandmaennchen/latest_template.md) · [诊断](sandmaennchen/diagnosis.md) |
| `scoobydoo` | IP_scoobydoo | 1 | `224` `IP_scoobydoo` | `high` | `backlog_needs_review` | [主模板](scoobydoo/latest_template.md) · [诊断](scoobydoo/diagnosis.md) |
| `scott` | IP_SCOTT | 1 | `142` `IP_SCOTT` | `low` | `backlog_needs_review` | [主模板](scott/latest_template.md) · [诊断](scott/diagnosis.md) |
| `sesame_street` | 芝麻街 (Sesame Street) | 1 | `253` `IP组-芝麻街-召回识别` | `low` | `backlog_needs_review` | [主模板](sesame_street/latest_template.md) · [诊断](sesame_street/diagnosis.md) |
| `sevendeadlysins` | IP_sevendeadlysins | 1 | `225` `IP_sevendeadlysins` | `high` | `supplement_asset_available_pending_approval` | [主模板](sevendeadlysins/latest_template.md) · [诊断](sevendeadlysins/diagnosis.md) |
| `sharks_rugby` | ip-sharks rugby | 1 | `329` `ip-sharks rugby` | `medium` | `backlog_needs_review` | [主模板](sharks_rugby/latest_template.md) · [诊断](sharks_rugby/diagnosis.md) |
| `shein_mark` | SHEIN 水印检测 | 1 | `445` `shein_mark_v2` | `low` | `backlog_needs_review` | [主模板](shein_mark/latest_template.md) · [诊断](shein_mark/diagnosis.md) |
| `shell` | IP_SHELL_strategy | 2 | `143::2` `IP_SHELL_strategy` | `high` | `no_assert_match` | [主模板](shell/latest_template.md) · [诊断](shell/diagnosis.md) |
| `shimano` | shimano | 1 | `446` `shimano` | `low` | `backlog_needs_review` | [主模板](shimano/latest_template.md) · [诊断](shimano/diagnosis.md) |
| `shingbright` | shingbright | 1 | `447` `shingbright` | `high` | `backlog_needs_review` | [主模板](shingbright/latest_template.md) · [诊断](shingbright/diagnosis.md) |
| `slamdunk` | IP_SLAMDUNK | 1 | `144` `IP_SLAMDUNK` | `high` | `backlog_needs_review` | [主模板](slamdunk/latest_template.md) · [诊断](slamdunk/diagnosis.md) |
| `slayer` | ip_slayer | 1 | `414` `ip_slayer` | `medium` | `approved_in_assert` | [主模板](slayer/latest_template.md) · [诊断](slayer/diagnosis.md) |
| `southcarolina` | ip_southcarolina | 1 | `415` `ip_southcarolina` | `medium` | `backlog_needs_review` | [主模板](southcarolina/latest_template.md) · [诊断](southcarolina/diagnosis.md) |
| `spainish_celebrity` | ip-spainish celebrity | 1 | `330` `ip-spainish celebrity` | `high` | `backlog_needs_review` | [主模板](spainish_celebrity/latest_template.md) · [诊断](spainish_celebrity/diagnosis.md) |
| `spirit` | IP_SPIRIT_IMG | 1 | `145` `IP_SPIRIT_IMG` | `low` | `supplement_asset_available_pending_approval` | [主模板](spirit/latest_template.md) · [诊断](spirit/diagnosis.md) |
| `spongebobsquarepants` | IP_SPONGEBOBSQUAREPANTS | 1 | `146` `IP_SPONGEBOBSQUAREPANTS` | `high` | `backlog_needs_review` | [主模板](spongebobsquarepants/latest_template.md) · [诊断](spongebobsquarepants/diagnosis.md) |
| `sport_star` | ip-sport star-prompt | 1 | `331` `ip-sport star-prompt` | `medium` | `backlog_needs_review` | [主模板](sport_star/latest_template.md) · [诊断](sport_star/diagnosis.md) |
| `sports_ball_general` | 通用体育俱乐部/联盟/球星 IP | 2 | `354` `ip_ball` | `medium` | `backlog_needs_review` | [主模板](sports_ball_general/latest_template.md) · [诊断](sports_ball_general/diagnosis.md) |
| `spotit` | spot_it | 2 | `448::2` `spot_it` | `high` | `backlog_needs_review` | [主模板](spotit/latest_template.md) · [诊断](spotit/diagnosis.md) |
| `squishmallows` | IP_squishmallows | 1 | `226` `IP_squishmallows` | `high` | `approved_in_assert` | [主模板](squishmallows/latest_template.md) · [诊断](squishmallows/diagnosis.md) |
| `starbucks` | IP_starbucks | 1 | `227` `IP_starbucks` | `high` | `no_assert_match` | [主模板](starbucks/latest_template.md) · [诊断](starbucks/diagnosis.md) |
| `startrek` | ip_startrek | 1 | `417` `ip_startrek` | `medium` | `approved_in_assert` | [主模板](startrek/latest_template.md) · [诊断](startrek/diagnosis.md) |
| `stealabrainrot` | IP_STEALABRAINROT | 1 | `147` `IP_STEALABRAINROT` | `high` | `no_assert_match` | [主模板](stealabrainrot/latest_template.md) · [诊断](stealabrainrot/diagnosis.md) |
| `stoneisland` | stoneisland | 1 | `449` `stoneisland` | `high` | `backlog_needs_review` | [主模板](stoneisland/latest_template.md) · [诊断](stoneisland/diagnosis.md) |
| `strawberryshortcake` | IP_strawberryshortcake | 2 | `228::2` `IP_strawberryshortcake` | `high` | `supplement_asset_available_pending_approval` | [主模板](strawberryshortcake/latest_template.md) · [诊断](strawberryshortcake/diagnosis.md) |
| `streetfighter` | streetfighter | 2 | `418::1` `streetfighter` | `medium` | `approved_in_assert` | [主模板](streetfighter/latest_template.md) · [诊断](streetfighter/diagnosis.md) |
| `sunlight` | Ip_Sunlight_prompt | 1 | `257` `Ip_Sunlight_prompt` | `low` | `backlog_needs_review` | [主模板](sunlight/latest_template.md) · [诊断](sunlight/diagnosis.md) |
| `super_mario` | 超级马里奥 (Super Mario) | 3 | `148::2` `IP_SUPERMARIO_HIGHACCURACY` | `medium` | `supplement_asset_available_pending_approval` | [主模板](super_mario/latest_template.md) · [诊断](super_mario/diagnosis.md) |
| `supreme` | Supreme | 2 | `251` `IP组-supreme-图像识别` | `high` | `backlog_needs_review` | [主模板](supreme/latest_template.md) · [诊断](supreme/diagnosis.md) |
| `suzuki` | IP_SUZUKI | 1 | `149` `IP_SUZUKI` | `high` | `supplement_asset_available_pending_approval` | [主模板](suzuki/latest_template.md) · [诊断](suzuki/diagnosis.md) |
| `swarovski` | IP-SWAROVSKI | 1 | `12` `IP-SWAROVSKI` | `medium` | `backlog_needs_review` | [主模板](swarovski/latest_template.md) · [诊断](swarovski/diagnosis.md) |
| `tangle` | IP_tangle | 1 | `230` `IP_tangle` | `high` | `backlog_needs_review` | [主模板](tangle/latest_template.md) · [诊断](tangle/diagnosis.md) |
| `taylorswift` | taylorswift | 2 | `450::1` `taylorswift` | `medium` | `backlog_needs_review` | [主模板](taylorswift/latest_template.md) · [诊断](taylorswift/diagnosis.md) |
| `tesla` | IP_TESLA | 1 | `150` `IP_TESLA` | `high` | `no_assert_match` | [主模板](tesla/latest_template.md) · [诊断](tesla/diagnosis.md) |
| `test_111` | test111 | 1 | `451` `test111` | `blocked_hygiene` | `not_applicable_non_ip_or_test` | [主模板](test_111/latest_template.md) · [诊断](test_111/diagnosis.md) |
| `test_5678` | 5678 | 1 | `1` `5678` | `blocked_hygiene` | `not_applicable_non_ip_or_test` | [主模板](test_5678/latest_template.md) · [诊断](test_5678/diagnosis.md) |
| `test_general_ip` | IPgeneraltest | 1 | `244` `IPgeneraltest` | `blocked_hygiene` | `not_applicable_non_ip_or_test` | [主模板](test_general_ip/latest_template.md) · [诊断](test_general_ip/diagnosis.md) |
| `test_lingjinglan` | lingjinglan_test | 1 | `429` `lingjinglan_test` | `blocked_hygiene` | `not_applicable_non_ip_or_test` | [主模板](test_lingjinglan/latest_template.md) · [诊断](test_lingjinglan/diagnosis.md) |
| `test_nyetest` | NyeTestCertKeywords | 6 | `269` `NyeTestCertKeywords` | `blocked_hygiene` | `not_applicable_non_ip_or_test` | [主模板](test_nyetest/latest_template.md) · [诊断](test_nyetest/diagnosis.md) |
| `thebadguys` | IP_THEBADGUYS | 1 | `151::1` `IP_THEBADGUYS` | `high` | `backlog_needs_review` | [主模板](thebadguys/latest_template.md) · [诊断](thebadguys/diagnosis.md) |
| `thenewyorker` | IP_THENEWYORKER_V1 | 1 | `152` `IP_THENEWYORKER_V1` | `medium` | `supplement_asset_available_pending_approval` | [主模板](thenewyorker/latest_template.md) · [诊断](thenewyorker/diagnosis.md) |
| `thesecretlifeofpets` | IP_TheSecretLifeofPets_db | 2 | `159::2` `IP_TheSecretLifeofPets_db` | `medium` | `supplement_asset_available_pending_approval` | [主模板](thesecretlifeofpets/latest_template.md) · [诊断](thesecretlifeofpets/diagnosis.md) |
| `thesimpsonver2` | IP_THESIMPSONver2 | 1 | `153` `IP_THESIMPSONver2` | `high` | `supplement_asset_available_pending_approval` | [主模板](thesimpsonver2/latest_template.md) · [诊断](thesimpsonver2/diagnosis.md) |
| `thomasandfriends` | ip_thomasandfriends | 1 | `419` `ip_thomasandfriends` | `low` | `backlog_needs_review` | [主模板](thomasandfriends/latest_template.md) · [诊断](thomasandfriends/diagnosis.md) |
| `tiffanyco_tiffany` | IP_TIFFANYCO_TIFFANY | 1 | `154` `IP_TIFFANYCO_TIFFANY` | `low` | `backlog_needs_review` | [主模板](tiffanyco_tiffany/latest_template.md) · [诊断](tiffanyco_tiffany/diagnosis.md) |
| `tintin` | IP_tintin | 1 | `231` `IP_tintin` | `high` | `supplement_asset_available_pending_approval` | [主模板](tintin/latest_template.md) · [诊断](tintin/diagnosis.md) |
| `tokyoghoul` | IP-Tokyoghoul-llm | 1 | `13` `IP-Tokyoghoul-llm` | `high` | `supplement_asset_available_pending_approval` | [主模板](tokyoghoul/latest_template.md) · [诊断](tokyoghoul/diagnosis.md) |
| `tomandjerry` | IP_TOMandJERRY | 1 | `157` `IP_TOMandJERRY` | `high` | `approved_in_assert` | [主模板](tomandjerry/latest_template.md) · [诊断](tomandjerry/diagnosis.md) |
| `tommy_hilfiger` | Tommy Hilfiger | 2 | `156` `IP_TOMMYHILFIGER_TOMMY2` | `high` | `backlog_needs_review` | [主模板](tommy_hilfiger/latest_template.md) · [诊断](tommy_hilfiger/diagnosis.md) |
| `totto` | totto | 1 | `454` `totto` | `low` | `backlog_needs_review` | [主模板](totto/latest_template.md) · [诊断](totto/diagnosis.md) |
| `toyota` | IP_toyota_llm | 2 | `232::1` `IP_toyota_llm` | `high` | `no_assert_match` | [主模板](toyota/latest_template.md) · [诊断](toyota/diagnosis.md) |
| `transportforlondon` | IP_TRANSPORTFORLONDON | 2 | `23::2` `IP_TRANSPORTFORLONDON` | `high` | `backlog_needs_review` | [主模板](transportforlondon/latest_template.md) · [诊断](transportforlondon/diagnosis.md) |
| `triumph` | IP_Triumph | 1 | `160` `IP_Triumph` | `medium` | `supplement_asset_available_pending_approval` | [主模板](triumph/latest_template.md) · [诊断](triumph/diagnosis.md) |
| `tro_anly` | ip_tro_anly | 1 | `420` `ip_tro_anly` | `high` | `backlog_needs_review` | [主模板](tro_anly/latest_template.md) · [诊断](tro_anly/diagnosis.md) |
| `trolls` | IP_Trolls | 1 | `161` `IP_Trolls` | `high` | `supplement_asset_available_pending_approval` | [主模板](trolls/latest_template.md) · [诊断](trolls/diagnosis.md) |
| `tumi` | IP_TUMI | 1 | `158` `IP_TUMI` | `low` | `backlog_needs_review` | [主模板](tumi/latest_template.md) · [诊断](tumi/diagnosis.md) |
| `twentyonepilots` | IP_TwentyOnePilots | 1 | `162` `IP_TwentyOnePilots` | `high` | `supplement_asset_available_pending_approval` | [主模板](twentyonepilots/latest_template.md) · [诊断](twentyonepilots/diagnosis.md) |
| `twizler` | IP_twizler | 1 | `233` `IP_twizler` | `high` | `no_assert_match` | [主模板](twizler/latest_template.md) · [诊断](twizler/diagnosis.md) |
| `ucl_wenzi` | IP_UCL_WENZI | 1 | `163` `IP_UCL_WENZI` | `high` | `no_assert_match` | [主模板](ucl_wenzi/latest_template.md) · [诊断](ucl_wenzi/diagnosis.md) |
| `uga` | 佐治亚大学斗牛犬队 (UGA) | 3 | `164::1` `IP_UGA` | `medium` | `backlog_needs_review` | [主模板](uga/latest_template.md) · [诊断](uga/diagnosis.md) |
| `ugg` | UGG Australia | 2 | `235` `IP_ugg_patent` | `high` | `supplement_asset_available_pending_approval` | [主模板](ugg/latest_template.md) · [诊断](ugg/diagnosis.md) |
| `underdog` | IP_underdog | 1 | `236` `IP_underdog` | `high` | `backlog_needs_review` | [主模板](underdog/latest_template.md) · [诊断](underdog/diagnosis.md) |
| `university_of_michigan` | 密歇根大学 (University of Michigan) | 3 | `396` `ip_michiganv3` | `high` | `backlog_needs_review` | [主模板](university_of_michigan/latest_template.md) · [诊断](university_of_michigan/diagnosis.md) |
| `university_of_utah` | 犹他大学 (University of Utah) | 2 | `422` `ip_universityofutah` | `high` | `backlog_needs_review` | [主模板](university_of_utah/latest_template.md) · [诊断](university_of_utah/diagnosis.md) |
| `universityofkentucky` | UNIVERSITYOFKENTUCKY | 1 | `273` `UNIVERSITYOFKENTUCKY` | `medium` | `backlog_needs_review` | [主模板](universityofkentucky/latest_template.md) · [诊断](universityofkentucky/diagnosis.md) |
| `usmc` | IP_USMC_2 | 2 | `165::2` `IP_USMC_2` | `low` | `backlog_needs_review` | [主模板](usmc/latest_template.md) · [诊断](usmc/diagnosis.md) |
| `van_cleef_arpels` | 梵克雅宝 (Van Cleef & Arpels) | 2 | `237` `IP_vancleefarpels_all` | `medium` | `approved_in_assert` | [主模板](van_cleef_arpels/latest_template.md) · [诊断](van_cleef_arpels/diagnosis.md) |
| `velcro` | ip_velcro | 1 | `424` `ip_velcro` | `high` | `backlog_needs_review` | [主模板](velcro/latest_template.md) · [诊断](velcro/diagnosis.md) |
| `vetements` | Ip_vetements_exception | 1 | `258` `Ip_vetements_exception` | `high` | `backlog_needs_review` | [主模板](vetements/latest_template.md) · [诊断](vetements/diagnosis.md) |
| `vision_street_wear` | Vision Street Wear | 2 | `167` `IP_VISION_TRADEMARK` | `high` | `backlog_needs_review` | [主模板](vision_street_wear/latest_template.md) · [诊断](vision_street_wear/diagnosis.md) |
| `vivienne_westwood` | IP_VIVIENNE_WESTWOOD | 1 | `168` `IP_VIVIENNE_WESTWOOD` | `low` | `backlog_needs_review` | [主模板](vivienne_westwood/latest_template.md) · [诊断](vivienne_westwood/diagnosis.md) |
| `vogue` | VOGUE 杂志 | 1 | `252` `IP组-vogue-召回识别` | `low` | `backlog_needs_review` | [主模板](vogue/latest_template.md) · [诊断](vogue/diagnosis.md) |
| `volkswagen` | 大众汽车 (Volkswagen) | 2 | `342` `ip_Volkswagen` | `high` | `backlog_needs_review` | [主模板](volkswagen/latest_template.md) · [诊断](volkswagen/diagnosis.md) |
| `warhammer` | IP-Warhammer-llm-black | 2 | `15::1` `IP-Warhammer-llm-black` | `high` | `supplement_asset_available_pending_approval` | [主模板](warhammer/latest_template.md) · [诊断](warhammer/diagnosis.md) |
| `whirlpool` | IP_whirlpool | 1 | `239` `IP_whirlpool` | `medium` | `backlog_needs_review` | [主模板](whirlpool/latest_template.md) · [诊断](whirlpool/diagnosis.md) |
| `whitefox` | ip-whitefox | 1 | `332` `ip-whitefox` | `low` | `backlog_needs_review` | [主模板](whitefox/latest_template.md) · [诊断](whitefox/diagnosis.md) |
| `wickedtrademark` | IP_WICKEDtrademark | 1 | `169` `IP_WICKEDtrademark` | `low` | `no_assert_match` | [主模板](wickedtrademark/latest_template.md) · [诊断](wickedtrademark/diagnosis.md) |
| `wilson` | IP_Wilson | 1 | `171` `IP_Wilson` | `medium` | `backlog_needs_review` | [主模板](wilson/latest_template.md) · [诊断](wilson/diagnosis.md) |
| `windows` | IP_windows | 1 | `240` `IP_windows` | `medium` | `no_assert_match` | [主模板](windows/latest_template.md) · [诊断](windows/diagnosis.md) |
| `wku` | IP_WKU | 1 | `170` `IP_WKU` | `medium` | `no_assert_match` | [主模板](wku/latest_template.md) · [诊断](wku/diagnosis.md) |
| `wondermachines` | IP_wondermachines_ceshi | 1 | `241` `IP_wondermachines_ceshi` | `low` | `no_assert_match` | [主模板](wondermachines/latest_template.md) · [诊断](wondermachines/diagnosis.md) |
| `wwe_wrestle` | wwe_wrestle | 1 | `460` `wwe_wrestle` | `medium` | `backlog_needs_review` | [主模板](wwe_wrestle/latest_template.md) · [诊断](wwe_wrestle/diagnosis.md) |
| `yamal` | ip_yamal_excepmtion | 1 | `425` `ip_yamal_excepmtion` | `medium` | `backlog_needs_review` | [主模板](yamal/latest_template.md) · [诊断](yamal/diagnosis.md) |
| `yanding` | IP_YANDING_PATENTPUNISH | 1 | `172` `IP_YANDING_PATENTPUNISH` | `high` | `no_assert_match` | [主模板](yanding/latest_template.md) · [诊断](yanding/diagnosis.md) |
| `yeti` | yeti | 1 | `461` `yeti` | `high` | `backlog_needs_review` | [主模板](yeti/latest_template.md) · [诊断](yeti/diagnosis.md) |
| `zelda` | ip_zelda | 1 | `426` `ip_zelda` | `high` | `backlog_needs_review` | [主模板](zelda/latest_template.md) · [诊断](zelda/diagnosis.md) |
| `zigzag` | IP_zigzag | 1 | `242` `IP_zigzag` | `low` | `approved_in_assert` | [主模板](zigzag/latest_template.md) · [诊断](zigzag/diagnosis.md) |
| `zipit` | IP_zipit | 1 | `243` `IP_zipit` | `high` | `backlog_needs_review` | [主模板](zipit/latest_template.md) · [诊断](zipit/diagnosis.md) |
| `zippo` | Zippo 打火机 | 2 | `24` `IP-zippo` | `low` | `backlog_needs_review` | [主模板](zippo/latest_template.md) · [诊断](zippo/diagnosis.md) |
