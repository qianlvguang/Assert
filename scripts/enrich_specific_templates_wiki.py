#!/usr/bin/env python3
"""Enrich entity-specific (Track B) audit templates via Assert local rescue & Wikipedia/Commons.

Separates online fetching (`--fetch`) from offline manifest & contact-sheet building (`--build`),
following `docs/standard_image_policy.md` strictly:
  - Existing Assert files rescued deterministically without duplication.
  - New Wiki reference files stored under `assets/standard_images/template_wiki_enrichment/<slug>/`
    with `source.<ext>` + deterministic `reference.png`, full provenance, SHA-256, dHash64,
    `is_synthetic_image=false`, and `review_status="identity_verified_pending_visual_review"`.
  - Contact sheets written to `output/template_wiki_enrichment/contact_sheets/`.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from asset_visual_helpers import dhash64  # noqa: E402

try:
    import resvg_py
except ImportError:
    resvg_py = None

DEFAULT_TAXONOMY_JSON = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.json"
DEFAULT_TEMPLETE_DIR = PROJECT_ROOT / "templete"
DEFAULT_ENRICH_ASSETS_DIR = PROJECT_ROOT / "assets" / "standard_images" / "template_wiki_enrichment"
DEFAULT_OUT_DIR = PROJECT_ROOT / "output" / "template_wiki_enrichment"
DEFAULT_CACHE_PATH = DEFAULT_OUT_DIR / "_wiki_cache.json"
DEFAULT_CONTACT_DIR = DEFAULT_OUT_DIR / "contact_sheets"
DEFAULT_MANIFEST_JSONL = PROJECT_ROOT / "manifests" / "template_wiki_enrichment.jsonl"
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "manifests" / "template_wiki_enrichment_summary.json"

WIKI_USER_AGENT = "AssertTemplateEnricher/1.0 (https://github.com/qianlvguang; standalone-audit-catalog)"
WIKI_HEADERS = {
    "User-Agent": WIKI_USER_AGENT,
    "Accept": "application/json,image/*,*/*;q=0.8",
}

# Verified local files already on disk in Assert that were not linked in template_library_manifest.json
LOCAL_RESCUE_MAP: dict[str, list[str]] = {
    "alabama": ["sports_crests_supplement/ncaa/alabama_333.png"],
    "bp": ["sch96_ip_supplement/brands/ip_bp.png"],
    "duke_university": ["sports_crests_supplement/ncaa/duke_150.png"],
    "florida": ["sports_crests_supplement/ncaa/florida_57.png"],
    "libertyuniversity": ["sports_crests_supplement/ncaa/liberty_2335.png"],
    "ohio": ["sports_crests_supplement/ncaa/ohio_state_194.png"],
    "oklahoma_university": ["sports_crests_supplement/ncaa/oklahoma_201.png"],
    "oregon": ["sports_crests_supplement/ncaa/oregon_2483.png"],
    "pokemon": [
        "assets/standard_images/pokemon_artwork/0025_pikachu/pokeapi_official_artwork/source.png",
        "assets/standard_images/pokemon_artwork/0006_charizard/pokeapi_official_artwork/source.png",
        "assets/standard_images/pokemon_artwork/0001_bulbasaur/pokeapi_official_artwork/source.png",
    ],
    "uga": ["sports_crests_supplement/ncaa/georgia_61.png"],
    "university_of_michigan": ["sports_crests_supplement/ncaa/michigan_130.png"],
    "universityofkentucky": ["sports_crests_supplement/ncaa/kentucky_96.png"],
}

# Pure structural / design-patent templates with no canonical Wiki visual entity
MANUAL_PATENT_SLUGS: set[str] = {
    "ajsnifty",
    "crocs_charms",
    "cucu",
    "cwt_legging",
    "doubleendedhandtool",
    "genies_perfume_atomizer",
    "jiaxiangye",
    "parkerbabyco",
    "pickulsgizmo",
    "shingbright",
    "tangle",
    "wondermachines",
    "yanding",
}

# Curated Wikipedia page titles grounded in the exact cleaned template prompt text
WIKI_TITLE_OVERRIDES: dict[str, str] = {
    "511": "5.11 Tactical",
    "abba": "ABBA",
    "acdcllm": "AC/DC",
    "adanola": "Adanola",
    "adventuretime": "Adventure Time",
    "agv": "AGV (company)",
    "alexandermcqueen": "Alexander McQueen",
    "alemannia_aachen": "Alemannia Aachen",
    "all_blacks": "New Zealand national rugby union team",
    "ami": "Ami Paris",
    "amiri": "Amiri (fashion house)",
    "amongus": "Among Us",
    "angry_birds": "Angry Birds",
    "annabelle": "Annabelle (doll)",
    "anpanman": "Anpanman",
    "apf": "Paraguayan Football Association",
    "apple": "Apple Watch",
    "arizona_university": "University of Arizona",
    "asmodee": "Asmodee",
    "atari": "Atari",
    "attack_on_titan": "Attack on Titan",
    "badcutebunny": "Bad Cute Bunny",
    "balenciaga_1103trademark": "Balenciaga",
    "banana_republic": "Banana Republic",
    "bebe": "Bebe Stores",
    "beck_s": "Beck's Brewery",
    "bench": "Bench (British clothing brand)",
    "benchmade": "Benchmade",
    "bensonboone": "Benson Boone",
    "bentley": "Bentley",
    "berserk": "Berserk (manga)",
    "beyonce": "Beyoncé",
    "bigfoot": "Bigfoot",
    "billionaire_boys_club": "Billionaire Boys Club (clothing retailer)",
    "bleach": "Bleach (TV series)",
    "bmw": "BMW",
    "brawl_stars": "Brawl Stars",
    "budweiser": "Budweiser",
    "buick": "Buick",
    "burberry": "Burberry",
    "butterfly": "Tamasu",
    "calvin_klein": "Calvin Klein",
    "cbf": "Brazilian Football Confederation",
    "celine": "Celine (brand)",
    "chainsawman": "Chainsaw Man",
    "champion": "Champion (sportswear)",
    "chanel_cc": "Chanel",
    "chevrolet": "Chevrolet",
    "chloe": "Chloé",
    "clash_royale": "Clash Royale",
    "cobra": "Cobra (manga)",
    "cohiba": "Cohiba (cigar brand)",
    "converseallstar": "Chuck Taylor All-Stars",
    "cookie_run": "Cookie Run",
    "cookies": "Cookies (company)",
    "coraline": "Coraline (film)",
    "corona": "Corona (beer)",
    "costadelmar_costa": "Costa Del Mar",
    "courtneymorgenstern": "Courtney Morgenstern",
    "covernat": "Covernat",
    "cowboybebop": "Cowboy Bebop",
    "crayonshinchan": "Crayon Shin-chan",
    "daddario": "D'Addario",
    "dandys_world": "Dandy's World",
    "dav_pilkey_dogman": "Dog Man",
    "dc_comics": "DC Comics",
    "dc_shoes": "DC Shoes",
    "demon_slayer": "Demon Slayer: Kimetsu no Yaiba",
    "dior": "Dior",
    "disney": "The Walt Disney Company",
    "dodge": "Dodge",
    "dominos": "Domino's",
    "dragonball": "Dragon Ball",
    "dsquared2": "Dsquared2",
    "dune": "Dune (franchise)",
    "ecco": "ECCO",
    "elvis": "Elvis Presley",
    "et": "E.T. the Extra-Terrestrial",
    "evelknievel": "Evel Knievel",
    "fallout": "Fallout (franchise)",
    "fender": "Fender Musical Instruments Corporation",
    "ferrari": "Ferrari",
    "ford": "Ford Motor Company",
    "forza": "Forza",
    "friends": "Friends",
    "gant": "Gant (retailer)",
    "gap": "Gap Inc.",
    "glassangelofficial": "Glass Angel",
    "godzilla": "Godzilla",
    "goodyear": "Goodyear Tire and Rubber Company",
    "goorinbros": "Goorin Bros.",
    "gopro_logoauto": "GoPro",
    "gorillaglue": "Gorilla Glue",
    "greenday": "Green Day",
    "guess": "Guess (clothing)",
    "guinness": "Guinness",
    "gulf": "Gulf Oil",
    "gunsnroses": "Guns N' Roses",
    "haribotitle": "Haribo",
    "harrypotter": "Harry Potter",
    "hatsune_miku": "Hatsune Miku",
    "hells_angles_motorcycle": "Hells Angels",
    "hendrickmotorsports": "Hendrick Motorsports",
    "hermes": "Hermès",
    "higuchi_yuko": "Yuko Higuchi",
    "hilton": "Hilton Worldwide",
    "hollister": "Hollister Co.",
    "honda": "Honda",
    "hotstuff": "Hot Stuff the Little Devil",
    "itmovie": "It (2017 film)",
    "jeep": "Jeep",
    "jenny_urquhart": "Jenny Urquhart",
    "jim_beam": "Jim Beam",
    "juicewrld": "Juice Wrld",
    "jujutsukaisen": "Jujutsu Kaisen",
    "juliusk9": "Julius-K9",
    "junjiito": "Junji Ito",
    "kaffe": "KAFFE (clothing)",
    "kimesranch": "Kimes Ranch",
    "kirby": "Kirby (series)",
    "kith": "Kith (brand)",
    "ktm": "KTM",
    "lacoste": "Lacoste",
    "ledzeppelin": "Led Zeppelin",
    "legorelated": "Lego",
    "lindseyferrell": "Lindsey Ferrell",
    "lionel_messi": "Lionel Messi",
    "loewe": "Loewe (fashion brand)",
    "louisvuitton": "Louis Vuitton",
    "lupinthethird": "Lupin the Third",
    "maison_margiela": "Maison Margiela",
    "mandms": "M&M's",
    "maradona": "Diego Maradona",
    "marcon": "Macron (sportswear)",
    "marilyn_monroe": "Marilyn Monroe",
    "marshall": "Marshall Amplification",
    "marvel": "Marvel Comics",
    "maryland": "University of Maryland, College Park",
    "mastermind": "Mastermind Japan",
    "mcdonald": "McDonald's",
    "mcm": "MCM Worldwide",
    "mega": "Mega Brands",
    "megaman": "Mega Man",
    "meitanteikonan": "Case Closed",
    "men_of_mayhem": "Men of Mayhem",
    "mercedes_benz": "Mercedes-Benz",
    "metallica": "Metallica",
    "michael_jackson": "Michael Jackson",
    "michigan_state": "Michigan State University",
    "miffyrabbit": "Miffy",
    "milwaukeetool": "Milwaukee Electric Tool Corporation",
    "minions": "Minions (Despicable Me)",
    "mitsubishipencil": "Mitsubishi Pencil Company",
    "miumiu": "Miu Miu",
    "molson_coors": "Molson Coors",
    "monchhichi": "Monchhichi",
    "money_heist_la_casa_de_papel": "Money Heist",
    "monopoly": "Monopoly (game)",
    "monsterenergy": "Monster Energy",
    "monsterhigh": "Monster High",
    "moschino": "Moschino",
    "mr_men_little_miss": "Mr. Men",
    "muhammad_ali": "Muhammad Ali",
    "my_dress": "My Dress-Up Darling",
    "my_hero_academia": "My Hero Academia",
    "naruto": "Naruto",
    "nba": "National Basketball Association",
    "nebraska": "University of Nebraska–Lincoln",
    "new_holland": "New Holland Agriculture",
    "newbalance": "New Balance",
    "neymar": "Neymar",
    "nhl": "National Hockey League",
    "nike": "Nike, Inc.",
    "nike_jordan": "Air Jordan",
    "ninewest": "Nine West",
    "nirvana": "Nirvana (band)",
    "novak_djokovic": "Novak Djokovic",
    "oakley": "Oakley, Inc.",
    "ohayou_spank": "Ohayō! Spank",
    "olympic": "Olympic Games",
    "one_direction": "One Direction",
    "one_piece": "One Piece",
    "oster": "Sunbeam Products",
    "pandorobo": "Pan Dorobou",
    "panini_0325quanliang": "Panini Group",
    "patagonia": "Patagonia, Inc.",
    "paw_patrol": "PAW Patrol",
    "peanuts": "Peanuts",
    "pepsi": "Pepsi",
    "pikmin": "Pikmin",
    "pinkpanther": "The Pink Panther",
    "pitbull": "Pitbull (rapper)",
    "plexaderm": "Plexaderm",
    "postyaustin": "Post Malone",
    "prada": "Prada",
    "purina": "Purina",
    "purple_innovation": "Purple (company)",
    "purplebrand": "Purple Brand",
    "rabanne_bag": "Paco Rabanne",
    "ralph_lauren": "Ralph Lauren Corporation",
    "ratt": "Ratt",
    "rbfa": "Royal Belgian Football Association",
    "rezero": "Re:Zero − Starting Life in Another World",
    "rfef": "Royal Spanish Football Federation",
    "rickandmorty": "Rick and Morty",
    "rilakkuma": "Rilakkuma",
    "rockybalboa": "Rocky Balboa",
    "rundmc": "Run-DMC",
    "rusty": "Rusty (surfwear)",
    "samsung_phonecase": "Samsung",
    "sandmaennchen": "Sandmännchen",
    "scoobydoo": "Scooby-Doo",
    "scott": "Scott Paper Company",
    "sesame_street": "Sesame Street",
    "sevendeadlysins": "The Seven Deadly Sins (manga)",
    "sharks_rugby": "Sharks (rugby union)",
    "shein_mark": "Shein",
    "shell": "Shell plc",
    "shimano": "Shimano",
    "slamdunk": "Slam Dunk (manga)",
    "slayer": "Slayer",
    "spirit": "Spirit: Stallion of the Cimarron",
    "spongebobsquarepants": "SpongeBob SquarePants",
    "spotit": "Dobble",
    "squishmallows": "Squishmallows",
    "starbucks": "Starbucks",
    "startrek": "Star Trek",
    "stealabrainrot": "Italian brainrot",
    "stoneisland": "Stone Island",
    "strawberryshortcake": "Strawberry Shortcake",
    "streetfighter": "Street Fighter",
    "sunlight": "Sunlight (cleaning product)",
    "super_mario": "Super Mario",
    "supreme": "Supreme (brand)",
    "suzuki": "Suzuki",
    "swarovski": "Swarovski",
    "taylorswift": "Taylor Swift",
    "tesla": "Tesla, Inc.",
    "thebadguys": "The Bad Guys (film)",
    "thenewyorker": "The New Yorker",
    "thesecretlifeofpets": "The Secret Life of Pets",
    "thesimpsonver2": "The Simpsons",
    "thomasandfriends": "Thomas & Friends",
    "tiffanyco_tiffany": "Tiffany & Co.",
    "tokyoghoul": "Tokyo Ghoul",
    "tomandjerry": "Tom and Jerry",
    "tommy_hilfiger": "Tommy Hilfiger (company)",
    "totto": "Totto",
    "toyota": "Toyota",
    "transportforlondon": "Transport for London",
    "triumph": "Triumph Motorcycles Ltd",
    "trolls": "Trolls (franchise)",
    "tumi": "Tumi, Inc.",
    "ucl_wenzi": "University of California, Los Angeles",
    "ugg": "Ugg boots",
    "underdog": "Underdog (TV series)",
    "university_of_utah": "University of Utah",
    "usmc": "United States Marine Corps",
    "van_cleef_arpels": "Van Cleef & Arpels",
    "velcro": "Velcro",
    "vetements": "Vetements",
    "vision_street_wear": "Vision Street Wear",
    "vivienne_westwood": "Vivienne Westwood",
    "vogue": "Vogue (magazine)",
    "volkswagen": "Volkswagen",
    "warhammer": "Warhammer",
    "whirlpool": "Whirlpool Corporation",
    "whitefox": "White Fox Boutique",
    "wickedtrademark": "Wicked (musical)",
    "wilson": "Wilson Sporting Goods",
    "windows": "Microsoft Windows",
    "wku": "Western Kentucky University",
    "wwe_wrestle": "WWE",
    "yamal": "Lamine Yamal",
    "yeti": "Yeti Holdings",
    "zelda": "The Legend of Zelda",
    "zigzag": "Zig-Zag (company)",
    "zipit": "Zipit",
    "zippo": "Zippo",
}

DENY_FILE_RE = re.compile(
    r"(?:commons-logo|wiki|ambox|padlock|question_book|edit-|flag_of_|map_of_|"
    r"locator_map|location_map|signature|autograph|icon_external|disambig|"
    r"crystal_clear|nuvola_|pictogram|\.ogg$|\.ogv$|\.webm$|\.pdf$|\.djvu$|\.tif+$)",
    re.IGNORECASE,
)

# Explicit replacement hints for visual QA catches (prioritize wordmark/logo SVG/PNG, forbid portraits/statues/museums)
EXPLICIT_FILE_HINTS: dict[str, list[str]] = {
    "alexandermcqueen": ["Alexander_McQueen_Logo.svg", "Alexander_McQueen_logo.svg", "McQueen_logo.svg"],
    "calvin_klein": ["Calvin_klein_logo.svg", "Calvin_Klein_logo.svg", "Calvin_klein_text_logo.svg", "CK_Calvin_Klein_logo.svg"],
    "dsquared2": ["Dsquared2_logo.svg", "DSQUARED2_Logo.svg", "Dsquared2_wordmark.svg"],
    "nike_jordan": ["Jumpman_logo.svg", "Air_Jordan_Logo.svg", "Jordan_logo.svg"],
    "oster": ["Oster_logo.svg", "Oster_wordmark.svg", "Osterizer_logo.png"],
    "vivienne_westwood": ["Vivienne_Westwood_logo.svg", "Vivienne_Westwood_Orb_logo.svg"],
    "velcro": ["Velcro_logo.svg", "Velcro_Companies_logo.svg", "Velcro-logo.svg"],
    "minions": ["Minions_logo.png", "Minions_The_Rise_of_Gru_logo.png", "Minions_(film)_logo.svg"],
    "rabanne_bag": ["Rabanne_logo.svg", "Paco_Rabanne_logo.svg", "Paco_Rabanne_wordmark.svg"],
    "meitanteikonan": ["Detective_Conan_logo.svg", "Case_Closed_logo.svg", "Meitantei_Conan_logo.svg"],
    "evelknievel": ["Evel_Knievel_logo.svg", "Evel_Knievel_logo.png"],
}

EXPLICIT_SEARCH_HINTS: dict[str, list[str]] = {
    "alexandermcqueen": ["Alexander McQueen logo", "McQueen fashion logo"],
    "calvin_klein": ["Calvin Klein logo", "Calvin Klein wordmark"],
    "dsquared2": ["Dsquared2 logo", "DSQUARED2"],
    "nike_jordan": ["Jumpman logo", "Air Jordan logo"],
    "oster": ["Oster logo", "Osterizer"],
    "vivienne_westwood": ["Vivienne Westwood logo", "Vivienne Westwood orb"],
    "velcro": ["Velcro logo", "Velcro brand logo"],
    "minions": ["Minions logo", "Despicable Me Minions logo"],
    "rabanne_bag": ["Paco Rabanne logo", "Rabanne wordmark"],
    "meitanteikonan": ["Detective Conan logo", "Case Closed logo", "Meitantei Conan"],
    "evelknievel": ["Evel Knievel emblem", "Evel Knievel"],
}

REPLACE_DENY_RE = re.compile(
    r"(?:portrait|shankbone|fashionwirepress|roundel|sculpture|statue|hooks|"
    r"museum|visited|sunbeam|upstage|chestertons|shutterstock|getty|1967|"
    r"cropped|headshot|by_[a-z]+_[a-z]+\.jpe?g)",
    re.IGNORECASE,
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _http_get_bytes(url: str, *, timeout: float = 25.0, retries: int = 2) -> tuple[bytes, str]:
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=WIKI_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                ctype = str(resp.headers.get("Content-Type") or "")
                return resp.read(), ctype
        except Exception as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(1.0 + attempt)
    raise RuntimeError(f"HTTP fetch failed for {url}: {last_err}")


def _http_get_json(url: str, *, delay: float = 0.2) -> dict[str, Any]:
    if delay > 0:
        time.sleep(delay)
    raw, _ = _http_get_bytes(url)
    return json.loads(raw.decode("utf-8"))


def _clean_wiki_filename(raw: str) -> str | None:
    s = str(raw or "").strip()
    if not s:
        return None
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()
    m_wiki = re.search(r"\[\[(?:File|Image):([^|\]]+)", s, re.I)
    if m_wiki:
        s = m_wiki.group(1).strip()
    m_gal = re.search(r"(?:File|Image):([^|\n\]]+\.(?:svg|png|jpe?g|webp))", s, re.I)
    if m_gal:
        s = m_gal.group(1).strip()
    s = re.sub(r"^(?:File|Image):", "", s, flags=re.I).strip()
    s = s.split("|")[0].strip().strip("[]{}<>\"'")
    if not s or "." not in s:
        return None
    ext = s.rsplit(".", 1)[-1].lower()
    if ext not in {"svg", "png", "jpg", "jpeg", "webp"}:
        return None
    if DENY_FILE_RE.search(s):
        return None
    return s.replace(" ", "_")


def _parse_infobox_candidates(wikitext: str, subtrack: str) -> list[str]:
    if not wikitext:
        return []
    if subtrack in {"B4_specific_celebrity_band_artist", "B2_specific_anime_game_media_ip"}:
        preferred_keys = [
            "logo", "image_logo", "wordmark", "emblem", "crest",
            "image", "image_name", "img", "poster",
        ]
    else:
        preferred_keys = [
            "logo", "image_logo", "company_logo", "wordmark", "emblem", "crest",
            "symbol", "seal", "badge", "image", "image_name", "img",
        ]
    found: list[str] = []
    seen: set[str] = set()
    for key in preferred_keys:
        pat = re.compile(rf"^\s*\|\s*{key}\s*=\s*(.+)$", re.I | re.M)
        for m in pat.finditer(wikitext):
            fn = _clean_wiki_filename(m.group(1))
            if fn and fn not in seen:
                seen.add(fn)
                found.append(fn)
    return found


def _batch_wiki_pages(titles: list[str]) -> dict[str, dict[str, Any]]:
    """Queries English Wikipedia in batches of 20 titles with extracts, wikitext, and pageimage."""
    results: dict[str, dict[str, Any]] = {}
    for start in range(0, len(titles), 20):
        batch = titles[start : start + 20]
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "titles": "|".join(batch),
            "prop": "extracts|revisions|pageimages|info",
            "exintro": "1",
            "explaintext": "1",
            "exsentences": "3",
            "rvprop": "content",
            "rvsection": "0",
            "piprop": "name|original|thumbnail",
            "pithumbsize": "1024",
            "inprop": "url",
        }
        url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        data = _http_get_json(url, delay=0.25)
        q = data.get("query") or {}
        norm_map = {n["from"]: n["to"] for n in q.get("normalized") or []}
        redir_map = {r["from"]: r["to"] for r in q.get("redirects") or []}
        pages_by_title = {p.get("title", ""): p for p in q.get("pages") or [] if not p.get("missing")}
        for orig in batch:
            t = norm_map.get(orig, orig)
            seen_t = set()
            while t in redir_map and t not in seen_t:
                seen_t.add(t)
                t = redir_map[t]
            if t in pages_by_title:
                p = pages_by_title[t]
                revs = p.get("revisions") or []
                wikitext = revs[0].get("content", "") if revs else ""
                results[orig] = {
                    "wiki_title": p.get("title", t),
                    "wiki_url": p.get("fullurl") or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(p.get('title', t).replace(' ', '_'))}",
                    "extract": (p.get("extract") or "").strip(),
                    "pageimage": p.get("pageimage"),
                    "wikitext_head": wikitext[:4000],
                }
    return results


def _search_commons_logo(query: str, subtrack: str) -> list[str]:
    """Searches Wikimedia Commons File namespace for official logos/marks with strict token checks."""
    suffix = " logo" if subtrack in {"B1_specific_brand_trademark", "B3_specific_sports_university"} else ""
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "list": "search",
        "srnamespace": "6",
        "srlimit": "8",
        "srsearch": f"{query}{suffix}".strip(),
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        data = _http_get_json(url, delay=0.2)
    except Exception:
        return []
    tokens = [t for t in re.findall(r"[a-z0-9]{2,}", query.lower()) if t not in {"the", "inc", "ltd", "company", "brand", "band", "film", "game"}]
    cands: list[tuple[int, str]] = []
    for hit in (data.get("query") or {}).get("search") or []:
        title = str(hit.get("title") or "")
        fn = _clean_wiki_filename(title)
        if not fn:
            continue
        low = fn.lower()
        if tokens and not any(tok in low for tok in tokens):
            continue
        score = 0
        if low.endswith(".svg"):
            score += 40
        elif low.endswith(".png"):
            score += 25
        if any(w in low for w in ("logo", "wordmark", "emblem", "crest", "seal", "insignia", "badge")):
            score += 30
        if any(w in low for w in ("headquarters", "store", "building", "shop", "sign", "plaza")):
            score -= 20
        cands.append((score, fn))
    cands.sort(key=lambda x: (-x[0], len(x[1])))
    return [fn for _, fn in cands[:4]]


def _resolve_file_imageinfo(filenames: list[str]) -> dict[str, dict[str, Any]]:
    """Resolves `File:<name>` metadata from enwiki (which transparently proxies Wikimedia Commons)."""
    out: dict[str, dict[str, Any]] = {}
    for start in range(0, len(filenames), 20):
        batch = filenames[start : start + 20]
        titles = [f"File:{fn}" if not fn.startswith("File:") else fn for fn in batch]
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "titles": "|".join(titles),
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": "1024",
        }
        url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        data = _http_get_json(url, delay=0.2)
        q = data.get("query") or {}
        norm_map = {n["from"]: n["to"] for n in q.get("normalized") or []}
        by_title = {p.get("title", ""): p for p in q.get("pages") or []}
        for orig_fn, t in zip(batch, titles):
            nt = norm_map.get(t, t)
            page = by_title.get(nt) or by_title.get(t)
            if not page:
                continue
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            ii = infos[0]
            extmeta = ii.get("extmetadata") or {}
            lic = ((extmeta.get("LicenseShortName") or {}).get("value") or "unknown").strip()
            artist_raw = ((extmeta.get("Artist") or {}).get("value") or "").strip()
            artist = re.sub(r"<[^>]+>", "", artist_raw).strip() or "unknown"
            out[orig_fn] = {
                "file_title": nt,
                "description_url": ii.get("descriptionurl") or "",
                "download_url": ii.get("url") or "",
                "thumb_url": ii.get("thumburl") or "",
                "mime": ii.get("mime") or "",
                "width": ii.get("width"),
                "height": ii.get("height"),
                "license": lic,
                "artist": artist,
                "imagerepository": page.get("imagerepository") or "wikipedia",
            }
    return out


def _detect_ext(raw: bytes, ctype: str, fallback_url: str) -> str:
    head = raw[:512].lstrip()
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    if raw.startswith(b"GIF87a") or raw.startswith(b"GIF89a"):
        return "gif"
    if b"<svg" in head.lower() or "svg" in ctype.lower() or fallback_url.lower().endswith(".svg"):
        return "svg"
    return "png"


def _save_source_and_reference(raw: bytes, ctype: str, download_url: str, target_dir: Path) -> dict[str, Any]:
    target_dir.mkdir(parents=True, exist_ok=True)
    ext = _detect_ext(raw, ctype, download_url)
    source_path = target_dir / f"source.{ext}"
    ref_path = target_dir / "reference.png"

    source_path.write_bytes(raw)
    transform_history = ["downloaded_original"]

    if ext == "svg":
        if resvg_py is None:
            raise RuntimeError("resvg_py unavailable to convert SVG deterministically")
        png_bytes = resvg_py.svg_to_bytes(svg_string=raw.decode("utf-8", errors="replace"), width=1024)
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        transform_history.append("resvg_rasterized_1024px")
    else:
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        transform_history.append("decoded_native_bitmap")

    # Reject completely empty / blank alpha images
    arr_alpha = img.getchannel("A")
    if arr_alpha.getextrema() == (0, 0):
        raise ValueError("decoded image is completely transparent/empty")

    tmp_ref = ref_path.with_name("reference.tmp.png")
    img.save(tmp_ref, format="PNG", optimize=True)
    tmp_ref.replace(ref_path)

    w, h = img.size
    return {
        "source_rel": source_path.relative_to(PROJECT_ROOT).as_posix(),
        "reference_rel": ref_path.relative_to(PROJECT_ROOT).as_posix(),
        "sha256": _sha256_file(ref_path),
        "source_sha256": _sha256_file(source_path),
        "width": w,
        "height": h,
        "dhash64": dhash64(img),
        "native_resolution_below_512": ext != "svg" and max(w, h) < 512,
        "transform_history": transform_history,
    }


def _load_existing_assert_map(templete_dir: Path, slug: str) -> dict[str, Any]:
    fam = json.loads((templete_dir / slug / "family.json").read_text(encoding="utf-8"))
    cov = fam.get("assert_asset_coverage") or {}
    approved_imgs: list[str] = []
    for m in cov.get("approved_matches") or []:
        for im in m.get("images") or []:
            cand = Path(im) if (PROJECT_ROOT / im).is_file() else Path(str(im).removeprefix("assets/"))
            if (PROJECT_ROOT / cand).is_file():
                approved_imgs.append(cand.as_posix())
    supp_imgs: list[str] = []
    for m in cov.get("supplement_matches") or []:
        lp = str(m.get("local_path") or "")
        if lp:
            cand = Path(lp) if (PROJECT_ROOT / lp).is_file() else Path(lp.removeprefix("assets/"))
            if (PROJECT_ROOT / cand).is_file():
                supp_imgs.append(cand.as_posix())
    return {
        "coverage_status": cov.get("coverage_status", "no_assert_match"),
        "approved_paths": sorted(set(approved_imgs)),
        "supplement_paths": sorted(set(supp_imgs)),
    }


def run_fetch(
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    assets_dir: Path = DEFAULT_ENRICH_ASSETS_DIR,
    cache_path: Path = DEFAULT_CACHE_PATH,
    limit: int = 0,
    retry_failed: bool = False,
) -> dict[str, Any]:
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    track_b = [f for f in tax["families"] if f["scope_track"] == "entity_specific"]

    cache: dict[str, Any] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    cache.setdefault("wiki_pages", {})
    cache.setdefault("commons_searches", {})
    cache.setdefault("file_infos", {})
    cache.setdefault("downloads", {})

    # Determine wiki titles needed for ALL Track B families (for summary + missing-image fetching)
    slug_to_title: dict[str, str] = {}
    missing_img_slugs: list[str] = []
    for f in track_b:
        slug = f["family_slug"]
        existing = _load_existing_assert_map(templete_dir, slug)
        has_local = bool(existing["approved_paths"] or existing["supplement_paths"] or slug in LOCAL_RESCUE_MAP)
        if not has_local and slug not in MANUAL_PATENT_SLUGS:
            missing_img_slugs.append(slug)
        if slug not in MANUAL_PATENT_SLUGS:
            title = WIKI_TITLE_OVERRIDES.get(slug) or slug.replace("_", " ").title()
            slug_to_title[slug] = title

    if limit > 0:
        missing_img_slugs = missing_img_slugs[:limit]

    # 1. Batch query Wikipedia summaries + infobox wikitext for any uncached titles
    titles_to_fetch = sorted({t for s, t in slug_to_title.items() if t not in cache["wiki_pages"]})
    if titles_to_fetch:
        fetched = _batch_wiki_pages(titles_to_fetch)
        cache["wiki_pages"].update(fetched)
        # Mark genuinely missing titles so we don't keep hitting them
        for t in titles_to_fetch:
            if t not in cache["wiki_pages"]:
                cache["wiki_pages"][t] = {"missing": True}
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Gather candidate image filenames for missing_img_slugs
    slug_candidates: dict[str, list[str]] = {}
    files_to_resolve: set[str] = set()
    for f in track_b:
        slug = f["family_slug"]
        if slug not in missing_img_slugs:
            continue
        prev_dl = cache["downloads"].get(slug)
        ref_file = assets_dir / slug / "reference.png"
        if prev_dl and prev_dl.get("status") == "downloaded" and ref_file.is_file():
            continue
        if prev_dl and prev_dl.get("status") == "no_file" and not retry_failed:
            continue

        title = slug_to_title.get(slug, "")
        wpage = cache["wiki_pages"].get(title) or {}
        cands: list[str] = []
        if not wpage.get("missing"):
            cands.extend(_parse_infobox_candidates(wpage.get("wikitext_head", ""), f["scope_subtrack"]))
            pi = wpage.get("pageimage")
            pi_clean = _clean_wiki_filename(pi or "")
            if pi_clean and pi_clean not in cands:
                cands.append(pi_clean)

        # If no logo/SVG found in infobox yet, also check Wikimedia Commons search
        if not any(c.lower().endswith(".svg") or "logo" in c.lower() for c in cands):
            c_key = f"{title}::{f['scope_subtrack']}"
            if c_key not in cache["commons_searches"]:
                cache["commons_searches"][c_key] = _search_commons_logo(title, f["scope_subtrack"])
            for fn in cache["commons_searches"][c_key]:
                if fn not in cands:
                    cands.append(fn)

        slug_candidates[slug] = cands[:5]
        for fn in slug_candidates[slug]:
            if fn not in cache["file_infos"]:
                files_to_resolve.add(fn)

    if files_to_resolve:
        resolved = _resolve_file_imageinfo(sorted(files_to_resolve))
        cache["file_infos"].update(resolved)
        for fn in files_to_resolve:
            if fn not in cache["file_infos"]:
                cache["file_infos"][fn] = {"missing": True}
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. Download best valid image candidate per slug
    dl_ok = 0
    dl_fail = 0
    for idx, slug in enumerate(missing_img_slugs, 1):
        ref_file = assets_dir / slug / "reference.png"
        prev_dl = cache["downloads"].get(slug)
        if prev_dl and prev_dl.get("status") == "downloaded" and ref_file.is_file():
            continue
        cands = slug_candidates.get(slug) or []
        saved = False
        for fn in cands:
            ii = cache["file_infos"].get(fn) or {}
            if ii.get("missing"):
                continue
            dl_url = ii.get("download_url") or ""
            if not dl_url:
                continue
            # Prefer rasterized thumburl for huge >4MB raster files, or raw SVG so resvg converts cleanly
            is_svg = dl_url.lower().endswith(".svg") or "svg" in str(ii.get("mime") or "").lower()
            fetch_url = dl_url if is_svg else (ii.get("thumb_url") or dl_url)
            try:
                time.sleep(0.15)
                raw, ctype = _http_get_bytes(fetch_url)
                if not is_svg and b"<svg" in raw[:200].lower():
                    pass
                saved_meta = _save_source_and_reference(raw, ctype, fetch_url, assets_dir / slug)
                title = slug_to_title.get(slug, "")
                wpage = cache["wiki_pages"].get(title) or {}
                cache["downloads"][slug] = {
                    "status": "downloaded",
                    "wiki_title": wpage.get("wiki_title") or title,
                    "source_page_url": wpage.get("wiki_url") or ii.get("description_url") or "",
                    "file_description_url": ii.get("description_url") or "",
                    "download_url": fetch_url,
                    "publisher": ii.get("imagerepository") or "wikimedia",
                    "license": ii.get("license") or "unknown",
                    "artist": ii.get("artist") or "unknown",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    **saved_meta,
                }
                saved = True
                dl_ok += 1
                break
            except Exception as exc:
                # Try thumburl fallback if SVG resvg failed
                if is_svg and ii.get("thumb_url"):
                    try:
                        time.sleep(0.15)
                        raw, ctype = _http_get_bytes(ii["thumb_url"])
                        saved_meta = _save_source_and_reference(raw, ctype, ii["thumb_url"], assets_dir / slug)
                        title = slug_to_title.get(slug, "")
                        wpage = cache["wiki_pages"].get(title) or {}
                        cache["downloads"][slug] = {
                            "status": "downloaded",
                            "wiki_title": wpage.get("wiki_title") or title,
                            "source_page_url": wpage.get("wiki_url") or ii.get("description_url") or "",
                            "file_description_url": ii.get("description_url") or "",
                            "download_url": ii["thumb_url"],
                            "publisher": ii.get("imagerepository") or "wikimedia",
                            "license": ii.get("license") or "unknown",
                            "artist": ii.get("artist") or "unknown",
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                            **saved_meta,
                        }
                        saved = True
                        dl_ok += 1
                        break
                    except Exception:
                        pass
                cache["downloads"][slug] = {"status": "fetch_error", "error": str(exc), "last_url": fetch_url}
        if not saved:
            if slug not in cache["downloads"] or cache["downloads"][slug].get("status") != "fetch_error":
                cache["downloads"][slug] = {"status": "no_file", "candidates_tried": cands}
            dl_fail += 1
        if idx % 20 == 0:
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "missing_img_targets": len(missing_img_slugs),
        "downloaded_new": dl_ok,
        "unresolved_or_error": dl_fail,
        "total_cached_wiki_pages": len(cache["wiki_pages"]),
    }


def _load_font(size: int = 12) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _make_checkerboard(w: int, h: int, cell: int = 12) -> Image.Image:
    im = Image.new("RGBA", (w, h), (250, 248, 243, 255))
    dr = ImageDraw.Draw(im)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2 == 1:
                dr.rectangle([x, y, min(w, x + cell), min(h, y + cell)], fill=(230, 225, 212, 255))
    return im


def _render_contact_sheets(items: list[dict[str, Any]], out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("wiki_enrich_batch_*.jpg"):
        old.unlink()
    if not items:
        return []
    font = _load_font(12)
    per_sheet = 25
    cols = 5
    cell_w, cell_h = 260, 220
    pad = 16
    sheet_paths: list[str] = []

    for b_idx in range(0, len(items), per_sheet):
        chunk = items[b_idx : b_idx + per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        canvas = Image.new("RGB", (cols * cell_w + pad * 2, rows * cell_h + 60), (240, 238, 230))
        dr = ImageDraw.Draw(canvas)
        batch_num = b_idx // per_sheet + 1
        dr.text(
            (pad, 14),
            f"Assert Wiki Enrichment QA Sheet #{batch_num} ({len(chunk)} items — identity_verified_pending_visual_review)",
            fill=(20, 20, 19),
            font=font,
        )
        for i, item in enumerate(chunk):
            r, c = divmod(i, cols)
            x0 = pad + c * cell_w
            y0 = 46 + r * cell_h
            dr.rectangle([x0 + 6, y0 + 6, x0 + cell_w - 6, y0 + cell_h - 6], fill=(251, 250, 246), outline=(226, 221, 208))
            cb = _make_checkerboard(cell_w - 24, 146)
            try:
                img = Image.open(PROJECT_ROOT / item["local_path"]).convert("RGBA")
                img.thumbnail((cell_w - 36, 134), Image.Resampling.LANCZOS)
                px = (cb.width - img.width) // 2
                py = (cb.height - img.height) // 2
                cb.alpha_composite(img, (px, py))
            except Exception:
                pass
            canvas.paste(cb.convert("RGB"), (x0 + 12, y0 + 12))
            lbl = f"{item['family_slug']} ({item['width']}x{item['height']})"
            dr.text((x0 + 12, y0 + 164), lbl[:34], fill=(20, 20, 19), font=font)
            dr.text((x0 + 12, y0 + 182), str(item.get("wiki_title") or "")[:34], fill=(111, 109, 100), font=font)

        out_path = out_dir / f"wiki_enrich_batch_{batch_num:02d}.jpg"
        canvas.save(out_path, format="JPEG", quality=90)
        sheet_paths.append(out_path.relative_to(PROJECT_ROOT).as_posix())
    return sheet_paths


def run_build(
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    assets_dir: Path = DEFAULT_ENRICH_ASSETS_DIR,
    cache_path: Path = DEFAULT_CACHE_PATH,
    contact_dir: Path = DEFAULT_CONTACT_DIR,
    manifest_jsonl: Path = DEFAULT_MANIFEST_JSONL,
    summary_json: Path = DEFAULT_SUMMARY_JSON,
) -> dict[str, Any]:
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    track_b = [f for f in tax["families"] if f["scope_track"] == "entity_specific"]
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    wiki_pages = cache.get("wiki_pages") or {}
    downloads = cache.get("downloads") or {}

    status_counts: Counter[str] = Counter()
    records: list[dict[str, Any]] = []
    qa_items: list[dict[str, Any]] = []

    for f in track_b:
        slug = f["family_slug"]
        existing = _load_existing_assert_map(templete_dir, slug)
        title = WIKI_TITLE_OVERRIDES.get(slug) or slug.replace("_", " ").title()
        wpage = wiki_pages.get(title) or {}
        if wpage.get("missing"):
            wpage = {}

        wiki_summary = {
            "wiki_title": wpage.get("wiki_title") or "",
            "wiki_url": wpage.get("wiki_url") or "",
            "extract": wpage.get("extract") or "",
        }

        ref_path = assets_dir / slug / "reference.png"
        dl = downloads.get(slug) or {}
        has_qa_replacement = bool(dl.get("replaced_from_qa") and dl.get("status") == "downloaded" and ref_path.is_file())

        if existing["approved_paths"] and not has_qa_replacement:
            status = "already_approved_in_assert"
            chosen_paths = existing["approved_paths"]
            assets_meta = _inspect_local_files(chosen_paths, review_status="approved_for_declared_reference_kind", publisher="assert_approved")
        elif existing["supplement_paths"] and not has_qa_replacement:
            status = "existing_assert_supplement_pending_approval"
            chosen_paths = existing["supplement_paths"]
            assets_meta = _inspect_local_files(chosen_paths, review_status="identity_verified_pending_visual_review", publisher="assert_supplement")
        elif slug in LOCAL_RESCUE_MAP and not has_qa_replacement:
            valid_rescue = [p for p in LOCAL_RESCUE_MAP[slug] if (PROJECT_ROOT / p).is_file()]
            if valid_rescue:
                status = "local_assert_rescued_pending_review"
                chosen_paths = valid_rescue
                assets_meta = _inspect_local_files(chosen_paths, review_status="identity_verified_pending_visual_review", publisher="assert_local_rescue")
            else:
                status = "source_missing"
                chosen_paths = []
                assets_meta = []
        elif slug in MANUAL_PATENT_SLUGS:
            status = "manual_patent_photo_required"
            chosen_paths = []
            assets_meta = []
        else:
            ref_path = assets_dir / slug / "reference.png"
            dl = downloads.get(slug) or {}
            if ref_path.is_file() and dl.get("status") == "downloaded":
                img = Image.open(ref_path)
                img.load()
                w, h = img.size
                d_hash = dhash64(img.convert("RGBA"))
                sha = _sha256_file(ref_path)
                rel = ref_path.relative_to(PROJECT_ROOT).as_posix()
                status = "wiki_fetched_pending_visual_review"
                chosen_paths = [rel]
                assets_meta = [
                    {
                        "asset_id": f"sha256_{sha}",
                        "local_path": rel,
                        "source_file_path": dl.get("source_rel"),
                        "sha256": sha,
                        "width": w,
                        "height": h,
                        "dhash64": d_hash,
                        "native_resolution_below_512": bool(dl.get("native_resolution_below_512")),
                        "source_page_url": dl.get("source_page_url") or dl.get("file_description_url") or "",
                        "download_url": dl.get("download_url") or "",
                        "publisher": dl.get("publisher") or "wikimedia",
                        "license": dl.get("license") or "unknown",
                        "fetched_at": dl.get("fetched_at") or "",
                        "is_synthetic_image": False,
                        "transform_history": dl.get("transform_history") or [],
                        "review_status": "identity_verified_pending_visual_review",
                    }
                ]
                qa_items.append(
                    {
                        "family_slug": slug,
                        "local_path": rel,
                        "width": w,
                        "height": h,
                        "wiki_title": wiki_summary["wiki_title"] or title,
                    }
                )
            else:
                status = "wiki_source_missing"
                chosen_paths = []
                assets_meta = []

        status_counts[status] += 1
        records.append(
            {
                "family_slug": slug,
                "canonical_entity_id": f"{f['scope_subtrack'][:2].lower()}:{slug}",
                "scope_subtrack": f["scope_subtrack"],
                "selected_latest_id": f["selected_latest_id"],
                "enrichment_status": status,
                "wiki_summary": wiki_summary,
                "image_paths": chosen_paths,
                "assets": assets_meta,
            }
        )

    contact_sheets = _render_contact_sheets(qa_items, contact_dir)

    manifest_jsonl.parent.mkdir(parents=True, exist_ok=True)
    tmp_j = manifest_jsonl.with_name(manifest_jsonl.name + ".tmp")
    with tmp_j.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp_j.replace(manifest_jsonl)

    visual_cov = sum(1 for r in records if r["image_paths"])
    summary = {
        "schema": "assert_template_wiki_enrichment_summary_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_entity_specific_families": len(records),
        "families_with_local_reference_image": visual_cov,
        "visual_candidate_coverage_rate": round(visual_cov / max(1, len(records)), 4),
        "strict_approved_rate": round(status_counts["already_approved_in_assert"] / max(1, len(records)), 4),
        "status_counts": dict(status_counts.most_common()),
        "contact_sheets": contact_sheets,
    }
    tmp_s = summary_json.with_name(summary_json.name + ".tmp")
    tmp_s.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_s.replace(summary_json)
    return summary


def _inspect_local_files(rel_paths: list[str], *, review_status: str, publisher: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rp in rel_paths:
        p = PROJECT_ROOT / rp
        img = Image.open(p)
        img.load()
        w, h = img.size
        sha = _sha256_file(p)
        out.append(
            {
                "asset_id": f"sha256_{sha}",
                "local_path": rp,
                "sha256": sha,
                "width": w,
                "height": h,
                "dhash64": dhash64(img.convert("RGBA")),
                "native_resolution_below_512": max(w, h) < 512,
                "publisher": publisher,
                "is_synthetic_image": False,
                "review_status": review_status,
            }
        )
    return out


def run_replace_slugs(
    slugs: list[str],
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    assets_dir: Path = DEFAULT_ENRICH_ASSETS_DIR,
    cache_path: Path = DEFAULT_CACHE_PATH,
    contact_dir: Path = DEFAULT_CONTACT_DIR,
) -> dict[str, Any]:
    """Targeted online replacement of specific visual-QA flagged slugs using explicit hints."""
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    tax_by_slug = {f["family_slug"]: f for f in tax["families"]}
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    cache.setdefault("wiki_pages", {})
    cache.setdefault("commons_searches", {})
    cache.setdefault("file_infos", {})
    cache.setdefault("downloads", {})

    slug_candidates: dict[str, list[str]] = {}
    files_to_resolve: set[str] = set()
    for slug in slugs:
        fam = tax_by_slug.get(slug, {})
        subtrack = str(fam.get("scope_subtrack") or "B1_specific_brand_trademark")
        cands: list[str] = list(EXPLICIT_FILE_HINTS.get(slug) or [])
        for query in EXPLICIT_SEARCH_HINTS.get(slug) or [WIKI_TITLE_OVERRIDES.get(slug, slug)]:
            for api_base in ("https://en.wikipedia.org/w/api.php", "https://commons.wikimedia.org/w/api.php"):
                params = {
                    "action": "query",
                    "format": "json",
                    "formatversion": "2",
                    "list": "search",
                    "srnamespace": "6",
                    "srlimit": "8",
                    "srsearch": query,
                }
                try:
                    data = _http_get_json(api_base + "?" + urllib.parse.urlencode(params), delay=0.2)
                except Exception:
                    continue
                for hit in (data.get("query") or {}).get("search") or []:
                    fn = _clean_wiki_filename(str(hit.get("title") or ""))
                    if not fn or REPLACE_DENY_RE.search(fn):
                        continue
                    if fn not in cands:
                        cands.append(fn)
        # Prioritize .svg / .png and logo/wordmark names
        def _rank(fn: str) -> tuple[int, int, str]:
            low = fn.lower()
            has_logo = int(any(k in low for k in ("logo", "wordmark", "jumpman", "orb", "emblem", "brand")))
            is_vec = 2 if low.endswith(".svg") else (1 if low.endswith(".png") else 0)
            return (-has_logo, -is_vec, fn)

        deduped = sorted(set(cands), key=_rank)[:8]
        slug_candidates[slug] = deduped
        for fn in deduped:
            files_to_resolve.add(fn)

    if files_to_resolve:
        resolved = _resolve_file_imageinfo(sorted(files_to_resolve))
        cache["file_infos"].update(resolved)
        for fn in files_to_resolve:
            if fn not in cache["file_infos"]:
                cache["file_infos"][fn] = {"missing": True}

    replaced: list[str] = []
    failed: list[str] = []
    qa_items: list[dict[str, Any]] = []
    for slug in slugs:
        title = WIKI_TITLE_OVERRIDES.get(slug) or slug.replace("_", " ").title()
        wpage = cache["wiki_pages"].get(title) or {}
        saved = False
        for fn in slug_candidates.get(slug) or []:
            if REPLACE_DENY_RE.search(fn):
                continue
            ii = cache["file_infos"].get(fn) or {}
            if ii.get("missing"):
                continue
            dl_url = ii.get("download_url") or ""
            if not dl_url:
                continue
            is_svg = dl_url.lower().endswith(".svg") or "svg" in str(ii.get("mime") or "").lower()
            fetch_url = dl_url if is_svg else (ii.get("thumb_url") or dl_url)
            try:
                time.sleep(0.15)
                raw, ctype = _http_get_bytes(fetch_url)
                saved_meta = _save_source_and_reference(raw, ctype, fetch_url, assets_dir / slug)
                cache["downloads"][slug] = {
                    "status": "downloaded",
                    "wiki_title": wpage.get("wiki_title") or title,
                    "source_page_url": wpage.get("wiki_url") or ii.get("description_url") or "",
                    "file_description_url": ii.get("description_url") or "",
                    "download_url": fetch_url,
                    "publisher": ii.get("imagerepository") or "wikimedia",
                    "license": ii.get("license") or "unknown",
                    "artist": ii.get("artist") or "unknown",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "replaced_from_qa": True,
                    **saved_meta,
                }
                qa_items.append(
                    {
                        "family_slug": slug,
                        "local_path": saved_meta["reference_rel"],
                        "width": saved_meta["width"],
                        "height": saved_meta["height"],
                        "wiki_title": fn,
                    }
                )
                replaced.append(slug)
                saved = True
                break
            except Exception:
                if is_svg and ii.get("thumb_url"):
                    try:
                        time.sleep(0.15)
                        raw, ctype = _http_get_bytes(ii["thumb_url"])
                        saved_meta = _save_source_and_reference(raw, ctype, ii["thumb_url"], assets_dir / slug)
                        cache["downloads"][slug] = {
                            "status": "downloaded",
                            "wiki_title": wpage.get("wiki_title") or title,
                            "source_page_url": wpage.get("wiki_url") or ii.get("description_url") or "",
                            "file_description_url": ii.get("description_url") or "",
                            "download_url": ii["thumb_url"],
                            "publisher": ii.get("imagerepository") or "wikimedia",
                            "license": ii.get("license") or "unknown",
                            "artist": ii.get("artist") or "unknown",
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                            "replaced_from_qa": True,
                            **saved_meta,
                        }
                        qa_items.append(
                            {
                                "family_slug": slug,
                                "local_path": saved_meta["reference_rel"],
                                "width": saved_meta["width"],
                                "height": saved_meta["height"],
                                "wiki_title": fn,
                            }
                        )
                        replaced.append(slug)
                        saved = True
                        break
                    except Exception:
                        pass
        if not saved:
            failed.append(slug)

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    # Render dedicated replacement QA sheet
    qa_path_rel = None
    if qa_items:
        sheets = _render_contact_sheets(qa_items, contact_dir / "_tmp_replace")
        if sheets:
            src_sheet = PROJECT_ROOT / sheets[0]
            dst_sheet = contact_dir / "wiki_replacements_qa.jpg"
            src_sheet.replace(dst_sheet)
            for leftover in (contact_dir / "_tmp_replace").glob("*"):
                leftover.unlink()
            (contact_dir / "_tmp_replace").rmdir()
            qa_path_rel = dst_sheet.relative_to(PROJECT_ROOT).as_posix()

    return {
        "requested_slugs": slugs,
        "replaced": replaced,
        "failed": failed,
        "qa_contact_sheet": qa_path_rel,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Online fetch Wikipedia summaries & reference logos")
    parser.add_argument("--replace-slugs", type=str, default="", help="Comma-separated slugs to re-fetch using explicit logo hints")
    parser.add_argument("--build", action="store_true", help="Offline build enrichment manifests and contact sheets")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of missing-image families during --fetch")
    parser.add_argument("--retry-failed", action="store_true", help="Retry previously failed/no_file slugs during --fetch")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.fetch and not args.build and not args.replace_slugs:
        args.build = True
    out: dict[str, Any] = {}
    if args.fetch:
        out["fetch"] = run_fetch(limit=args.limit, retry_failed=args.retry_failed)
    if args.replace_slugs:
        slugs = [s.strip() for s in args.replace_slugs.split(",") if s.strip()]
        out["replace"] = run_replace_slugs(slugs)
    if args.build:
        out["build"] = run_build()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
