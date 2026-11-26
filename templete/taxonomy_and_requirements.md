# 352 审核模板同族科学分类与审核需求全量提取报告

- **生成时间**: `2026-11-26T02:25:35.428426+00:00`
- **样本范围**: 全量 `352` 个同族模板（来自 `templete/index.json`，基于完整未截断清洗文本解析）

## 一、MECE 二维分类总表（权利方基数 × 审核机制）

| 主分类 Track | 子分类 Subtrack | 含义 | 同族数 | 占比 |
|---|---|---|---:|---:|
| 广域识别模板 (`broad_domain`) | `A1_open_set_cross_domain_ip` | A1 跨域开放集商标/IP/宿主隔离识别 | **10** | 2.8% |
| 广域识别模板 (`broad_domain`) | `A2_vertical_open_set_or_multi_entity` | A2 垂直品类/多实体列表联合审核 | **14** | 4.0% |
| 广域识别模板 (`broad_domain`) | `A3_pairwise_visual_mechanism` | A3 双图对比防二创/规避机制 | **1** | 0.3% |
| 广域识别模板 (`broad_domain`) | `A4_auxiliary_governance_workflow` | A4 非视觉商品辅助治理与法务合规流 | **11** | 3.1% |
| 特定产品/IP/品牌 (`entity_specific`) | `B1_specific_brand_trademark` | B1 特定商业品牌/商标识别 | **139** | 39.5% |
| 特定产品/IP/品牌 (`entity_specific`) | `B2_specific_anime_game_media_ip` | B2 特定动漫/游戏/影视/玩具IP识别 | **87** | 24.7% |
| 特定产品/IP/品牌 (`entity_specific`) | `B3_specific_sports_university` | B3 特定体育联盟/球队/高校IP识别 | **29** | 8.2% |
| 特定产品/IP/品牌 (`entity_specific`) | `B4_specific_celebrity_band_artist` | B4 特定名人/乐队/球星/艺术家识别 | **34** | 9.7% |
| 特定产品/IP/品牌 (`entity_specific`) | `B5_specific_design_patent_product` | B5 特定产品外观专利/结构装潢识别 | **18** | 5.1% |
| 隔离异常模板 (`quarantined_excluded`) | `Q1_test_junk` | Q1 测试占位/废案隔离 | **5** | 1.4% |
| 隔离异常模板 (`quarantined_excluded`) | `Q2_cross_entity_paste_bug` | Q2 跨实体错贴 Bug 隔离 | **4** | 1.1% |

> 合计：**广域识别模板 `36` 族 (10.2%)** · **特定产品/IP/品牌识别模板 `307` 族 (87.2%)** · **隔离异常模板 `9` 族 (2.6%)**，MECE 总计 `352` 族。

## 二、广域识别模板全清单（36 族）与审计需求映射

| Subtrack | `family_slug` | 默认主版标题 | 模态策略 | 关键机制/要求 | CPT-SFT 路由 |
|---|---|---|---|---|---|
| `A1_open_set_cross_domain_ip` | `brand_gemini_general` | `ip_brand_gemini_general` | `image_and_text_joint` | conservative_insufficient_evidence_abstain, material_consistency_check, subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `brand_goods_consistent_multi_img` | `ip_brand_goods_consistent_multi_imgV2` | `image_and_text_joint` | common_word_disambiguation, compatibility_exemption, subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `cluster_gemini` | `ip_cluster_gemini_grounding` | `image_and_text_joint` | common_word_disambiguation, compatibility_exemption, conservative_insufficient_evidence_abstain | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `general_ip_model_nxy` | `general_IP_Model_nxy` | `image_only` | subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `general_rihe` | `ip_general_rihe` | `image_and_text_joint` | conservative_insufficient_evidence_abstain, material_consistency_check, subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `infringement_detection` | `IP_Infringement_Detection` | `image_only` | - | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `logo_similar_judge` | `logo_similar_judge` | `image_only` | conservative_insufficient_evidence_abstain, generic_style_exclusion | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `risk_evaluation` | `risk_ip_adds_evaluation_gemini` | `image_and_text_joint` | boolean_compound_logic, material_consistency_check, subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `riskdata_iplogo_brand_gemini` | `riskdata_iplogo_brand_gemini` | `image_and_text_joint` | subject_host_isolation | `A1_broad_curriculum` |
| `A1_open_set_cross_domain_ip` | `tro_anly` | `ip_tro_anly` | `image_and_text_joint` | common_word_disambiguation, conservative_insufficient_evidence_abstain, generic_style_exclusion | `A1_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `artist` | `ip_artist` | `image_only` | - | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `band_music_general` | `ip_band_v2` | `image_and_text_joint` | - | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `cars_automotive_general` | `hemier-cars-selfmodel` | `image_and_text_joint` | boolean_compound_logic, compatibility_exemption, subject_host_isolation | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `counterfeit_jerseys` | `IP-Counterfeit Jerseys` | `image_and_text_joint` | material_consistency_check | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `counterfeit_watch` | `IP-Counterfeit Watch` | `image_only` | common_word_disambiguation, compatibility_exemption, generic_style_exclusion | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `hemier_league` | `hemier-league-selfmodel` | `image_and_text_joint` | boolean_compound_logic, conservative_insufficient_evidence_abstain, subject_host_isolation | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `household` | `IP_Household` | `image_and_text_joint` | - | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `infringementcards` | `ip_infringementcards` | `image_and_text_joint` | material_consistency_check, subject_host_isolation | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `kpop` | `ip-kpop` | `image_and_text_joint` | boolean_compound_logic | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `merchtraffic` | `MerchTraffic` | `image_and_text_joint` | - | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `nin1_game_console` | `ip_nin1new` | `image_and_text_joint` | compatibility_exemption | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `spainish_celebrity` | `ip-spainish celebrity` | `image_and_text_joint` | boolean_compound_logic, common_word_disambiguation, conservative_insufficient_evidence_abstain | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `sport_star` | `ip-sport star-prompt` | `image_and_text_joint` | boolean_compound_logic | `A2_broad_curriculum` |
| `A2_vertical_open_set_or_multi_entity` | `sports_ball_general` | `ip_ball` | `image_and_text_joint` | boolean_compound_logic, common_word_disambiguation, conservative_insufficient_evidence_abstain | `A2_broad_curriculum` |
| `A3_pairwise_visual_mechanism` | `twizler` | `IP_twizler` | `pairwise_image_comparison` | common_word_disambiguation, subject_host_isolation | `A3_broad_curriculum` |
| `A4_auxiliary_governance_workflow` | `aux_audit_feedback_optimizer` | `ip_audit_feedback_optimizer` | `image_and_text_joint` | compatibility_exemption, conservative_insufficient_evidence_abstain, material_consistency_check | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_black_word_risk_reviewer` | `black_word_risk_reviewer` | `text_primary_or_only` | common_word_disambiguation, compatibility_exemption | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_brand_alliance` | `ip_brand_alliance_discoverer` | `text_primary_or_only` | common_word_disambiguation, subject_host_isolation | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_brand_collab` | `ip_brand_collab_auditor` | `text_primary_or_only` | - | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_crawlplatform_anti_risk` | `crawlplatform_anti_risk` | `image_only` | compatibility_exemption, conservative_insufficient_evidence_abstain | `A4_doc_screenshot_sft` |
| `A4_auxiliary_governance_workflow` | `aux_identifying_fake_brands` | `Identifying_fake_brands` | `text_primary_or_only` | conservative_insufficient_evidence_abstain, generic_style_exclusion | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_invoices` | `Invoices` | `image_only` | common_word_disambiguation | `A4_doc_screenshot_sft` |
| `A4_auxiliary_governance_workflow` | `aux_logos_review_verification_text` | `logos_review_verification_text` | `text_primary_or_only` | compatibility_exemption | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_tro_brandname_alignment` | `tro_brandname_alignment_gemini` | `text_primary_or_only` | common_word_disambiguation | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_tro_brandname_rec` | `tro_brandname_rec_gemini` | `text_primary_or_only` | - | `A4_text_legal_sft_budgeted` |
| `A4_auxiliary_governance_workflow` | `aux_tro_warning_case_process` | `tro_warning_case_process_dome` | `text_primary_or_only` | compatibility_exemption, conservative_insufficient_evidence_abstain | `A4_text_legal_sft_budgeted` |

## 三、全量 352 族审核需求频次统计

### 3.1 模态决策策略 (`modality_decision_policy`)
| 策略 | 同族数 | 含义 |
|---|---:|---|
| `image_and_text_joint` | 262 | 图文联合判定（结合商品标题与图像证据） |
| `image_only` | 79 | 纯视觉主导判断 |
| `text_primary_or_only` | 8 | 纯文本/案件元数据主判 |
| `image_overrides_text` | 2 | 图片绝对优先（严防仅标题含词无视觉标时误杀） |
| `pairwise_image_comparison` | 1 | 双图对比（敏感母本图 vs 待审风险图） |

### 3.2 视觉识别要素需求 (`visual_cues_required`)
| 视觉线索 | 涉及同族数 | 说明 |
|---|---:|---|
| `logo_wordmark` | 241 | 品牌文字标/图形Logo拓扑 |
| `character_mascot_likeness` | 141 | 角色/吉祥物外观与特征组合 |
| `ocr_deformed_or_obfuscated_text` | 106 | 形变/遮挡/涂抹/谐音拼写OCR |
| `derivative_fanart_style` | 80 | 二创/Q版/重绘与风格边界判定 |
| `human_portrait_celebrity` | 74 | 真人肖像/乐队舞台/公众人物特征 |
| `trade_dress_pattern_packaging` | 48 | 老花暗纹/拼接装潢/包装设计 |
| `3d_product_geometry_patent` | 33 | 产品三维结构/功能件/专利几何 |
| `jersey_crest_colors` | 32 | 队徽/球衣配色/号码与奖杯标识 |
| `document_or_webpage_screenshot` | 10 | 凭证/法律文书/网页截图取证 |
| `watermark_or_crop` | 3 | 水印/小区域局部裁切检测 |

### 3.3 边界防错与推理机制需求 (`boundary_and_exclusion_mechanisms`)
| 机制 | 涉及同族数 | 说明 |
|---|---:|---|
| `subject_host_isolation` | 141 | 售卖主体锁定与宿主/背景隔离 |
| `boolean_compound_logic` | 120 | 多条款布尔组合求值 (AND/OR) |
| `common_word_disambiguation` | 88 | 日常词汇/通用图案消歧 |
| `compatibility_exemption` | 47 | 适配/兼容词豁免（如适用于/for） |
| `material_consistency_check` | 39 | 图文载体/材质一致性核验 |
| `conservative_insufficient_evidence_abstain` | 23 | 证据不足保守拒判（不强猜） |
| `generic_style_exclusion` | 17 | 纯画风/通用元素排除（防误杀原创） |
| `reverse_elimination_fast_reject` | 8 | 反向剔除快速免审机制 |

### 3.4 输出协议形态 (`output_contract.format`)
| 输出格式 | 同族数 |
|---|---:|
| `json_res_reason` | 339 |
| `freeform_or_checklist` | 9 |
| `boolean_true_false_with_reason` | 3 |
| `legal_structured_json` | 1 |
