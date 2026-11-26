#!/usr/bin/env python3
"""Build an offline warm-paper editorial HTML audit workbench for Assert/templete.

Reads `manifests/template_library_manifest.json`, `templete/index.json`, and every
family's `family.json` + `raw_records.jsonl`, resolves verified local Assert reference
image paths relative to `templete/`, and writes a self-contained zero-CDN HTML
gallery & review workbench (`templete/review_dashboard.html`) styled after
`Study/Paper/gallery.html`.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import re
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLETE_DIR = PROJECT_ROOT / "templete"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "manifests" / "template_library_manifest.json"
DEFAULT_TAXONOMY_PATH = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.json"
DEFAULT_ENRICH_PATH = PROJECT_ROOT / "manifests" / "template_wiki_enrichment.jsonl"
DEFAULT_VISUAL_AUDIT_PATH = PROJECT_ROOT / "manifests" / "template_visual_audit_decisions.jsonl"
DEFAULT_REVIEWS_AUDITED_PATH = PROJECT_ROOT / "manifests" / "assert_template_reviews_audited.json"
DEFAULT_CHARACTER_DOSSIERS_PATH = PROJECT_ROOT / "manifests" / "character_wiki_dossiers.jsonl"
DEFAULT_CHARACTER_PORTRAITS_PATH = PROJECT_ROOT / "manifests" / "character_wiki_portraits.jsonl"
DEFAULT_OUTPUT_HTML = DEFAULT_TEMPLETE_DIR / "review_dashboard.html"
PREVIEW_MAX_EDGE = 320
PORTRAIT_MAX_EDGE = 176


def _resolve_asset_file(raw_path: str, templete_dir: Path) -> tuple[str, str, Path] | None:
    """Resolves an Assert image path to `(asset_key, rel_to_templete, abs_path)`."""
    cleaned = str(raw_path or "").strip()
    if not cleaned:
        return None
    candidates = [cleaned]
    if cleaned.startswith("assets/"):
        candidates.append(cleaned[len("assets/") :])
    root_resolved = PROJECT_ROOT.resolve()
    templete_resolved = templete_dir.resolve()
    for cand in candidates:
        abs_path = (PROJECT_ROOT / cand).resolve()
        if abs_path.is_file():
            try:
                rel_to_root = abs_path.relative_to(root_resolved)
                prefix = "../" * len(templete_resolved.relative_to(root_resolved).parts)
                asset_key = rel_to_root.as_posix()
                return asset_key, prefix + asset_key, abs_path
            except ValueError:
                return None
    return None


def _encode_image_data_uri(abs_path: Path, max_edge: int = PREVIEW_MAX_EDGE) -> str:
    """Encodes a local image as a compact (<=360px preview) base64 data URI."""
    try:
        with Image.open(abs_path) as im:
            im.load()
            rgba = im.convert("RGBA")
            if max(rgba.size) > max_edge:
                rgba.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
            min_alpha, _ = rgba.getchannel("A").getextrema()
            buf = io.BytesIO()
            if min_alpha < 255:
                rgba.save(buf, format="PNG", optimize=True)
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                return f"data:image/png;base64,{b64}"
            rgb = Image.new("RGB", rgba.size, (255, 255, 255))
            rgb.paste(rgba, mask=rgba.getchannel("A"))
            rgb.save(buf, format="JPEG", quality=78, optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{b64}"
    except Exception:
        pass
    mime, _ = mimetypes.guess_type(abs_path.name)
    if not mime or not mime.startswith("image/"):
        mime = "image/png"
    b64 = base64.b64encode(abs_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                rows.append(json.loads(s))
    return rows


BROAD_DOMAIN_CLEAN_NAMES: dict[str, str] = {
    "artist": "原创画师 / 艺术家版权通用识别",
    "aux_audit_feedback_optimizer": "线上错例反馈与规则优化流",
    "aux_black_word_risk_reviewer": "敏感黑词与跨类商标文本风控",
    "aux_brand_alliance": "品牌联名与权利关联挖掘",
    "aux_brand_collab": "品牌联名真实性审核",
    "aux_crawlplatform_anti_risk": "抓取平台反爬与风控状态识别",
    "aux_identifying_fake_brands": "山寨与伪造品牌名鉴别",
    "aux_invoices": "进货发票真伪与货单一致性核验",
    "aux_logos_review_verification_text": "法律判决文本结构化校验",
    "aux_tro_brandname_alignment": "TRO 涉诉品牌名规范对齐",
    "aux_tro_brandname_rec": "TRO 涉诉品牌名召回识别",
    "aux_tro_warning_case_process": "TRO 诉讼预警与案件节点处理",
    "band_music_general": "乐队 / 歌手通用版权与周边识别",
    "brand_gemini_general": "通用品牌宿主隔离与材质一致性审核",
    "brand_goods_consistent_multi_img": "多图商品品牌与动态名单一致性审核",
    "cars_automotive_general": "汽车品牌通用侵权与配件适配豁免",
    "cluster_gemini": "聚类品牌 / 独立站图搜归因审查",
    "counterfeit_jerseys": "无 Logo 球衣配色与版型抄袭识别",
    "counterfeit_watch": "奢侈名表闭集多品牌侵权治理",
    "general_ip_model_nxy": "通用多场景视觉 IP 识别",
    "general_rihe": "日韩 / 通用 IP 宿主隔离识别",
    "hemier_league": "北美体育联盟 (MLB / NHL) 联合审核",
    "household": "家居日用品外观专利与结构通用审核",
    "infringement_detection": "跨域商品侵权风险综合判定",
    "infringementcards": "集换式卡牌侵权与卡套/卡膜豁免",
    "kpop": "K-Pop 偶像团体官方周边与标识识别",
    "logo_similar_judge": "商标 Logo 相似度对齐判定",
    "merchtraffic": "MerchTraffic 艺人官方演出周边识别",
    "nin1_game_console": "N 合 1 怀旧游戏机通用判定与早教机豁免",
    "risk_evaluation": "多模态商品与广告综合风险评估",
    "riskdata_iplogo_brand_gemini": "风险库商标 Logo 视觉检测",
    "spainish_celebrity": "西班牙名人与体育明星通用识别",
    "sport_star": "体育明星个人 IP 与签名商品通用识别",
    "sports_ball_general": "通用体育俱乐部 / 联盟 / 球星 IP",
    "tro_anly": "TRO 诉讼风险商品通用分析",
    "twizler": "双图对比 AI 二创 / 裁剪防规避审核",
}

ENTITY_NAME_OVERRIDES: dict[str, str] = {
    "511": "5.11 Tactical",
    "acdc": "AC/DC",
    "acdcllm": "AC/DC",
    "adanola": "Adanola",
    "agv": "AGV",
    "ajsnifty": "AJS Nifty",
    "ami": "AMI Paris",
    "amiri": "Amiri",
    "apf": "巴拉圭足协 (APF)",
    "badcutebunny": "Bad Cute Bunny",
    "brand": "Brand（错贴模板待重修）",
    "cookies": "Cookies",
    "courtneymorgenstern": "Courtney Morgenstern",
    "covernat": "Covernat",
    "cucu": "Cucu",
    "cwt_legging": "CWT Legging",
    "doubleendedhandtool": "Double-Ended Hand Tool",
    "genies_perfume_atomizer": "Genies Perfume Atomizer",
    "goorinbros": "Goorin Bros",
    "jenny_urquhart": "Jenny Urquhart",
    "jiaxiangye": "Jiaxiangye",
    "kaffe": "KAFFE",
    "kimesranch": "Kimes Ranch",
    "libertyuniversity": "Liberty University",
    "lindseyferrell": "Lindsey Ferrell",
    "men_of_mayhem": "Men of Mayhem",
    "milan_ac": "AC 米兰 (AC Milan)",
    "pandorobo": "面包小偷 (Pandorobo)",
    "parkerbabyco": "Parker Baby Co.",
    "pickulsgizmo": "Pickuls Gizmo",
    "plexaderm": "Plexaderm",
    "purplebrand": "Purple Brand",
    "rusty": "Rusty",
    "southcarolina": "南卡罗来纳大学 (South Carolina)",
    "tangle": "Tangle",
    "test_111": "测试废案 (test111)",
    "test_5678": "测试废案 (5678)",
    "test_general_ip": "测试废案 (IPgeneraltest)",
    "test_lingjinglan": "测试废案 (lingjinglan)",
    "test_nyetest": "测试废案 (NyeTest)",
    "tintin": "丁丁历险记 (Tintin)",
    "tumi": "TUMI",
    "twentyonepilots": "Twenty One Pilots",
}

_ACRONYM_WORDS = {
    "bmw", "bp", "agv", "nba", "nfl", "nhl", "mlb", "ncaa", "apf", "tumi",
    "kaffe", "cwt", "ami", "acdc", "kfc", "ugg", "ysl", "lv", "ck", "dkny",
    "dhl", "ups", "fedex", "ea", "jbl", "gopro", "nasa", "fbi", "ufc", "wwe",
    "f1", "dc", "uno", "lego",
}

_FLAG_ACTION_MAP: dict[str, str] = {
    "missing_exclusion_clause": "补充反向排除条款：明确豁免日常通用元素、配件适配词（suitable for）或纯无标基础款，降低高误杀。",
    "rel_metadata_mismatch": "核对并修正主版 `rel` 关联实体标签，消除元数据错绑导致的训练与调度误触发。",
    "underspecified_rubric": "细化可观测量化视觉判据（结构、文字标、配色组合与载体要求），补齐正负例对照。",
    "broken_json_schema": "修复输出 JSON 字段名拼写与闭合括号，确保严格符合推理阶段 JSON 契约。",
    "typo_or_logic_defect": "修正最新主版中的错别字或“是/否”逻辑反转表述，防止 SFT 阶段学到矛盾判据。",
    "weak_anchor_or_escape_hatch": "收紧主观兜底/自由发挥表述，强制仅以图像可见决定性视觉锚点作为判别依据。",
    "style_only_trigger_risk": "补充画风剥离门控（Step 1 排除通用美术风格/时代质感，Step 2 核验特有角色结构或徽记组合）。",
    "cross_entity_paste_bug": "【阻塞】最新主版正文疑似错贴其他 IP/品牌规则，必须整篇核对重写后再参与训练或评测。",
    "empty_placeholder_variable": "补全或删除未展开的空变量占位符，保证模版离线可执行。",
    "duplicate_role_header": "去重合并重复的 Role / System 段落，消除指令冲突。",
    "empty_or_trivial_body": "最新主版正文空壳或过短，需补充完整审核对象定义、判定边界与输出规范。",
}


def _derive_entity_name(
    slug: str,
    raw_display_name: str,
    scope_track: str,
    wiki_title: str,
    supplement_matches: list[dict[str, Any]],
) -> str:
    if slug in BROAD_DOMAIN_CLEAN_NAMES:
        return BROAD_DOMAIN_CLEAN_NAMES[slug]
    if slug in ENTITY_NAME_OVERRIDES:
        return ENTITY_NAME_OVERRIDES[slug]

    raw = str(raw_display_name or "").strip()
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", raw))
    looks_like_tpl = bool(
        re.match(r"^(?:ip|IP)[_\-\s]", raw)
        or re.search(r"_(?:V\d+|db_\d+|ALLRULE|strategy|prompt|TRADEMARK|\d{4}trademark)\b", raw, re.I)
        or re.search(r"(?:模版|模板)$", raw)
    )
    if has_cjk and not looks_like_tpl:
        return raw

    wt = str(wiki_title or "").strip()
    if wt:
        wt_clean = re.sub(
            r"\s*\((?:manga|doll|company|brand|film|video game|TV series|British clothing brand|characters?|franchise|band|comics?|sportswear)\)\s*$",
            "",
            wt,
            flags=re.I,
        ).strip()
        if wt_clean:
            return wt_clean

    for m in supplement_matches or []:
        zh = str(m.get("name_zh") or "").strip()
        en = str(m.get("name_en") or "").strip()
        if zh and en and zh.lower() != en.lower():
            return f"{zh} ({en})"
        if zh or en:
            return zh or en

    s = re.sub(r"^(?:ip|IP)[_\-\s]+", "", raw or slug)
    s = re.sub(r"(?:_db_\d+|_v\d+|_\d{4}trademark|_trademark|_allrule|_strategy|_prompt|_tradename|llm)$", "", s, flags=re.I)
    s = re.sub(r"[-_]+", " ", s).strip()
    words = []
    for w in s.split():
        wl = w.lower()
        if wl in _ACRONYM_WORDS or (w.isupper() and len(w) <= 4):
            words.append(w.upper())
        elif w.islower() or w.isupper():
            words.append(w.capitalize())
        else:
            words.append(w)
    return " ".join(words) or slug


def _build_latest_audit(default_member: dict[str, Any], fam_recommendations: list[str]) -> dict[str, Any]:
    flags = list(default_member.get("hygiene_flags") or [])
    findings = list(default_member.get("findings") or [])
    disp = str(default_member.get("disposition") or "active_ip")
    actions: list[str] = []
    for fl in flags:
        act = _FLAG_ACTION_MAP.get(fl)
        if act and act not in actions:
            actions.append(act)
    for rec in fam_recommendations or []:
        if rec and rec not in actions and len(actions) < 5:
            actions.append(rec)
    if not actions:
        actions.append("最新主版判据结构完整、无阻塞性语法或逻辑缺陷，可直接作为当前业务审核与 SFT 规则基准。")

    if disp in ("quarantine_paste_bug", "quarantine_test_junk"):
        verdict = "需拦截隔离"
    elif disp == "needs_body_completion" or flags:
        verdict = "需优化最新主版"
    else:
        verdict = "最新主版可直接复用"

    return {
        "version_key": str(default_member.get("version_key") or default_member.get("id") or ""),
        "id": int(default_member.get("id") or 0),
        "title": str(default_member.get("title") or ""),
        "chars": int(default_member.get("chars") or 0),
        "disposition": disp,
        "export_cleanups_count": int(default_member.get("export_cleanups_count") or 0),
        "hygiene_flags": flags,
        "findings": findings,
        "verdict": verdict,
        "action_items": actions,
    }


def _build_training_advice(
    scope_track: str,
    scope_subtrack: str,
    entity_name: str,
    latest_audit: dict[str, Any],
    audit_req: dict[str, Any],
    char_count: int,
    portrait_count: int,
    asset_count: int,
    supports_derivative: bool,
) -> dict[str, Any]:
    bnds = set(audit_req.get("boundary_and_exclusion_mechanisms") or [])
    cues = set(audit_req.get("visual_cues_required") or [])
    flags = set(latest_audit.get("hygiene_flags") or [])
    disp = latest_audit.get("disposition") or "active_ip"

    if scope_track == "quarantined_excluded" or disp in ("quarantine_paste_bug", "quarantine_test_junk"):
        return {
            "gate_status": "excluded_quarantine",
            "gate_label": "严禁直接入训（隔离清理后方可重入）",
            "cpt_plan": ["已列入模板隔离清单，严格排除在 CPT Mid-Training 与合成图文文档之外，防止错误实体先验污染梯度。"],
            "sft_plan": ["严禁使用该家族正文构造 SFT 正例；仅在 `fix_template_prompt_bug` 修复并人工复核通过后才允许重新分配 `doc_family_id`。"],
            "eval_plan": ["从 Flash / Pro 基准评测集移除或单独作为“异常样本拦截”单测。"],
        }

    needs_prompt_fix = bool(flags & {"broken_json_schema", "typo_or_logic_defect", "empty_or_trivial_body", "cross_entity_paste_bug", "rel_metadata_mismatch"})
    total_visuals = asset_count + portrait_count
    needs_assets = scope_track == "entity_specific" and total_visuals == 0

    if needs_prompt_fix:
        gate_status = "fix_prompt_first"
        gate_label = "先修最新主版缺陷，再入 SFT"
    elif needs_assets:
        gate_status = "enrich_assets_first"
        gate_label = "补齐 Assert 标准视觉图后入 CPT"
    else:
        gate_status = "ready_for_training"
        gate_label = "具备 CPT + SFT 双通道入训条件"

    cpt_plan: list[str] = []
    sft_plan: list[str] = []
    eval_plan: list[str] = []

    if scope_track == "broad_domain":
        if scope_subtrack == "A4_auxiliary_governance_workflow":
            cpt_plan.append("A4 属于文本/凭证/运维治理流，严格遵守 CPT `qa_prose <= 15%` 上限，不抢占主力视觉 IP 配额；仅发票/网页截图类可少量混入多模态图文语料。")
            sft_plan.append("通过 `--sft-mixed-budget` 配额进入统一双模 SFT，重点强化多字段 JSON 输出稳定率；运维类反馈模板建议直连 Pro 阶段 `error_cluster_miner.py`。")
        else:
            cpt_plan.append("以视觉机制先导的数据为主：`Datawheel` + `Assert` 多品牌锚定 + 线 B `v6_edit_pairs` 生成“换宿主 / 背景无关 Logo 注入 / 局部涂抹遮挡”反事实对比文档。")
            if scope_subtrack == "A3_pairwise_visual_mechanism":
                cpt_plan.append("复用 `ch_v2_derivative_pair` 与 `ch_v6_edit_cf_pair`，强化原图 vs AI 二创 / 裁剪镜像的双图对齐感知。")
            if scope_subtrack in ("A2_vertical_open_set_or_multi_entity",):
                cpt_plan.append("按垂直领域打包多图共现语料，高幻觉域（画师/公众人物）绑定 RAG Top-K 召回文本段落，避免裸权重硬背长尾人名。")
            sft_plan.append("在 `rule_grounded_audit_sft` 中构造“同图切换闭集名单 / 更改售卖宿主 → 判决翻转”对抗三元组，训练指令边界严格服从。")
    else:
        if scope_subtrack == "B2_specific_anime_game_media_ip":
            if char_count > 0:
                cpt_plan.append(f"已匹配 {char_count} 条多源角色档案与 {portrait_count} 张立绘，优先把 `character_wiki_cpt_prose.jsonl` 中的无标记双语外貌散文与真实多载体商品图混排写入 CPT（`doc_text_repeat == 1`）。")
            else:
                cpt_plan.append(f"当前缺少 Wiki 角色词条，需从版权方官网/台账补充「{entity_name}」核心角色设定与三视图后再灌入 CPT。")
        elif scope_subtrack in ("B1_specific_brand_trademark", "B3_specific_sports_university"):
            cpt_plan.append(f"以当前 {total_visuals} 张官方 Logo / 徽章图为核心视觉锚点，叠加多载体透视/刺绣/磨损合成样本，建立对「{entity_name}」标徽及字标的抗形变先验。")
        elif scope_subtrack == "B4_specific_celebrity_band_artist":
            cpt_plan.append("重点注入舞台海报、签名周边、演出服与专辑视觉图，结合演出文本传记消除普通人名重名。")
        else:
            cpt_plan.append("针对 3D 结构/外观专利，优先采集多视角（正面/侧面/爆炸图/透视图）实物参照图进入 CPT，单张正面平面 Logo 不足以学成几何边界。")

        if "generic_style_exclusion" in bnds or supports_derivative:
            sft_plan.append("配比「25% 原版正例 / 25% 可核验二创正例 / 30% 同画风原创强负例 / 20% 证据不足拒判」，强制执行“画风剥离 + 核心视觉特征组合验证”。")
        if "compatibility_exemption" in bnds:
            sft_plan.append("构造含 `suitable for / compatible with` 适配词的零标配件负例，防止把标题适配词误判为本体侵权。")
        if "subject_host_isolation" in bnds:
            sft_plan.append("构造“手机壳/周边本体 vs 宿主设备/模特身上标”宿主隔离负例，确保只审核心售卖商品。")
        if "common_word_disambiguation" in bnds:
            sft_plan.append("针对常见英文单词/地名/动物日常义构造纯语义强负例（无专属字体与徽记时必须判 `false`）。")
        if not sft_plan:
            sft_plan.append("严格遵循 `rule_grounded_audit_sft` 双模格式（7:3 Think-ON / Clean-Direct），绑定「仅见标题词但实图无标 → 判 false」以图覆文负例。")

    eval_plan.append(f"维持 `doc_family_overlap == 0` 与 `sft_overlap == 0`；当前本地参考图共计 {total_visuals} 张（其中角色立绘 {portrait_count} 张），评测时分拆 Closed-Set 与 Strict OOD 切片核验精准率与误杀率。")
    if "conservative_insufficient_evidence_abstain" in bnds or scope_subtrack in ("B4_specific_celebrity_band_artist", "A2_vertical_open_set_or_multi_entity"):
        eval_plan.append("增设低清裁切/无可靠出处切片，单独核验“证据不足时拒绝强猜（abstain）”指标。")

    return {
        "gate_status": gate_status,
        "gate_label": gate_label,
        "cpt_plan": cpt_plan,
        "sft_plan": sft_plan,
        "eval_plan": eval_plan,
    }


def _attach_inter_class_links(families: list[dict[str, Any]]) -> None:
    by_slug = {f["family_slug"]: f for f in families}
    broad_pool = [f for f in families if f["scope_track"] == "broad_domain"]
    subtrack_to_broad: dict[str, list[tuple[str, str]]] = {
        "B2_specific_anime_game_media_ip": [
            ("twizler", "同类涉及二创重绘/裁剪规避时的通用双图机制参考"),
            ("general_ip_model_nxy", "多动漫/角色视觉锚点通用判断基准"),
            ("infringementcards", "若衍生为卡牌/贴纸品类时的卡套豁免联动"),
        ],
        "B1_specific_brand_trademark": [
            ("brand_gemini_general", "同属品牌商标类的宿主隔离与材质一致性通用准则"),
            ("brand_goods_consistent_multi_img", "多图/多SKU场景品牌名单一致性校准"),
            ("logo_similar_judge", "Logo 视觉近似与山寨微改判别底座"),
        ],
        "B3_specific_sports_university": [
            ("sports_ball_general", "体育俱乐部/联盟/球星通用归因与地名消歧"),
            ("counterfeit_jerseys", "无标球衣条纹配色版型抄袭补充判定"),
            ("hemier_league", "北美主流体育联盟多队徽闭集参照"),
        ],
        "B4_specific_celebrity_band_artist": [
            ("band_music_general", "乐队/歌手与演出周边的跨实体召回约束"),
            ("merchtraffic", "艺人官方巡演授权周边判别模式对齐"),
            ("artist", "原创画师/艺术家人像版权边界参照"),
        ],
        "B5_specific_design_patent_product": [
            ("household", "家居及日用商品 3D 外观专利通用审核标准"),
            ("cars_automotive_general", "涉及工农业/汽配配件时的适配词豁免参考"),
            ("counterfeit_watch", "精密工业造型细节多维度比对参照"),
        ],
    }

    for f in families:
        slug = f["family_slug"]
        track = f["scope_track"]
        sub = f["scope_subtrack"]
        arch_set = set(f.get("archetypes") or [])

        # Peer families in same subtrack ranked by shared archetypes & risk
        peers_scored: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
        for other in families:
            if other["family_slug"] == slug or other["scope_track"] == "quarantined_excluded":
                continue
            if other["scope_track"] != track:
                continue
            same_sub = 1 if other["scope_subtrack"] == sub else 0
            shared_arch = len(arch_set & set(other.get("archetypes") or []))
            if not same_sub and shared_arch == 0:
                continue
            same_deriv = 1 if other["supports_derivative"] == f["supports_derivative"] else 0
            peers_scored.append(((same_sub, shared_arch, same_deriv), other))
        peers_scored.sort(key=lambda x: (-x[0][0], -x[0][1], -x[0][2], x[1]["family_slug"]))

        related_peers = [
            {
                "slug": other["family_slug"],
                "entity_name": other["entity_name"],
                "scope_subtrack": other["scope_subtrack"],
                "inter_class_risk": other["inter_class_risk"],
                "shared_archetypes": sorted(arch_set & set(other.get("archetypes") or [])),
            }
            for _, other in peers_scored[:6]
        ]

        linked_general: list[dict[str, Any]] = []
        governed_ips: list[dict[str, Any]] = []
        if track == "entity_specific":
            for b_slug, reason in subtrack_to_broad.get(sub, []):
                bf = by_slug.get(b_slug)
                if bf:
                    linked_general.append({"slug": b_slug, "entity_name": bf["entity_name"], "reason": reason})
            if f["supports_derivative"] and all(x["slug"] != "twizler" for x in linked_general):
                bf = by_slug.get("twizler")
                if bf:
                    linked_general.append({"slug": "twizler", "entity_name": bf["entity_name"], "reason": "该实体支持二创识别，与防规避对比机制强相关"})
        elif track == "broad_domain":
            # Reverse map: find specific IPs aligned with this general template
            target_subs = [sk for sk, pairs in subtrack_to_broad.items() if any(bs == slug for bs, _ in pairs)]
            for other in families:
                if other["scope_track"] != "entity_specific":
                    continue
                if other["scope_subtrack"] in target_subs or (arch_set & set(other.get("archetypes") or [])):
                    governed_ips.append({"slug": other["family_slug"], "entity_name": other["entity_name"], "scope_subtrack": other["scope_subtrack"]})
                    if len(governed_ips) >= 8:
                        break
            # Also list other broad peers in same subtrack if related_peers is short
            if len(related_peers) < 4:
                for bf in broad_pool:
                    if bf["family_slug"] != slug and all(p["slug"] != bf["family_slug"] for p in related_peers):
                        related_peers.append(
                            {
                                "slug": bf["family_slug"],
                                "entity_name": bf["entity_name"],
                                "scope_subtrack": bf["scope_subtrack"],
                                "inter_class_risk": bf["inter_class_risk"],
                                "shared_archetypes": sorted(arch_set & set(bf.get("archetypes") or [])),
                            }
                        )
                        if len(related_peers) >= 6:
                            break

        f["inter_class_links"] = {
            "related_peers": related_peers,
            "linked_general_templates": linked_general,
            "governed_specific_examples": governed_ips,
        }


def assemble_dashboard_payload(
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    taxonomy_path: Path = DEFAULT_TAXONOMY_PATH,
    enrichment_path: Path = DEFAULT_ENRICH_PATH,
    visual_audit_path: Path = DEFAULT_VISUAL_AUDIT_PATH,
    reviews_audited_path: Path = DEFAULT_REVIEWS_AUDITED_PATH,
    character_dossiers_path: Path = DEFAULT_CHARACTER_DOSSIERS_PATH,
    character_portraits_path: Path = DEFAULT_CHARACTER_PORTRAITS_PATH,
    embed_images: bool = True,
    include_prompt_bodies: bool = True,
) -> dict[str, Any]:
    """Loads all families, taxonomy/requirements, visual audit verdicts, and image previews."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_data = json.loads((templete_dir / "index.json").read_text(encoding="utf-8"))

    taxonomy_by_slug: dict[str, dict[str, Any]] = {}
    scope_track_counts: Counter[str] = Counter()
    scope_subtrack_counts: Counter[str] = Counter()
    if taxonomy_path.exists():
        tax_data = json.loads(taxonomy_path.read_text(encoding="utf-8"))
        for t in tax_data.get("families") or []:
            taxonomy_by_slug[str(t["family_slug"])] = t

    enrich_by_slug: dict[str, dict[str, Any]] = {}
    enrichment_status_counts: Counter[str] = Counter()
    for row in _load_jsonl(enrichment_path):
        enrich_by_slug[str(row["family_slug"])] = row

    visual_by_slug: dict[str, dict[str, Any]] = {}
    visual_status_counts: Counter[str] = Counter()
    for row in _load_jsonl(visual_audit_path):
        visual_by_slug[str(row["family_slug"])] = row

    image_data_uris: dict[str, str] = {}
    portraits_by_slug: dict[str, list[dict[str, Any]]] = {}
    portrait_by_char: dict[tuple[str, str], dict[str, Any]] = {}
    total_char_portraits = 0
    for prow in _load_jsonl(character_portraits_path):
        if prow.get("status") != "ok":
            continue
        p_slug = str(prow.get("family_slug") or "")
        p_char = str(prow.get("character_name") or "")
        resolved = _resolve_asset_file(str(prow.get("local_path") or ""), templete_dir)
        if not p_slug or not resolved:
            continue
        p_key, p_rel, p_abs = resolved
        if embed_images and p_key not in image_data_uris:
            image_data_uris[p_key] = _encode_image_data_uri(p_abs, max_edge=PORTRAIT_MAX_EDGE)
        p_item = {
            "character_name": p_char,
            "source": str(prow.get("source") or "fandom"),
            "preview_key": p_key,
            "preview_rel_path": p_rel,
            "width": int(prow.get("width") or 0),
            "height": int(prow.get("height") or 0),
        }
        portraits_by_slug.setdefault(p_slug, []).append(p_item)
        portrait_by_char[(p_slug, p_char)] = p_item
        total_char_portraits += 1

    chars_by_slug: dict[str, list[dict[str, Any]]] = {}
    total_char_dossiers = 0
    for row in _load_jsonl(character_dossiers_path):
        s_key = str(row["family_slug"])
        c_name = str(row.get("character_name") or "")
        lst = chars_by_slug.setdefault(s_key, [])
        p_match = portrait_by_char.get((s_key, c_name))
        if len(lst) < 12 or p_match is not None:
            if len(lst) >= 12 and p_match is not None:
                # Ensure sampled portrait characters stay visible even if beyond index 12
                replace_idx = next((i for i, existing in enumerate(lst) if not existing.get("portrait_key")), None)
                if replace_idx is not None:
                    lst.pop(replace_idx)
                    total_char_dossiers -= 1
                else:
                    continue
            lst.append(
                {
                    "character_name": c_name,
                    "source": row.get("source") or "",
                    "language": row.get("language") or "",
                    "source_url": row.get("source_url") or "",
                    "portrait_key": p_match["preview_key"] if p_match else "",
                    "portrait_rel": p_match["preview_rel_path"] if p_match else "",
                    "visual_anchors": list(row.get("visual_anchors_extracted") or [])[:6],
                    "visual_appearance": str(row.get("visual_appearance") or "")[:420],
                    "overview": str(row.get("overview") or "")[:320],
                }
            )
            total_char_dossiers += 1

    default_reviews: dict[str, Any] = {}
    if reviews_audited_path.exists():
        rev_doc = json.loads(reviews_audited_path.read_text(encoding="utf-8"))
        default_reviews = dict(rev_doc.get("reviews") or {})

    families_out: list[dict[str, Any]] = []
    archetype_family_counts: Counter[str] = Counter()
    resolved_images = total_char_portraits

    for entry in index_data["families"]:
        slug = str(entry["family_slug"])
        fam_dir = templete_dir / slug
        fam = json.loads((fam_dir / "family.json").read_text(encoding="utf-8"))
        raw_by_id = {int(r["id"]): r for r in _load_jsonl(fam_dir / "raw_records.jsonl")}

        for arch in fam.get("archetypes") or []:
            archetype_family_counts[arch] += 1

        enriched_members: list[dict[str, Any]] = []
        for m in fam.get("members") or []:
            mid = int(m["id"])
            raw = raw_by_id.get(mid, {})
            cleaned_text = str(m.get("cleaned_body") or raw.get("body") or raw.get("body_head") or "") if include_prompt_bodies else ""
            m_clean = {k: v for k, v in m.items() if include_prompt_bodies or k not in {"body", "body_head", "raw_body", "cleaned_body", "export_cleanups"}}
            enriched_members.append(
                {
                    **m_clean,
                    "version_key": str(m.get("version_key") or mid),
                    "cleaned_body": cleaned_text,
                    "export_cleanups_count": int(m.get("export_cleanups_count") or 0),
                }
            )

        vis_rec = visual_by_slug.get(slug) or {}
        vis_status = str(vis_rec.get("visual_audit_status") or "")
        vis_note = str(vis_rec.get("visual_audit_note") or "")
        if vis_status:
            visual_status_counts[vis_status] += 1
        rejected_keys = {str(p) for p in (vis_rec.get("rejected_image_paths") or [])}
        purge_all_wiki = vis_status == "rejected_mismatch_purged"

        cov = fam.get("assert_asset_coverage") or {}
        approved_out: list[dict[str, Any]] = []
        for item in cov.get("approved_matches") or []:
            previews: list[str] = []
            preview_keys: list[str] = []
            for img in item.get("images") or []:
                resolved = _resolve_asset_file(str(img), templete_dir)
                if resolved:
                    asset_key, rel, abs_path = resolved
                    if asset_key in rejected_keys or purge_all_wiki:
                        continue
                    previews.append(rel)
                    preview_keys.append(asset_key)
                    if embed_images and asset_key not in image_data_uris:
                        image_data_uris[asset_key] = _encode_image_data_uri(abs_path)
                    resolved_images += 1
            approved_out.append({**item, "preview_rel_paths": previews, "preview_keys": preview_keys})

        supplement_out: list[dict[str, Any]] = []
        for item in cov.get("supplement_matches") or []:
            resolved = _resolve_asset_file(str(item.get("local_path") or ""), templete_dir)
            rel: str | None = None
            asset_key_val: str | None = None
            if resolved:
                cand_key, cand_rel, abs_path = resolved
                if cand_key not in rejected_keys and not purge_all_wiki:
                    asset_key_val, rel = cand_key, cand_rel
                    if embed_images and asset_key_val not in image_data_uris:
                        image_data_uris[asset_key_val] = _encode_image_data_uri(abs_path)
                    resolved_images += 1
            supplement_out.append({**item, "preview_rel_path": rel, "preview_key": asset_key_val})

        tax_rec = taxonomy_by_slug.get(slug) or {}
        scope_track = str(tax_rec.get("scope_track") or "entity_specific")
        scope_subtrack = str(tax_rec.get("scope_subtrack") or "B1_specific_brand_trademark")
        scope_track_counts[scope_track] += 1
        scope_subtrack_counts[scope_subtrack] += 1

        enr_rec = enrich_by_slug.get(slug) or {}
        enr_status = str(enr_rec.get("enrichment_status") or "")
        if enr_status:
            enrichment_status_counts[enr_status] += 1
        enriched_matches: list[dict[str, Any]] = []
        if not purge_all_wiki:
            for asset in enr_rec.get("assets") or []:
                resolved = _resolve_asset_file(str(asset.get("local_path") or ""), templete_dir)
                if resolved:
                    asset_key_val, rel, abs_path = resolved
                    if asset_key_val in rejected_keys:
                        continue
                    if embed_images and asset_key_val not in image_data_uris:
                        image_data_uris[asset_key_val] = _encode_image_data_uri(abs_path)
                    resolved_images += 1
                    enriched_matches.append(
                        {
                            "preview_rel_path": rel,
                            "preview_key": asset_key_val,
                            "enrichment_status": enr_status,
                            "visual_audit_status": vis_status,
                            "publisher": asset.get("publisher") or "",
                            "license": asset.get("license") or "",
                            "width": asset.get("width"),
                            "height": asset.get("height"),
                            "source_page_url": asset.get("source_page_url") or "",
                        }
                    )

        sel_vkey = str(fam.get("selected_latest_version_key") or fam["selected_latest_id"])
        default_member = next((m for m in enriched_members if m["version_key"] == sel_vkey), enriched_members[0])
        wiki_sum = enr_rec.get("wiki_summary") or {}
        entity_name = _derive_entity_name(
            slug=slug,
            raw_display_name=fam["display_name"],
            scope_track=scope_track,
            wiki_title=str(wiki_sum.get("wiki_title") or ""),
            supplement_matches=supplement_out,
        )
        latest_audit = _build_latest_audit(default_member, fam.get("recommendations") or [])
        audit_req = tax_rec.get("audit_requirements") or {}
        fam_chars = chars_by_slug.get(slug) or []
        fam_portraits = portraits_by_slug.get(slug) or []
        approved_img_cnt = sum(len(x.get("preview_rel_paths") or []) for x in approved_out)
        supp_img_cnt = sum(1 for x in supplement_out if x.get("preview_rel_path"))
        enr_img_cnt = len(enriched_matches)
        training_advice = _build_training_advice(
            scope_track=scope_track,
            scope_subtrack=scope_subtrack,
            entity_name=entity_name,
            latest_audit=latest_audit,
            audit_req=audit_req,
            char_count=len(fam_chars),
            portrait_count=len(fam_portraits),
            asset_count=approved_img_cnt + supp_img_cnt + enr_img_cnt,
            supports_derivative=bool(fam["supports_derivative"]),
        )

        families_out.append(
            {
                "family_slug": slug,
                "display_name": fam["display_name"],
                "entity_name": entity_name,
                "member_count": fam["member_count"],
                "history_versions_count": max(0, len(enriched_members) - 1),
                "selected_latest_id": fam["selected_latest_id"],
                "selected_latest_version_key": sel_vkey,
                "selected_latest_title": fam["selected_latest_title"],
                "version_selection_confidence": fam["version_selection_confidence"],
                "version_selection_reason": fam["version_selection_reason"],
                "parallel_sub_scopes": bool(fam["parallel_sub_scopes"]),
                "total_export_cleanups": int(fam.get("total_export_cleanups") or 0),
                "archetypes": fam["archetypes"],
                "supports_derivative": bool(fam["supports_derivative"]),
                "inter_class_risk": fam["inter_class_risk"],
                "all_hygiene_flags": fam["all_hygiene_flags"],
                "recommendations": fam.get("recommendations") or [],
                "latest_audit": latest_audit,
                "training_advice": training_advice,
                "scope_track": scope_track,
                "scope_subtrack": scope_subtrack,
                "rights_holder_cardinality": tax_rec.get("rights_holder_cardinality") or "1",
                "classification_evidence": tax_rec.get("classification_evidence") or "",
                "audit_requirements": audit_req,
                "enrichment_status": enr_status,
                "visual_audit_status": vis_status,
                "visual_audit_note": vis_note,
                "wiki_summary": wiki_sum,
                "character_dossiers": fam_chars,
                "character_portraits": fam_portraits,
                "assert_asset_coverage": {
                    "coverage_status": cov.get("coverage_status", "no_assert_match"),
                    "approved_matches": approved_out,
                    "supplement_matches": supplement_out,
                    "enriched_matches": enriched_matches,
                    "backlog_matches": cov.get("backlog_matches") or [],
                },
                "members": enriched_members,
            }
        )

    _attach_inter_class_links(families_out)

    return {
        "schema": "assert_template_review_dashboard_v2",
        "public_redacted": not include_prompt_bodies,
        "generated_at": manifest.get("generated_at"),
        "total_raw_records": manifest.get("total_raw_records", manifest.get("total_raw_templates", 461)),
        "total_unpacked_versions": manifest.get("total_unpacked_versions", sum(f["member_count"] for f in families_out)),
        "total_families": len(families_out),
        "multi_member_families": manifest["multi_member_families"],
        "total_export_cleanups": manifest.get("total_export_cleanups", 0),
        "records_with_export_cleanups": manifest.get("records_with_export_cleanups", 0),
        "resolved_preview_images": resolved_images,
        "embedded_images_count": len(image_data_uris),
        "character_dossiers_count": total_char_dossiers,
        "character_portraits_count": total_char_portraits,
        "image_data_uris": image_data_uris,
        "default_reviews": default_reviews,
        "scope_track_counts": dict(scope_track_counts),
        "scope_subtrack_counts": dict(sorted(scope_subtrack_counts.items())),
        "enrichment_status_counts": dict(enrichment_status_counts),
        "visual_audit_counts": dict(visual_status_counts),
        "disposition_counts": manifest["disposition_counts"],
        "hygiene_flag_counts": manifest["hygiene_flag_counts"],
        "inter_class_risk_counts": manifest["inter_class_risk_counts"],
        "assert_coverage_counts": manifest["assert_coverage_counts"],
        "archetype_family_counts": dict(sorted(archetype_family_counts.items(), key=lambda x: (-x[1], x[0]))),
        "families": families_out,
    }


def _safe_json_for_script_tag(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return raw.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>审核模板画廊 · Assert Archive</title>
<style>
/* ============================================================
   Claude / Anthropic 编辑部纸感：暖纸底、衬线标题、赤陶强调、细描边
   ============================================================ */
:root{
  --serif:ui-serif,"New York","Iowan Old Style","Palatino","Palatino Linotype",
          "Songti SC","Noto Serif SC",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter",
         "PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,"JetBrains Mono",monospace;

  --bg:#F0EEE6;
  --bg-deep:#E6E2D6;
  --panel:#FBFAF6;
  --panel-2:#F5F2E9;
  --ink:#141413;
  --ink-2:#3A3A36;
  --muted:#6F6D64;
  --line:#E2DDD0;
  --line-2:#CFC9B8;
  --accent:#BE5A38;
  --accent-ink:#8F3E23;
  --accent-soft:#F4E7E0;
  --warn:#B47425;
  --warn-soft:#F7EFE1;
  --sage:#4E7A5B;
  --sage-soft:#EAF2EC;
  --crimson:#A83B32;
  --crimson-soft:#F6E6E4;
  --slate:#4A6B82;
  --slate-soft:#EAEFF3;
  --plum:#7A5585;
  --plum-soft:#F1EBF4;
  --chip:#ECE8DC;
  --code-bg:#F3F0E7;
  --shadow-1:0 1px 2px rgba(28,25,20,.045);
  --shadow-2:0 3px 8px rgba(28,25,20,.05),0 12px 28px rgba(28,25,20,.08);
  --shadow-3:0 8px 20px rgba(28,25,20,.08),0 28px 60px rgba(28,25,20,.14);
  --ease:cubic-bezier(.2,.7,.3,1);
  --gx:0px;
  --gy:0px;
}
html[data-theme="dark"]{
  --bg:#181715;
  --bg-deep:#11100F;
  --panel:#23221F;
  --panel-2:#2A2824;
  --ink:#F2EFE7;
  --ink-2:#D5D0C5;
  --muted:#9A968B;
  --line:#34322C;
  --line-2:#49453D;
  --accent:#E28B6B;
  --accent-ink:#F2AC91;
  --accent-soft:#352620;
  --warn:#DCA154;
  --warn-soft:#31271A;
  --sage:#78AD87;
  --sage-soft:#1D2A21;
  --crimson:#E07A70;
  --crimson-soft:#341E1C;
  --slate:#7CA3BD;
  --slate-soft:#1E272E;
  --plum:#B48CC0;
  --plum-soft:#2A2130;
  --chip:#2C2A25;
  --code-bg:#1D1C19;
  --shadow-1:0 1px 2px rgba(0,0,0,.45);
  --shadow-2:0 3px 8px rgba(0,0,0,.4),0 12px 28px rgba(0,0,0,.35);
  --shadow-3:0 8px 20px rgba(0,0,0,.45),0 28px 64px rgba(0,0,0,.55);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:var(--sans);font-size:15px;line-height:1.66;
  letter-spacing:.004em;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  font-variant-numeric:tabular-nums;
  transition:padding-left .3s var(--ease),background .35s var(--ease),color .35s var(--ease);
}
/* 背景层 1：纸面暖色渍 + 鼠标微视差 */
body::before{
  content:'';position:fixed;inset:-28px;z-index:-2;pointer-events:none;
  transform:translate3d(var(--gx),var(--gy),0);
  transition:transform .45s var(--ease);
  background:
    radial-gradient(760px 520px at 14% 4%,  rgba(190,150,105,.085), transparent 62%),
    radial-gradient(680px 460px at 86% 10%, rgba(175,160,130,.072), transparent 60%),
    radial-gradient(900px 620px at 52% 104%,rgba(150,130,100,.06), transparent 66%),
    radial-gradient(1200px 700px at 50% -12%, color-mix(in srgb,var(--panel) 55%,transparent), transparent 72%);
}
html[data-theme="dark"] body::before{
  background:
    radial-gradient(760px 520px at 14% 4%,  rgba(224,138,106,.05), transparent 62%),
    radial-gradient(680px 460px at 86% 10%, rgba(200,180,150,.035), transparent 60%),
    radial-gradient(900px 620px at 52% 104%,rgba(160,130,100,.035), transparent 66%);
}
/* 背景层 2：纸张纤维颗粒（内联 SVG，离线可用） */
body::after{
  content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;
  opacity:.4;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='p'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23p)' opacity='0.34'/%3E%3C/svg%3E");
  background-size:220px 220px;
}
html[data-theme="dark"] body::after{opacity:.28;mix-blend-mode:soft-light}
a{color:var(--accent-ink);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:2px}
button,input,select,textarea{font-family:inherit;color:inherit}

/* 温润细滚动条 */
#sidebar,.overlay,.md .tbl,.stoc,.prompt-pre{scrollbar-width:thin;scrollbar-color:var(--line-2) transparent}
#sidebar::-webkit-scrollbar,.overlay::-webkit-scrollbar,.md .tbl::-webkit-scrollbar,.prompt-pre::-webkit-scrollbar{width:7px;height:7px}
#sidebar::-webkit-scrollbar-thumb,.overlay::-webkit-scrollbar-thumb,.md .tbl::-webkit-scrollbar-thumb,.prompt-pre::-webkit-scrollbar-thumb{
  background:var(--line-2);border-radius:99px;border:2px solid transparent;background-clip:padding-box;
}
.stoc::-webkit-scrollbar{height:0}

/* ============ 顶栏 ============ */
header{
  position:sticky;top:0;z-index:30;
  background:color-mix(in srgb,var(--bg) 68%,transparent);
  backdrop-filter:blur(22px) saturate(1.3);
  -webkit-backdrop-filter:blur(22px) saturate(1.3);
  box-shadow:inset 0 1px 0 color-mix(in srgb,#fff 42%,transparent);
  border-bottom:1px solid transparent;
  transition:border-color .25s,box-shadow .25s,background .25s;
}
header.scrolled{
  background:color-mix(in srgb,var(--bg) 84%,transparent);
  border-bottom-color:color-mix(in srgb,var(--line) 85%,transparent);
  box-shadow:inset 0 1px 0 color-mix(in srgb,#fff 42%,transparent),
             0 10px 28px -20px rgba(28,25,20,.45);
}
html[data-theme="dark"] header{box-shadow:inset 0 1px 0 rgba(255,255,255,.05)}
#prog{
  position:absolute;left:0;bottom:-1px;height:2px;width:0;
  background:var(--accent);border-radius:0 2px 2px 0;transition:width .1s linear;
}
.hwrap{
  max-width:1280px;margin:0 auto;padding:20px 30px 14px;
  transition:padding .25s var(--ease);
}
header.scrolled .hwrap{padding:11px 30px 10px}
.htop{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.hbrand{display:flex;flex-direction:column;gap:1px}
.heyebrow{
  font-family:var(--mono);font-size:10px;letter-spacing:.14em;
  color:var(--muted);text-transform:uppercase;line-height:1.2;
  max-height:16px;overflow:hidden;opacity:.85;
  transition:max-height .22s var(--ease),opacity .2s,margin .22s;
}
header.scrolled .heyebrow{max-height:0;opacity:0}
h1{
  font-family:var(--serif);font-size:24px;margin:0;font-weight:600;
  letter-spacing:-.012em;color:var(--ink);line-height:1.2;
  transition:font-size .22s var(--ease);
}
header.scrolled h1{font-size:20px}
.count{
  color:var(--muted);font-size:12px;font-weight:500;
  padding:4px 10px;border-radius:99px;background:var(--chip);
  border:1px solid var(--line);display:inline-flex;align-items:center;gap:4px;
}
.count b{color:var(--ink);font-weight:650}
.spacer{flex:1}
.iconbtn{
  display:inline-flex;align-items:center;gap:6px;
  border:1px solid var(--line);background:color-mix(in srgb,var(--panel) 55%,transparent);
  color:var(--ink-2);border-radius:8px;padding:7px 11px;font-size:12.5px;
  cursor:pointer;font-family:inherit;font-weight:500;
  transition:border-color .18s,color .18s,background .18s,transform .12s;
}
.iconbtn svg{width:14px;height:14px;flex:none;opacity:.82}
.iconbtn:hover{border-color:var(--line-2);color:var(--ink);background:var(--panel)}
.iconbtn[aria-pressed="true"]{
  border-color:color-mix(in srgb,var(--accent) 45%,var(--line));
  background:var(--accent-soft);color:var(--accent-ink);
}
.iconbtn:active{transform:translateY(1px)}

.tools{
  display:flex;gap:8px;margin-top:15px;flex-wrap:wrap;align-items:center;
  transition:margin-top .22s var(--ease);
}
header.scrolled .tools{margin-top:10px}
.searchwrap{position:relative;flex:1 1 240px;min-width:220px;display:flex;align-items:center}
.search-ico{
  position:absolute;left:12px;width:15px;height:15px;color:var(--muted);
  pointer-events:none;transition:color .18s;
}
.searchwrap:focus-within .search-ico{color:var(--accent)}
input[type=search]{
  width:100%;padding:8px 56px 8px 36px;border-radius:9px;
  border:1px solid color-mix(in srgb,var(--line) 90%,transparent);
  background:color-mix(in srgb,var(--panel) 78%,transparent);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  color:var(--ink);font:inherit;font-size:13.5px;outline:none;
  box-shadow:inset 0 1px 0 color-mix(in srgb,#fff 40%,transparent);
  transition:border-color .18s,box-shadow .18s,background .18s;
}
input[type=search]::-webkit-search-cancel-button{display:none}
input[type=search]::placeholder{color:var(--muted)}
input[type=search]:focus{
  border-color:color-mix(in srgb,var(--accent) 55%,var(--line-2));
  background:var(--panel);
  box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 12%,transparent);
}
.search-kbd{
  position:absolute;right:10px;pointer-events:none;
  font-family:var(--mono);font-size:11px;color:var(--muted);
  border:1px solid var(--line);background:var(--chip);
  border-radius:5px;padding:1px 6px;line-height:1.4;
}
.search-clear{
  position:absolute;right:9px;border:none;background:var(--chip);color:var(--muted);
  width:20px;height:20px;border-radius:50%;cursor:pointer;display:grid;place-items:center;
  padding:0;font-size:12px;line-height:1;transition:background .15s,color .15s;
}
.search-clear[hidden]{display:none}
.search-clear:hover{background:var(--accent-soft);color:var(--accent-ink)}
select{
  padding:8px 10px;border-radius:9px;border:1px solid var(--line);
  background:var(--panel);color:var(--ink-2);font:inherit;font-size:12.5px;cursor:pointer;
  transition:border-color .18s;max-width:170px;
}
select:hover{border-color:var(--line-2)}
.toggle{
  display:flex;align-items:center;gap:6px;padding:8px 11px;border-radius:9px;
  border:1px solid var(--line);background:var(--panel);
  font-size:12.5px;color:var(--ink-2);cursor:pointer;user-select:none;
  transition:border-color .18s,background .18s,color .18s;
}
.toggle:hover{border-color:var(--line-2)}
.toggle:has(input:checked){border-color:var(--accent);background:var(--accent-soft);color:var(--accent-ink)}
.toggle input{margin:0;accent-color:var(--accent)}

.view-seg{
  display:inline-flex;border:1px solid var(--line);background:var(--panel);
  border-radius:9px;padding:2px;gap:2px;
}
.vbtn{
  border:none;background:transparent;color:var(--muted);
  border-radius:7px;width:30px;height:29px;display:grid;place-items:center;
  cursor:pointer;padding:0;transition:background .16s,color .16s;
}
.vbtn svg{width:15px;height:15px}
.vbtn:hover{color:var(--ink)}
.vbtn[aria-pressed="true"]{background:var(--accent-soft);color:var(--accent-ink)}

.chips{
  display:flex;gap:6px;flex-wrap:wrap;margin-top:11px;align-items:center;
  transition:margin-top .22s var(--ease);
}
header.scrolled .chips{margin-top:8px}
.chip{
  display:inline-flex;align-items:center;gap:6px;
  border:1px solid var(--line);background:color-mix(in srgb,var(--panel) 45%,transparent);
  color:var(--muted);border-radius:99px;padding:4px 11px;font-size:12px;font-weight:500;
  cursor:pointer;user-select:none;font-family:inherit;
  transition:border-color .18s,background .18s,color .18s,transform .12s;
}
.chip-dot{width:7px;height:7px;border-radius:50%;flex:none;opacity:.88}
.chip:hover{border-color:var(--line-2);color:var(--ink-2);background:var(--panel)}
.chip[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#FCFAF6}
.chip[aria-pressed=true] .chip-dot{background:#FCFAF6 !important;opacity:.95}
.chip .n{opacity:.6;font-variant-numeric:tabular-nums;font-size:11px}
.chip[aria-pressed=true] .n{opacity:.88}
.chip-clear{
  border-style:dashed;color:var(--accent-ink);background:transparent;
  border-color:color-mix(in srgb,var(--accent) 35%,var(--line));
}
.chip-clear:hover{background:var(--accent-soft);border-color:var(--accent)}

/* ============ 左侧审核概览侧栏（仿 gallery.html #topo） ============ */
#sidebar{
  position:fixed;left:0;top:0;bottom:0;width:356px;z-index:70;
  display:flex;flex-direction:column;gap:14px;
  padding:20px 18px 16px;overflow:auto;
  background:color-mix(in srgb,var(--panel) 80%,transparent);
  backdrop-filter:blur(22px) saturate(1.25);
  -webkit-backdrop-filter:blur(22px) saturate(1.25);
  border-right:1px solid var(--line);
  box-shadow:inset -1px 0 0 color-mix(in srgb,#fff 35%,transparent);
  transform:translateX(-100%);
  transition:transform .3s var(--ease);
}
body.side-open #sidebar{transform:none}
body.side-open{padding-left:356px}
.topo-head{display:flex;flex-direction:column;gap:3px}
.topo-title{font-family:var(--serif);font-size:18px;font-weight:600;letter-spacing:-.005em}
.topo-sub{font-size:11.5px;color:var(--muted)}
.side-box{
  display:flex;flex-direction:column;gap:6px;padding:11px 12px;
  border:1px solid var(--line);border-radius:10px;
  background:color-mix(in srgb,var(--panel-2) 68%,transparent);
}
.tt-h{
  font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--muted);margin-bottom:2px;font-weight:600;display:flex;justify-content:space-between;align-items:center;
}
.prog-meter{height:7px;background:var(--chip);border-radius:99px;overflow:hidden;border:1px solid var(--line)}
.prog-meter-fill{height:100%;background:var(--sage);border-radius:99px;transition:width .25s var(--ease)}
.bar-row{
  display:grid;grid-template-columns:minmax(0,1fr) 82px 34px;align-items:center;gap:8px;
  padding:3px 5px;border-radius:6px;cursor:pointer;border:1px solid transparent;
  background:none;text-align:left;font:inherit;color:var(--ink-2);width:100%;
  transition:background .14s,border-color .14s;
}
.bar-row:hover{background:var(--chip);border-color:var(--line)}
.bar-row[aria-pressed="true"]{background:var(--accent-soft);border-color:color-mix(in srgb,var(--accent) 45%,var(--line));color:var(--accent-ink)}
.bar-lbl{font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-trk{display:block;height:6px;background:var(--chip);border-radius:99px;overflow:hidden}
.bar-fill{display:block;height:100%;border-radius:99px;background:var(--accent)}
.bar-num{font-family:var(--mono);font-size:10.5px;color:var(--muted);text-align:right}
.topo-legend{display:flex;flex-wrap:wrap;gap:5px}
.tl-item{
  display:inline-flex;align-items:center;gap:5px;font-size:11px;color:var(--muted);
  background:transparent;border:1px solid var(--line);border-radius:99px;padding:3px 8px;
  cursor:pointer;font-family:inherit;transition:border-color .15s,background .15s,color .15s;
}
.tl-item:hover{border-color:var(--line-2);color:var(--ink);background:var(--panel)}
.tl-item[aria-pressed="true"]{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink)}
.tl-dot{width:7px;height:7px;border-radius:50%;flex:none}
.tt-row{
  display:flex;align-items:center;gap:7px;padding:5px 6px;border-radius:6px;
  border:1px solid transparent;background:none;cursor:pointer;text-align:left;
  font:inherit;color:var(--ink-2);transition:background .15s,border-color .15s;width:100%;
}
.tt-row:hover{background:var(--chip);border-color:var(--line)}
.tt-num{font:600 10px var(--mono);padding:2px 5px;border-radius:4px;flex:none;background:var(--crimson-soft);color:var(--crimson)}
.tt-t{flex:1;min-width:0;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tt-c{font:600 10px var(--mono);color:var(--muted);flex:none}
.topo-foot{
  display:flex;flex-direction:column;gap:7px;margin-top:auto;
  padding-top:12px;border-top:1px solid var(--line);
}
.foot-actions{display:flex;gap:6px;flex-wrap:wrap}
.topo-hint{font-size:10.5px;color:var(--muted);line-height:1.5}
@media(max-width:1180px){
  body.side-open{padding-left:0}
  body.side-open .overlay{left:0}
}

/* ============ 主栏目大分类 + 类目导航栏 + 高级筛选 + 品类图片抽样展区 ============ */
.pillar-bar{
  display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center;
}
.pillar-btn{
  display:inline-flex;align-items:center;gap:7px;
  border:1px solid var(--line);background:color-mix(in srgb,var(--panel) 72%,transparent);
  color:var(--ink-2);border-radius:10px;padding:7px 14px;font-size:13px;font-weight:600;
  cursor:pointer;transition:border-color .16s,background .16s,color .16s,box-shadow .16s;
}
.pillar-btn:hover{border-color:var(--line-2);background:var(--panel);color:var(--ink)}
.pillar-btn[aria-pressed="true"]{
  background:var(--ink);border-color:var(--ink);color:var(--bg);
  box-shadow:var(--shadow-1);
}
.pillar-btn .pn{
  font-family:var(--mono);font-size:11px;font-weight:600;opacity:.76;
  padding:1px 6px;border-radius:99px;background:color-mix(in srgb,var(--ink) 9%,transparent);
}
.pillar-btn[aria-pressed="true"] .pn{background:rgba(255,255,255,.22);color:inherit;opacity:1}
.pillar-btn.pillar-quar{margin-left:auto;font-weight:500;font-size:12px;padding:6px 11px;color:var(--muted)}
.pillar-btn.pillar-quar[aria-pressed="true"]{background:var(--crimson);border-color:var(--crimson);color:#FCFAF6}
.link-chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:6px}
.link-chip{
  display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:8px;
  border:1px solid var(--line);background:var(--panel);color:var(--ink-2);
  font-size:12px;font-weight:500;cursor:pointer;transition:border-color .15s,background .15s,color .15s;
}
.link-chip:hover{border-color:var(--accent);background:var(--accent-soft);color:var(--accent-ink)}
.hist-archive{
  margin-top:12px;border:1px dashed var(--line-2);border-radius:10px;padding:8px 12px;
  background:color-mix(in srgb,var(--panel-2) 60%,transparent);
}
.hist-archive>summary{
  cursor:pointer;font-size:12.5px;font-weight:600;color:var(--muted);user-select:none;
}
.cat-tabs{
  display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;padding-bottom:2px;
}
.cat-tab{
  display:inline-flex;align-items:center;gap:6px;
  border:1px solid var(--line);background:color-mix(in srgb,var(--panel) 65%,transparent);
  color:var(--ink-2);border-radius:9px;padding:6px 12px;font-size:12.5px;font-weight:500;
  cursor:pointer;transition:border-color .16s,background .16s,color .16s;
}
.cat-tab:hover{border-color:var(--line-2);background:var(--panel);color:var(--ink)}
.cat-tab[aria-pressed="true"]{
  background:var(--accent);border-color:var(--accent);color:#FCFAF6;font-weight:600;
}
.cat-tab .cn{
  font-family:var(--mono);font-size:11px;opacity:.72;
  padding:0 5px;border-radius:99px;background:color-mix(in srgb,var(--ink) 8%,transparent);
}
.cat-tab[aria-pressed="true"] .cn{background:rgba(255,255,255,.22);opacity:1}

.adv-details{position:relative}
.adv-details>summary{
  list-style:none;display:inline-flex;align-items:center;gap:5px;
  padding:8px 11px;border-radius:9px;border:1px solid var(--line);background:var(--panel);
  font-size:12.5px;color:var(--ink-2);cursor:pointer;user-select:none;
}
.adv-details>summary::-webkit-details-marker{display:none}
.adv-details[open]>summary{border-color:var(--accent);background:var(--accent-soft);color:var(--accent-ink)}
.adv-panel{
  position:absolute;right:0;top:calc(100% + 6px);z-index:45;min-width:300px;
  padding:12px;border-radius:11px;border:1px solid var(--line-2);
  background:var(--panel);box-shadow:var(--shadow-2);
  display:flex;flex-direction:column;gap:8px;
}
.adv-panel .adv-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.adv-panel select{max-width:none;flex:1 1 130px}

.showcase{margin:0 0 26px;display:flex;flex-direction:column;gap:14px}
.showcase[hidden]{display:none}
.showcase-top{
  display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;
  padding-bottom:8px;border-bottom:1px solid var(--line);
}
.showcase-top h2{font-family:var(--serif);font-size:19px;font-weight:600;margin:0;color:var(--ink)}
.showcase-sub{font-size:12.5px;color:var(--muted)}
.showcase-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
.sc-card{
  background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:14px 16px;box-shadow:var(--shadow-1);display:flex;flex-direction:column;gap:10px;
}
.sc-head{display:flex;align-items:center;justify-content:space-between;gap:8px}
.sc-title{font-family:var(--serif);font-size:15.5px;font-weight:600;color:var(--ink)}
.sc-desc{font-size:12px;color:var(--muted);line-height:1.45}
.sc-tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
@media(min-width:960px){.sc-tiles{grid-template-columns:repeat(6,minmax(0,1fr))}}
.stile{
  display:flex;flex-direction:column;gap:4px;border:1px solid var(--line);
  border-radius:8px;background:var(--panel-2);padding:5px;min-width:0;
  transition:border-color .16s,transform .14s;
}
.stile:hover{border-color:var(--accent);transform:translateY(-1px)}
.stile-img{
  height:74px;border-radius:6px;overflow:hidden;cursor:zoom-in;
  display:flex;align-items:center;justify-content:center;padding:4px;
  background-color:#faf8f3;
  background-image:
    linear-gradient(45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(-45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#e6e1d4 75%),
    linear-gradient(-45deg,transparent 75%,#e6e1d4 75%);
  background-size:10px 10px;background-position:0 0,0 5px,5px -5px,-5px 0;
}
.stile-img img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.stile-lbl{
  font-size:11px;color:var(--ink-2);font-weight:500;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;cursor:pointer;text-align:center;border:none;background:none;padding:1px 2px;
}
.stile-lbl:hover{color:var(--accent-ink);text-decoration:underline}

.cat-sec{display:flex;flex-direction:column;gap:12px;margin-bottom:28px}
.cat-sec-head{
  display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
  padding-bottom:7px;border-bottom:1px solid var(--line);
}
.cat-sec-head h2{font-family:var(--serif);font-size:18px;font-weight:600;margin:0;color:var(--ink)}
.cat-sec-cnt{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.cat-sec-desc{font-size:12.5px;color:var(--muted)}
.cat-sec-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(318px,1fr));gap:14px}
.grid.list-view .cat-sec-grid{grid-template-columns:1fr;gap:9px}

.char-card-row{display:flex;gap:12px;align-items:flex-start}
.char-portrait{
  width:76px;height:76px;flex:none;border-radius:8px;border:1px solid var(--line);padding:4px;
  cursor:zoom-in;display:flex;align-items:center;justify-content:center;
  background-color:#faf8f3;
  background-image:
    linear-gradient(45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(-45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#e6e1d4 75%),
    linear-gradient(-45deg,transparent 75%,#e6e1d4 75%);
  background-size:10px 10px;background-position:0 0,0 5px,5px -5px,-5px 0;
}
.char-portrait img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.char-body{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px}

/* ============ 卡片画廊 ============ */
main{max-width:1280px;margin:0 auto;padding:22px 30px 110px}
.grid{display:flex;flex-direction:column;gap:6px}
.grid.flat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(318px,1fr));gap:14px}
.grid.list-view.flat-grid{display:grid;grid-template-columns:1fr;gap:9px}

@keyframes cardIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes fadeOut{from{opacity:1}to{opacity:0}}
@keyframes sheetIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes sheetOut{to{opacity:0;transform:translateY(8px)}}

.card{
  --tc:var(--accent);
  position:relative;display:flex;flex-direction:column;gap:8px;
  padding:18px 19px 15px;border-radius:12px;
  background:var(--panel);
  background-image:linear-gradient(180deg,color-mix(in srgb,#fff 52%,transparent) 0%,transparent 46%);
  border:1px solid var(--line);
  box-shadow:var(--shadow-1), inset 0 1px 0 color-mix(in srgb,#fff 55%,transparent);
  cursor:pointer;overflow:hidden;
  transition:border-color .2s,box-shadow .25s,transform .25s var(--ease),background .2s;
  animation:cardIn .38s var(--ease) backwards;
  animation-delay:calc(var(--i,0) * 10ms);
}
.card::before{
  content:'';position:absolute;left:0;right:0;top:0;height:2.5px;
  background:var(--tc);opacity:.6;transition:opacity .2s,height .2s;
}
.card:hover{
  transform:translateY(-2px);
  border-color:color-mix(in srgb,var(--tc) 38%,var(--line-2));
  background:color-mix(in srgb,var(--panel) 62%,var(--panel-2));
  box-shadow:var(--shadow-2), inset 0 1px 0 color-mix(in srgb,#fff 70%,transparent);
}
.card:hover::before{opacity:1}
.card:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
html[data-theme="dark"] .card{background-image:linear-gradient(180deg,rgba(255,255,255,.04) 0%,transparent 58%)}
html[data-theme="dark"] .card:hover{background-image:linear-gradient(180deg,rgba(255,255,255,.065) 0%,transparent 58%)}

.chead{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.num{
  font-family:var(--mono);font-size:11px;font-weight:650;
  background:color-mix(in srgb,var(--tc) 14%,transparent);
  color:color-mix(in srgb,var(--tc) 78%,var(--ink));
  border:1px solid color-mix(in srgb,var(--tc) 25%,transparent);
  border-radius:6px;padding:3px 7px;min-width:36px;text-align:center;
  transition:background .18s,color .18s,border-color .18s;
}
.card:hover .num{background:var(--tc);border-color:var(--tc);color:#FCFAF6}
.kind{
  font-size:10.5px;color:var(--muted);border:1px solid var(--line);
  border-radius:5px;padding:2px 6px;font-weight:500;
}
.kind.kind-guide{border-style:dashed;opacity:.9;color:var(--plum);border-color:color-mix(in srgb,var(--plum) 35%,var(--line))}
.cident{
  font-family:var(--mono);font-size:10.5px;color:var(--muted);opacity:.78;
  max-width:128px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.date{margin-left:auto;font-size:11.5px;color:var(--muted);display:inline-flex;align-items:center;gap:5px}
.rev-pill{
  font-size:10.5px;padding:1px 6px;border-radius:99px;font-weight:600;
  border:1px solid var(--line);background:var(--chip);color:var(--ink-2);
}
.rev-pill.rev-approved{background:var(--sage-soft);color:var(--sage);border-color:color-mix(in srgb,var(--sage) 32%,var(--line))}
.rev-pill.rev-needs_fix{background:var(--warn-soft);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,var(--line))}
.rev-pill.rev-needs_asset{background:var(--plum-soft);color:var(--plum);border-color:color-mix(in srgb,var(--plum) 35%,var(--line))}
.rev-pill.rev-quarantined{background:var(--crimson-soft);color:var(--crimson);border-color:color-mix(in srgb,var(--crimson) 35%,var(--line))}

.ctitle-row{display:flex;align-items:flex-start;gap:10px;justify-content:space-between;margin-top:2px}
.ctitle-text{min-width:0;flex:1;display:flex;flex-direction:column;gap:2px}
.ctitle{
  font-family:var(--serif);font-size:16.5px;font-weight:600;
  line-height:1.35;letter-spacing:-.006em;color:var(--ink);
  text-wrap:balance;margin-top:0;
}
.card-thumbs{display:flex;gap:5px;flex:none;align-items:center}
.card-thumb{
  width:52px;height:52px;border-radius:8px;border:1px solid var(--line);padding:4px;
  cursor:zoom-in;flex:none;position:relative;overflow:hidden;
  display:flex;align-items:center;justify-content:center;
  background-color:#faf8f3;
  background-image:
    linear-gradient(45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(-45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#e6e1d4 75%),
    linear-gradient(-45deg,transparent 75%,#e6e1d4 75%);
  background-size:8px 8px;background-position:0 0,0 4px,4px -4px,-4px 0;
  transition:border-color .16s,transform .16s;
}
.card-thumb:hover{border-color:var(--accent);transform:scale(1.04)}
.card-thumb img{width:100%;height:100%;object-fit:contain;display:block}
.card-thumb-more{
  position:absolute;right:2px;bottom:2px;font-family:var(--mono);font-size:9px;font-weight:700;
  background:rgba(20,20,19,.72);color:#fff;border-radius:4px;padding:0 3px;line-height:1.35;
}
.czh{font-size:12.6px;color:var(--accent-ink);font-weight:500;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.csum{
  font-size:12.8px;color:var(--muted);line-height:1.62;text-wrap:pretty;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;
}
.cfoot{
  display:flex;align-items:center;justify-content:space-between;gap:8px;
  margin-top:auto;padding-top:9px;border-top:1px dashed color-mix(in srgb,var(--line) 75%,transparent);
}
.tags{display:flex;gap:5px;flex-wrap:wrap;min-width:0}
.tag{
  --ttc:var(--muted);
  display:inline-flex;align-items:center;gap:4px;
  font-size:11px;background:transparent;color:var(--muted);
  border:1px solid var(--line);border-radius:5px;padding:2px 7px;
  transition:border-color .18s,color .18s;
}
.tag-dot{width:5px;height:5px;border-radius:50%;background:var(--ttc);opacity:.85;flex:none}
.card:hover .tag{border-color:var(--line-2);color:var(--ink-2)}
.cmeta{
  display:inline-flex;align-items:center;gap:6px;flex:none;
  font-family:var(--mono);font-size:10.5px;color:var(--muted);
}
.cdeg{
  padding:1px 5px;border-radius:4px;background:var(--chip);
  border:1px solid var(--line);color:var(--ink-2);
}

/* 列表视图卡片布局 */
.grid.list-view .card{
  display:grid;grid-template-columns:auto minmax(0,1.7fr) minmax(0,1fr) auto;
  align-items:center;gap:14px;padding:12px 16px 12px 18px;border-radius:10px;
}
.grid.list-view .card::before{width:3px;height:auto;right:auto;bottom:0;top:0;left:0}
.grid.list-view .chead{flex-wrap:nowrap;gap:6px}
.grid.list-view .cident,.grid.list-view .date,.grid.list-view .csum{display:none}
.grid.list-view .lmain{min-width:0;display:flex;flex-direction:column;gap:2px}
.grid.list-view .ctitle-row{margin-top:0;align-items:center;gap:8px}
.grid.list-view .card-thumb{width:34px;height:34px;padding:2px;border-radius:6px}
.grid.list-view .card-thumb:nth-child(n+2){display:none}
.grid.list-view .ctitle{font-size:15px;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid.list-view .czh{font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid.list-view .cfoot{margin:0;padding:0;border:none;justify-content:flex-end;gap:10px}
.grid.list-view .tags{flex-wrap:nowrap;overflow:hidden}
.grid.list-view .ldate{font-size:11.5px;color:var(--muted);font-family:var(--mono);white-space:nowrap}
.grid:not(.list-view) .ldate{display:none}
.grid:not(.list-view) .lmain{display:contents}

.empty{
  grid-column:1/-1;text-align:center;padding:84px 20px;color:var(--muted);
  font-family:var(--serif);font-size:16px;border:1px dashed var(--line-2);
  border-radius:12px;background:color-mix(in srgb,var(--panel) 50%,transparent);
}

/* ============ 详情浮层 ============ */
.overlay{
  position:fixed;inset:0;z-index:60;display:none;overflow:auto;
  background:color-mix(in srgb,var(--bg-deep) 68%,transparent);
  backdrop-filter:blur(12px) saturate(.9);
  -webkit-backdrop-filter:blur(12px) saturate(.9);
}
.overlay.open{display:block;animation:fadeIn .22s var(--ease)}
body.side-open .overlay{left:356px}
.overlay.closing{animation:fadeOut .18s var(--ease) forwards}
.sheet{
  max-width:940px;margin:38px auto 96px;
  background:color-mix(in srgb,var(--panel) 95%,transparent);
  backdrop-filter:blur(26px) saturate(1.15);
  -webkit-backdrop-filter:blur(26px) saturate(1.15);
  border:1px solid color-mix(in srgb,var(--line) 92%,transparent);
  border-radius:14px;overflow:hidden;
  box-shadow:var(--shadow-3), inset 0 1px 0 color-mix(in srgb,#fff 60%,transparent);
  animation:sheetIn .28s var(--ease);
}
.overlay.closing .sheet{animation:sheetOut .18s var(--ease) forwards}
.shead{
  position:sticky;top:0;z-index:3;
  background:color-mix(in srgb,var(--panel) 80%,transparent);
  backdrop-filter:blur(18px) saturate(1.25);
  -webkit-backdrop-filter:blur(18px) saturate(1.25);
  border-bottom:1px solid color-mix(in srgb,var(--line) 88%,transparent);
  box-shadow:inset 0 1px 0 color-mix(in srgb,#fff 45%,transparent);
}
.shead-top{padding:16px 26px 13px;display:flex;gap:14px;align-items:flex-start}
.shead .meta{flex:1;min-width:0}
.shead h2{
  font-family:var(--serif);font-size:20px;margin:0 0 6px;
  line-height:1.34;font-weight:600;letter-spacing:-.006em;text-wrap:balance;color:var(--ink);
}
.shead .sub{font-size:12px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.sacts{display:flex;gap:6px;flex-shrink:0;align-items:center;flex-wrap:wrap}
.sacts .iconbtn{padding:5px 9px;font-size:11.5px}
.close{
  border:1px solid var(--line);background:transparent;color:var(--ink-2);
  border-radius:8px;width:32px;height:32px;cursor:pointer;display:grid;place-items:center;
  transition:border-color .18s,color .18s,background .18s;
}
.close svg{width:15px;height:15px}
.close:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
.sprog{position:absolute;left:0;bottom:-1px;height:2px;width:0;background:var(--accent);transition:width .08s linear}
.stoc{
  display:flex;gap:5px;overflow-x:auto;padding:9px 26px 11px;
  border-top:1px dashed color-mix(in srgb,var(--line) 65%,transparent);
}
.stoc-item{
  flex:none;border:1px solid var(--line);background:transparent;color:var(--muted);
  border-radius:99px;padding:3px 10px;font-size:11.5px;font-family:inherit;
  cursor:pointer;white-space:nowrap;transition:border-color .15s,color .15s,background .15s;
}
.stoc-item:hover{border-color:var(--line-2);color:var(--ink);background:var(--panel-2)}
.stoc-item.active{border-color:var(--accent);background:var(--accent-soft);color:var(--accent-ink);font-weight:600}
.sbody{padding:26px 34px 44px}

/* ============ 编辑部内容样式（仿 gallery.html .md） ============ */
.md{
  font-family:var(--sans);font-size:14.5px;line-height:1.75;
  max-width:82ch;margin:0 auto;overflow-wrap:break-word;color:var(--ink-2);
}
.md h2{
  font-family:var(--serif);color:var(--ink);line-height:1.32;
  letter-spacing:-.008em;margin:1.7em 0 .65em;font-weight:600;font-size:18.5px;
  padding-bottom:.35em;border-bottom:1px solid var(--line);
  position:relative;padding-left:.75em;scroll-margin-top:138px;
  display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;
}
.md h2:first-child{margin-top:0}
.md h2::before{
  content:'';position:absolute;left:0;top:.22em;bottom:.5em;width:3px;
  background:var(--accent);border-radius:2px;
}
.md blockquote{
  margin:1em 0;padding:.75em 1.15em;border-left:3px solid var(--accent);
  background:var(--accent-soft);color:var(--ink-2);border-radius:0 8px 8px 0;font-size:13.5px;
}
.md blockquote.bq-warn{border-left-color:var(--warn);background:var(--warn-soft)}
.md blockquote.bq-err{border-left-color:var(--crimson);background:var(--crimson-soft)}
.md blockquote.bq-tip{
  border-left-color:var(--accent);
  background:color-mix(in srgb,var(--accent-soft) 72%,var(--panel));
}
.md code{
  font-family:var(--mono);font-size:12.2px;line-height:1.55;
  background:var(--code-bg);padding:.14em .38em;border-radius:4px;
  color:var(--accent-ink);border:1px solid var(--line);
}
.md pre{
  background:var(--code-bg);border:1px solid var(--line);border-radius:9px;
  padding:15px 17px;overflow:auto;margin:1em 0;position:relative;
  max-height:420px;white-space:pre-wrap;word-break:break-word;
}
.md pre::before{
  content:attr(data-lang);position:absolute;right:58px;top:9px;
  font-family:var(--mono);font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);opacity:.6;
}
.copy-btn{
  position:absolute;right:9px;top:7px;border:1px solid var(--line);
  background:var(--panel);color:var(--muted);border-radius:6px;
  padding:2px 8px;font:500 10.5px var(--sans);cursor:pointer;
  transition:border-color .15s,color .15s,background .15s;
}
.copy-btn:hover{border-color:var(--line-2);color:var(--ink)}
.copy-btn.copied{border-color:var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
.md pre code{background:none;padding:0;border:none;color:var(--ink);font-size:12.4px;line-height:1.68}
mark.err-tok{
  background:var(--crimson-soft);color:var(--crimson);
  border:1px solid color-mix(in srgb,var(--crimson) 35%,var(--line));
  border-radius:3px;padding:0 3px;font-weight:700;
}
.md .tbl{
  margin:1em 0;border:1px solid var(--line);border-radius:9px;
  overflow:auto;max-height:60vh;background:var(--panel);
}
.md table{border-collapse:collapse;width:100%;margin:0;font-size:12.8px;display:table}
.md thead th{
  position:sticky;top:0;z-index:1;background:var(--chip);
  font-weight:600;color:var(--ink);white-space:nowrap;border-bottom:1px solid var(--line-2);
}
.md th,.md td{padding:8px 11px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
.md tr:last-child td{border-bottom:none}
.md tbody tr:nth-child(even) td{background:color-mix(in srgb,var(--panel-2) 55%,transparent)}
.md tbody tr:hover td{background:color-mix(in srgb,var(--accent-soft) 50%,transparent)}

/* 人工复核面板 */
.review-box{
  border:1px solid var(--line);background:var(--panel-2);border-radius:10px;
  padding:12px 14px;display:flex;flex-direction:column;gap:9px;
}
.review-btns{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.rev-btn{
  border:1px solid var(--line);background:var(--panel);color:var(--ink-2);
  padding:5px 11px;border-radius:99px;font-size:12px;cursor:pointer;font-weight:500;
  transition:all .15s;
}
.rev-btn:hover{border-color:var(--line-2);color:var(--ink)}
.rev-btn.on-approved{background:var(--sage-soft);border-color:var(--sage);color:var(--sage);font-weight:700}
.rev-btn.on-needs_fix{background:var(--warn-soft);border-color:var(--warn);color:var(--warn);font-weight:700}
.rev-btn.on-needs_asset{background:var(--plum-soft);border-color:var(--plum);color:var(--plum);font-weight:700}
.rev-btn.on-quarantined{background:var(--crimson-soft);border-color:var(--crimson);color:var(--crimson);font-weight:700}
.review-note{
  width:100%;border:1px solid var(--line);background:var(--panel);border-radius:8px;
  padding:8px 10px;font-size:13px;resize:vertical;min-height:48px;outline:none;color:var(--ink);
}
.review-note:focus{border-color:var(--accent)}

/* 版本标签与并排对照 */
.ver-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.ver-tab{
  border:1px solid var(--line);background:var(--panel-2);color:var(--ink-2);
  padding:5px 10px;border-radius:8px;font-size:12px;cursor:pointer;
  display:inline-flex;align-items:center;gap:5px;transition:all .15s;
}
.ver-tab:hover{border-color:var(--line-2)}
.ver-tab.active{background:var(--accent);color:#FCFAF6;border-color:var(--accent)}
.ver-tab.is-bad{border-style:dashed;border-color:color-mix(in srgb,var(--crimson) 50%,var(--line))}
.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.compare-col{
  border:1px solid var(--line);border-radius:10px;padding:12px;
  background:color-mix(in srgb,var(--panel-2) 45%,var(--panel));min-width:0;
}
.meta-kv{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;margin-top:8px}
.badge{
  display:inline-flex;align-items:center;gap:4px;padding:2px 7px;border-radius:5px;
  font-size:11px;font-weight:500;border:1px solid var(--line);background:var(--panel-2);color:var(--ink-2);
}
.badge-red{background:var(--crimson-soft);color:var(--crimson);border-color:color-mix(in srgb,var(--crimson) 35%,var(--line))}
.badge-warn{background:var(--warn-soft);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,var(--line))}
.badge-sage{background:var(--sage-soft);color:var(--sage);border-color:color-mix(in srgb,var(--sage) 35%,var(--line))}
.badge-accent{background:var(--accent-soft);color:var(--accent-ink);border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}
.badge-plum{background:var(--plum-soft);color:var(--plum);border-color:color-mix(in srgb,var(--plum) 35%,var(--line))}

/* Assert 参考图棋盘格卡片 */
.asset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(188px,1fr));gap:12px;margin-top:10px}
.asset-card{
  border:1px solid var(--line);border-radius:10px;overflow:hidden;
  background:var(--panel-2);display:flex;flex-direction:column;
}
.checkerboard{
  height:142px;display:flex;align-items:center;justify-content:center;padding:10px;cursor:zoom-in;
  background-color:#faf8f3;
  background-image:
    linear-gradient(45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(-45deg,#e6e1d4 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#e6e1d4 75%),
    linear-gradient(-45deg,transparent 75%,#e6e1d4 75%);
  background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0;
}
html[data-theme="dark"] .checkerboard,
html[data-theme="dark"] .card-thumb,
html[data-theme="dark"] .stile-img,
html[data-theme="dark"] .char-portrait{
  background-color:#d8d3c6;
  background-image:
    linear-gradient(45deg,#c5bfb0 25%,transparent 25%),
    linear-gradient(-45deg,#c5bfb0 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#c5bfb0 75%),
    linear-gradient(-45deg,transparent 75%,#c5bfb0 75%);
}
.checkerboard img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.asset-info{padding:8px 10px;font-size:11.5px;display:flex;flex-direction:column;gap:3px}
.asset-strip{
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  padding:10px 12px;margin:0 0 18px;border:1px solid var(--line);
  border-radius:10px;background:var(--panel-2);
}
.asset-strip-label{font-size:12px;color:var(--muted);font-weight:600;margin-right:4px}
.asset-strip-item{
  width:68px;height:68px;padding:6px;border-radius:8px;border:1px solid var(--line);
  flex:none;cursor:zoom-in;transition:border-color .16s,transform .16s;
}
.asset-strip-item:hover{border-color:var(--accent);transform:scale(1.04)}
.img-fallback{font-size:10.5px;color:var(--muted);text-align:center;line-height:1.3;padding:4px}

/* 底部上一族 / 下一族导航 */
.snav{
  max-width:82ch;margin:26px auto 0;padding-top:18px;border-top:1px solid var(--line);
  display:grid;grid-template-columns:1fr 1fr;gap:12px;
}
.snav-btn{
  display:flex;flex-direction:column;gap:3px;padding:11px 14px;border-radius:10px;
  border:1px solid var(--line);background:var(--panel-2);color:var(--ink-2);
  cursor:pointer;text-align:left;font-family:inherit;min-width:0;
  transition:border-color .18s,background .18s,transform .15s;
}
.snav-btn.next{text-align:right;align-items:flex-end}
.snav-btn:hover{border-color:var(--accent);background:var(--panel);transform:translateY(-1px)}
.snav-dir{font-size:11px;font-family:var(--mono);color:var(--accent-ink)}
.snav-t{font-size:12.5px;font-weight:600;color:var(--ink);width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* 灯箱 & 回顶部 */
.modal{
  position:fixed;inset:0;z-index:90;background:color-mix(in srgb,var(--bg-deep) 78%,transparent);
  backdrop-filter:blur(10px);display:none;align-items:center;justify-content:center;padding:24px;
}
.modal.open{display:flex;animation:fadeIn .18s var(--ease)}
.modal-card{
  background:var(--panel);border:1px solid var(--line-2);border-radius:14px;
  min-width:min(440px,90vw);max-width:90vw;max-height:90vh;padding:16px;
  display:flex;flex-direction:column;gap:10px;overflow:hidden;
  box-shadow:var(--shadow-3);
}
.modal-img-wrap{
  height:auto;min-height:220px;max-height:70vh;width:100%;
  display:flex;align-items:center;justify-content:center;
  padding:20px;border-radius:10px;border:1px solid var(--line);
  overflow:hidden;cursor:default;flex:1 1 auto;
}
.modal-img-wrap img{
  max-width:min(78vw,780px);max-height:62vh;width:auto;height:auto;
  object-fit:contain;display:block;
}

#toTop{
  position:fixed;right:28px;bottom:28px;z-index:40;
  width:40px;height:40px;border-radius:10px;border:1px solid var(--line);
  background:color-mix(in srgb,var(--panel) 76%,transparent);
  backdrop-filter:blur(16px) saturate(1.25);
  color:var(--ink-2);cursor:pointer;display:grid;place-items:center;
  box-shadow:var(--shadow-2), inset 0 1px 0 color-mix(in srgb,#fff 50%,transparent);
  opacity:0;transform:translateY(8px);pointer-events:none;
  transition:opacity .22s,transform .22s,border-color .18s,color .18s;
}
#toTop svg{width:16px;height:16px}
#toTop.show{opacity:1;transform:none;pointer-events:auto}
#toTop:hover{border-color:var(--accent);color:var(--accent)}

@media(max-width:760px){
  .grid.list-view .card{grid-template-columns:auto minmax(0,1fr)}
  .grid.list-view .cfoot{grid-column:1 / -1;justify-content:flex-start}
  .compare-grid{grid-template-columns:1fr}
}
@media(max-width:600px){
  .hwrap,main{padding-left:16px;padding-right:16px}
  header.scrolled .hwrap{padding-left:16px;padding-right:16px}
  .grid{grid-template-columns:1fr}
  .sheet{margin:0;border-radius:0;min-height:100vh}
  .shead-top,.stoc{padding-left:18px;padding-right:18px}
  .sbody{padding:20px 18px 48px}
  .snav{grid-template-columns:1fr}
  h1{font-size:21px}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.001ms !important;animation-delay:0ms !important;
    transition-duration:.001ms !important;scroll-behavior:auto !important}
}
</style>
</head>
<body>
<header id="top">
  <div id="prog"></div>
  <div class="hwrap">
    <div class="htop">
      <div class="hbrand">
        <div class="heyebrow">ASSERT · IP VISUAL &amp; AUDIT ARCHIVE</div>
        <h1>审核模板与参考图画廊</h1>
      </div>
      <span class="count" id="count"></span>
      <span class="spacer"></span>
      <button class="iconbtn" id="showcaseToggle" title="展开或收起各品类抓爬图片抽样展区" aria-pressed="true">抽样展区</button>
      <button class="iconbtn" id="sideToggle" title="展开/收起审计统计概览（快捷键 G）">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="4" cy="4" r="1.8"/><circle cx="12" cy="4" r="1.8"/><circle cx="8" cy="12" r="1.8"/><path d="M5.6 5.2l1.6 5.2M10.4 5.2l-1.6 5.2M5.8 4h4.4"/></svg>
        统计概览
      </button>
      <button class="iconbtn" id="exportCsvBtn" title="导出当前筛选结果为 CSV">导出 CSV</button>
      <button class="iconbtn" id="themeBtn" title="切换明暗主题">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="8" cy="8" r="3.2"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M12.6 3.4l-1.1 1.1M4.5 11.5l-1.1 1.1"/></svg>
        明暗
      </button>
    </div>

    <div class="pillar-bar" id="pillarTabs" role="tablist" aria-label="主栏目切换"></div>
    <div class="cat-tabs" id="catTabs" role="tablist" aria-label="子品类分类"></div>

    <div class="tools">
      <div class="searchwrap">
        <svg class="search-ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/></svg>
        <input type="search" id="q" placeholder="搜索品牌 / IP / 角色名（如 Rem、Kirby、Nike）…" autocomplete="off" spellcheck="false">
        <button type="button" class="search-clear" id="qClear" hidden aria-label="清空搜索">✕</button>
        <kbd class="search-kbd" id="qKbd">/</kbd>
      </div>
      <label class="toggle"><input type="checkbox" id="chk-hasimg"> 仅看有图</label>
      <label class="toggle"><input type="checkbox" id="chk-haschar"> 仅含角色立绘</label>
      <select id="f-rev" title="按人工复核筛选">
        <option value="">复核：全部</option>
        <option value="unreviewed">未复核</option>
        <option value="approved">已通过</option>
        <option value="needs_fix">需修模板</option>
        <option value="needs_asset">需补标准图</option>
        <option value="quarantined">隔离废弃</option>
      </select>
      <select id="sort" title="排序方式">
        <option value="images-desc">有图优先</option>
        <option value="defects-desc">缺陷数 ↓</option>
        <option value="risk-desc">类间风险 ↓</option>
        <option value="members-desc">版本数 ↓</option>
        <option value="id-asc">主版 ID ↑</option>
        <option value="slug-asc">目录名 A-Z</option>
      </select>
      <details class="adv-details" id="advDetails">
        <summary>高级筛选</summary>
        <div class="adv-panel">
          <div class="adv-row">
            <select id="f-track" title="按广域/特定对象分轨筛选"></select>
            <select id="f-risk" title="按类间风险筛选"></select>
            <select id="f-cov" title="按 Assert 图库覆盖筛选"></select>
          </div>
          <div class="adv-row">
            <label class="toggle"><input type="checkbox" id="chk-deriv"> 仅含二创</label>
            <label class="toggle"><input type="checkbox" id="chk-multi"> 仅多版本</label>
            <label class="toggle"><input type="checkbox" id="chk-defect"> 仅存缺陷</label>
            <button type="button" class="iconbtn" id="btnResetFilters" style="margin-left:auto;">清空筛选</button>
          </div>
        </div>
      </details>
      <div class="view-seg" role="group" aria-label="视图模式">
        <button type="button" class="vbtn" data-view="grid" aria-pressed="true" title="网格卡片视图">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="2.2" y="2.2" width="4.6" height="4.6" rx="1"/><rect x="9.2" y="2.2" width="4.6" height="4.6" rx="1"/><rect x="2.2" y="9.2" width="4.6" height="4.6" rx="1"/><rect x="9.2" y="9.2" width="4.6" height="4.6" rx="1"/></svg>
        </button>
        <button type="button" class="vbtn" data-view="list" aria-pressed="false" title="紧凑列表视图">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2.5 4h11M2.5 8h11M2.5 12h11"/></svg>
        </button>
      </div>
    </div>
    <div class="chips" id="chips"></div>
  </div>
</header>

<aside id="sidebar" aria-label="审核概览与筛选统计">
  <div class="topo-head">
    <div class="topo-title">当前工作台统计概览</div>
    <div class="topo-sub" id="sideStats">加载中…</div>
  </div>

  <div class="side-box" id="sideProgress"></div>
  <div class="side-box" id="sideFlags"></div>
  <div class="side-box" id="sideCov"></div>
  <div class="side-box" id="sideGate"></div>
  <div class="side-box" id="sidePasteBugs"></div>

  <div class="topo-foot">
    <div class="foot-actions">
      <button type="button" class="iconbtn" id="btnExportRev">导出复核 JSON</button>
      <button type="button" class="iconbtn" id="btnImportRev">导入复核 JSON</button>
      <button type="button" class="iconbtn" id="btnResetDefaultRev" title="清除本地改动并恢复全量预审结默认结果">恢复默认审结</button>
      <input type="file" id="importFile" accept=".json" style="display:none">
    </div>
    <span class="topo-hint">仅按最新有效主版、当前真实图库与 CPT/SFT 门控实时汇总 · 按 <code>G</code> 收起/展开侧栏</span>
  </div>
</aside>

<main>
  <section class="showcase" id="showcase"></section>
  <div class="grid" id="grid"></div>
</main>

<div class="overlay" id="overlay"><div class="sheet" id="sheet"></div></div>

<div class="modal" id="lightbox">
  <div class="modal-card">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
      <strong id="lb-title" style="font-family:var(--serif);font-size:15px;">图片预览</strong>
      <button class="iconbtn" id="lb-close">关闭 (Esc)</button>
    </div>
    <div class="modal-img-wrap checkerboard"><img id="lb-img" src="" alt="reference"></div>
    <div id="lb-meta" style="font-size:12px;color:var(--muted);font-family:var(--mono);word-break:break-all;line-height:1.45;"></div>
  </div>
</div>

<button id="toTop" title="回到顶部" aria-label="回到顶部">
  <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 13V3M3.5 7.2L8 2.8l4.5 4.4"/></svg>
</button>

<script id="audit-data" type="application/json">__AUDIT_DATA_JSON__</script>
<script>
(function () {
  "use strict";

  const DATA = JSON.parse(document.getElementById("audit-data").textContent);
  const FAMILIES = DATA.families;
  const FAM_BY_SLUG = new Map(FAMILIES.map(f => [f.family_slug, f]));
  const REVIEW_KEY = "assert_template_review_v1";
  const THEME_KEY = "assert_template_theme_v1";
  const VIEW_KEY = "assert_template_view_v1";
  const SIDE_KEY = "assert_template_side_v1";

  const DISP_LABEL = {
    active_ip: "有效 IP 模板",
    route_auxiliary_non_ip: "辅助/非视觉 IP",
    quarantine_paste_bug: "跨实体错贴隔离",
    quarantine_test_junk: "测试垃圾隔离",
    needs_body_completion: "空壳待补全",
  };
  const RISK_LABEL = {
    high: "高风险",
    medium: "中风险",
    low: "低风险",
    blocked_hygiene: "卫生阻塞",
  };
  const RISK_RANK = { high: 4, medium: 3, low: 2, blocked_hygiene: 1 };
  const RISK_COLOR = {
    high: "#BE5A38",
    medium: "#B47425",
    low: "#4E7A5B",
    blocked_hygiene: "#A83B32",
  };
  const COV_LABEL = {
    approved_in_assert: "Assert 已批准",
    supplement_asset_available_pending_approval: "补充图待批",
    backlog_needs_review: "1119 待办",
    no_assert_match: "暂无匹配",
    not_applicable_non_ip_or_test: "非IP/测试",
  };
  const REV_LABEL = {
    approved: "已通过",
    needs_fix: "需修模板",
    needs_asset: "需补标准图",
    quarantined: "隔离废弃",
  };
  const FLAG_LABEL = {
    missing_exclusion_clause: "缺反向排除条款",
    rel_metadata_mismatch: "rel 误绑",
    underspecified_rubric: "判据过笼统",
    broken_json_schema: "JSON 契约损坏",
    typo_or_logic_defect: "错别字/逻辑错误",
    weak_anchor_or_escape_hatch: "主观逃生舱兜底",
    style_only_trigger_risk: "唯画风触发风险",
    cross_entity_paste_bug: "跨实体错贴",
    empty_placeholder_variable: "空占位符",
    duplicate_role_header: "角色段重复",
    empty_or_trivial_body: "空壳正文",
  };
  const ARCH_LABEL = {
    anime_derivative_two_step: "动漫二创两步法",
    brand_logo_trademark: "品牌商标/图形",
    design_patent_trade_dress: "外观专利/装潢",
    common_word_disambiguation: "常见词/字母消歧",
    subject_host_isolation: "主体与宿主隔离",
    auto_parts_compatibility_obfuscation: "汽配适配/涂抹",
    sports_collegiate_celebrity: "体育/高校/名人",
    image_title_conflict: "图文冲突优先",
    boolean_rule_reverse_elim: "布尔/反向剔除",
    multi_image_open_set: "多图/开放集",
    fuzzy_ocr_deformation: "OCR 遮挡变形",
    non_ip_auxiliary: "非 IP 辅助治理",
  };
  const ARCH_COLOR = {
    anime_derivative_two_step: "#BE5A38",
    brand_logo_trademark: "#4A6B82",
    design_patent_trade_dress: "#7A5585",
    common_word_disambiguation: "#B47425",
    subject_host_isolation: "#4E7A5B",
    auto_parts_compatibility_obfuscation: "#8F3E23",
    sports_collegiate_celebrity: "#4A6B82",
    image_title_conflict: "#B47425",
    boolean_rule_reverse_elim: "#6F6D64",
    multi_image_open_set: "#7A5585",
    fuzzy_ocr_deformation: "#A83B32",
    non_ip_auxiliary: "#6F6D64",
  };

  const TRACK_LABEL = {
    broad_domain: "广域识别 (Track A)",
    entity_specific: "特定对象 (Track B)",
    quarantined_excluded: "隔离异常 (Track Q)",
  };
  const SUBTRACK_LABEL = {
    A1_open_set_cross_domain_ip: "A1 跨域开放集",
    A2_vertical_open_set_or_multi_entity: "A2 垂直多实体",
    A3_pairwise_visual_mechanism: "A3 双图对比防规避",
    A4_auxiliary_governance_workflow: "A4 辅助合规流",
    B1_specific_brand_trademark: "B1 特定品牌/商标",
    B2_specific_anime_game_media_ip: "B2 特定动漫/游戏IP",
    B3_specific_sports_university: "B3 特定体育/高校",
    B4_specific_celebrity_band_artist: "B4 特定名人/乐队",
    B5_specific_design_patent_product: "B5 特定外观专利",
    Q1_test_junk: "Q1 测试废案",
    Q2_cross_entity_paste_bug: "Q2 错贴Bug",
  };
  const CUE_LABEL = {
    logo_wordmark: "Logo/文字标",
    character_mascot_likeness: "角色/吉祥物",
    derivative_fanart_style: "二创/重绘边界",
    "3d_product_geometry_patent": "3D结构/专利几何",
    trade_dress_pattern_packaging: "老花/装潢配色",
    jersey_crest_colors: "队徽/球衣配色",
    human_portrait_celebrity: "真人肖像/舞台",
    ocr_deformed_or_obfuscated_text: "形变/遮挡OCR",
    watermark_or_crop: "水印/局部裁切",
    document_or_webpage_screenshot: "凭证/网页截图",
  };
  const BND_LABEL = {
    subject_host_isolation: "主体/宿主隔离",
    material_consistency_check: "材质一致性",
    compatibility_exemption: "适配词豁免",
    common_word_disambiguation: "日常词消歧",
    generic_style_exclusion: "纯画风排除",
    reverse_elimination_fast_reject: "反向剔除免审",
    boolean_compound_logic: "布尔组合求值",
    conservative_insufficient_evidence_abstain: "证据不足拒判",
  };

  const SPECIFIC_CATS = [
    { key: "B2_specific_anime_game_media_ip", label: "动漫 / 游戏 IP", desc: "角色造型、吉祥物外观、正版作品与二创同人边界（含多源 Wiki 设定与角色立绘）" },
    { key: "B1_specific_brand_trademark", label: "品牌 / 商标", desc: "注册品牌 Logo、文字商标（Wordmark）与假冒标识审核" },
    { key: "B3_specific_sports_university", label: "体育 / 高校", desc: "职业联盟、俱乐部队徽、大学校徽与官方应援衍生品" },
    { key: "B4_specific_celebrity_band_artist", label: "名人 / 乐队", desc: "音乐人、乐队视觉标识、舞台肖像与个人品牌版权" },
    { key: "B5_specific_design_patent_product", label: "外观专利", desc: "3D 产品几何结构、外观设计专利与特定装潢造型" },
  ];
  const BROAD_CATS = [
    { key: "A1_open_set_cross_domain_ip", label: "A1 跨域开放集", desc: "不绑定单一品牌，聚焦售卖主体锁定、宿主隔离、材质一致性与图搜归因" },
    { key: "A2_vertical_open_set_or_multi_entity", label: "A2 垂直多实体", desc: "汽车/名表/球衣/卡牌/怀旧游戏机/K-Pop 闭集名单边界与品类前置豁免" },
    { key: "A3_pairwise_visual_mechanism", label: "A3 双图防规避", desc: "母本图 vs 待审图对比，拦截 AI 二创重绘、裁剪与镜像规避" },
    { key: "A4_auxiliary_governance_workflow", label: "A4 辅助合规治理", desc: "发票凭证、黑词风控、TRO 诉讼节点与错例反馈运维工作流" },
  ];
  const QUAR_CATS = [
    { key: "Q2_cross_entity_paste_bug", label: "Q2 跨实体错贴", desc: "标题与正文检测实体互相矛盾，已隔离禁止训练" },
    { key: "Q1_test_junk", label: "Q1 测试废案", desc: "历史联调测试记录，仅供归档排查" },
  ];
  const ALL_CATS = [...SPECIFIC_CATS, ...BROAD_CATS, ...QUAR_CATS];
  const CAT_META = new Map(ALL_CATS.map(c => [c.key, c]));
  function getPillarCats(pillar) {
    if (pillar === "broad_domain") return BROAD_CATS;
    if (pillar === "quarantined_excluded") return QUAR_CATS;
    return SPECIFIC_CATS;
  }
  function getFamName(f) {
    return (f && (f.entity_name || f.display_name)) || "";
  }
  function getFamCat(f) {
    return f.scope_subtrack || (f.scope_track === "broad_domain" ? "A1_open_set_cross_domain_ip" : f.scope_track === "quarantined_excluded" ? "Q1_test_junk" : "B1_specific_brand_trademark");
  }

  let reviews = loadReviews();
  let state = {
    q: "",
    pillar: "entity_specific",
    cat: "all",
    track: "",
    risk: "",
    cov: "",
    rev: "",
    flag: "",
    arch: "",
    gate: "",
    visGroup: "",
    disp: "",
    hasImg: false,
    hasChar: false,
    showShowcase: true,
    deriv: false,
    multi: false,
    defect: false,
    unreviewed: false,
    sort: "images-desc",
    view: localStorage.getItem(VIEW_KEY) || "grid",
  };

  let currentOpenSlug = null;
  let currentMemberKey = null;
  let compareMode = false;
  let currentFiltered = [];
  let currentPreviews = [];

  function escapeHtml(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function loadReviews() {
    const defaults = DATA.default_reviews || {};
    try {
      const saved = JSON.parse(localStorage.getItem(REVIEW_KEY) || "{}") || {};
      return { ...defaults, ...saved };
    } catch (_) {
      return { ...defaults };
    }
  }
  function saveReviews() {
    try { localStorage.setItem(REVIEW_KEY, JSON.stringify(reviews)); } catch (_) {}
  }
  function getReview(slug) { return reviews[slug] || { status: "", note: "" }; }
  function countReviewed() {
    let n = 0;
    for (const f of FAMILIES) if (reviews[f.family_slug] && reviews[f.family_slug].status) n++;
    return n;
  }

  function highlightDefects(rawText) {
    const esc = escapeHtml(rawText || "");
    return esc
      .replace(/(?<![a-zA-Z])(jason|ture|treue)(?![a-zA-Z])/gi, '<mark class="err-tok">$1</mark>')
      .replace(/(default形式|\(&quot;res&quot;|【&quot;res&quot;|（&quot;res&quot;|&quot;reason&quot;：|Maga Man|密歇嘎大学|主管涂抹|allblakcs|oklahomo|excepmtion|universityu|以尺规则)/gi, '<mark class="err-tok">$1</mark>');
  }

  function cardColor(f) {
    if (f.inter_class_risk === "blocked_hygiene") return "#A83B32";
    if (f.supports_derivative || f.inter_class_risk === "high") return "#BE5A38";
    if (f.inter_class_risk === "medium") return "#B47425";
    const c = f.assert_asset_coverage.coverage_status;
    if (c === "approved_in_assert") return "#4E7A5B";
    return ARCH_COLOR[f.archetypes[0]] || "#4A6B82";
  }

  function resolveImgSrc(key, fallbackPath) {
    if (DATA.image_data_uris && key && DATA.image_data_uris[key]) {
      return DATA.image_data_uris[key];
    }
    return fallbackPath || "";
  }

  function getFamilyPreviews(f) {
    const cov = f.assert_asset_coverage || {};
    const out = [];
    const seen = new Set();

    for (const item of cov.approved_matches || []) {
      const paths = item.preview_rel_paths || [];
      const keys = item.preview_keys || [];
      for (let i = 0; i < paths.length; i++) {
        const path = paths[i];
        const key = keys[i] || "";
        const dedupeKey = key || path;
        if (!dedupeKey || seen.has(dedupeKey)) continue;
        seen.add(dedupeKey);
        const src = resolveImgSrc(key, path);
        if (!src) continue;
        out.push({
          key,
          path,
          src,
          badge: "Assert 已批准",
          badgeCls: "badge-sage",
          title: item.canonical_entity_id || item.entity_id,
          sub: item.entity_id,
        });
      }
    }

    for (const item of cov.supplement_matches || []) {
      const path = item.preview_rel_path || "";
      const key = item.preview_key || "";
      const dedupeKey = key || path;
      if (!dedupeKey || seen.has(dedupeKey)) continue;
      seen.add(dedupeKey);
      const src = resolveImgSrc(key, path);
      if (!src) continue;
      const isVisOk = f.visual_audit_status === "approved_visual_reference" || f.visual_audit_status === "approved_with_enrichment_note";
      out.push({
        key,
        path,
        src,
        badge: isVisOk ? "补充图·目视审结通过" : "补充参考图(待正式批)",
        badgeCls: isVisOk ? "badge-sage" : "badge-accent",
        title: `${item.name_zh || ""} ${item.name_en ? "/ " + item.name_en : ""}`.trim() || item.entity_id,
        sub: `${item.source} · ${item.entity_id}`,
      });
    }

    for (const p of f.character_portraits || []) {
      const key = p.preview_key || "";
      const path = p.preview_rel_path || "";
      const dedupeKey = key || path;
      if (!dedupeKey || seen.has(dedupeKey)) continue;
      seen.add(dedupeKey);
      const src = resolveImgSrc(key, path);
      if (!src) continue;
      out.push({
        key,
        path,
        src,
        kind: "portrait",
        badge: "角色立绘 · " + (p.source || "wiki"),
        badgeCls: "badge-plum",
        title: p.character_name || f.display_name,
        sub: `${f.display_name} · ${p.width || "?"}x${p.height || "?"}`,
      });
    }

    for (const item of cov.enriched_matches || []) {
      const path = item.preview_rel_path || "";
      const key = item.preview_key || "";
      const dedupeKey = key || path;
      if (!dedupeKey || seen.has(dedupeKey)) continue;
      seen.add(dedupeKey);
      const src = resolveImgSrc(key, path);
      if (!src) continue;
      const vStatus = item.visual_audit_status || f.visual_audit_status || "";
      let badge = item.enrichment_status === "local_assert_rescued_pending_review" ? "本地 Assert 关联待核" : "Wiki 补全待核";
      let badgeCls = "badge-accent";
      if (vStatus === "approved_visual_reference") {
        badge = "视觉审结已通过";
        badgeCls = "badge-sage";
      } else if (vStatus === "approved_with_enrichment_note") {
        badge = "审结通过(建议补多视角)";
        badgeCls = "badge-sage";
      } else if (vStatus === "manual_asset_required") {
        badge = "部分参考(仍缺结构图)";
        badgeCls = "badge-warn";
      }
      out.push({
        key,
        path,
        src,
        badge,
        badgeCls,
        title: (f.wiki_summary && f.wiki_summary.wiki_title) || f.display_name || f.family_slug,
        sub: `${item.width || "?"}x${item.height || "?"} · ${item.license || item.publisher || "wikimedia"}`,
      });
    }
    return out;
  }

  function hasPreviewImg(f) {
    return getFamilyPreviews(f).length > 0;
  }

  function openLightbox(item) {
    if (!item || !item.src) return;
    document.getElementById("lb-title").textContent = item.title || "图片预览";
    document.getElementById("lb-img").src = item.src;
    document.getElementById("lb-meta").textContent = `${item.badge} · ${item.sub} · ${item.key || item.path}`;
    document.getElementById("lightbox").classList.add("open");
  }

  function renderPreviewImgTag(item) {
    return `<img src="${escapeHtml(item.src)}" alt="${escapeHtml(item.title)}" onerror="this.outerHTML='<span class=img-fallback>图片加载失败</span>'">`;
  }

  function nonTruncFlags(f) {
    return f.all_hygiene_flags || [];
  }

  function matchesVisGroup(f, vg) {
    if (!vg) return true;
    if (vg === "has_img") return hasPreviewImg(f);
    if (vg === "has_portrait") return (f.character_portraits || []).length > 0;
    if (vg === "vis_approved") return f.visual_audit_status === "approved_visual_reference" || f.visual_audit_status === "approved_with_enrichment_note";
    if (vg === "vis_needs_asset") return f.visual_audit_status === "manual_asset_required" || f.visual_audit_status === "rejected_mismatch_purged";
    if (vg === "non_visual") return f.scope_track !== "entity_specific";
    return true;
  }

  function familyMatches(f, opts = {}) {
    const ignorePillar = Boolean(opts.ignorePillar);
    const ignoreCat = Boolean(opts.ignoreCat);
    const crossPillarFilter = Boolean(state.q.trim() || state.track || state.flag || state.gate || state.visGroup);
    if (!ignorePillar && !crossPillarFilter && state.pillar && f.scope_track !== state.pillar) return false;
    if (!ignoreCat && !crossPillarFilter && state.cat && state.cat !== "all" && getFamCat(f) !== state.cat) return false;
    if (state.track && f.scope_track !== state.track) return false;
    if (state.risk && f.inter_class_risk !== state.risk) return false;
    if (state.cov && f.assert_asset_coverage.coverage_status !== state.cov) return false;
    if (state.flag && !((f.latest_audit && f.latest_audit.hygiene_flags) || []).includes(state.flag)) return false;
    if (state.gate && ((f.training_advice && f.training_advice.gate_status) || "") !== state.gate) return false;
    if (state.visGroup && !matchesVisGroup(f, state.visGroup)) return false;
    if (state.arch && !(f.archetypes || []).includes(state.arch)) return false;
    if (state.disp && !f.members.some(m => m.disposition === state.disp)) return false;

    const rStatus = getReview(f.family_slug).status;
    if (state.rev === "unreviewed" && rStatus) return false;
    if (state.rev && state.rev !== "unreviewed" && rStatus !== state.rev) return false;

    if (state.hasImg && !hasPreviewImg(f)) return false;
    if (state.hasChar && !(f.character_portraits || []).length) return false;
    if (state.deriv && !f.supports_derivative) return false;
    if (state.multi && f.member_count < 2) return false;
    if (state.defect && nonTruncFlags(f).length === 0) return false;
    if (state.unreviewed && rStatus) return false;

    if (state.q.trim()) {
      const q = state.q.trim().toLowerCase();
      const hay = [
        f.family_slug, getFamName(f), f.display_name,
        ...(f.all_hygiene_flags || []), ...(f.archetypes || []),
        ...(f.character_dossiers || []).flatMap(c => [c.character_name || "", ...(c.visual_anchors || []), c.visual_appearance || ""]),
        ...f.members.flatMap(m => [String(m.id), m.version_key || "", m.title, ...(m.rel || []), m.cleaned_body || "", ...(m.findings || [])]),
      ].join("\n").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }

  function getFiltered() {
    const list = FAMILIES.filter(familyMatches);
    list.sort((a, b) => {
      if (state.sort === "images-desc") {
        const d = getFamilyPreviews(b).length - getFamilyPreviews(a).length;
        if (d !== 0) return d;
        return nonTruncFlags(b).length - nonTruncFlags(a).length || a.selected_latest_id - b.selected_latest_id;
      }
      if (state.sort === "defects-desc") {
        const d = nonTruncFlags(b).length - nonTruncFlags(a).length;
        if (d !== 0) return d;
        return (RISK_RANK[b.inter_class_risk] || 0) - (RISK_RANK[a.inter_class_risk] || 0) || a.selected_latest_id - b.selected_latest_id;
      }
      if (state.sort === "risk-desc") {
        const d = (RISK_RANK[b.inter_class_risk] || 0) - (RISK_RANK[a.inter_class_risk] || 0);
        if (d !== 0) return d;
        return b.member_count - a.member_count || a.selected_latest_id - b.selected_latest_id;
      }
      if (state.sort === "members-desc") {
        return b.member_count - a.member_count || a.family_slug.localeCompare(b.family_slug);
      }
      if (state.sort === "id-asc") return a.selected_latest_id - b.selected_latest_id;
      return a.family_slug.localeCompare(b.family_slug);
    });
    return list;
  }

  function populateSelects() {
    const fill = (id, allLbl, mapObj, countsObj) => {
      const el = document.getElementById(id);
      const opts = [`<option value="">${escapeHtml(allLbl)}</option>`];
      for (const [k, lbl] of Object.entries(mapObj)) {
        const c = countsObj && countsObj[k] != null ? ` (${countsObj[k]})` : "";
        opts.push(`<option value="${escapeHtml(k)}">${escapeHtml(lbl + c)}</option>`);
      }
      el.innerHTML = opts.join("");
    };
    fill("f-track", "范围分轨：全部", TRACK_LABEL, DATA.scope_track_counts);
    fill("f-risk", "类间风险：全部", RISK_LABEL, DATA.inter_class_risk_counts);
    fill("f-cov", "Assert 图库：全部", COV_LABEL, DATA.assert_coverage_counts);
  }

  function renderPillarTabs() {
    const el = document.getElementById("pillarTabs");
    if (!el) return;
    const pool = FAMILIES.filter(f => familyMatches(f, { ignorePillar: true, ignoreCat: true }));
    const cnt = { entity_specific: 0, broad_domain: 0, quarantined_excluded: 0 };
    for (const f of pool) cnt[f.scope_track] = (cnt[f.scope_track] || 0) + 1;
    el.innerHTML = `
      <button type="button" class="pillar-btn" data-pillar="entity_specific" aria-pressed="${state.pillar === "entity_specific"}">
        特定 IP / 品牌库 <span class="pn">${cnt.entity_specific || 0}</span>
      </button>
      <button type="button" class="pillar-btn" data-pillar="broad_domain" aria-pressed="${state.pillar === "broad_domain"}">
        广域通用模板库 <span class="pn">${cnt.broad_domain || 0}</span>
      </button>
      <button type="button" class="pillar-btn pillar-quar" data-pillar="quarantined_excluded" aria-pressed="${state.pillar === "quarantined_excluded"}">
        隔离异常归档 <span class="pn">${cnt.quarantined_excluded || 0}</span>
      </button>
    `;
    el.querySelectorAll(".pillar-btn[data-pillar]").forEach(b => b.addEventListener("click", () => {
      const p = b.getAttribute("data-pillar") || "entity_specific";
      if (state.pillar !== p) {
        state.pillar = p;
        state.cat = "all";
        renderAll();
      }
    }));
  }

  function renderCatTabs() {
    const el = document.getElementById("catTabs");
    if (!el) return;
    const cats = getPillarCats(state.pillar);
    const baseMatched = FAMILIES.filter(f => familyMatches(f, { ignoreCat: true }));
    const counts = {};
    for (const f of baseMatched) {
      const ck = getFamCat(f);
      counts[ck] = (counts[ck] || 0) + 1;
    }
    const allLabel = state.pillar === "broad_domain" ? "全部通用模板" : state.pillar === "quarantined_excluded" ? "全部隔离项" : "全部特定 IP";
    const btns = [`<button type="button" class="cat-tab" data-cat="all" aria-pressed="${state.cat === "all"}">${allLabel} <span class="cn">${baseMatched.length}</span></button>`];
    for (const c of cats) {
      btns.push(`<button type="button" class="cat-tab" data-cat="${c.key}" aria-pressed="${state.cat === c.key}" title="${escapeHtml(c.desc)}">${escapeHtml(c.label)} <span class="cn">${counts[c.key] || 0}</span></button>`);
    }
    el.innerHTML = btns.join("");
    el.querySelectorAll(".cat-tab[data-cat]").forEach(b => b.addEventListener("click", () => {
      state.cat = b.getAttribute("data-cat") || "all";
      renderAll();
    }));
  }

  function renderShowcase() {
    const el = document.getElementById("showcase");
    if (!el) return;
    if (!state.showShowcase || Boolean(state.q.trim()) || state.pillar === "quarantined_excluded") {
      el.hidden = true;
      el.innerHTML = "";
      return;
    }

    if (state.pillar === "broad_domain") {
      el.hidden = false;
      const bPool = FAMILIES.filter(f => f.scope_track === "broad_domain");
      const scHtml = BROAD_CATS.map(c => {
        const subFams = bPool.filter(f => getFamCat(f) === c.key);
        return `
          <div class="sc-card">
            <div class="sc-head">
              <div>
                <div class="sc-title">${escapeHtml(c.label)} <span class="cat-sec-cnt">${subFams.length} 族</span></div>
                <div class="sc-desc">${escapeHtml(c.desc)}</div>
              </div>
              <button type="button" class="iconbtn" data-sc-cat="${escapeHtml(c.key)}" style="padding:4px 9px;font-size:11.5px;flex:none;">筛选 →</button>
            </div>
            <div class="link-chips">
              ${subFams.slice(0, 6).map(sf => `<button type="button" class="link-chip" data-sc-slug="${escapeHtml(sf.family_slug)}">${escapeHtml(getFamName(sf))}</button>`).join("")}
            </div>
          </div>
        `;
      }).join("");
      el.innerHTML = `
        <div class="showcase-top">
          <div>
            <h2>广域通用审核模板 · 能力全景与 CPT-SFT 协同路线</h2>
            <div class="showcase-sub">广域模板不绑定单一具体品牌，重点解决宿主隔离、闭集名单边界、前置豁免、双图 AI 防规避与法务合规（<a href="../docs/broad_domain_cpt_sft_roadmap.md" target="_blank">查看完整 CPT-SFT 路线图 MD ↗</a>）</div>
          </div>
        </div>
        <div class="showcase-grid">${scHtml}</div>
      `;
      el.querySelectorAll("[data-sc-cat]").forEach(b => b.addEventListener("click", () => {
        state.cat = b.getAttribute("data-sc-cat") || "all";
        renderAll();
      }));
      el.querySelectorAll("[data-sc-slug]").forEach(b => b.addEventListener("click", () => {
        openSheet(b.getAttribute("data-sc-slug"));
      }));
      return;
    }

    el.hidden = false;
    const targetCats = state.cat === "all"
      ? SPECIFIC_CATS.map(c => c.key)
      : [state.cat];

    const cardsHtml = [];
    for (const ck of targetCats) {
      const meta = CAT_META.get(ck);
      const famPool = FAMILIES.filter(f => getFamCat(f) === ck);
      const tiles = [];
      const seenSrc = new Set();

      if (ck === "B2_specific_anime_game_media_ip") {
        for (const f of famPool) {
          for (const p of f.character_portraits || []) {
            if (tiles.length >= 6) break;
            const src = resolveImgSrc(p.preview_key, p.preview_rel_path);
            if (!src || seenSrc.has(src)) continue;
            seenSrc.add(src);
            tiles.push({
              slug: f.family_slug,
              src,
              label: p.character_name,
              item: { key: p.preview_key, path: p.preview_rel_path, src, badge: "角色立绘 · " + (p.source || "wiki"), title: p.character_name, sub: getFamName(f) },
            });
          }
          if (tiles.length >= 6) break;
        }
      }
      for (const f of famPool) {
        if (tiles.length >= 6) break;
        const pre = getFamilyPreviews(f)[0];
        if (!pre || !pre.src || seenSrc.has(pre.src)) continue;
        seenSrc.add(pre.src);
        tiles.push({
          slug: f.family_slug,
          src: pre.src,
          label: getFamName(f),
          item: pre,
        });
      }
      if (!tiles.length) continue;

      const withImgCnt = famPool.filter(hasPreviewImg).length;
      cardsHtml.push(`
        <div class="sc-card">
          <div class="sc-head">
            <div>
              <div class="sc-title">${escapeHtml(meta ? meta.label : ck)} <span class="cat-sec-cnt">${withImgCnt}/${famPool.length} 有图</span></div>
              <div class="sc-desc">${escapeHtml(meta ? meta.desc : "")}</div>
            </div>
            ${state.cat === "all" ? `<button type="button" class="iconbtn" data-sc-cat="${escapeHtml(ck)}" style="padding:4px 9px;font-size:11.5px;flex:none;">进入类目 →</button>` : ""}
          </div>
          <div class="sc-tiles">
            ${tiles.map((t, idx) => `
              <div class="stile">
                <div class="stile-img" data-sc-cat-idx="${escapeHtml(ck)}:${idx}" title="点击放大：${escapeHtml(t.label)}">
                  <img src="${escapeHtml(t.src)}" alt="${escapeHtml(t.label)}">
                </div>
                <button type="button" class="stile-lbl" data-sc-slug="${escapeHtml(t.slug)}" title="打开详情：${escapeHtml(t.label)}">${escapeHtml(t.label)}</button>
              </div>
            `).join("")}
          </div>
        </div>
      `);
      el._tileLookup = el._tileLookup || {};
      el._tileLookup[ck] = tiles;
    }

    if (!cardsHtml.length) {
      el.hidden = true;
      el.innerHTML = "";
      return;
    }

    el.innerHTML = `
      <div class="showcase-top">
        <div>
          <h2>各品类抓爬图片抽样展区</h2>
          <div class="showcase-sub">点击缩略图直接放大查看，点击下方 IP / 角色名直达 6 段式完整档案（立绘 ${DATA.character_portraits_count || 0} 张 · 参考图共 ${DATA.embedded_images_count || 0} 张）</div>
        </div>
      </div>
      <div class="showcase-grid">${cardsHtml.join("")}</div>
    `;

    el.querySelectorAll("[data-sc-cat]").forEach(b => b.addEventListener("click", () => {
      state.cat = b.getAttribute("data-sc-cat") || "all";
      renderAll();
    }));
    el.querySelectorAll("[data-sc-slug]").forEach(b => b.addEventListener("click", () => {
      openSheet(b.getAttribute("data-sc-slug"));
    }));
    el.querySelectorAll("[data-sc-cat-idx]").forEach(box => box.addEventListener("click", () => {
      const [ck, idx] = (box.getAttribute("data-sc-cat-idx") || "").split(":");
      const tile = el._tileLookup && el._tileLookup[ck] && el._tileLookup[ck][Number(idx)];
      if (tile && tile.item) openLightbox(tile.item);
    }));
  }

  const GATE_LABELS = {
    ready_for_training: "具备 CPT+SFT 入训条件",
    fix_prompt_first: "先修最新主版再入 SFT",
    enrich_assets_first: "先补视觉标准图再入 CPT",
    excluded_quarantine: "隔离禁止入训",
  };
  const VIS_GROUP_LABELS = {
    has_img: "已有本地参考图/立绘",
    has_portrait: "含角色立绘 (B2 抽样)",
    vis_approved: "视觉审结已通过",
    vis_needs_asset: "仍需人工补标准图",
    non_visual: "广域通用规则与隔离项",
  };
  const LATEST_FLAG_LABEL = {
    broken_json_schema: "JSON 格式错误",
    missing_exclusion_clause: "缺反向排除条款",
    rel_metadata_mismatch: "rel 实体误绑",
    typo_or_logic_defect: "错别字/逻辑错误",
    underspecified_rubric: "判据过笼统",
    cross_entity_paste_bug: "最新主版错贴",
    empty_placeholder_variable: "空占位符",
    weak_anchor_or_escape_hatch: "主观兜底表述",
    style_only_trigger_risk: "唯画风触发风险",
    duplicate_role_header: "角色段重复",
    empty_or_trivial_body: "空壳正文",
  };

  function renderChips() {
    const chipsEl = document.getElementById("chips");
    if (!chipsEl) return;
    const parts = [];
    if (state.track) parts.push(`<span class="chip" aria-pressed="true">${escapeHtml(TRACK_LABEL[state.track] || state.track)}</span>`);
    if (state.risk) parts.push(`<span class="chip" aria-pressed="true">风险：${escapeHtml(RISK_LABEL[state.risk] || state.risk)}</span>`);
    if (state.cov) parts.push(`<span class="chip" aria-pressed="true">原Assert库：${escapeHtml(COV_LABEL[state.cov] || state.cov)}</span>`);
    if (state.flag) parts.push(`<button type="button" class="chip" data-clr="flag" aria-pressed="true">最新主版问题：${escapeHtml(LATEST_FLAG_LABEL[state.flag] || state.flag)} ✕</button>`);
    if (state.visGroup) parts.push(`<button type="button" class="chip" data-clr="visGroup" aria-pressed="true">图库状态：${escapeHtml(VIS_GROUP_LABELS[state.visGroup] || state.visGroup)} ✕</button>`);
    if (state.gate) parts.push(`<button type="button" class="chip" data-clr="gate" aria-pressed="true">入训门控：${escapeHtml(GATE_LABELS[state.gate] || state.gate)} ✕</button>`);
    if (state.arch) parts.push(`<button type="button" class="chip" data-clr="arch" aria-pressed="true">${escapeHtml(ARCH_LABEL[state.arch] || state.arch)} ✕</button>`);
    if (state.deriv) parts.push(`<span class="chip" aria-pressed="true">仅含二创</span>`);
    if (state.multi) parts.push(`<span class="chip" aria-pressed="true">仅多版本</span>`);
    if (state.defect) parts.push(`<span class="chip" aria-pressed="true">仅存缺陷</span>`);
    if (state.unreviewed) parts.push(`<span class="chip" aria-pressed="true">仅看未复核</span>`);

    const hasAnyFilter = Boolean(parts.length || state.q || (state.cat && state.cat !== "all") || state.rev || state.hasImg || state.hasChar);
    if (hasAnyFilter) {
      parts.push(`<button type="button" class="chip chip-clear" id="chipClearAll">清空全部筛选</button>`);
    }
    chipsEl.innerHTML = parts.join("");
    chipsEl.querySelectorAll("[data-clr]").forEach(b => b.addEventListener("click", () => {
      state[b.getAttribute("data-clr")] = "";
      renderAll();
    }));
    const clr = document.getElementById("chipClearAll");
    if (clr) clr.addEventListener("click", resetFilters);
  }

  function renderSidebar() {
    const sc = DATA.scope_track_counts || {};
    document.getElementById("sideStats").textContent =
      `特定 IP ${sc.entity_specific || 0} · 广域通用 ${sc.broad_domain || 0} · 隔离 ${sc.quarantined_excluded || 0} · 参考图 ${DATA.embedded_images_count || 0}（立绘 ${DATA.character_portraits_count || 0}）`;

    // 1. 人工复核状态分布（按 352 个对象）
    const revCounts = { approved: 0, needs_fix: 0, needs_asset: 0, quarantined: 0, unreviewed: 0 };
    for (const f of FAMILIES) {
      const rs = getReview(f.family_slug).status;
      if (rs && revCounts[rs] != null) revCounts[rs]++;
      else revCounts.unreviewed++;
    }
    const revN = FAMILIES.length - revCounts.unreviewed;
    const pct = Math.round((revN / Math.max(1, FAMILIES.length)) * 100);
    const revRows = [
      ["approved", "已通过", "#4E7A5B"],
      ["needs_fix", "需修最新主版", "#B47425"],
      ["needs_asset", "需补标准图", "#7A5585"],
      ["quarantined", "隔离废弃", "#A83B32"],
      ["unreviewed", "未复核", "#6F6D64"],
    ].filter(([k]) => revCounts[k] > 0);
    document.getElementById("sideProgress").innerHTML = `
      <div class="tt-h"><span>1. 人工复核状态 (${FAMILIES.length} 对象)</span><span>${revN} / ${FAMILIES.length} (${pct}%)</span></div>
      <div class="prog-meter"><div class="prog-meter-fill" style="width:${pct}%"></div></div>
      ${revRows.map(([k, lbl, col]) => `
        <button type="button" class="bar-row" data-side-rev="${k}" aria-pressed="${state.rev === k}">
          <span class="bar-lbl">${lbl}</span>
          <span class="bar-trk"><span class="bar-fill" style="width:${Math.max(4, Math.round(revCounts[k] / FAMILIES.length * 100))}%;background:${col}"></span></span>
          <span class="bar-num">${revCounts[k]}</span>
        </button>
      `).join("")}
    `;

    // 2. 最新主版审计问题分布（严格仅统计最新有效主版）
    const latestFlagCounts = {};
    for (const f of FAMILIES) {
      for (const fl of ((f.latest_audit && f.latest_audit.hygiene_flags) || [])) {
        latestFlagCounts[fl] = (latestFlagCounts[fl] || 0) + 1;
      }
    }
    const flagEntries = Object.entries(latestFlagCounts).sort((a, b) => b[1] - a[1]);
    const maxFlag = flagEntries.length ? flagEntries[0][1] : 1;
    document.getElementById("sideFlags").innerHTML =
      `<div class="tt-h"><span>2. 最新主版审计问题 (不含旧版)</span><span>${flagEntries.reduce((s, x) => s + x[1], 0)} 项</span></div>` +
      (flagEntries.length ? flagEntries.map(([k, v]) => `
        <button type="button" class="bar-row" data-side-flag="${escapeHtml(k)}" aria-pressed="${state.flag === k}">
          <span class="bar-lbl">${escapeHtml(LATEST_FLAG_LABEL[k] || FLAG_LABEL[k] || k)}</span>
          <span class="bar-trk"><span class="bar-fill" style="width:${Math.max(4, Math.round(v / maxFlag * 100))}%;background:#B47425"></span></span>
          <span class="bar-num">${v}</span>
        </button>
      `).join("") : `<div style="font-size:12px;color:var(--muted);">最新主版无缺陷</div>`);

    // 3. 当前真实图库与角色立绘覆盖（实时口径，替换旧版 1119 口径）
    const visCounts = {
      has_img: FAMILIES.filter(f => matchesVisGroup(f, "has_img")).length,
      has_portrait: FAMILIES.filter(f => matchesVisGroup(f, "has_portrait")).length,
      vis_approved: FAMILIES.filter(f => matchesVisGroup(f, "vis_approved")).length,
      vis_needs_asset: FAMILIES.filter(f => matchesVisGroup(f, "vis_needs_asset")).length,
      non_visual: FAMILIES.filter(f => matchesVisGroup(f, "non_visual")).length,
    };
    const visRows = [
      ["has_img", "已有本地参考图 / 立绘", "#4E7A5B"],
      ["vis_approved", "视觉审结已通过", "#4E7A5B"],
      ["has_portrait", "含 B2 抽样角色立绘", "#7A5585"],
      ["vis_needs_asset", "仍需人工补标准图", "#B47425"],
      ["non_visual", "广域通用规则与隔离项", "#6F6D64"],
    ];
    document.getElementById("sideCov").innerHTML =
      `<div class="tt-h"><span>3. 当前真实图库覆盖 (实时)</span><span>${visCounts.has_img} 有图</span></div>` +
      visRows.map(([k, lbl, col]) => `
        <button type="button" class="bar-row" data-side-vis="${k}" aria-pressed="${state.visGroup === k}">
          <span class="bar-lbl">${lbl}</span>
          <span class="bar-trk"><span class="bar-fill" style="width:${Math.max(4, Math.round(visCounts[k] / FAMILIES.length * 100))}%;background:${col}"></span></span>
          <span class="bar-num">${visCounts[k]}</span>
        </button>
      `).join("");

    // 4. CPT / SFT 训练入训门控分布
    const gateCounts = { ready_for_training: 0, fix_prompt_first: 0, enrich_assets_first: 0, excluded_quarantine: 0 };
    for (const f of FAMILIES) {
      const gs = (f.training_advice && f.training_advice.gate_status) || "fix_prompt_first";
      gateCounts[gs] = (gateCounts[gs] || 0) + 1;
    }
    const gateRows = [
      ["ready_for_training", "具备 CPT+SFT 入训条件", "#4E7A5B"],
      ["fix_prompt_first", "先修最新主版再入 SFT", "#B47425"],
      ["enrich_assets_first", "先补标准图再入 CPT", "#7A5585"],
      ["excluded_quarantine", "隔离禁止入训", "#A83B32"],
    ].filter(([k]) => gateCounts[k] > 0);
    document.getElementById("sideGate").innerHTML =
      `<div class="tt-h"><span>4. CPT / SFT 入训门控</span><span>${FAMILIES.length}</span></div>` +
      gateRows.map(([k, lbl, col]) => `
        <button type="button" class="bar-row" data-side-gate="${k}" aria-pressed="${state.gate === k}">
          <span class="bar-lbl">${lbl}</span>
          <span class="bar-trk"><span class="bar-fill" style="width:${Math.max(4, Math.round(gateCounts[k] / FAMILIES.length * 100))}%;background:${col}"></span></span>
          <span class="bar-num">${gateCounts[k]}</span>
        </button>
      `).join("");

    // 5. 最新主版错贴拦截直达（严格仅列出最新主版仍为错贴的对象）
    const latestPasteBugs = FAMILIES
      .filter(f => ((f.latest_audit && f.latest_audit.hygiene_flags) || []).includes("cross_entity_paste_bug"))
      .map(f => ({
        slug: f.family_slug,
        name: getFamName(f),
        vkey: (f.latest_audit && f.latest_audit.version_key) || f.selected_latest_version_key,
      }));
    document.getElementById("sidePasteBugs").innerHTML =
      `<div class="tt-h"><span>最新主版错贴拦截 (${latestPasteBugs.length})</span></div>` +
      (latestPasteBugs.length ? latestPasteBugs.map(p => `
        <button type="button" class="tt-row" data-goto-slug="${escapeHtml(p.slug)}" data-goto-vkey="${escapeHtml(p.vkey)}">
          <span class="tt-num">#${escapeHtml(p.vkey)}</span>
          <span class="tt-t">${escapeHtml(p.name)}</span>
          <span class="tt-c">${escapeHtml(p.slug)}</span>
        </button>
      `).join("") : `<div style="font-size:12px;color:var(--muted);">无最新主版错贴</div>`);

    document.querySelectorAll("[data-side-rev]").forEach(b => b.addEventListener("click", () => {
      const k = b.getAttribute("data-side-rev");
      state.rev = state.rev === k ? "" : k;
      renderAll();
    }));
    document.querySelectorAll("[data-side-flag]").forEach(b => b.addEventListener("click", () => {
      const k = b.getAttribute("data-side-flag");
      state.flag = state.flag === k ? "" : k;
      renderAll();
    }));
    document.querySelectorAll("[data-side-vis]").forEach(b => b.addEventListener("click", () => {
      const k = b.getAttribute("data-side-vis");
      state.visGroup = state.visGroup === k ? "" : k;
      renderAll();
    }));
    document.querySelectorAll("[data-side-gate]").forEach(b => b.addEventListener("click", () => {
      const k = b.getAttribute("data-side-gate");
      state.gate = state.gate === k ? "" : k;
      renderAll();
    }));
    document.querySelectorAll("[data-goto-slug]").forEach(b => b.addEventListener("click", () => {
      openSheet(b.getAttribute("data-goto-slug"), b.getAttribute("data-goto-vkey"));
    }));
  }

  function renderCardHtml(f, idx) {
    const tc = cardColor(f);
    const selM = f.members.find(m => m.version_key === f.selected_latest_version_key) || f.members[0];
    const rev = getReview(f.family_slug).status;
    const latestAudit = f.latest_audit || {};
    const latestFlags = latestAudit.hygiene_flags || [];
    const chars = f.character_dossiers || [];
    const portraits = f.character_portraits || [];
    const previews = getFamilyPreviews(f);

    let summary = "";
    if (chars.length) {
      const names = chars.map(c => c.character_name).filter(Boolean).slice(0, 5).join(" · ");
      summary = `角色档案（${chars.length}）：${names}${chars.length > 5 ? " 等" : ""}`;
    } else if (f.wiki_summary && f.wiki_summary.extract) {
      summary = String(f.wiki_summary.extract).slice(0, 110);
    } else if (f.classification_evidence) {
      summary = String(f.classification_evidence).slice(0, 110);
    } else {
      summary = (selM.cleaned_body || "").replace(/^#+\s*[^\n]*\n+/g, "").replace(/[>\n]+/g, " ").trim().slice(0, 110) || "暂无摘要";
    }

    const catInfo = CAT_META.get(getFamCat(f));
    const catLbl = catInfo ? catInfo.label : (SUBTRACK_LABEL[f.scope_subtrack] || f.scope_subtrack);
    const revHtml = rev ? `<span class="rev-pill rev-${escapeHtml(rev)}">${escapeHtml(REV_LABEL[rev] || rev)}</span>` : "";

    const thumbsHtml = previews.length
      ? `<div class="card-thumbs">${previews.slice(0, 3).map((p, pIdx) => `
          <div class="card-thumb" data-card-slug="${escapeHtml(f.family_slug)}" data-card-thumb-idx="${pIdx}" title="点击放大：${escapeHtml(p.title)}">
            ${renderPreviewImgTag(p)}
            ${pIdx === 2 && previews.length > 3 ? `<span class="card-thumb-more">+${previews.length - 3}</span>` : ""}
          </div>
        `).join("")}</div>`
      : "";

    const footBadges = [`<span class="tag">${escapeHtml(catLbl)}</span>`];
    if (portraits.length) footBadges.push(`<span class="tag" style="color:var(--plum)">立绘×${portraits.length}</span>`);
    else if (previews.length) footBadges.push(`<span class="tag" style="color:var(--sage)">参考图×${previews.length}</span>`);
    if (latestFlags.length) footBadges.push(`<span class="tag" style="color:var(--warn)">最新待优×${latestFlags.length}</span>`);

    return `
      <article class="card" style="--tc:${tc};--i:${Math.min(idx, 12)}" tabindex="0" data-slug="${escapeHtml(f.family_slug)}">
        <div class="lmain">
          <div class="ctitle-row">
            <div class="ctitle-text">
              <div class="ctitle">${escapeHtml(getFamName(f))}</div>
              <div style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin-top:3px;">
                ${revHtml}
                ${f.supports_derivative ? `<span class="badge badge-plum" style="padding:1px 5px;font-size:10px;">含二创</span>` : ""}
                ${f.member_count > 1 ? `<span class="kind">${f.member_count} 版</span>` : ""}
              </div>
            </div>
            ${thumbsHtml}
          </div>
          <div class="csum">${escapeHtml(summary)}</div>
        </div>
        <div class="cfoot">
          <div class="tags">${footBadges.join("")}</div>
          <div class="cmeta">
            ${chars.length ? `<span class="cdeg">档案×${chars.length}</span>` : ""}
          </div>
        </div>
      </article>
    `;
  }

  function renderGrid(filtered) {
    currentFiltered = filtered;
    const grid = document.getElementById("grid");
    const useGrouped = state.cat === "all" && !state.q.trim() && !state.track;
    grid.classList.toggle("list-view", state.view === "list");
    grid.classList.toggle("flat-grid", !useGrouped || !filtered.length);

    const tplTotal = filtered.reduce((s, f) => s + f.member_count, 0);
    document.getElementById("count").innerHTML = `<b>${filtered.length}</b> / ${FAMILIES.length} 个对象 · ${tplTotal} 版模板`;

    if (!filtered.length) {
      grid.innerHTML = `<div class="empty">没有匹配的审核对象，试着切换上方栏目或清空筛选。</div>`;
      return;
    }

    if (useGrouped) {
      const catOrder = (state.flag || state.gate || state.visGroup) ? ALL_CATS : getPillarCats(state.pillar);
      const groups = new Map(catOrder.map(c => [c.key, []]));
      for (const f of filtered) {
        const ck = getFamCat(f);
        if (!groups.has(ck)) groups.set(ck, []);
        groups.get(ck).push(f);
      }
      const secHtml = [];
      for (const c of catOrder) {
        const list = groups.get(c.key) || [];
        if (!list.length) continue;
        secHtml.push(`
          <section class="cat-sec" data-sec-cat="${c.key}">
            <div class="cat-sec-head">
              <h2>${escapeHtml(c.label)}</h2>
              <span class="cat-sec-cnt">${list.length} 个对象</span>
              <span class="cat-sec-desc">${escapeHtml(c.desc)}</span>
            </div>
            <div class="cat-sec-grid">
              ${list.map((f, idx) => renderCardHtml(f, idx)).join("")}
            </div>
          </section>
        `);
      }
      grid.innerHTML = secHtml.join("");
    } else {
      grid.innerHTML = filtered.map((f, idx) => renderCardHtml(f, idx)).join("");
    }

    grid.querySelectorAll(".card-thumb[data-card-slug]").forEach(el => {
      el.addEventListener("click", e => {
        e.stopPropagation();
        const fam = FAM_BY_SLUG.get(el.getAttribute("data-card-slug"));
        if (!fam) return;
        const item = getFamilyPreviews(fam)[Number(el.getAttribute("data-card-thumb-idx"))];
        openLightbox(item);
      });
    });

    grid.querySelectorAll(".card[data-slug]").forEach(el => {
      el.addEventListener("click", () => openSheet(el.getAttribute("data-slug")));
      el.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openSheet(el.getAttribute("data-slug"));
        }
      });
    });
  }

  function renderPromptBlock(m, isDefault) {
    const cleanNote = m.export_cleanups_count > 0
      ? `<span class="badge badge-sage" title="原始导出包含运行时商品标题/属性，已自动还原为标准占位符">已清理 ${m.export_cleanups_count} 处导出硬编码</span>`
      : "";
    const pasteBanner = m.disposition === "quarantine_paste_bug"
      ? `<blockquote class="bq-err"><strong>跨实体错贴 Bug：</strong>该版本标题与正文检测对象矛盾，已自动降级隔离，请勿直接用于训练或评测。</blockquote>`
      : "";

    const relHtml = (m.rel && m.rel.length)
      ? m.rel.map(r => `<span class="badge ${(m.hygiene_flags || []).includes("rel_metadata_mismatch") ? "badge-red" : ""}">${escapeHtml(r)}</span>`).join(" ")
      : `<span class="badge">空</span>`;

    const inlineHtml = (m.inline_versions && m.inline_versions.length)
      ? `<div class="meta-kv"><strong>同记录拆包来源：</strong>${m.inline_versions.map(v => `<span class="badge badge-accent">${escapeHtml(v)}</span>`).join(" ")}</div>`
      : "";

    return `
      <div>
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
          <div>
            <strong>#${escapeHtml(m.version_key)} ${escapeHtml(m.title)}</strong>
            ${isDefault ? `<span class="badge badge-sage">默认主版</span>` : `<span class="badge">历史/并行版</span>`}
          </div>
          <div style="display:flex;gap:5px;flex-wrap:wrap;">
            ${cleanNote}
            <span class="badge">${m.chars} 字</span>
            <span class="badge ${m.disposition === "active_ip" ? "badge-accent" : "badge-red"}">${escapeHtml(DISP_LABEL[m.disposition] || m.disposition)}</span>
          </div>
        </div>
        ${pasteBanner}
        ${(DATA.public_redacted || !m.cleaned_body)
          ? `<blockquote class="bq-tip">公开同步版已隐藏 Prompt 正文，仅保留模板版本元数据、最新主版审计建议、Wiki 知识与 Assert 图片资产、类间联系及 CPT/SFT 训练建议。</blockquote>`
          : `<pre data-lang="PROMPT"><button type="button" class="copy-btn">复制</button><code>${highlightDefects(m.cleaned_body || "")}</code></pre>`}
        <div class="meta-kv"><strong>关联实体 rel：</strong>${relHtml}</div>
        ${inlineHtml}
      </div>
    `;
  }

  function navNeighbors(slug) {
    const pool = currentFiltered.length ? currentFiltered : FAMILIES;
    const idx = pool.findIndex(f => f.family_slug === slug);
    if (idx < 0) return { prev: null, next: null };
    return {
      prev: idx > 0 ? pool[idx - 1] : null,
      next: idx < pool.length - 1 ? pool[idx + 1] : null,
    };
  }

  function renderSheet() {
    const fam = FAM_BY_SLUG.get(currentOpenSlug);
    if (!fam) return;
    const defaultMember = fam.members.find(m => m.version_key === fam.selected_latest_version_key) || fam.members[0];
    if (!currentMemberKey || !fam.members.some(m => m.version_key === currentMemberKey)) {
      currentMemberKey = defaultMember.version_key;
    }
    const curMember = fam.members.find(m => m.version_key === currentMemberKey) || defaultMember;
    const rev = getReview(fam.family_slug);

    const cov = fam.assert_asset_coverage;
    currentPreviews = getFamilyPreviews(fam);

    const topStripHtml = currentPreviews.length
      ? `<div class="asset-strip">
          <span class="asset-strip-label">标准参考图 (${currentPreviews.length})</span>
          ${currentPreviews.slice(0, 6).map((a, idx) => `
            <div class="checkerboard asset-strip-item" data-preview-idx="${idx}" title="点击放大：${escapeHtml(a.title)}">
              ${renderPreviewImgTag(a)}
            </div>
          `).join("")}
          <button type="button" class="iconbtn" id="btnJumpAssets" style="margin-left:auto;">跳至完整图库 ↓</button>
        </div>`
      : "";

    const assetGridHtml = currentPreviews.length
      ? `<div class="asset-grid">${currentPreviews.map((a, idx) => `
          <div class="asset-card">
            <div class="checkerboard" data-preview-idx="${idx}" title="点击放大查看">
              ${renderPreviewImgTag(a)}
            </div>
            <div class="asset-info">
              <div><span class="badge ${a.badgeCls}">${escapeHtml(a.badge)}</span></div>
              <strong style="word-break:break-word;">${escapeHtml(a.title)}</strong>
              <span style="color:var(--muted);word-break:break-all;">${escapeHtml(a.sub)}</span>
            </div>
          </div>
        `).join("")}</div>`
      : `<p style="color:var(--muted);font-size:13.5px;">当前同族在 Assert 中暂无已落地的本地参考预览图。</p>`;

    const backlogRows = (cov.backlog_matches || []).slice(0, 12).map(b => `
      <tr>
        <td><code>${escapeHtml(b.entity_id)}</code></td>
        <td>${escapeHtml(b.title)}</td>
        <td>${escapeHtml(b.source_domain || "")}</td>
        <td><span class="badge">${escapeHtml(b.status || "")}</span></td>
      </tr>
    `).join("");
    const backlogHtml = backlogRows
      ? `<div class="tbl"><table><thead><tr><th>Entity ID</th><th>标题</th><th>域</th><th>状态</th></tr></thead><tbody>${backlogRows}</tbody></table></div>`
      : "";

    const verTabsHtml = fam.members.map(m => {
      const isAct = m.version_key === curMember.version_key;
      const isDef = m.version_key === defaultMember.version_key;
      const isBad = m.disposition === "quarantine_paste_bug" || m.disposition === "quarantine_test_junk" || m.disposition === "needs_body_completion";
      return `<button type="button" class="ver-tab ${isAct ? "active" : ""} ${isBad ? "is-bad" : ""}" data-vkey="${escapeHtml(m.version_key)}">
        ${isDef ? "✅ " : ""}${isBad ? "⛔ " : ""}#${escapeHtml(m.version_key)} ${escapeHtml(m.title)} (${m.chars}字)
      </button>`;
    }).join("");

    const otherForCompare = curMember.version_key === defaultMember.version_key
      ? (fam.members.find(x => x.version_key !== defaultMember.version_key) || curMember)
      : curMember;
    const versionsBodyHtml = compareMode && fam.member_count >= 2
      ? `<div class="compare-grid">
           <div class="compare-col">${renderPromptBlock(defaultMember, true)}</div>
           <div class="compare-col">${renderPromptBlock(otherForCompare, false)}</div>
         </div>`
      : renderPromptBlock(curMember, curMember.version_key === defaultMember.version_key);

    const la = fam.latest_audit || {};
    const laFlags = la.hygiene_flags || [];
    const laFindings = la.findings || [];
    const laActions = la.action_items || fam.recommendations || [];
    const historyMembers = fam.members.filter(m => m.version_key !== defaultMember.version_key);
    const histRows = historyMembers.map(m => `<tr>
      <td><code>#${escapeHtml(m.version_key)}</code></td>
      <td><code>${escapeHtml(m.title)}</code></td>
      <td>${m.chars}</td>
      <td><code>${escapeHtml(m.disposition)}</code></td>
    </tr>`).join("");
    const histArchiveHtml = historyMembers.length
      ? `<details class="hist-archive">
          <summary>历史/并行版本存档（${historyMembers.length} 版 · 仅供追溯，不做审计建议）</summary>
          <div class="tbl" style="margin-top:8px;">
            <table>
              <thead><tr><th>版本键</th><th>历史模板标题</th><th>字数</th><th>状态归类</th></tr></thead>
              <tbody>${histRows}</tbody>
            </table>
          </div>
        </details>`
      : "";

    const revBtnsHtml = [
      ["approved", "✓ 通过"],
      ["needs_fix", "✎ 需修模板"],
      ["needs_asset", "🖼 需补标准图"],
      ["quarantined", "⛔ 隔离废弃"],
    ].map(([k, lbl]) => `<button type="button" class="rev-btn ${rev.status === k ? "on-" + k : ""}" data-rev-val="${k}">${lbl}</button>`).join("");

    const { prev, next } = navNeighbors(fam.family_slug);
    const snavHtml = (prev || next) ? `
      <div class="snav">
        ${prev ? `<button type="button" class="snav-btn" data-nav-slug="${escapeHtml(prev.family_slug)}">
          <span class="snav-dir">← 上一个对象</span>
          <span class="snav-t">${escapeHtml(getFamName(prev))}</span>
        </button>` : `<span></span>`}
        ${next ? `<button type="button" class="snav-btn next" data-nav-slug="${escapeHtml(next.family_slug)}">
          <span class="snav-dir">下一个对象 →</span>
          <span class="snav-t">${escapeHtml(getFamName(next))}</span>
        </button>` : `<span></span>`}
      </div>
    ` : "";

    const req = fam.audit_requirements || {};
    const cues = (req.visual_cues_required || []).map(c => `<span class="badge">${escapeHtml(CUE_LABEL[c] || c)}</span>`).join(" ");
    const bnds = (req.boundary_and_exclusion_mechanisms || []).map(b => `<span class="badge badge-sage">${escapeHtml(BND_LABEL[b] || b)}</span>`).join(" ");
    const wiki = fam.wiki_summary || {};
    const wikiBox = wiki.extract
      ? `<blockquote><strong>Wiki 百科释义（<a href="${escapeHtml(wiki.wiki_url || "#")}" target="_blank">${escapeHtml(wiki.wiki_title || getFamName(fam))} ↗</a>）：</strong>${escapeHtml(wiki.extract)}</blockquote>`
      : `<p style="color:var(--muted);font-size:13px;">暂无通用 Wiki 词条摘要${fam.scope_track === "broad_domain" ? "（广域规则不绑定单一 Wiki 实体）" : ""}。</p>`;

    const relData = fam.inter_class_links || {};
    const peersHtml = (relData.related_peers || []).length
      ? `<div class="link-chips">${relData.related_peers.map(p => `<button type="button" class="link-chip" data-jump-slug="${escapeHtml(p.slug)}">${escapeHtml(p.entity_name)} <span style="opacity:.6;font-size:11px;">${escapeHtml(RISK_LABEL[p.inter_class_risk] || "")}</span></button>`).join("")}</div>`
      : `<span style="color:var(--muted);font-size:12.5px;">暂无同机制高相似邻近对象。</span>`;
    const genLinksHtml = (relData.linked_general_templates || []).length
      ? `<div style="display:flex;flex-direction:column;gap:6px;margin-top:6px;">${relData.linked_general_templates.map(g => `<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;"><button type="button" class="link-chip" data-jump-slug="${escapeHtml(g.slug)}">${escapeHtml(g.entity_name)} →</button><span style="font-size:12.5px;color:var(--muted);">${escapeHtml(g.reason)}</span></div>`).join("")}</div>`
      : "";
    const govLinksHtml = (relData.governed_specific_examples || []).length
      ? `<div style="margin-top:8px;"><strong>典型适用具体 IP / 品牌举例：</strong><div class="link-chips">${relData.governed_specific_examples.map(g => `<button type="button" class="link-chip" data-jump-slug="${escapeHtml(g.slug)}">${escapeHtml(g.entity_name)}</button>`).join("")}</div></div>`
      : "";

    const tr = fam.training_advice || {};
    const gateBadgeCls = tr.gate_status === "ready_for_training" ? "badge-sage" : tr.gate_status === "excluded_quarantine" ? "badge-red" : "badge-warn";

    const chars = fam.character_dossiers || [];
    const srcMap = { moegirl: "萌娘百科", fandom: "Fandom Wiki", zhwiki: "中文维基", enwiki: "English Wiki" };
    const charCardsHtml = chars.length
      ? `<h3 style="margin:16px 0 8px;font-family:var(--serif);font-size:16px;">多源 Wiki 角色视觉与设定档案 (${chars.length})</h3>` + chars.map(c => {
          const anch = (c.visual_anchors || []).map(a => `<span class="badge badge-plum">${escapeHtml(a)}</span>`).join(" ");
          const desc = c.visual_appearance || c.overview || "";
          const pSrc = c.portrait_key ? resolveImgSrc(c.portrait_key, c.portrait_rel) : "";
          const pIdx = c.portrait_key ? currentPreviews.findIndex(p => p.key === c.portrait_key) : -1;
          const thumbHtml = pSrc
            ? `<div class="char-portrait checkerboard" ${pIdx >= 0 ? `data-preview-idx="${pIdx}"` : ""} title="点击放大：${escapeHtml(c.character_name)}"><img src="${escapeHtml(pSrc)}" alt="${escapeHtml(c.character_name)}"></div>`
            : "";
          return `
            <div class="review-box" style="margin-bottom:10px;">
              <div class="char-card-row">
                ${thumbHtml}
                <div class="char-body">
                  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
                    <strong>${escapeHtml(c.character_name)}</strong>
                    <div style="display:flex;gap:6px;align-items:center;">
                      <span class="badge badge-accent">${escapeHtml(srcMap[c.source] || c.source)}</span>
                      ${c.source_url ? `<a class="iconbtn" style="padding:2px 8px;font-size:11px;" href="${escapeHtml(c.source_url)}" target="_blank">原文</a>` : ""}
                    </div>
                  </div>
                  ${anch ? `<div class="meta-kv" style="margin-top:2px;">${anch}</div>` : ""}
                  ${desc ? `<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">${escapeHtml(desc)}</div>` : ""}
                </div>
              </div>
            </div>
          `;
        }).join("")
      : "";

    const sheet = document.getElementById("sheet");
    sheet.innerHTML = `
      <div class="shead">
        <div class="sprog" id="sprog"></div>
        <div class="shead-top">
          <div class="meta">
            <h2>${escapeHtml(getFamName(fam))}</h2>
            <div class="sub">
              <code>${escapeHtml(fam.family_slug)}</code>
              <span class="badge badge-plum">${escapeHtml(SUBTRACK_LABEL[fam.scope_subtrack] || fam.scope_subtrack)}</span>
              <span>· 最新主版 <code>#${fam.selected_latest_id}</code></span>
              <span class="badge ${fam.inter_class_risk === "high" || fam.inter_class_risk === "blocked_hygiene" ? "badge-red" : fam.inter_class_risk === "medium" ? "badge-warn" : "badge-sage"}">${escapeHtml(RISK_LABEL[fam.inter_class_risk] || fam.inter_class_risk)}</span>
              ${fam.supports_derivative ? `<span class="badge badge-plum">涉及二创/同人</span>` : ""}
            </div>
          </div>
          <div class="sacts">
            ${DATA.public_redacted ? "" : `<a class="iconbtn" href="${escapeHtml(fam.family_slug)}/latest_template.md" target="_blank">主模板 MD</a>`}
            <a class="iconbtn" href="${escapeHtml(fam.family_slug)}/diagnosis.md" target="_blank">诊断 MD</a>
            ${chars.length ? `<a class="iconbtn" href="${escapeHtml(fam.family_slug)}/character_dossier.md" target="_blank">角色档案 MD</a>` : ""}
            ${DATA.public_redacted ? "" : `<a class="iconbtn" href="${escapeHtml(fam.family_slug)}/family.json" target="_blank">JSON</a>`}
            <button type="button" class="close" id="sheetClose" aria-label="关闭">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 4l8 8M12 4l-8 8"/></svg>
            </button>
          </div>
        </div>
        <div class="stoc" id="stoc">
          <button type="button" class="stoc-item active" data-sec="sec-target">1. 审核对象</button>
          <button type="button" class="stoc-item" data-sec="sec-prompt">2. 当前审核 Prompt (${fam.member_count})</button>
          <button type="button" class="stoc-item" data-sec="sec-audit">3. 审计建议 (仅最新版)</button>
          <button type="button" class="stoc-item" data-sec="sec-wiki-assert">4. Wiki 知识与 Assert (${currentPreviews.length}图)</button>
          <button type="button" class="stoc-item" data-sec="sec-relations">5. 类间联系</button>
          <button type="button" class="stoc-item" data-sec="sec-training">6. 训练建议</button>
        </div>
      </div>

      <div class="sbody">
        <div class="md">
          ${topStripHtml}

          <h2 id="sec-target">1. 审核对象</h2>
          <div class="review-box">
            <div class="meta-kv" style="margin-top:0;">
              <strong>对象标准名：</strong><span>${escapeHtml(getFamName(fam))}</span>
              <strong>栏目归属：</strong><span class="badge">${escapeHtml(TRACK_LABEL[fam.scope_track] || fam.scope_track)}</span>
              <span class="badge badge-plum">${escapeHtml(SUBTRACK_LABEL[fam.scope_subtrack] || fam.scope_subtrack)}</span>
              <strong>主版模板名：</strong><code>${escapeHtml(fam.selected_latest_title)}</code>
            </div>
            <div style="font-size:13px;color:var(--ink-2);">${escapeHtml(fam.classification_evidence || "暂无对象说明")}</div>
            ${cues ? `<div class="meta-kv" style="margin-top:2px;"><strong>所需视觉锚点：</strong>${cues}</div>` : ""}
            ${bnds ? `<div class="meta-kv" style="margin-top:2px;"><strong>判别与豁免边界：</strong>${bnds}</div>` : ""}
            <div style="border-top:1px dashed var(--line);padding-top:9px;margin-top:2px;">
              <div class="review-btns">
                <strong style="font-size:12px;">人工复核：</strong>
                ${revBtnsHtml}
                ${rev.status ? `<button type="button" class="rev-btn" id="btnRevClear">清除</button>` : ""}
                <span id="revSavedHint" style="margin-left:auto;font-size:11.5px;color:var(--muted);">自动保存至 localStorage</span>
              </div>
              <textarea class="review-note" id="revNote" style="margin-top:7px;" placeholder="记录对「${escapeHtml(getFamName(fam))}」的人工复核结论…">${escapeHtml(rev.note || "")}</textarea>
            </div>
          </div>

          <h2 id="sec-prompt">
            <span>2. 当前审核 Prompt（无论好坏完整展示）</span>
            ${fam.member_count >= 2 ? `<button type="button" class="iconbtn" id="btnCompare" aria-pressed="${compareMode}">与最新主版 (#${defaultMember.id}) 并排对比</button>` : ""}
          </h2>
          <blockquote class="bq-tip">
            <strong>默认主版（最新有效版）：</strong><code>#${fam.selected_latest_id} ${escapeHtml(fam.selected_latest_title)}</code>（${defaultMember.chars} 字） · 选取依据：${escapeHtml(fam.version_selection_reason)}
            ${fam.parallel_sub_scopes ? `<br><strong>多场景提示：</strong>该对象存在多个并行子模板，可点击下方版本标签逐个查看原文。` : ""}
          </blockquote>
          <div class="ver-tabs">${verTabsHtml}</div>
          ${versionsBodyHtml}

          <h2 id="sec-audit">3. 审计建议（仅针对最新主版 #${escapeHtml(la.version_key || fam.selected_latest_id)}）</h2>
          <div class="review-box">
            <div class="meta-kv" style="margin-top:0;">
              <strong>主版审计结论：</strong>
              <span class="badge ${laFlags.length || la.disposition !== "active_ip" ? "badge-warn" : "badge-sage"}">${escapeHtml(la.verdict || "待审核")}</span>
              <strong>版本：</strong><code>#${escapeHtml(la.version_key || fam.selected_latest_id)} (${escapeHtml(la.title || fam.selected_latest_title)})</code>
              <span>· 字数 ${la.chars || defaultMember.chars}</span>
              ${la.export_cleanups_count ? `<span class="badge badge-sage">已自动清理 ${la.export_cleanups_count} 处导出硬编码</span>` : ""}
            </div>
            ${laFlags.length ? `<div class="meta-kv"><strong>主版检出缺陷：</strong>${laFlags.map(fl => `<span class="badge badge-warn">${escapeHtml(FLAG_LABEL[fl] || fl)}</span>`).join(" ")}</div>` : ""}
            ${laFindings.length ? `<ul style="margin:4px 0 0 18px;padding:0;font-size:13px;color:var(--crimson);">${laFindings.map(fi => `<li>${escapeHtml(fi)}</li>`).join("")}</ul>` : ""}
            <div style="margin-top:4px;">
              <strong style="font-size:13px;">面向最新主版的修改建议：</strong>
              <ul style="margin:4px 0 0 18px;padding:0;font-size:13.5px;color:var(--ink-2);line-height:1.6;">
                ${laActions.map(a => `<li>${escapeHtml(a)}</li>`).join("")}
              </ul>
            </div>
          </div>
          ${histArchiveHtml}

          <h2 id="sec-wiki-assert">4. Wiki 知识与 Assert 资产</h2>
          ${wikiBox}
          <h3 style="margin:12px 0 6px;font-family:var(--serif);font-size:16px;">Assert 参考图库与抽样角色立绘 (${currentPreviews.length})</h3>
          ${assetGridHtml}
          ${backlogHtml}
          ${charCardsHtml}

          <h2 id="sec-relations">5. 类间联系</h2>
          <div class="review-box">
            <div class="meta-kv" style="margin-top:0;">
              <strong>类间混淆风险：</strong>
              <span class="badge ${fam.inter_class_risk === "high" || fam.inter_class_risk === "blocked_hygiene" ? "badge-red" : fam.inter_class_risk === "medium" ? "badge-warn" : "badge-sage"}">${escapeHtml(RISK_LABEL[fam.inter_class_risk] || fam.inter_class_risk)}</span>
              <strong>模态决策策略：</strong><code>${escapeHtml(req.modality_decision_policy || "-")}</code>
              ${(fam.archetypes || []).map(a => `<span class="badge">${escapeHtml(ARCH_LABEL[a] || a)}</span>`).join(" ")}
            </div>
            <div>
              <strong style="font-size:13px;">同类/共享判别机制的关联对象（点击跳转）：</strong>
              ${peersHtml}
            </div>
            ${genLinksHtml ? `<div><strong style="font-size:13px;">对应的广域通用模板规则：</strong>${genLinksHtml}</div>` : ""}
            ${govLinksHtml}
          </div>

          <h2 id="sec-training">6. 训练建议（CPT / SFT）</h2>
          <div class="review-box">
            <div class="meta-kv" style="margin-top:0;">
              <strong>入训门控状态：</strong><span class="badge ${gateBadgeCls}">${escapeHtml(tr.gate_label || "-")}</span>
              <strong>CPT-SFT 路由标签：</strong><code>${escapeHtml(req.cpt_sft_route || "-")}</code>
            </div>
            <div>
              <strong style="font-size:13px;">CPT（领域知识与视觉锚点注入）：</strong>
              <ul style="margin:4px 0 0 18px;padding:0;font-size:13.5px;color:var(--ink-2);line-height:1.6;">
                ${(tr.cpt_plan || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}
              </ul>
            </div>
            <div>
              <strong style="font-size:13px;">SFT（规则边界与强负例对抗）：</strong>
              <ul style="margin:4px 0 0 18px;padding:0;font-size:13.5px;color:var(--ink-2);line-height:1.6;">
                ${(tr.sft_plan || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}
              </ul>
            </div>
            <div>
              <strong style="font-size:13px;">评测集切分与防泄漏核验：</strong>
              <ul style="margin:4px 0 0 18px;padding:0;font-size:13.5px;color:var(--ink-2);line-height:1.6;">
                ${(tr.eval_plan || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}
              </ul>
            </div>
          </div>
        </div>
        ${snavHtml}
      </div>
    `;

    sheet.querySelector("#sheetClose").addEventListener("click", closeSheet);
    sheet.querySelectorAll(".ver-tab[data-vkey]").forEach(b => b.addEventListener("click", () => {
      currentMemberKey = b.getAttribute("data-vkey");
      renderSheet();
    }));
    const cmpBtn = sheet.querySelector("#btnCompare");
    if (cmpBtn) cmpBtn.addEventListener("click", () => { compareMode = !compareMode; renderSheet(); });

    sheet.querySelectorAll(".rev-btn[data-rev-val]").forEach(b => b.addEventListener("click", () => {
      const val = b.getAttribute("data-rev-val");
      const cur = getReview(fam.family_slug);
      reviews[fam.family_slug] = { status: val, note: cur.note || "", updated_at: new Date().toISOString() };
      saveReviews();
      renderSidebar();
      renderGrid(getFiltered());
      renderSheet();
    }));
    const clrBtn = sheet.querySelector("#btnRevClear");
    if (clrBtn) clrBtn.addEventListener("click", () => {
      delete reviews[fam.family_slug];
      saveReviews();
      renderSidebar();
      renderGrid(getFiltered());
      renderSheet();
    });
    const noteEl = sheet.querySelector("#revNote");
    noteEl.addEventListener("input", () => {
      const cur = getReview(fam.family_slug);
      reviews[fam.family_slug] = { status: cur.status || "", note: noteEl.value, updated_at: new Date().toISOString() };
      saveReviews();
      const hint = sheet.querySelector("#revSavedHint");
      if (hint) hint.textContent = "已保存 ✓";
    });

    sheet.querySelectorAll(".stoc-item[data-sec]").forEach(b => b.addEventListener("click", () => {
      const t = document.getElementById(b.getAttribute("data-sec"));
      if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
    }));
    sheet.querySelectorAll("[data-nav-slug]").forEach(b => b.addEventListener("click", () => {
      openSheet(b.getAttribute("data-nav-slug"));
    }));
    sheet.querySelectorAll("[data-jump-slug]").forEach(b => b.addEventListener("click", () => {
      openSheet(b.getAttribute("data-jump-slug"));
    }));
    sheet.querySelectorAll(".copy-btn").forEach(btn => btn.addEventListener("click", () => {
      const code = btn.parentElement.querySelector("code").textContent || "";
      const done = () => {
        btn.textContent = "已复制";
        btn.classList.add("copied");
        setTimeout(() => { btn.textContent = "复制"; btn.classList.remove("copied"); }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(done).catch(() => {});
      }
    }));
    const jumpAssetsBtn = sheet.querySelector("#btnJumpAssets");
    if (jumpAssetsBtn) {
      jumpAssetsBtn.addEventListener("click", () => {
        const t = document.getElementById("sec-wiki-assert");
        if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    sheet.querySelectorAll(".checkerboard[data-preview-idx]").forEach(el => el.addEventListener("click", () => {
      const item = currentPreviews[Number(el.getAttribute("data-preview-idx"))];
      openLightbox(item);
    }));
  }

  const overlay = document.getElementById("overlay");
  function openSheet(slug, memberKey = null) {
    if (!FAM_BY_SLUG.has(slug)) return;
    currentOpenSlug = slug;
    currentMemberKey = memberKey;
    renderSheet();
    overlay.classList.remove("closing");
    overlay.classList.add("open");
    overlay.scrollTop = 0;
    try { history.replaceState(null, "", "#f=" + encodeURIComponent(slug)); } catch (_) {}
  }
  function closeSheet() {
    if (!overlay.classList.contains("open")) return;
    overlay.classList.add("closing");
    setTimeout(() => {
      overlay.classList.remove("open", "closing");
      currentOpenSlug = null;
    }, 180);
    try { history.replaceState(null, "", location.pathname + location.search); } catch (_) {}
  }

  overlay.addEventListener("scroll", () => {
    const prog = document.getElementById("sprog");
    if (prog) {
      const max = overlay.scrollHeight - overlay.clientHeight;
      prog.style.width = (max > 0 ? Math.min(100, overlay.scrollTop / max * 100) : 0) + "%";
    }
    const secs = ["sec-target", "sec-prompt", "sec-audit", "sec-wiki-assert", "sec-relations", "sec-training"];
    let cur = secs[0];
    for (const id of secs) {
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top < 200) cur = id;
    }
    document.querySelectorAll(".stoc-item").forEach(b => b.classList.toggle("active", b.getAttribute("data-sec") === cur));
  }, { passive: true });
  overlay.addEventListener("click", e => { if (e.target === overlay) closeSheet(); });

  function syncControls() {
    const scBtn = document.getElementById("showcaseToggle");
    if (scBtn) scBtn.setAttribute("aria-pressed", String(state.showShowcase));
    document.getElementById("q").value = state.q;
    document.getElementById("qClear").hidden = !state.q;
    document.getElementById("qKbd").hidden = Boolean(state.q);
    document.getElementById("f-track").value = state.track;
    document.getElementById("f-risk").value = state.risk;
    document.getElementById("f-cov").value = state.cov;
    document.getElementById("f-rev").value = state.rev;
    document.getElementById("sort").value = state.sort;
    document.getElementById("chk-hasimg").checked = state.hasImg;
    const hcEl = document.getElementById("chk-haschar");
    if (hcEl) hcEl.checked = state.hasChar;
    document.getElementById("chk-deriv").checked = state.deriv;
    document.getElementById("chk-multi").checked = state.multi;
    document.getElementById("chk-defect").checked = state.defect;
    document.querySelectorAll(".vbtn[data-view]").forEach(b => b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === state.view)));
  }

  function resetFilters() {
    state.q = ""; state.pillar = "entity_specific"; state.cat = "all"; state.track = ""; state.risk = ""; state.cov = ""; state.rev = "";
    state.flag = ""; state.arch = ""; state.gate = ""; state.visGroup = ""; state.disp = "";
    state.hasImg = false; state.hasChar = false; state.deriv = false; state.multi = false; state.defect = false; state.unreviewed = false;
    renderAll();
  }

  function renderAll() {
    syncControls();
    renderPillarTabs();
    renderCatTabs();
    renderShowcase();
    renderChips();
    renderSidebar();
    renderGrid(getFiltered());
  }

  // Controls wiring
  const scToggleEl = document.getElementById("showcaseToggle");
  if (scToggleEl) scToggleEl.addEventListener("click", () => { state.showShowcase = !state.showShowcase; renderAll(); });
  const qEl = document.getElementById("q");
  qEl.addEventListener("input", () => { state.q = qEl.value; renderAll(); });
  document.getElementById("qClear").addEventListener("click", () => { state.q = ""; renderAll(); qEl.focus(); });
  document.getElementById("f-track").addEventListener("change", e => { state.track = e.target.value; renderAll(); });
  document.getElementById("f-risk").addEventListener("change", e => { state.risk = e.target.value; renderAll(); });
  document.getElementById("f-cov").addEventListener("change", e => { state.cov = e.target.value; renderAll(); });
  document.getElementById("f-rev").addEventListener("change", e => { state.rev = e.target.value; renderAll(); });
  document.getElementById("sort").addEventListener("change", e => { state.sort = e.target.value; renderAll(); });
  document.getElementById("chk-hasimg").addEventListener("change", e => { state.hasImg = e.target.checked; renderAll(); });
  const chkCharEl = document.getElementById("chk-haschar");
  if (chkCharEl) chkCharEl.addEventListener("change", e => { state.hasChar = e.target.checked; renderAll(); });
  document.getElementById("chk-deriv").addEventListener("change", e => { state.deriv = e.target.checked; renderAll(); });
  document.getElementById("chk-multi").addEventListener("change", e => { state.multi = e.target.checked; renderAll(); });
  document.getElementById("chk-defect").addEventListener("change", e => { state.defect = e.target.checked; renderAll(); });
  const btnResetEl = document.getElementById("btnResetFilters");
  if (btnResetEl) btnResetEl.addEventListener("click", resetFilters);

  document.querySelectorAll(".vbtn[data-view]").forEach(b => b.addEventListener("click", () => {
    state.view = b.getAttribute("data-view");
    localStorage.setItem(VIEW_KEY, state.view);
    renderAll();
  }));

  document.getElementById("themeBtn").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", cur);
    localStorage.setItem(THEME_KEY, cur);
  });

  const sideBtn = document.getElementById("sideToggle");
  function setSidebar(open) {
    document.body.classList.toggle("side-open", open);
    localStorage.setItem(SIDE_KEY, open ? "1" : "0");
    sideBtn.setAttribute("aria-pressed", String(open));
  }
  sideBtn.addEventListener("click", () => setSidebar(!document.body.classList.contains("side-open")));

  document.getElementById("btnResetDefaultRev").addEventListener("click", () => {
    try { localStorage.removeItem(REVIEW_KEY); } catch (_) {}
    reviews = { ...(DATA.default_reviews || {}) };
    renderAll();
    if (currentOpenSlug) renderSheet();
  });
  document.getElementById("btnExportRev").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify({ schema: "assert_template_review_v1", exported_at: new Date().toISOString(), reviews }, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "assert_template_reviews.json";
    a.click();
  });
  document.getElementById("btnImportRev").addEventListener("click", () => document.getElementById("importFile").click());
  document.getElementById("importFile").addEventListener("change", e => {
    const f = e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result || "{}"));
        const incoming = parsed.reviews || parsed;
        if (incoming && typeof incoming === "object") {
          reviews = { ...reviews, ...incoming };
          saveReviews();
          renderAll();
          if (currentOpenSlug) renderSheet();
        }
      } catch (err) { alert("导入 JSON 失败: " + err); }
    };
    reader.readAsText(f);
  });

  document.getElementById("exportCsvBtn").addEventListener("click", () => {
    const rows = getFiltered();
    const escCsv = s => '"' + String(s == null ? "" : s).replace(/"/g, '""') + '"';
    const header = ["family_slug", "display_name", "member_count", "selected_latest_id", "selected_latest_title", "inter_class_risk", "supports_derivative", "assert_coverage", "hygiene_flags", "review_status", "review_note"];
    const lines = [header.join(",")];
    for (const f of rows) {
      const r = getReview(f.family_slug);
      lines.push([
        f.family_slug, f.display_name, f.member_count, f.selected_latest_id, f.selected_latest_title,
        f.inter_class_risk, f.supports_derivative, f.assert_asset_coverage.coverage_status,
        (f.all_hygiene_flags || []).join(";"), r.status || "", r.note || "",
      ].map(escCsv).join(","));
    }
    const blob = new Blob(["\ufeff" + lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "assert_templates_filtered.csv";
    a.click();
  });

  // Lightbox & Keyboard shortcuts
  const lb = document.getElementById("lightbox");
  document.getElementById("lb-close").addEventListener("click", () => lb.classList.remove("open"));
  lb.addEventListener("click", e => { if (e.target === lb) lb.classList.remove("open"); });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      if (lb.classList.contains("open")) { lb.classList.remove("open"); return; }
      if (overlay.classList.contains("open")) { closeSheet(); return; }
    }
    const tag = (document.activeElement && document.activeElement.tagName || "").toLowerCase();
    const typing = tag === "input" || tag === "textarea" || tag === "select";
    if (!typing && e.key === "/") {
      e.preventDefault(); qEl.focus(); return;
    }
    if (!typing && e.key === "g" && !overlay.classList.contains("open")) {
      e.preventDefault(); setSidebar(!document.body.classList.contains("side-open")); return;
    }
    if (!typing && overlay.classList.contains("open") && currentOpenSlug) {
      const { prev, next } = navNeighbors(currentOpenSlug);
      if (e.key === "ArrowLeft" && prev) { e.preventDefault(); openSheet(prev.family_slug); }
      else if (e.key === "ArrowRight" && next) { e.preventDefault(); openSheet(next.family_slug); }
    }
  });

  // Scroll progress, sticky header & warm-paper pointer parallax (matching gallery.html)
  const headerEl = document.getElementById("top");
  const progEl = document.getElementById("prog");
  const toTopEl = document.getElementById("toTop");
  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY || document.documentElement.scrollTop || 0;
      const h = document.documentElement.scrollHeight - window.innerHeight;
      headerEl.classList.toggle("scrolled", y > 6);
      progEl.style.width = (h > 0 ? Math.min(100, y / h * 100) : 0) + "%";
      toTopEl.classList.toggle("show", y > 500);
      ticking = false;
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  toTopEl.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduceMotion && window.matchMedia("(pointer:fine)").matches) {
    let mx = 0, my = 0, raf = null;
    window.addEventListener("pointermove", e => {
      mx = (e.clientX / window.innerWidth - 0.5) * 26;
      my = (e.clientY / window.innerHeight - 0.5) * 20;
      if (raf) return;
      raf = requestAnimationFrame(() => {
        document.body.style.setProperty("--gx", mx.toFixed(1) + "px");
        document.body.style.setProperty("--gy", my.toFixed(1) + "px");
        raf = null;
      });
    }, { passive: true });
  }

  // Boot
  const savedTheme = localStorage.getItem(THEME_KEY) || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  populateSelects();
  const sideDefault = localStorage.getItem(SIDE_KEY) === "1";
  setSidebar(sideDefault);
  renderAll();
  const hm = location.hash.match(/^#f=([^&]+)/);
  if (hm) {
    try { openSheet(decodeURIComponent(hm[1])); } catch (_) {}
  }
})();
</script>
</body>
</html>
"""


def build_review_html(
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    taxonomy_path: Path = DEFAULT_TAXONOMY_PATH,
    enrichment_path: Path = DEFAULT_ENRICH_PATH,
    output_html: Path = DEFAULT_OUTPUT_HTML,
    embed_images: bool = True,
    include_prompt_bodies: bool = True,
) -> dict[str, Any]:
    payload = assemble_dashboard_payload(
        templete_dir=templete_dir,
        manifest_path=manifest_path,
        taxonomy_path=taxonomy_path,
        enrichment_path=enrichment_path,
        embed_images=embed_images,
        include_prompt_bodies=include_prompt_bodies,
    )
    json_str = _safe_json_for_script_tag(payload)
    html = HTML_TEMPLATE.replace("__AUDIT_DATA_JSON__", json_str)
    output_html = output_html.resolve()
    output_html.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_html.with_name(output_html.name + ".tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(output_html)
    try:
        rel_out = str(output_html.relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        rel_out = str(output_html)
    return {
        "output_html": rel_out,
        "bytes": output_html.stat().st_size,
        "public_redacted": payload.get("public_redacted", False),
        "total_families": payload["total_families"],
        "total_raw_records": payload["total_raw_records"],
        "total_unpacked_versions": payload["total_unpacked_versions"],
        "total_export_cleanups": payload["total_export_cleanups"],
        "resolved_preview_images": payload["resolved_preview_images"],
        "embedded_images_count": payload["embedded_images_count"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templete-dir", type=Path, default=DEFAULT_TEMPLETE_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output-html", type=Path, default=DEFAULT_OUTPUT_HTML)
    parser.add_argument(
        "--no-embed-images",
        action="store_true",
        help="Skip base64 image embedding and use relative paths instead.",
    )
    parser.add_argument(
        "--public-no-prompts",
        action="store_true",
        help="Omit prompt bodies so the HTML can be safely synced to a public repo.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = build_review_html(
        templete_dir=args.templete_dir,
        manifest_path=args.manifest,
        output_html=args.output_html,
        embed_images=not args.no_embed_images,
        include_prompt_bodies=not args.public_no_prompts,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
