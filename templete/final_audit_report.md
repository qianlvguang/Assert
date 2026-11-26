# 352 审核模板同族与参考图全量终审报告（待检阅签收）

- **审结时间**: `2026-11-26T11:30:00+08:00`
- **覆盖范围**: 全量 **352 族**审核模板（533 拆包版本）+ 全量 **307 族**特定对象视觉参考图
- **交互复核载体**: 打开 `templete/review_dashboard.html` 即已预载全部 352 族审结状态与审结意见（支持逐条覆写与导出）。

## 一、审结结论总览

| 审结结论 (`review_status`) | 总计 (352) | 广域 Track A (36) | 特定对象 Track B (307) | 隔离 Track Q (9) | 处置建议 |
|---|---:|---:|---:|---:|---|
| ✅ **已通过 (`approved`)** | **186** | 18 | 168 | 0 | 可直接投入 CPT-SFT 或线上基线 |
| ✎ **需修模板 (`needs_fix`)** | **136** | 18 | 118 | 0 | 修复 JSON 语法/错字/占位符/`rel` 误绑后复审 |
| 🖼 **需补标准图 (`needs_asset`)** | **21** | 0 | 21 | 0 | 模板正文健康，需业务补充实拍专利图或官方图标 |
| ⛔ **隔离废弃 (`quarantined`)** | **9** | 0 | 0 | 9 | 严禁入训，先修错贴 Bug 或清除测试废案 |

## 二、特定对象（307 族）参考图目视验收与净化台账

- **目视验真通过**: **267 / 307 (87.0%)**（含 `approved_visual_reference=204` 与 `approved_with_enrichment_note=63`）
- **当场剔除错配 (`rejected_mismatch_purged`)**: **9** 族（已从画廊预览与交付白名单中屏蔽）
- **需人工补实拍/官图 (`manual_asset_required`)**: **31** 族

### 2.1 目视整改通过的重点替换项（已二次视觉核验 `wiki_replacements_qa.jpg`）
| `family_slug` | 原错误候选 | 整改后采用图元 | 视觉审结状态 |
|---|---|---|---|
| `alexandermcqueen` | 设计师本人肖像 | `Alexander_McQueen_2018_logo.svg` | ✅ 核准替换 |
| `calvin_klein` | 设计师本人肖像 | `CK_Calvin_Klein_logo.svg` | ✅ 核准替换 |
| `dsquared2` | 创始人双人合照 | `DSQUARED2.png` | ✅ 核准替换 |
| `nike_jordan` | 约旦皇家空军徽标 | `Jumpman_logo.svg` | ✅ 核准替换 |
| `velcro` | 魔术贴织物微距图 | `Velcro_Brand.svg` | ✅ 核准替换 |
| `vivienne_westwood` | 设计师本人肖像 | `Vivienne_Westwood_'Orb'_company_logo` | ✅ 核准（注：含土星环+手写标） |
| `minions` | 街头雕塑摄影 | `Minions_(film)_logo.svg` | ✅ 核准（注：建议补角色三视图） |
| `evelknievel` | Harley 博物馆标（已剔除） | `At_Home_With_Evel_Knievel.jpg` | ✅ 核准（本人档案照，建议补徽记） |
| `triumph` | 含 `ip_triumph_international.png` | 仅保留 `ip_triumph_motorcycles.png` | ✅ 核准单图、已剔除内衣错配 |

### 2.2 确认错配并已硬清除（`rejected_mismatch_purged`，共 9 族）
| `family_slug` | 清除原因 | 后续动作 |
|---|---|---|
| `bigfoot` | 错配清除：命中 1967 年 Patterson-Gimlin 森林模糊影照，非品牌/文创视觉标识 | 从品牌官网/官店手工补正图 |
| `cookies` | 错配清除：命中 Craig's Cookies 烘焙店标，非目标潮牌 Cookies | 从品牌官网/官店手工补正图 |
| `glassangelofficial` | 错配清除：命中普通圣诞玻璃天使挂件，非品牌官方参考图 | 从品牌官网/官店手工补正图 |
| `meitanteikonan` | 错配清除：二次替换命中 ABS-CBN 电视台标，非《名侦探柯南》作品图标 | 从品牌官网/官店手工补正图 |
| `oster` | 错配清除：二次替换命中奥地利能源协会标，非厨具品牌 Oster | 从品牌官网/官店手工补正图 |
| `purple_innovation` | 错配清除：命中 Chestertons 房产机构紫色标，非网格凝胶枕专利 | 从品牌官网/官店手工补正图 |
| `purplebrand` | 错配清除：命中 Upstage 标而非服装品牌 PURPLE BRAND | 从品牌官网/官店手工补正图 |
| `totto` | 错配清除：命中日剧《小豆豆》标题标，非箱包品牌 TOTTO | 从品牌官网/官店手工补正图 |
| `zipit` | 错配清除：命中早期 Linux 掌机 Zipit，非单拉链包 Zipit 专利结构 | 从品牌官网/官店手工补正图 |

### 2.3 需人工补图清单（`audit_status=needs_asset`，且正文健康）
| `family_slug` | 子轨道 | 缺口说明 |
|---|---|---|
| `ajsnifty` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `amiri` | `B1_specific_brand_trademark` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `apple` | `B5_specific_design_patent_product` | 已有苹果剪影 Logo，但 IP_APPLE_WATCHBAND 需官方各代 Apple Watch 表带结构对比图 |
| `cookies` | `B1_specific_brand_trademark` | 错配清除：命中 Craig's Cookies 烘焙店标，非目标潮牌 Cookies |
| `courtneymorgenstern` | `B4_specific_celebrity_band_artist` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `cucu` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `doubleendedhandtool` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `genies_perfume_atomizer` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `goorinbros` | `B1_specific_brand_trademark` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `jenny_urquhart` | `B4_specific_celebrity_band_artist` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `kaffe` | `B1_specific_brand_trademark` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `lindseyferrell` | `B4_specific_celebrity_band_artist` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `meitanteikonan` | `B2_specific_anime_game_media_ip` | 错配清除：二次替换命中 ABS-CBN 电视台标，非《名侦探柯南》作品图标 |
| `men_of_mayhem` | `B1_specific_brand_trademark` | Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充 |
| `pickulsgizmo` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `purplebrand` | `B1_specific_brand_trademark` | 错配清除：命中 Upstage 标而非服装品牌 PURPLE BRAND |
| `rabanne_bag` | `B5_specific_design_patent_product` | 已有 Paco Rabanne 字标，但模板核心审金属圆片链甲包体装潢，仍缺包型结构实拍图 |
| `tangle` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `wondermachines` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `yanding` | `B5_specific_design_patent_product` | 纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图 |
| `zipit` | `B5_specific_design_patent_product` | 错配清除：命中早期 Linux 掌机 Zipit，非单拉链包 Zipit 专利结构 |

## 三、隔离废弃清单（`quarantined` · 9 族）
| `family_slug` | 子轨道 | 主版 ID | 审结意见 |
|---|---|---:|---|
| `brand` | `Q2_cross_entity_paste_bug` | `179` | 【Q2 跨实体错贴隔离】disposition=quarantine_paste_bug（标题与正文权利实体矛盾，须人工修复模板后才能使用）；Pro 阶段应定性为 fix_template_prompt_bug（不更新模型权重），人工修订后再启用。 |
| `deutsches_rotes_kreuz` | `Q2_cross_entity_paste_bug` | `7` | 【Q2 跨实体错贴隔离】disposition=quarantine_paste_bug（标题与正文权利实体矛盾，须人工修复模板后才能使用）；Pro 阶段应定性为 fix_template_prompt_bug（不更新模型权重），人工修订后再启用。 |
| `southcarolina` | `Q2_cross_entity_paste_bug` | `415` | 【Q2 跨实体错贴隔离】disposition=quarantine_paste_bug（标题与正文权利实体矛盾，须人工修复模板后才能使用）；Pro 阶段应定性为 fix_template_prompt_bug（不更新模型权重），人工修订后再启用。 |
| `test_111` | `Q1_test_junk` | `451` | 【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。 |
| `test_5678` | `Q1_test_junk` | `1` | 【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。 |
| `test_general_ip` | `Q1_test_junk` | `244` | 【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。 |
| `test_lingjinglan` | `Q1_test_junk` | `429` | 【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。 |
| `test_nyetest` | `Q1_test_junk` | `269` | 【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。 |
| `tintin` | `Q2_cross_entity_paste_bug` | `231` | 【Q2 跨实体错贴隔离】disposition=quarantine_paste_bug（标题与正文权利实体矛盾，须人工修复模板后才能使用）；Pro 阶段应定性为 fix_template_prompt_bug（不更新模型权重），人工修订后再启用。 |

## 四、需修模板清单（`needs_fix` · 重点优先项一览，全量已写入画廊）
| `family_slug` | 子轨道 | 主版 ID | 检测缺陷 |
|---|---|---:|---|
| `511` | `B1_specific_brand_trademark` | `27` | broken_json_schema |
| `adanola` | `B1_specific_brand_trademark` | `301` | broken_json_schema |
| `alemannia_aachen` | `B3_specific_sports_university` | `334` | broken_json_schema |
| `all_blacks` | `B3_specific_sports_university` | `345` | rel_metadata_mismatch |
| `ami` | `B1_specific_brand_trademark` | `32` | broken_json_schema |
| `amongus` | `B2_specific_anime_game_media_ip` | `16` | broken_json_schema, typo_or_logic_defect |
| `annabelle` | `B2_specific_anime_game_media_ip` | `33` | broken_json_schema |
| `atari` | `B2_specific_anime_game_media_ip` | `175` | broken_json_schema |
| `attack_on_titan` | `B2_specific_anime_game_media_ip` | `39` | broken_json_schema |
| `aux_audit_feedback_optimizer` | `A4_auxiliary_governance_workflow` | `352` | rel_metadata_mismatch |
| `aux_black_word_risk_reviewer` | `A4_auxiliary_governance_workflow` | `277` | rel_metadata_mismatch |
| `aux_brand_alliance` | `A4_auxiliary_governance_workflow` | `358` | rel_metadata_mismatch |
| `aux_brand_collab` | `A4_auxiliary_governance_workflow` | `359` | rel_metadata_mismatch |
| `aux_crawlplatform_anti_risk` | `A4_auxiliary_governance_workflow` | `292` | rel_metadata_mismatch |
| `aux_tro_brandname_alignment` | `A4_auxiliary_governance_workflow` | `455` | rel_metadata_mismatch |
| `aux_tro_brandname_rec` | `A4_auxiliary_governance_workflow` | `457` | rel_metadata_mismatch |
| `badcutebunny` | `B2_specific_anime_game_media_ip` | `353` | broken_json_schema |
| `balenciaga_1103trademark` | `B1_specific_brand_trademark` | `40` | broken_json_schema |
| `balmain` | `B1_specific_brand_trademark` | `355` | broken_json_schema |
| `bebe` | `B1_specific_brand_trademark` | `41` | broken_json_schema |
| `bensonboone` | `B4_specific_celebrity_band_artist` | `276` | broken_json_schema |
| `berserk` | `B2_specific_anime_game_media_ip` | `43` | broken_json_schema |
| `bigfoot` | `B1_specific_brand_trademark` | `45` | broken_json_schema |
| `billionaire_boys_club` | `B1_specific_brand_trademark` | `47` | broken_json_schema, rel_metadata_mismatch |
| `bmw` | `B1_specific_brand_trademark` | `178` | broken_json_schema |
| `brand_gemini_general` | `A1_open_set_cross_domain_ip` | `362` | rel_metadata_mismatch |
| `brand_goods_consistent_multi_img` | `A1_open_set_cross_domain_ip` | `366` | rel_metadata_mismatch |
| `brawl_stars` | `B2_specific_anime_game_media_ip` | `280` | empty_placeholder_variable, rel_metadata_mismatch |
| `butterfly` | `B1_specific_brand_trademark` | `54` | broken_json_schema |
| `calvin_klein` | `B1_specific_brand_trademark` | `55` | broken_json_schema |
| `cars_automotive_general` | `A2_vertical_open_set_or_multi_entity` | `298` | rel_metadata_mismatch |
| `celine` | `B1_specific_brand_trademark` | `369` | broken_json_schema |
| `chainsawman` | `B2_specific_anime_game_media_ip` | `281` | broken_json_schema |
| `chanel_cc` | `B1_specific_brand_trademark` | `57` | broken_json_schema |
| `clash_royale` | `B2_specific_anime_game_media_ip` | `371` | rel_metadata_mismatch |
| `cluster_gemini` | `A1_open_set_cross_domain_ip` | `375` | rel_metadata_mismatch |
| `cohiba` | `B1_specific_brand_trademark` | `289` | rel_metadata_mismatch |
| `converseallstar` | `B1_specific_brand_trademark` | `290` | broken_json_schema |
| `coraline` | `B2_specific_anime_game_media_ip` | `60` | rel_metadata_mismatch |
| `cowboybebop` | `B2_specific_anime_game_media_ip` | `61` | broken_json_schema |
| `crocs_charms` | `B5_specific_design_patent_product` | `185` | broken_json_schema |
| `cwt_legging` | `B5_specific_design_patent_product` | `377` | uncleaned_sku_text_residue |
| `daddario` | `B1_specific_brand_trademark` | `64` | broken_json_schema |
| `dior` | `B1_specific_brand_trademark` | `69` | broken_json_schema |
| `dodge` | `B1_specific_brand_trademark` | `191` | broken_json_schema |
| `dsquared2` | `B1_specific_brand_trademark` | `6` | empty_placeholder_variable, rel_metadata_mismatch |
| `duke_university` | `B3_specific_sports_university` | `380` | typo_or_logic_defect |
| `dune` | `B2_specific_anime_game_media_ip` | `71` | underspecified_rubric |
| `general_ip_model_nxy` | `A1_open_set_cross_domain_ip` | `293` | underspecified_rubric |
| `glassangelofficial` | `B4_specific_celebrity_band_artist` | `294` | broken_json_schema, rel_metadata_mismatch |
| `harrypotter` | `B2_specific_anime_game_media_ip` | `10` | typo_or_logic_defect |
| `hatsune_miku` | `B2_specific_anime_game_media_ip` | `84` | broken_json_schema, style_only_trigger_risk |
| `hells_angles_motorcycle` | `B1_specific_brand_trademark` | `85` | broken_json_schema |
| `hemier_league` | `A2_vertical_open_set_or_multi_entity` | `299` | rel_metadata_mismatch |
| `hendrickmotorsports` | `B3_specific_sports_university` | `88` | broken_json_schema |
| `higuchi_yuko` | `B4_specific_celebrity_band_artist` | `318` | typo_or_logic_defect |
| `hilton` | `B1_specific_brand_trademark` | `94` | broken_json_schema |
| `honda` | `B1_specific_brand_trademark` | `202` | broken_json_schema |
| `infringement_detection` | `A1_open_set_cross_domain_ip` | `96` | rel_metadata_mismatch |
| `infringementcards` | `A2_vertical_open_set_or_multi_entity` | `389` | broken_json_schema, rel_metadata_mismatch |
| `itmovie` | `B2_specific_anime_game_media_ip` | `427` | broken_json_schema |
| `jeep` | `B1_specific_brand_trademark` | `390` | broken_json_schema |
| `jiaxiangye` | `B5_specific_design_patent_product` | `97` | broken_json_schema |
| `juicewrld` | `B4_specific_celebrity_band_artist` | `19` | typo_or_logic_defect |
| `jujutsukaisen` | `B2_specific_anime_game_media_ip` | `98` | broken_json_schema |
| `juliusk9` | `B1_specific_brand_trademark` | `259` | broken_json_schema, underspecified_rubric |
| `kimesranch` | `B1_specific_brand_trademark` | `204` | broken_json_schema |
| `kirby` | `B2_specific_anime_game_media_ip` | `428` | broken_json_schema |
| `kith` | `B1_specific_brand_trademark` | `260` | broken_json_schema |
| `ledzeppelin` | `B4_specific_celebrity_band_artist` | `100` | broken_json_schema |
| `legorelated` | `B2_specific_anime_game_media_ip` | `391` | broken_json_schema |
| `maradona` | `B4_specific_celebrity_band_artist` | `306` | broken_json_schema |
| `mastermind` | `B1_specific_brand_trademark` | `262` | broken_json_schema |
| `megaman` | `B2_specific_anime_game_media_ip` | `20` | rel_metadata_mismatch |
| `merchtraffic` | `A2_vertical_open_set_or_multi_entity` | `264` | underspecified_rubric |
| `metallica` | `B4_specific_celebrity_band_artist` | `213` | rel_metadata_mismatch |
| `milwaukeetool` | `B1_specific_brand_trademark` | `321` | broken_json_schema |
| `minions` | `B2_specific_anime_game_media_ip` | `119` | broken_json_schema |
| `molson_coors` | `B1_specific_brand_trademark` | `400` | typo_or_logic_defect |
| `money_heist_la_casa_de_papel` | `B2_specific_anime_game_media_ip` | `416` | typo_or_logic_defect |
| `monopoly` | `B2_specific_anime_game_media_ip` | `333` | underspecified_rubric |
| `monsterenergy` | `B1_specific_brand_trademark` | `434` | rel_metadata_mismatch |
| `monsterhigh` | `B2_specific_anime_game_media_ip` | `120` | rel_metadata_mismatch |
| `mr_men_little_miss` | `B2_specific_anime_game_media_ip` | `430` | empty_placeholder_variable, rel_metadata_mismatch |
| `my_dress` | `B2_specific_anime_game_media_ip` | `323` | rel_metadata_mismatch |
| `my_hero_academia` | `B2_specific_anime_game_media_ip` | `215` | broken_json_schema |
| `nba` | `B3_specific_sports_university` | `122` | rel_metadata_mismatch |
| `neymar` | `B4_specific_celebrity_band_artist` | `308` | broken_json_schema |
| `nhl` | `B3_specific_sports_university` | `265` | rel_metadata_mismatch |
| `nirvana` | `B4_specific_celebrity_band_artist` | `406` | broken_json_schema |
| `novak_djokovic` | `B4_specific_celebrity_band_artist` | `266` | rel_metadata_mismatch |
| `oklahoma_university` | `B3_specific_sports_university` | `421` | typo_or_logic_defect |
| `olympic` | `B3_specific_sports_university` | `127` | rel_metadata_mismatch |
| `oster` | `B1_specific_brand_trademark` | `128` | broken_json_schema |
| `pandorobo` | `B2_specific_anime_game_media_ip` | `325` | broken_json_schema |
| `parkerbabyco` | `B5_specific_design_patent_product` | `218` | broken_json_schema |
| `paw_patrol` | `B2_specific_anime_game_media_ip` | `130` | broken_json_schema |
| `peanuts` | `B2_specific_anime_game_media_ip` | `131` | broken_json_schema |
| `pikmin` | `B2_specific_anime_game_media_ip` | `411` | broken_json_schema |
| `pitbull` | `B4_specific_celebrity_band_artist` | `326` | broken_json_schema |
| `plexaderm` | `B1_specific_brand_trademark` | `137` | rel_metadata_mismatch |
| `postyaustin` | `B4_specific_celebrity_band_artist` | `220` | broken_json_schema |
| `purple_innovation` | `B5_specific_design_patent_product` | `136` | broken_json_schema |
| `ralph_lauren` | `B1_specific_brand_trademark` | `328` | broken_json_schema |
| `ratt` | `B4_specific_celebrity_band_artist` | `138` | typo_or_logic_defect |
| `rilakkuma` | `B2_specific_anime_game_media_ip` | `310` | rel_metadata_mismatch |
| `risk_evaluation` | `A1_open_set_cross_domain_ip` | `443` | duplicate_role_header, rel_metadata_mismatch |
| `riskdata_iplogo_brand_gemini` | `A1_open_set_cross_domain_ip` | `444` | rel_metadata_mismatch |
| `rusty` | `B1_specific_brand_trademark` | `222` | broken_json_schema, rel_metadata_mismatch |
| `shingbright` | `B5_specific_design_patent_product` | `447` | broken_json_schema, underspecified_rubric |
| `slamdunk` | `B2_specific_anime_game_media_ip` | `144` | broken_json_schema |
| `slayer` | `B4_specific_celebrity_band_artist` | `414` | broken_json_schema |
| `spirit` | `B2_specific_anime_game_media_ip` | `145` | rel_metadata_mismatch |
| `spongebobsquarepants` | `B2_specific_anime_game_media_ip` | `146` | broken_json_schema |
| `spotit` | `B2_specific_anime_game_media_ip` | `448` | broken_json_schema, underspecified_rubric |
| `starbucks` | `B1_specific_brand_trademark` | `227` | broken_json_schema |
| `stealabrainrot` | `B2_specific_anime_game_media_ip` | `147` | rel_metadata_mismatch |
| `taylorswift` | `B4_specific_celebrity_band_artist` | `450` | rel_metadata_mismatch |
| `thebadguys` | `B2_specific_anime_game_media_ip` | `151` | empty_placeholder_variable |
| `thenewyorker` | `B1_specific_brand_trademark` | `152` | broken_json_schema |
| `thesimpsonver2` | `B2_specific_anime_game_media_ip` | `153` | broken_json_schema, style_only_trigger_risk |
| `thomasandfriends` | `B2_specific_anime_game_media_ip` | `419` | broken_json_schema |
| `tomandjerry` | `B2_specific_anime_game_media_ip` | `157` | broken_json_schema |
| `tommy_hilfiger` | `B1_specific_brand_trademark` | `156` | broken_json_schema |
| `totto` | `B1_specific_brand_trademark` | `454` | rel_metadata_mismatch |
| `toyota` | `B1_specific_brand_trademark` | `232` | broken_json_schema |
| `trolls` | `B2_specific_anime_game_media_ip` | `161` | broken_json_schema, style_only_trigger_risk |
| `twentyonepilots` | `B4_specific_celebrity_band_artist` | `162` | rel_metadata_mismatch |
| `universityofkentucky` | `B3_specific_sports_university` | `273` | broken_json_schema |
| `van_cleef_arpels` | `B1_specific_brand_trademark` | `237` | rel_metadata_mismatch |
| `vivienne_westwood` | `B1_specific_brand_trademark` | `168` | broken_json_schema |
| `warhammer` | `B2_specific_anime_game_media_ip` | `15` | rel_metadata_mismatch |
| `whitefox` | `B1_specific_brand_trademark` | `332` | broken_json_schema |
| `wickedtrademark` | `B1_specific_brand_trademark` | `169` | broken_json_schema |
| `yamal` | `B4_specific_celebrity_band_artist` | `425` | typo_or_logic_defect |
| `zigzag` | `B1_specific_brand_trademark` | `242` | broken_json_schema |
