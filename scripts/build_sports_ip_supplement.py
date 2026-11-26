#!/usr/bin/env python3
"""体育联赛队徽（五大联赛 / NBA / NFL / MLB / NHL / NCAA）与 96 模板 IP 官标独立补充包构建器。

由 Assert 独立管理采集、验收与文件导出：
1. 网络抓取与离线构建严格解耦：
   - `--fetch`      仅执行在线拉取（Wikipedia 批量 API + GitHub `luukhopman/football-logos` + Wikimedia 官标），保存原始 API 响应与图片；
   - `--build-pack` 100% 离线执行（PIL/resvg 校验、主色/比例/dHash 视觉索引、CPT/ImageGen-v2 JSONL 导出、
                    96 模板覆盖台账与棋盘格底图可视对照表生成）。
2. 所有生成文本保持真实世界商品/图标自然表述，杜绝内部实现术语；所有真实官方图元显式标注
   `is_synthetic_image: false` 与 `synthetic_image_count: 0`，确保不挤占 Mid-Training 合成图 25% 配额。
3. 支持 `--only sports|sch96|all`、`--retry-failed`（仅补采缺失/失败项）、`--force`（强制全量重采）、`--image-root-prefix <prefix>`、`--bundle-tar`。

典型用法：
    .venv/bin/python scripts/build_sports_ip_supplement.py --fetch
    .venv/bin/python scripts/build_sports_ip_supplement.py --build-pack
    .venv/bin/python scripts/build_sports_ip_supplement.py --build-pack --bundle-tar
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import sys
import tarfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from asset_visual_helpers import (
    dhash64,
    geometry_from_aspect,
    hamming,
    rgb_to_color_name,
)

try:
    import resvg_py
except ImportError:
    resvg_py = None

ASSETS_DIR = PROJECT_ROOT
MANIFESTS_DIR = PROJECT_ROOT / "output" / "sports_ip_supplement" / "manifests"
SPORTS_ASSETS_DIR = ASSETS_DIR / "sports_crests_supplement"
SCH96_ASSETS_DIR = ASSETS_DIR / "sch96_ip_supplement"

OUT_DIR = PROJECT_ROOT / "output" / "sports_ip_supplement"
RAW_API_DIR = OUT_DIR / "_raw_api"
FETCH_LEDGER_PATH = OUT_DIR / "_fetch_ledger.json"
CONTACT_SHEETS_DIR = OUT_DIR / "contact_sheets"

SPORTS_MANIFEST_PATH = MANIFESTS_DIR / "sports_crests_supplement.json"
SCH96_MANIFEST_PATH = MANIFESTS_DIR / "sch96_ip_supplement.json"

WIKI_USER_AGENT = (
    "AssertSupplementBuilder/1.0 "
    "(standalone-reference-image-catalog)"
)
WIKI_HEADERS = {
    "User-Agent": WIKI_USER_AGENT,
    "Accept": "application/json,image/png,image/svg+xml,*/*;q=0.8",
}
GITHUB_HEADERS = {
    "User-Agent": WIKI_USER_AGENT,
    "Accept": "application/vnd.github+json",
}

FORBIDDEN_JARGON = (
    "程序化生成",
    "程序化",
    "矢量图",
    "矢量",
    "SVG",
    "svg",
    "基准模式",
    "Stage A",
)

# ---------------------------------------------------------------------------
# Part 1: Sports Leagues & NCAA Config
# ---------------------------------------------------------------------------

LEAGUE_CONFIGS: List[Dict[str, Any]] = [
    {
        "league_id": "premier_league",
        "league_group": "football_big5",
        "sport": "football",
        "sport_zh": "足球",
        "country_zh": "英格兰",
        "name_en": "Premier League",
        "name_zh": "英格兰足球超级联赛（英超）",
        "short_zh": "英超",
        "github_dir": "England - Premier League",
        "wiki_titles": ["Premier League"],
        "wiki_file_hints": ["Premier_League_Logo.svg", "Premier_League_Rebrand_2016.svg"],
        "simple_icon": "premierleague",
        "template_ids": ["381_hemier_league_selfmodel"],
    },
    {
        "league_id": "la_liga",
        "league_group": "football_big5",
        "sport": "football",
        "sport_zh": "足球",
        "country_zh": "西班牙",
        "name_en": "La Liga",
        "name_zh": "西班牙足球甲级联赛（西甲）",
        "short_zh": "西甲",
        "github_dir": "Spain - LaLiga",
        "wiki_titles": ["La Liga"],
        "wiki_file_hints": ["LaLiga_2023_Horizontal_Logo.svg", "LaLiga_EA_Sports_2023_Vertical_Logo.svg", "LaLiga.svg"],
        "simple_icon": "laliga",
        "template_ids": [],
    },
    {
        "league_id": "serie_a",
        "league_group": "football_big5",
        "sport": "football",
        "sport_zh": "足球",
        "country_zh": "意大利",
        "name_en": "Serie A",
        "name_zh": "意大利足球甲级联赛（意甲）",
        "short_zh": "意甲",
        "github_dir": "Italy - Serie A",
        "wiki_titles": ["Serie A"],
        "wiki_file_hints": ["Serie_A_2024_logo.svg", "Serie_A_logo_2022.svg"],
        "simple_icon": None,
        "template_ids": [],
    },
    {
        "league_id": "bundesliga",
        "league_group": "football_big5",
        "sport": "football",
        "sport_zh": "足球",
        "country_zh": "德国",
        "name_en": "Bundesliga",
        "name_zh": "德国足球甲级联赛（德甲）",
        "short_zh": "德甲",
        "github_dir": "Germany - Bundesliga",
        "wiki_titles": ["Bundesliga"],
        "wiki_file_hints": ["Bundesliga_logo_(2017).svg"],
        "simple_icon": None,
        "template_ids": [],
    },
    {
        "league_id": "ligue_1",
        "league_group": "football_big5",
        "sport": "football",
        "sport_zh": "足球",
        "country_zh": "法国",
        "name_en": "Ligue 1",
        "name_zh": "法国足球甲级联赛（法甲）",
        "short_zh": "法甲",
        "github_dir": "France - Ligue 1",
        "wiki_titles": ["Ligue 1"],
        "wiki_file_hints": ["Logo_Ligue_1_McDonald's_2024.svg", "Ligue_1_2024_Logo.svg", "Ligue1_logo.svg"],
        "simple_icon": None,
        "template_ids": [],
    },
    {
        "league_id": "nba",
        "league_group": "us_pro_core",
        "sport": "basketball",
        "sport_zh": "篮球",
        "country_zh": "美国/北美",
        "name_en": "NBA",
        "name_zh": "美国职业篮球联赛（NBA）",
        "short_zh": "NBA",
        "wiki_titles": ["National Basketball Association"],
        "wiki_file_hints": ["NBA_logo.svg", "National_Basketball_Association_logo.svg"],
        "simple_icon": "nba",
        "template_ids": ["151_IP_NBA_Positive"],
        "teams": [
            ("Atlanta Hawks", "Atlanta Hawks", "ATL"),
            ("Boston Celtics", "Boston Celtics", "BOS"),
            ("Brooklyn Nets", "Brooklyn Nets", "BKN"),
            ("Charlotte Hornets", "Charlotte Hornets", "CHA"),
            ("Chicago Bulls", "Chicago Bulls", "CHI"),
            ("Cleveland Cavaliers", "Cleveland Cavaliers", "CLE"),
            ("Dallas Mavericks", "Dallas Mavericks", "DAL"),
            ("Denver Nuggets", "Denver Nuggets", "DEN"),
            ("Detroit Pistons", "Detroit Pistons", "DET"),
            ("Golden State Warriors", "Golden State Warriors", "GSW"),
            ("Houston Rockets", "Houston Rockets", "HOU"),
            ("Indiana Pacers", "Indiana Pacers", "IND"),
            ("Los Angeles Clippers", "Los Angeles Clippers", "LAC"),
            ("Los Angeles Lakers", "Los Angeles Lakers", "LAL"),
            ("Memphis Grizzlies", "Memphis Grizzlies", "MEM"),
            ("Miami Heat", "Miami Heat", "MIA"),
            ("Milwaukee Bucks", "Milwaukee Bucks", "MIL"),
            ("Minnesota Timberwolves", "Minnesota Timberwolves", "MIN"),
            ("New Orleans Pelicans", "New Orleans Pelicans", "NOP"),
            ("New York Knicks", "New York Knicks", "NYK"),
            ("Oklahoma City Thunder", "Oklahoma City Thunder", "OKC"),
            ("Orlando Magic", "Orlando Magic", "ORL"),
            ("Philadelphia 76ers", "Philadelphia 76ers", "PHI"),
            ("Phoenix Suns", "Phoenix Suns", "PHX"),
            ("Portland Trail Blazers", "Portland Trail Blazers", "POR"),
            ("Sacramento Kings", "Sacramento Kings", "SAC"),
            ("San Antonio Spurs", "San Antonio Spurs", "SAS"),
            ("Toronto Raptors", "Toronto Raptors", "TOR"),
            ("Utah Jazz", "Utah Jazz", "UTA"),
            ("Washington Wizards", "Washington Wizards", "WAS"),
        ],
    },
    {
        "league_id": "nfl",
        "league_group": "us_pro_core",
        "sport": "american_football",
        "sport_zh": "美式橄榄球",
        "country_zh": "美国",
        "name_en": "NFL",
        "name_zh": "美国国家橄榄球联盟（NFL）",
        "short_zh": "NFL",
        "wiki_titles": ["National Football League"],
        "wiki_file_hints": ["National_Football_League_logo.svg"],
        "simple_icon": None,
        "template_ids": [],
        "teams": [
            ("Arizona Cardinals", "Arizona Cardinals", "ARI"),
            ("Atlanta Falcons", "Atlanta Falcons", "ATL"),
            ("Baltimore Ravens", "Baltimore Ravens", "BAL"),
            ("Buffalo Bills", "Buffalo Bills", "BUF"),
            ("Carolina Panthers", "Carolina Panthers", "CAR"),
            ("Chicago Bears", "Chicago Bears", "CHI"),
            ("Cincinnati Bengals", "Cincinnati Bengals", "CIN"),
            ("Cleveland Browns", "Cleveland Browns", "CLE"),
            ("Dallas Cowboys", "Dallas Cowboys", "DAL"),
            ("Denver Broncos", "Denver Broncos", "DEN"),
            ("Detroit Lions", "Detroit Lions", "DET"),
            ("Green Bay Packers", "Green Bay Packers", "GB"),
            ("Houston Texans", "Houston Texans", "HOU"),
            ("Indianapolis Colts", "Indianapolis Colts", "IND"),
            ("Jacksonville Jaguars", "Jacksonville Jaguars", "JAX"),
            ("Kansas City Chiefs", "Kansas City Chiefs", "KC"),
            ("Las Vegas Raiders", "Las Vegas Raiders", "LV"),
            ("Los Angeles Chargers", "Los Angeles Chargers", "LAC"),
            ("Los Angeles Rams", "Los Angeles Rams", "LAR"),
            ("Miami Dolphins", "Miami Dolphins", "MIA"),
            ("Minnesota Vikings", "Minnesota Vikings", "MIN"),
            ("New England Patriots", "New England Patriots", "NE"),
            ("New Orleans Saints", "New Orleans Saints", "NO"),
            ("New York Giants", "New York Giants", "NYG"),
            ("New York Jets", "New York Jets", "NYJ"),
            ("Philadelphia Eagles", "Philadelphia Eagles", "PHI"),
            ("Pittsburgh Steelers", "Pittsburgh Steelers", "PIT"),
            ("San Francisco 49ers", "San Francisco 49ers", "SF"),
            ("Seattle Seahawks", "Seattle Seahawks", "SEA"),
            ("Tampa Bay Buccaneers", "Tampa Bay Buccaneers", "TB"),
            ("Tennessee Titans", "Tennessee Titans", "TEN"),
            ("Washington Commanders", "Washington Commanders", "WAS"),
        ],
    },
    {
        "league_id": "mlb",
        "league_group": "us_pro_extended",
        "sport": "baseball",
        "sport_zh": "棒球",
        "country_zh": "美国/北美",
        "name_en": "MLB",
        "name_zh": "美国职业棒球大联盟（MLB）",
        "short_zh": "MLB",
        "wiki_titles": ["Major League Baseball"],
        "wiki_file_hints": ["Major_League_Baseball_logo.svg"],
        "simple_icon": "mlb",
        "template_ids": [],
        "teams": [
            ("Arizona Diamondbacks", "Arizona Diamondbacks", "ARI"),
            ("Atlanta Braves", "Atlanta Braves", "ATL"),
            ("Athletics", "Athletics (baseball)", "ATH"),
            ("Baltimore Orioles", "Baltimore Orioles", "BAL"),
            ("Boston Red Sox", "Boston Red Sox", "BOS"),
            ("Chicago Cubs", "Chicago Cubs", "CHC"),
            ("Chicago White Sox", "Chicago White Sox", "CHW"),
            ("Cincinnati Reds", "Cincinnati Reds", "CIN"),
            ("Cleveland Guardians", "Cleveland Guardians", "CLE"),
            ("Colorado Rockies", "Colorado Rockies", "COL"),
            ("Detroit Tigers", "Detroit Tigers", "DET"),
            ("Houston Astros", "Houston Astros", "HOU"),
            ("Kansas City Royals", "Kansas City Royals", "KC"),
            ("Los Angeles Angels", "Los Angeles Angels", "LAA"),
            ("Los Angeles Dodgers", "Los Angeles Dodgers", "LAD"),
            ("Miami Marlins", "Miami Marlins", "MIA"),
            ("Milwaukee Brewers", "Milwaukee Brewers", "MIL"),
            ("Minnesota Twins", "Minnesota Twins", "MIN"),
            ("New York Mets", "New York Mets", "NYM"),
            ("New York Yankees", "New York Yankees", "NYY"),
            ("Philadelphia Phillies", "Philadelphia Phillies", "PHI"),
            ("Pittsburgh Pirates", "Pittsburgh Pirates", "PIT"),
            ("San Diego Padres", "San Diego Padres", "SD"),
            ("San Francisco Giants", "San Francisco Giants", "SF"),
            ("Seattle Mariners", "Seattle Mariners", "SEA"),
            ("St. Louis Cardinals", "St. Louis Cardinals", "STL"),
            ("Tampa Bay Rays", "Tampa Bay Rays", "TB"),
            ("Texas Rangers", "Texas Rangers", "TEX"),
            ("Toronto Blue Jays", "Toronto Blue Jays", "TOR"),
            ("Washington Nationals", "Washington Nationals", "WSH"),
        ],
    },
    {
        "league_id": "nhl",
        "league_group": "us_pro_extended",
        "sport": "ice_hockey",
        "sport_zh": "冰球",
        "country_zh": "北美",
        "name_en": "NHL",
        "name_zh": "北美职业冰球联盟（NHL）",
        "short_zh": "NHL",
        "wiki_titles": ["National Hockey League"],
        "wiki_file_hints": ["05_NHL_Shield.svg", "National_Hockey_League_logo.svg"],
        "simple_icon": "nhl",
        "template_ids": [],
        "teams": [
            ("Anaheim Ducks", "Anaheim Ducks", "ANA"),
            ("Boston Bruins", "Boston Bruins", "BOS"),
            ("Buffalo Sabres", "Buffalo Sabres", "BUF"),
            ("Calgary Flames", "Calgary Flames", "CGY"),
            ("Carolina Hurricanes", "Carolina Hurricanes", "CAR"),
            ("Chicago Blackhawks", "Chicago Blackhawks", "CHI"),
            ("Colorado Avalanche", "Colorado Avalanche", "COL"),
            ("Columbus Blue Jackets", "Columbus Blue Jackets", "CBJ"),
            ("Dallas Stars", "Dallas Stars", "DAL"),
            ("Detroit Red Wings", "Detroit Red Wings", "DET"),
            ("Edmonton Oilers", "Edmonton Oilers", "EDM"),
            ("Florida Panthers", "Florida Panthers", "FLA"),
            ("Los Angeles Kings", "Los Angeles Kings", "LAK"),
            ("Minnesota Wild", "Minnesota Wild", "MIN"),
            ("Montreal Canadiens", "Montreal Canadiens", "MTL"),
            ("Nashville Predators", "Nashville Predators", "NSH"),
            ("New Jersey Devils", "New Jersey Devils", "NJD"),
            ("New York Islanders", "New York Islanders", "NYI"),
            ("New York Rangers", "New York Rangers", "NYR"),
            ("Ottawa Senators", "Ottawa Senators", "OTT"),
            ("Philadelphia Flyers", "Philadelphia Flyers", "PHI"),
            ("Pittsburgh Penguins", "Pittsburgh Penguins", "PIT"),
            ("San Jose Sharks", "San Jose Sharks", "SJS"),
            ("Seattle Kraken", "Seattle Kraken", "SEA"),
            ("St. Louis Blues", "St. Louis Blues", "STL"),
            ("Tampa Bay Lightning", "Tampa Bay Lightning", "TBL"),
            ("Toronto Maple Leafs", "Toronto Maple Leafs", "TOR"),
            ("Utah Mammoth", "Utah Mammoth", "UTA"),
            ("Vancouver Canucks", "Vancouver Canucks", "VAN"),
            ("Vegas Golden Knights", "Vegas Golden Knights", "VGK"),
            ("Washington Capitals", "Washington Capitals", "WSH"),
            ("Winnipeg Jets", "Winnipeg Jets", "WPG"),
        ],
    },
]

NCAA_TARGETS: List[Dict[str, Any]] = [
    {"espn_id": "150", "slug": "duke", "name_en": "Duke Blue Devils", "name_zh": "杜克大学蓝魔队", "template_ids": ["471_ip_duke", "473_ip_duke_excepmtion"]},
    {"espn_id": "61", "slug": "georgia", "name_en": "Georgia Bulldogs", "name_zh": "佐治亚大学斗牛犬队（UGA）", "template_ids": ["202_IP_UGA_1"]},
    {"espn_id": "57", "slug": "florida", "name_en": "Florida Gators", "name_zh": "佛罗里达大学短吻鳄队", "template_ids": ["475_ip_florida"]},
    {"espn_id": "201", "slug": "oklahoma", "name_en": "Oklahoma Sooners", "name_zh": "俄克拉荷马大学捷足者队", "template_ids": ["511_ip_oklahoma"]},
    {"espn_id": "2335", "slug": "liberty", "name_en": "Liberty Flames", "name_zh": "自由大学火焰队", "template_ids": ["126_IP_LibertyUniversity"]},
    {"espn_id": "333", "slug": "alabama", "name_en": "Alabama Crimson Tide", "name_zh": "阿拉巴马大学红潮队", "template_ids": []},
    {"espn_id": "130", "slug": "michigan", "name_en": "Michigan Wolverines", "name_zh": "密歇根大学狼獾队", "template_ids": []},
    {"espn_id": "194", "slug": "ohio_state", "name_en": "Ohio State Buckeyes", "name_zh": "俄亥俄州立大学七叶树队", "template_ids": []},
    {"espn_id": "251", "slug": "texas", "name_en": "Texas Longhorns", "name_zh": "得克萨斯大学长角牛队", "template_ids": []},
    {"espn_id": "87", "slug": "notre_dame", "name_en": "Notre Dame Fighting Irish", "name_zh": "圣母大学爱尔兰战士队", "template_ids": []},
    {"espn_id": "153", "slug": "north_carolina", "name_en": "North Carolina Tar Heels", "name_zh": "北卡罗来纳大学焦油踵队", "template_ids": []},
    {"espn_id": "96", "slug": "kentucky", "name_en": "Kentucky Wildcats", "name_zh": "肯塔基大学野猫队", "template_ids": []},
    {"espn_id": "2305", "slug": "kansas", "name_en": "Kansas Jayhawks", "name_zh": "堪萨斯大学捷鹰队", "template_ids": []},
    {"espn_id": "99", "slug": "lsu", "name_en": "LSU Tigers", "name_zh": "路易斯安那州立大学老虎队", "template_ids": []},
    {"espn_id": "30", "slug": "usc", "name_en": "USC Trojans", "name_zh": "南加州大学特洛伊人队", "template_ids": []},
    {"espn_id": "228", "slug": "clemson", "name_en": "Clemson Tigers", "name_zh": "克莱姆森大学老虎队", "template_ids": []},
    {"espn_id": "213", "slug": "penn_state", "name_en": "Penn State Nittany Lions", "name_zh": "宾夕法尼亚州立大学尼塔尼雄狮队", "template_ids": []},
    {"espn_id": "2483", "slug": "oregon", "name_en": "Oregon Ducks", "name_zh": "俄勒冈大学鸭子队", "template_ids": []},
    {"espn_id": "2633", "slug": "tennessee", "name_en": "Tennessee Volunteers", "name_zh": "田纳西大学志愿者队", "template_ids": []},
    {"espn_id": "2", "slug": "auburn", "name_en": "Auburn Tigers", "name_zh": "奥本大学老虎队", "template_ids": []},
]

SPORTS_TEAM_FILE_HINTS: Dict[str, List[str]] = {
    "sports_ncaa_georgia": ["Georgia_Athletics_logo.svg"],
    "sports_ncaa_texas": ["Texas_Longhorns_logo.svg"],
    "sports_ncaa_notre_dame": ["Nd_athletics_gold_logo_2015.svg", "Notre_Dame_Fighting_Irish_logo.svg"],
    "sports_ncaa_lsu": ["LSU_Athletics_logo.svg"],
    "sports_ncaa_oregon": ["Oregon_Ducks_logo.svg"],
    "sports_ncaa_tennessee": ["Tennessee_Volunteers_logo.svg"],
    "sports_ncaa_auburn": ["Auburn_Tigers_logo.svg"],
    "sports_nba_cleveland_cavaliers": ["Cleveland_Cavaliers_logo.svg"],
    "sports_nfl_buffalo_bills": ["Buffalo_Bills_logo_1974-present.svg", "Buffalo_Bills_logo.svg"],
    "sports_nfl_green_bay_packers": ["Green_Bay_Packers_logo.svg"],
    "sports_nfl_kansas_city_chiefs": ["Kansas_City_Chiefs_logo.svg"],
    "sports_nfl_los_angeles_chargers": ["Los_Angeles_Chargers_logo.svg"],
    "sports_nfl_san_francisco_49ers": ["San_Francisco_49ers_logo.svg"],
    "sports_nfl_washington_commanders": ["Washington_Commanders_logo.svg"],
    "sports_mlb_kansas_city_royals": ["Kansas_City_Royals_Primary_Logo.svg", "Kansas_City_Royals_logo.svg"],
    "sports_mlb_minnesota_twins": ["Minnesota_Twins_New_Logo.svg", "Minnesota_Twins_logo.svg"],
    "sports_mlb_tampa_bay_rays": ["Tampa_Bay_Rays_Logo.svg"],
    "sports_nhl_boston_bruins": ["Boston_Bruins.svg", "Boston_Bruins_100th_anniversary_logo.svg"],
    "sports_nhl_philadelphia_flyers": ["Philadelphia_Flyers.svg"],
}

# Comprehensive official Chinese team name dictionary (NBA/NFL/MLB/NHL + European Big 5 & promoted clubs)
TEAM_ZH_MAP: Dict[str, str] = {
    # --- Premier League ---
    "Arsenal": "阿森纳足球俱乐部",
    "Aston Villa": "阿斯顿维拉足球俱乐部",
    "AFC Bournemouth": "伯恩茅斯足球俱乐部",
    "Bournemouth": "伯恩茅斯足球俱乐部",
    "Brentford": "布伦特福德足球俱乐部",
    "Brighton & Hove Albion": "布莱顿足球俱乐部",
    "Brighton and Hove Albion": "布莱顿足球俱乐部",
    "Burnley": "伯恩利足球俱乐部",
    "Chelsea": "切尔西足球俱乐部",
    "Crystal Palace": "水晶宫足球俱乐部",
    "Everton": "埃弗顿足球俱乐部",
    "Fulham": "富勒姆足球俱乐部",
    "Ipswich Town": "伊普斯威奇足球俱乐部",
    "Leeds United": "利兹联足球俱乐部",
    "Leicester City": "莱斯特城足球俱乐部",
    "Liverpool": "利物浦足球俱乐部",
    "Luton Town": "卢顿足球俱乐部",
    "Manchester City": "曼彻斯特城（曼城）足球俱乐部",
    "Manchester United": "曼彻斯特联（曼联）足球俱乐部",
    "Newcastle United": "纽卡斯尔联足球俱乐部",
    "Nottingham Forest": "诺丁汉森林足球俱乐部",
    "Sheffield United": "谢菲尔德联足球俱乐部",
    "Southampton": "南安普顿足球俱乐部",
    "Sunderland": "桑德兰足球俱乐部",
    "Tottenham Hotspur": "托特纳姆热刺足球俱乐部",
    "West Ham United": "西汉姆联足球俱乐部",
    "Wolverhampton Wanderers": "狼队足球俱乐部",
    "Coventry City": "考文垂足球俱乐部",
    "Middlesbrough": "米德尔斯堡足球俱乐部",
    "Norwich City": "诺维奇足球俱乐部",
    "Watford": "沃特福德足球俱乐部",
    "West Bromwich Albion": "西布罗姆维奇足球俱乐部",
    "Blackburn Rovers": "布莱克本流浪者足球俱乐部",
    "Bristol City": "布里斯托尔城足球俱乐部",
    "Sheffield Wednesday": "谢菲尔德星期三足球俱乐部",
    "Hull City": "赫尔城足球俱乐部",
    "Stoke City": "斯托克城足球俱乐部",
    "Swansea City": "斯旺西足球俱乐部",
    "Birmingham City": "伯明翰城足球俱乐部",
    "Wrexham": "雷克瑟姆足球俱乐部",
    # --- La Liga ---
    "Alavés": "阿拉维斯足球俱乐部",
    "Deportivo Alavés": "阿拉维斯足球俱乐部",
    "Almeria": "阿尔梅里亚足球俱乐部",
    "Almería": "阿尔梅里亚足球俱乐部",
    "Athletic Club": "毕尔巴鄂竞技足球俱乐部",
    "Athletic Bilbao": "毕尔巴鄂竞技足球俱乐部",
    "Atlético Madrid": "马德里竞技足球俱乐部",
    "Atletico Madrid": "马德里竞技足球俱乐部",
    "Atlético de Madrid": "马德里竞技足球俱乐部",
    "Barcelona": "巴塞罗那足球俱乐部",
    "FC Barcelona": "巴塞罗那足球俱乐部",
    "Celta Vigo": "维戈塞尔塔足球俱乐部",
    "RC Celta": "维戈塞尔塔足球俱乐部",
    "Cádiz": "加的斯足球俱乐部",
    "Elche": "埃尔切足球俱乐部",
    "Espanyol": "西班牙人足球俱乐部",
    "RCD Espanyol": "西班牙人足球俱乐部",
    "Getafe": "赫塔费足球俱乐部",
    "Girona": "赫罗纳足球俱乐部",
    "Granada": "格拉纳达足球俱乐部",
    "Las Palmas": "拉斯帕尔马斯足球俱乐部",
    "Leganés": "莱加内斯足球俱乐部",
    "Leganes": "莱加内斯足球俱乐部",
    "Levante": "莱万特足球俱乐部",
    "Mallorca": "马略卡足球俱乐部",
    "RCD Mallorca": "马略卡足球俱乐部",
    "Osasuna": "奥萨苏纳足球俱乐部",
    "CA Osasuna": "奥萨苏纳足球俱乐部",
    "Oviedo": "皇家奥维耶多足球俱乐部",
    "Real Oviedo": "皇家奥维耶多足球俱乐部",
    "Rayo Vallecano": "巴列卡诺足球俱乐部",
    "Real Betis": "皇家贝蒂斯足球俱乐部",
    "Real Madrid": "皇家马德里足球俱乐部",
    "Real Sociedad": "皇家社会足球俱乐部",
    "Real Valladolid": "巴拉多利德足球俱乐部",
    "Sevilla": "塞维利亚足球俱乐部",
    "Valencia": "瓦伦西亚足球俱乐部",
    "Villarreal": "比利亚雷亚尔足球俱乐部",
    "Racing Santander": "桑坦德竞技足球俱乐部",
    "Eibar": "埃瓦尔足球俱乐部",
    "Sporting Gijón": "希洪竞技足球俱乐部",
    "Real Zaragoza": "萨拉戈萨足球俱乐部",
    "Mirandés": "米兰德斯足球俱乐部",
    # --- Serie A ---
    "AC Milan": "AC米兰足球俱乐部",
    "Milan": "AC米兰足球俱乐部",
    "Atalanta": "亚特兰大足球俱乐部",
    "Bologna": "博洛尼亚足球俱乐部",
    "Cagliari": "卡利亚里足球俱乐部",
    "Como": "科莫足球俱乐部",
    "Cremonese": "克雷莫内塞足球俱乐部",
    "Empoli": "恩波利足球俱乐部",
    "Fiorentina": "佛罗伦萨足球俱乐部",
    "Frosinone": "弗罗西诺内足球俱乐部",
    "Genoa": "热那亚足球俱乐部",
    "Hellas Verona": "维罗纳足球俱乐部",
    "Inter": "国际米兰足球俱乐部",
    "Internazionale": "国际米兰足球俱乐部",
    "Inter Milan": "国际米兰足球俱乐部",
    "Juventus": "尤文图斯足球俱乐部",
    "Lazio": "拉齐奥足球俱乐部",
    "Lecce": "莱切足球俱乐部",
    "Monza": "蒙扎足球俱乐部",
    "Napoli": "那不勒斯足球俱乐部",
    "Parma": "帕尔马足球俱乐部",
    "Pisa": "比萨足球俱乐部",
    "AS Roma": "罗马足球俱乐部",
    "Roma": "罗马足球俱乐部",
    "Salernitana": "萨勒尼塔纳足球俱乐部",
    "Sassuolo": "萨索洛足球俱乐部",
    "Spezia": "斯佩齐亚足球俱乐部",
    "Torino": "都灵足球俱乐部",
    "Udinese": "乌迪内斯足球俱乐部",
    "Venezia": "威尼斯足球俱乐部",
    "Sampdoria": "桑普多利亚足球俱乐部",
    "Palermo": "巴勒莫足球俱乐部",
    "Bari": "巴里足球俱乐部",
    "Modena": "摩德纳足球俱乐部",
    # --- Bundesliga ---
    "1. FC Heidenheim": "海登海姆足球俱乐部",
    "1. FC Heidenheim 1846": "海登海姆足球俱乐部",
    "Heidenheim": "海登海姆足球俱乐部",
    "1. FC Köln": "科隆足球俱乐部",
    "FC Cologne": "科隆足球俱乐部",
    "1. FC Union Berlin": "柏林联合足球俱乐部",
    "Union Berlin": "柏林联合足球俱乐部",
    "Bayer Leverkusen": "勒沃库森足球俱乐部",
    "Bayern Munich": "拜仁慕尼黑足球俱乐部",
    "FC Bayern Munich": "拜仁慕尼黑足球俱乐部",
    "Borussia Dortmund": "多特蒙德足球俱乐部",
    "Borussia Mönchengladbach": "门兴格拉德巴赫足球俱乐部",
    "Borussia Monchengladbach": "门兴格拉德巴赫足球俱乐部",
    "Eintracht Frankfurt": "法兰克福足球俱乐部",
    "FC Augsburg": "奥格斯堡足球俱乐部",
    "Augsburg": "奥格斯堡足球俱乐部",
    "FC St. Pauli": "圣保利足球俱乐部",
    "St. Pauli": "圣保利足球俱乐部",
    "Hamburger SV": "汉堡足球俱乐部",
    "Hamburg": "汉堡足球俱乐部",
    "Holstein Kiel": "荷尔斯泰因基尔足球俱乐部",
    "Mainz": "美因茨足球俱乐部",
    "1. FSV Mainz 05": "美因茨足球俱乐部",
    "FSV Mainz 05": "美因茨足球俱乐部",
    "RB Leipzig": "RB莱比锡足球俱乐部",
    "SC Freiburg": "弗赖堡足球俱乐部",
    "Freiburg": "弗赖堡足球俱乐部",
    "SV Elversberg": "埃尔弗斯贝格足球俱乐部",
    "SV Darmstadt 98": "达姆施塔特足球俱乐部",
    "TSG Hoffenheim": "霍芬海姆足球俱乐部",
    "Hoffenheim": "霍芬海姆足球俱乐部",
    "VfB Stuttgart": "斯图加特足球俱乐部",
    "Stuttgart": "斯图加特足球俱乐部",
    "VfL Bochum": "波鸿足球俱乐部",
    "VfL Wolfsburg": "沃尔夫斯堡足球俱乐部",
    "Wolfsburg": "沃尔夫斯堡足球俱乐部",
    "Werder Bremen": "云达不莱梅足球俱乐部",
    "SV Werder Bremen": "云达不莱梅足球俱乐部",
    "Hertha Berlin": "柏林赫塔足球俱乐部",
    "Schalke 04": "沙尔克04足球俱乐部",
    "Fortuna Düsseldorf": "杜塞尔多夫足球俱乐部",
    "1. FC Kaiserslautern": "凯泽斯劳滕足球俱乐部",
    "Hannover 96": "汉诺威96足球俱乐部",
    "SC Paderborn 07": "帕德博恩足球俱乐部",
    # --- Ligue 1 ---
    "AJ Auxerre": "欧塞尔足球俱乐部",
    "Auxerre": "欧塞尔足球俱乐部",
    "AS Monaco": "摩纳哥足球俱乐部",
    "Monaco": "摩纳哥足球俱乐部",
    "AS Saint-Étienne": "圣埃蒂安足球俱乐部",
    "Saint-Étienne": "圣埃蒂安足球俱乐部",
    "Angers": "昂热足球俱乐部",
    "Angers SCO": "昂热足球俱乐部",
    "Brest": "布雷斯特足球俱乐部",
    "Stade Brestois 29": "布雷斯特足球俱乐部",
    "Clermont Foot": "克莱蒙足球俱乐部",
    "Le Havre": "勒阿弗尔足球俱乐部",
    "Le Havre AC": "勒阿弗尔足球俱乐部",
    "Lens": "朗斯足球俱乐部",
    "RC Lens": "朗斯足球俱乐部",
    "Lille": "里尔足球俱乐部",
    "LOSC Lille": "里尔足球俱乐部",
    "Lorient": "洛里昂足球俱乐部",
    "FC Lorient": "洛里昂足球俱乐部",
    "Lyon": "里昂足球俱乐部",
    "Olympique Lyonnais": "里昂足球俱乐部",
    "Marseille": "马赛足球俱乐部",
    "Olympique de Marseille": "马赛足球俱乐部",
    "Metz": "梅斯足球俱乐部",
    "FC Metz": "梅斯足球俱乐部",
    "Montpellier": "蒙彼利埃足球俱乐部",
    "Nantes": "南特足球俱乐部",
    "FC Nantes": "南特足球俱乐部",
    "Nice": "尼斯足球俱乐部",
    "OGC Nice": "尼斯足球俱乐部",
    "Paris FC": "巴黎FC足球俱乐部",
    "Paris Saint-Germain": "巴黎圣日耳曼足球俱乐部",
    "Reims": "兰斯足球俱乐部",
    "Stade de Reims": "兰斯足球俱乐部",
    "Rennes": "雷恩足球俱乐部",
    "Stade Rennais": "雷恩足球俱乐部",
    "Strasbourg": "斯特拉斯堡足球俱乐部",
    "RC Strasbourg": "斯特拉斯堡足球俱乐部",
    "RC Strasbourg Alsace": "斯特拉斯堡足球俱乐部",
    "Toulouse": "图卢兹足球俱乐部",
    "Toulouse FC": "图卢兹足球俱乐部",
    "Dunkerque": "敦刻尔克足球俱乐部",
    "Guingamp": "甘冈足球俱乐部",
    "Red Star": "红星足球俱乐部",
    # --- NBA (30) ---
    "Atlanta Hawks": "亚特兰大老鹰",
    "Boston Celtics": "波士顿凯尔特人",
    "Brooklyn Nets": "布鲁克林篮网",
    "Charlotte Hornets": "夏洛特黄蜂",
    "Chicago Bulls": "芝加哥公牛",
    "Cleveland Cavaliers": "克利夫兰骑士",
    "Dallas Mavericks": "达拉斯独行侠",
    "Denver Nuggets": "丹佛掘金",
    "Detroit Pistons": "底特律活塞",
    "Golden State Warriors": "金州勇士",
    "Houston Rockets": "休斯顿火箭",
    "Indiana Pacers": "印第安纳步行者",
    "LA Clippers": "洛杉矶快船",
    "Los Angeles Clippers": "洛杉矶快船",
    "Los Angeles Lakers": "洛杉矶湖人",
    "Memphis Grizzlies": "孟菲斯灰熊",
    "Miami Heat": "迈阿密热火",
    "Milwaukee Bucks": "密尔沃基雄鹿",
    "Minnesota Timberwolves": "明尼苏达森林狼",
    "New Orleans Pelicans": "新奥尔良鹈鹕",
    "New York Knicks": "纽约尼克斯",
    "Oklahoma City Thunder": "俄克拉荷马城雷霆",
    "Orlando Magic": "奥兰多魔术",
    "Philadelphia 76ers": "费城76人",
    "Phoenix Suns": "菲尼克斯太阳",
    "Portland Trail Blazers": "波特兰开拓者",
    "Sacramento Kings": "萨克拉门托国王",
    "San Antonio Spurs": "圣安东尼奥马刺",
    "Toronto Raptors": "多伦多猛龙",
    "Utah Jazz": "犹他爵士",
    "Washington Wizards": "华盛顿奇才",
    # --- NFL (32) ---
    "Arizona Cardinals": "亚利桑那红雀",
    "Atlanta Falcons": "亚特兰大猎鹰",
    "Baltimore Ravens": "巴尔的摩乌鸦",
    "Buffalo Bills": "布法罗比尔",
    "Carolina Panthers": "卡罗来纳黑豹",
    "Chicago Bears": "芝加哥熊",
    "Cincinnati Bengals": "辛辛那提猛虎",
    "Cleveland Browns": "克利夫兰布朗",
    "Dallas Cowboys": "达拉斯牛仔",
    "Denver Broncos": "丹佛野马",
    "Detroit Lions": "底特律雄狮",
    "Green Bay Packers": "绿湾包装工",
    "Houston Texans": "休斯顿德州人",
    "Indianapolis Colts": "印第安纳波利斯小马",
    "Jacksonville Jaguars": "杰克逊维尔美洲虎",
    "Kansas City Chiefs": "堪萨斯城酋长",
    "Las Vegas Raiders": "拉斯维加斯突袭者",
    "Los Angeles Chargers": "洛杉矶闪电",
    "Los Angeles Rams": "洛杉矶公羊",
    "Miami Dolphins": "迈阿密海豚",
    "Minnesota Vikings": "明尼苏达维京人",
    "New England Patriots": "新英格兰爱国者",
    "New Orleans Saints": "新奥尔良圣徒",
    "New York Giants": "纽约巨人",
    "New York Jets": "纽约喷气机",
    "Philadelphia Eagles": "费城老鹰",
    "Pittsburgh Steelers": "匹兹堡钢人",
    "San Francisco 49ers": "旧金山49人",
    "Seattle Seahawks": "西雅图海鹰",
    "Tampa Bay Buccaneers": "坦帕湾海盗",
    "Tennessee Titans": "田纳西泰坦",
    "Washington Commanders": "华盛顿指挥官",
    # --- MLB (30) ---
    "Arizona Diamondbacks": "亚利桑那响尾蛇",
    "Atlanta Braves": "亚特兰大勇士",
    "Athletics": "奥克兰/萨克拉门托运动家",
    "Oakland Athletics": "奥克兰运动家",
    "Baltimore Orioles": "巴尔的摩金莺",
    "Boston Red Sox": "波士顿红袜",
    "Chicago Cubs": "芝加哥小熊",
    "Chicago White Sox": "芝加哥白袜",
    "Cincinnati Reds": "辛辛那提红人",
    "Cleveland Guardians": "克利夫兰守护者",
    "Colorado Rockies": "科罗拉多洛矶",
    "Detroit Tigers": "底特律老虎",
    "Houston Astros": "休斯顿太空人",
    "Kansas City Royals": "堪萨斯城皇家",
    "Los Angeles Angels": "洛杉矶天使",
    "Los Angeles Dodgers": "洛杉矶道奇",
    "Miami Marlins": "迈阿密马林鱼",
    "Milwaukee Brewers": "密尔沃基酿酒人",
    "Minnesota Twins": "明尼苏达双城",
    "New York Mets": "纽约大都会",
    "New York Yankees": "纽约洋基",
    "Philadelphia Phillies": "费城费城人",
    "Pittsburgh Pirates": "匹兹堡海盗",
    "San Diego Padres": "圣地亚哥教士",
    "San Francisco Giants": "旧金山巨人",
    "Seattle Mariners": "西雅图水手",
    "St. Louis Cardinals": "圣路易斯红雀",
    "Tampa Bay Rays": "坦帕湾光芒",
    "Texas Rangers": "得克萨斯游骑兵",
    "Toronto Blue Jays": "多伦多蓝鸟",
    "Washington Nationals": "华盛顿国民",
    # --- NHL (32) ---
    "Anaheim Ducks": "安纳海姆鸭",
    "Boston Bruins": "波士顿棕熊",
    "Buffalo Sabres": "布法罗军刀",
    "Calgary Flames": "卡尔加里火焰",
    "Carolina Hurricanes": "卡罗来纳飓风",
    "Chicago Blackhawks": "芝加哥黑鹰",
    "Colorado Avalanche": "科罗拉多雪崩",
    "Columbus Blue Jackets": "哥伦布蓝衣",
    "Dallas Stars": "达拉斯星",
    "Detroit Red Wings": "底特律红翼",
    "Edmonton Oilers": "埃德蒙顿油人",
    "Florida Panthers": "佛罗里达美洲豹",
    "Los Angeles Kings": "洛杉矶国王",
    "Minnesota Wild": "明尼苏达荒野",
    "Montreal Canadiens": "蒙特利尔加拿大人",
    "Montréal Canadiens": "蒙特利尔加拿大人",
    "Nashville Predators": "纳什维尔掠夺者",
    "New Jersey Devils": "新泽西魔鬼",
    "New York Islanders": "纽约岛人",
    "New York Rangers": "纽约游骑兵",
    "Ottawa Senators": "渥太华参议员",
    "Philadelphia Flyers": "费城飞人",
    "Pittsburgh Penguins": "匹兹堡企鹅",
    "San Jose Sharks": "圣何塞鲨鱼",
    "Seattle Kraken": "西雅图海妖",
    "St. Louis Blues": "圣路易斯蓝调",
    "Tampa Bay Lightning": "坦帕湾闪电",
    "Toronto Maple Leafs": "多伦多枫叶",
    "Utah Hockey Club": "犹他冰球俱乐部",
    "Utah Mammoth": "犹他猛犸象",
    "Vancouver Canucks": "温哥华加人",
    "Vegas Golden Knights": "拉斯维加斯金骑士",
    "Washington Capitals": "华盛顿首都人",
    "Winnipeg Jets": "温尼伯喷气机",
    # --- Additional luukhopman/football-logos club filename variants ---
    "Arsenal FC": "阿森纳足球俱乐部",
    "FC Arsenal": "阿森纳足球俱乐部",
    "Chelsea FC": "切尔西足球俱乐部",
    "FC Chelsea": "切尔西足球俱乐部",
    "Brentford FC": "布伦特福德足球俱乐部",
    "Burnley FC": "伯恩利足球俱乐部",
    "Everton FC": "埃弗顿足球俱乐部",
    "Fulham FC": "富勒姆足球俱乐部",
    "Liverpool FC": "利物浦足球俱乐部",
    "Sunderland AFC": "桑德兰足球俱乐部",
    "RCD Espanyol Barcelona": "西班牙人足球俱乐部",
    "Real Betis Balompié": "皇家贝蒂斯足球俱乐部",
    "Real Betis Balompie": "皇家贝蒂斯足球俱乐部",
    "Celta de Vigo": "维戈塞尔塔足球俱乐部",
    "Elche CF": "埃尔切足球俱乐部",
    "Getafe CF": "赫塔费足球俱乐部",
    "Girona FC": "赫罗纳足球俱乐部",
    "Levante UD": "莱万特足球俱乐部",
    "Sevilla FC": "塞维利亚足球俱乐部",
    "Valencia CF": "瓦伦西亚足球俱乐部",
    "Villarreal CF": "比利亚雷亚尔足球俱乐部",
    "ACF Fiorentina": "佛罗伦萨足球俱乐部",
    "Atalanta BC": "亚特兰大足球俱乐部",
    "Bologna FC 1909": "博洛尼亚足球俱乐部",
    "Cagliari Calcio": "卡利亚里足球俱乐部",
    "Como 1907": "科莫足球俱乐部",
    "Genoa CFC": "热那亚足球俱乐部",
    "Juventus FC": "尤文图斯足球俱乐部",
    "Parma Calcio 1913": "帕尔马足球俱乐部",
    "Pisa Sporting Club": "比萨足球俱乐部",
    "SS Lazio": "拉齐奥足球俱乐部",
    "SSC Napoli": "那不勒斯足球俱乐部",
    "Torino FC": "都灵足球俱乐部",
    "Udinese Calcio": "乌迪内斯足球俱乐部",
    "US Cremonese": "克雷莫内塞足球俱乐部",
    "US Lecce": "莱切足球俱乐部",
    "US Sassuolo": "萨索洛足球俱乐部",
    "1.FC Heidenheim 1846": "海登海姆足球俱乐部",
    "1.FC Köln": "科隆足球俱乐部",
    "1.FC Koln": "科隆足球俱乐部",
    "1.FC Union Berlin": "柏林联合足球俱乐部",
    "1.FSV Mainz 05": "美因茨足球俱乐部",
    "Bayer 04 Leverkusen": "勒沃库森足球俱乐部",
    "FC Bayern Munich": "拜仁慕尼黑足球俱乐部",
    "FC Lorient": "洛里昂足球俱乐部",
    "FC Metz": "梅斯足球俱乐部",
    "FC Toulouse": "图卢兹足球俱乐部",
    "Olympique Lyon": "里昂足球俱乐部",
    "Olympique Marseille": "马赛足球俱乐部",
    "RC Strasbourg Alsace": "斯特拉斯堡足球俱乐部",
    "Stade Rennais FC": "雷恩足球俱乐部",
    "Deportivo A Coruña": "拉科鲁尼亚足球俱乐部",
    "Málaga CF": "马拉加足球俱乐部",
    "Frosinone Calcio": "弗罗西诺内足球俱乐部",
    "FC Schalke 04": "沙尔克04足球俱乐部",
    "SV 07 Elversberg": "埃尔弗斯贝格足球俱乐部",
    "TSG 1899 Hoffenheim": "霍芬海姆足球俱乐部",
    "ESTAC Troyes": "特鲁瓦足球俱乐部",
    "Le Mans FC": "勒芒足球俱乐部",
}


def _strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )


def _norm_team_key(text: str) -> str:
    s = _strip_accents(text).lower().replace("&", "and")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


_NORM_TEAM_ZH_MAP: Dict[str, str] = {_norm_team_key(k): v for k, v in TEAM_ZH_MAP.items()}


def resolve_team_zh(name_en: str) -> str:
    """Resolve official Chinese team name with accent- and affix-tolerant lookup."""
    if name_en in TEAM_ZH_MAP:
        return TEAM_ZH_MAP[name_en]
    nk = _norm_team_key(name_en)
    if nk in _NORM_TEAM_ZH_MAP:
        return _NORM_TEAM_ZH_MAP[nk]
    stripped = re.sub(r"^(?:1\s+)?(?:fc|cf|ac|acf|sc|ssc|as|ud|cd|rcd|rc|ca|ss|us|afc|sv|vfl|vfb|tsg|fsv|ogc|aj|losc)\s+", "", nk)
    stripped = re.sub(r"\s+(?:fc|cf|sc|afc|ac|1909|1913|1907|1846|1899|04|05|29|98)$", "", stripped).strip()
    if stripped in _NORM_TEAM_ZH_MAP:
        return _NORM_TEAM_ZH_MAP[stripped]
    return ""


FOOTBALL_WIKI_ALIASES: Dict[str, str] = {
    "1.FC Heidenheim 1846": "1. FC Heidenheim",
    "1.FC Köln": "1. FC Köln",
    "1.FC Union Berlin": "1. FC Union Berlin",
    "1.FSV Mainz 05": "1. FSV Mainz 05",
    "Bayer 04 Leverkusen": "Bayer 04 Leverkusen",
    "Bayern Munich": "FC Bayern Munich",
    "Borussia Mönchengladbach": "Borussia Mönchengladbach",
    "FC St. Pauli": "FC St. Pauli",
    "FC Toulouse": "Toulouse FC",
    "Olympique Lyon": "Olympique Lyonnais",
    "Olympique Marseille": "Olympique de Marseille",
    "Paris FC": "Paris FC",
    "Paris Saint-Germain": "Paris Saint-Germain F.C.",
    "RC Lens": "RC Lens",
    "RC Strasbourg Alsace": "RC Strasbourg Alsace",
    "Stade Brestois 29": "Stade Brestois 29",
    "Stade Rennais FC": "Stade Rennais F.C.",
    "AS Monaco": "AS Monaco FC",
    "LOSC Lille": "Lille OSC",
    "Inter Milan": "Inter Milan",
    "AC Milan": "AC Milan",
    "AS Roma": "AS Roma",
    "SS Lazio": "S.S. Lazio",
    "Juventus FC": "Juventus FC",
    "SSC Napoli": "SSC Napoli",
    "ACF Fiorentina": "ACF Fiorentina",
    "Atalanta BC": "Atalanta BC",
    "Bologna FC 1909": "Bologna FC 1909",
    "Parma Calcio 1913": "Parma Calcio 1913",
    "Pisa Sporting Club": "Pisa SC",
    "Como 1907": "Como 1907",
    "US Cremonese": "US Cremonese",
    "US Lecce": "US Lecce",
    "US Sassuolo": "US Sassuolo Calcio",
    "Genoa CFC": "Genoa CFC",
    "Cagliari Calcio": "Cagliari Calcio",
    "Udinese Calcio": "Udinese Calcio",
    "Torino FC": "Torino FC",
    "Hellas Verona": "Hellas Verona FC",
    "Athletic Bilbao": "Athletic Bilbao",
    "Atlético de Madrid": "Atlético Madrid",
    "CA Osasuna": "CA Osasuna",
    "Celta de Vigo": "RC Celta de Vigo",
    "Deportivo Alavés": "Deportivo Alavés",
    "Elche CF": "Elche CF",
    "FC Barcelona": "FC Barcelona",
    "Getafe CF": "Getafe CF",
    "Girona FC": "Girona FC",
    "Levante UD": "Levante UD",
    "Rayo Vallecano": "Rayo Vallecano",
    "RCD Espanyol Barcelona": "RCD Espanyol",
    "RCD Mallorca": "RCD Mallorca",
    "Real Betis Balompié": "Real Betis",
    "Real Madrid": "Real Madrid CF",
    "Real Oviedo": "Real Oviedo",
    "Real Sociedad": "Real Sociedad",
    "Sevilla FC": "Sevilla FC",
    "Valencia CF": "Valencia CF",
    "Villarreal CF": "Villarreal CF",
    "Arsenal FC": "Arsenal F.C.",
    "Aston Villa": "Aston Villa F.C.",
    "AFC Bournemouth": "AFC Bournemouth",
    "Brentford FC": "Brentford F.C.",
    "Brighton & Hove Albion": "Brighton & Hove Albion F.C.",
    "Burnley FC": "Burnley F.C.",
    "Chelsea FC": "Chelsea F.C.",
    "Crystal Palace": "Crystal Palace F.C.",
    "Everton FC": "Everton F.C.",
    "Fulham FC": "Fulham F.C.",
    "Leeds United": "Leeds United F.C.",
    "Liverpool FC": "Liverpool F.C.",
    "Manchester City": "Manchester City F.C.",
    "Manchester United": "Manchester United F.C.",
    "Newcastle United": "Newcastle United F.C.",
    "Nottingham Forest": "Nottingham Forest F.C.",
    "Sunderland AFC": "Sunderland A.F.C.",
    "Tottenham Hotspur": "Tottenham Hotspur F.C.",
    "West Ham United": "West Ham United F.C.",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers F.C.",
}

# Iconic derby/rival team name pairs (substring or exact match on name_en within league)
ICONIC_RIVALS: List[Tuple[str, str, str, str]] = [
    ("premier_league", "Manchester United", "Manchester City", "曼彻斯特德比"),
    ("premier_league", "Arsenal", "Tottenham Hotspur", "北伦敦德比"),
    ("premier_league", "Liverpool", "Everton", "默西塞德德比"),
    ("premier_league", "Chelsea", "Arsenal", "伦敦豪门德比"),
    ("la_liga", "Real Madrid", "Barcelona", "西班牙国家德比"),
    ("la_liga", "Real Madrid", "Atlético", "马德里德比"),
    ("la_liga", "Barcelona", "Espanyol", "加泰罗尼亚德比"),
    ("la_liga", "Sevilla", "Real Betis", "塞维利亚德比"),
    ("serie_a", "Inter", "AC Milan", "米兰德比"),
    ("serie_a", "Juventus", "Torino", "都灵德比"),
    ("serie_a", "AS Roma", "Lazio", "罗马德比"),
    ("serie_a", "Juventus", "Inter", "意大利国家德比"),
    ("bundesliga", "Bayern Munich", "Borussia Dortmund", "德国国家德比"),
    ("bundesliga", "Leverkusen", "Köln", "莱茵德比"),
    ("ligue_1", "Paris Saint-Germain", "Marseille", "法国国家德比"),
    ("ligue_1", "Lyon", "Saint-Étienne", "罗讷河谷德比"),
    ("nba", "Los Angeles Lakers", "Clippers", "洛杉矶德比"),
    ("nba", "Los Angeles Lakers", "Boston Celtics", "黄绿宿敌对决"),
    ("nba", "New York Knicks", "Brooklyn Nets", "纽约同城德比"),
    ("nba", "Golden State Warriors", "Cleveland Cavaliers", "总决赛经典对决"),
    ("nfl", "Dallas Cowboys", "Houston Texans", "得州德比"),
    ("nfl", "New York Giants", "New York Jets", "纽约同城对决"),
    ("nfl", "Kansas City Chiefs", "San Francisco 49ers", "超级碗经典对决"),
    ("nfl", "Green Bay Packers", "Chicago Bears", "百年宿敌对决"),
    ("mlb", "New York Yankees", "Boston Red Sox", "基袜百年世仇"),
    ("mlb", "New York Yankees", "New York Mets", "纽约地铁大战"),
    ("mlb", "Los Angeles Dodgers", "San Francisco Giants", "加州世仇对决"),
    ("nhl", "Toronto Maple Leafs", "Montreal Canadiens", "原始六队加拿大世仇"),
    ("nhl", "New York Rangers", "New York Islanders", "纽约冰球德比"),
    ("ncaa", "Duke Blue Devils", "North Carolina Tar Heels", "烟草之路宿敌"),
    ("ncaa", "Ohio State Buckeyes", "Michigan Wolverines", "百年宿敌对决"),
    ("ncaa", "Georgia Bulldogs", "Florida Gators", "东南联盟宿敌对决"),
]


# ---------------------------------------------------------------------------
# Part 2: Complete 96-Template Registry & Unique Entity Definitions
# ---------------------------------------------------------------------------

# Maps every single template (#1..#96) from the user's table to a canonical entity_id
TEMPLATE_96_REGISTRY: List[Tuple[int, str, str, str]] = [
    # (rank, template_name, entity_id, note)
    (1, "158_IP_OSTER", "ip_oster", "Oster 小家电"),
    (2, "476_ip_ford", "ip_ford", "福特（主模板）"),
    (3, "323_JULIUSK9", "ip_julius_k9", "Julius-K9 宠物用品"),
    (4, "028_IP_ohayou_spank", "ip_ohayou_spank", "おはよう!スパンク（Spank 日漫）"),
    (5, "381_hemier_league_selfmodel", "sports_premier_league", "英超联赛（模板名拼写变体 hemier_league）"),
    (6, "221_IP_bmw", "ip_bmw", "宝马"),
    (7, "311_IP_friends", "ip_friends", "老友记"),
    (8, "197_IP_Triumph", "ip_triumph", "Triumph（同时涵盖摩托与内衣双品牌）"),
    (9, "351_bleach", "ip_bleach", "死神 BLEACH"),
    (10, "269_IP_metallica", "ip_metallica", "Metallica 乐队"),
    (11, "301_IP_vancleefarpels_test", "ip_van_cleef_arpels", "梵克雅宝"),
    (12, "289_IP_squishmallows", "ip_squishmallows", "Squishmallows 毛绒玩具"),
    (13, "518_ip_slayer", "ip_slayer", "Slayer 乐队"),
    (14, "356_champion1103test0511", "ip_champion", "Champion 运动品牌"),
    (15, "443_ip_balmain", "ip_balmain", "Balmain 巴尔曼"),
    (16, "283_IP_rezero", "ip_rezero", "Re:从零开始的异世界生活"),
    (17, "235_IP_demonslayer_ceshi_1", "ip_demon_slayer", "鬼灭之刃（测试1）"),
    (18, "470_ip_dragonball", "ip_dragon_ball", "七龙珠"),
    (19, "107_IP_HATSUNEMIKU_V4", "ip_hatsune_miku", "初音未来 V4"),
    (20, "523_ip_streetfighter", "ip_street_fighter", "街头霸王"),
    (21, "047_IP_APPLE_WATCHBAND", "ip_apple_watch", "苹果 / Apple Watch 表带"),
    (22, "288_IP_sevendeadlysins", "ip_seven_deadly_sins", "七大罪"),
    (23, "191_IP_TOMandJERRY", "ip_tom_and_jerry", "猫和老鼠"),
    (24, "232_IP_davpilkey_test", "ip_dav_pilkey", "Dav Pilkey（神探狗狗/内裤超人）"),
    (25, "138_IP_MIFFYRABBIT_HIGHACCURACY", "ip_miffy", "米菲兔 Miffy"),
    (26, "343_SUPERMARIO_WORD", "ip_super_mario", "超级马力欧"),
    (27, "294_IP_tintin", "ip_tintin", "丁丁历险记"),
    (28, "473_ip_duke_excepmtion", "sports_ncaa_duke", "杜克大学（例外模板）"),
    (29, "035_IP_ADVENTURETIME", "ip_adventure_time", "探险活宝"),
    (30, "305_IP_zigzag", "ip_zig_zag", "Zig-Zag 卷烟纸品牌"),
    (31, "509_ip_nirvana2", "ip_nirvana", "涅槃乐队 Nirvana（v2）"),
    (32, "090_IP_DOMINOS", "ip_dominos", "达美乐披萨 Domino's"),
    (33, "508_ip_nirvana", "ip_nirvana", "涅槃乐队 Nirvana"),
    (34, "389_ip_NEW_HOLLAND", "ip_new_holland", "纽荷兰农机 New Holland"),
    (35, "064_IP_BP", "ip_bp", "英国石油 BP"),
    (36, "263_IP_mandms", "ip_mms", "M&M's 巧克力豆"),
    (37, "285_IP_rusty", "ip_rusty", "Rusty 冲浪服饰（R Dot 标）"),
    (38, "182_IP_SUZUKI", "ip_suzuki", "铃木 Suzuki"),
    (39, "068_IP_Budweiser", "ip_budweiser", "百威啤酒 Budweiser"),
    (40, "020_IP_cars_aurelia_llm_black", "ip_cars_aurelia_ambig", "歧义待确认：皮克斯《赛车总动员》/ 蓝旗亚 Aurelia"),
    (41, "441_ip_badcutebunny", "ip_badcutebunny_manual", "待人工确认：电商泛词或 Bad Bunny 相关"),
    (42, "478_ip_ford_copy", "ip_ford", "福特（copy 变体）"),
    (43, "409_ip_onepiece", "ip_one_piece", "海贼王 / 航海王"),
    (44, "122_IP_JUJUTSUKAISEN", "ip_jujutsu_kaisen", "咒术回战"),
    (45, "195_IP_TheSecretLifeofPets", "ip_secret_life_of_pets", "爱宠大机密"),
    (46, "522_ip_startrek", "ip_star_trek", "星际迷航"),
    (47, "412_ip_ralphlauren", "ip_ralph_lauren", "拉夫劳伦 Ralph Lauren"),
    (48, "187_IP_THESIMPSONver2", "ip_the_simpsons", "辛普森一家"),
    (49, "202_IP_UGA_1", "sports_ncaa_georgia", "佐治亚大学（UGA）"),
    (50, "096_IP_FALLOUT", "ip_fallout", "辐射 Fallout"),
    (51, "186_IP_THENEWYORKER_V1", "ip_the_new_yorker", "纽约客杂志 The New Yorker"),
    (52, "145_IP_MYHEROACADEMIA", "ip_my_hero_academia", "我的英雄学院"),
    (53, "317_IP", "ip_generic_317", "泛化模板（无核心实体名）"),
    (54, "151_IP_NBA_Positive", "sports_nba", "NBA 联赛"),
    (55, "298_IP_ugg_patent", "ip_ugg", "UGG 品牌"),
    (56, "385_ip_Jenny_Urquhart_prompt", "ip_jenny_urquhart", "Jenny Urquhart 英国插画家"),
    (57, "056_IP_BEYONCE", "ip_beyonce", "碧昂丝 Beyoncé"),
    (58, "485_ip_godzilla_3", "ip_godzilla", "哥斯拉"),
    (59, "291_IP_strawberryshortcake", "ip_strawberry_shortcake", "草莓甜心 Strawberry Shortcake"),
    (60, "237_IP_demonslayer_huawen", "ip_demon_slayer", "鬼灭之刃（花纹变体）"),
    (61, "471_ip_duke", "sports_ncaa_duke", "杜克大学"),
    (62, "475_ip_florida", "sports_ncaa_florida", "佛罗里达大学（Gators）"),
    (63, "125_IP_LOEWE", "ip_loewe", "罗意威 LOEWE"),
    (64, "486_ip_gulf", "ip_gulf", "海湾石油 Gulf"),
    (65, "392_ip_Rilakkuma_prompt", "ip_rilakkuma", "轻松小熊 Rilakkuma"),
    (66, "215_IP_atari", "ip_atari", "雅达利 Atari"),
    (67, "198_IP_Trolls", "ip_trolls", "梦工厂魔发精灵 Trolls"),
    (68, "162_IP_PEANUTS_copy", "ip_peanuts", "花生漫画 / 史努比 Peanuts"),
    (69, "199_IP_TwentyOnePilots", "ip_twenty_one_pilots", "二十一号飞行员乐队"),
    (70, "261_IP_louisvuitton", "ip_louis_vuitton", "路易威登 Louis Vuitton"),
    (71, "310_IP_disney", "ip_disney", "迪士尼 Disney"),
    (72, "234_IP_demonslayer_ceshi", "ip_demon_slayer", "鬼灭之刃（测试）"),
    (73, "086_IP_DCCOMICS_HIGHACCURACY", "ip_dc_comics", "DC 漫画"),
    (74, "400_ip_dragonball", "ip_dragon_ball", "七龙珠（二号模板）"),
    (75, "444_ip_band", "ip_generic_band", "泛化模板（乐队类目，无指定实体）"),
    (76, "180_IP_STEALABRAINROT", "ip_steal_a_brainrot", "Steal a Brainrot（Roblox 热门游戏）"),
    (77, "014_IP_Tokyoghoul_llm_black", "ip_tokyo_ghoul", "东京喰种"),
    (78, "442_ip_ball", "ip_generic_ball", "泛化模板（球类类目，无指定实体）"),
    (79, "103_IP_HATSUNEMIKU1103", "ip_hatsune_miku", "初音未来（1103）"),
    (80, "002_AUDIselfmodel", "ip_audi", "奥迪 Audi"),
    (81, "244_IP_evelknievel", "ip_evel_knievel", "Evel Knievel 特技车手"),
    (82, "226_IP_costadelmar_COSTA", "ip_costa_del_mar", "Costa Del Mar 太阳镜"),
    (83, "355_chainsawman", "ip_chainsaw_man", "电锯人 Chainsaw Man"),
    (84, "178_IP_SPIRIT_IMG", "ip_spirit_ambig", "歧义待确认：梦工厂《小马王 Spirit》/ Spirit Halloween"),
    (85, "479_ip_ford_mat", "ip_ford", "福特（mat 变体）"),
    (86, "220_IP_beyonce_strategy", "ip_beyonce", "碧昂丝（策略变体）"),
    (87, "159_IP_PAWPATROL_COPYRIGHT", "ip_paw_patrol", "汪汪队立大功 PAW Patrol"),
    (88, "331_NOVAK_DJOKOVICselfmodel", "ip_novak_djokovic", "诺瓦克·德约科维奇（ND 个人徽标）"),
    (89, "017_IP_Warhammer_llm_black", "ip_warhammer", "战锤 Warhammer"),
    (90, "406_ip_my_dress_llm_black", "ip_my_dress_up_darling", "更衣人偶坠入爱河"),
    (91, "252_IP_gunsnroses_strategy", "ip_guns_n_roses", "枪炮与玫瑰乐队 Guns N' Roses"),
    (92, "480_ip_ford_prompt", "ip_ford", "福特（prompt 变体）"),
    (93, "377_guess_test", "ip_guess", "GUESS 时尚品牌"),
    (94, "511_ip_oklahoma", "sports_ncaa_oklahoma", "俄克拉荷马大学"),
    (95, "438_ip_artist", "ip_generic_artist", "泛化模板（艺术家类目，无指定实体）"),
    (96, "126_IP_LibertyUniversity", "sports_ncaa_liberty", "自由大学"),
]

# Unique downloadable / resolvable IP entity specs (for Part 2; sports_linked items resolve to Part 1)
SCH96_ENTITY_SPECS: List[Dict[str, Any]] = [
    # --- Brands & Corporate Marks ---
    {
        "entity_id": "ip_oster",
        "subdir": "brands",
        "category": "needs_manual_ref",
        "v2_domain": "brand",
        "name_en": "Oster",
        "name_zh": "奥斯特 Oster（小家电）",
        "wiki_titles": ["John Oster Manufacturing Company"],
        "wiki_file_hints": ["Oster_logo.svg", "Osterizer_logo.svg"],
        "commons_queries": ["\"Oster\" appliance logo"],
        "skip_fetch": True,
        "desc_zh": "美国小家电与搅拌机品牌 Oster 的官方文字标识，常见于厨房电器面板、包装盒与产品铭牌。",
    },
    {
        "entity_id": "ip_ford",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Ford",
        "name_zh": "福特汽车 Ford",
        "wiki_titles": ["Ford Motor Company"],
        "wiki_file_hints": ["Ford_logo_flat.svg", "Ford_Motor_Company_Logo.svg"],
        "commons_queries": ["Ford_logo_flat.svg", "Ford Motor Company logo"],
        "local_existing": [],
        "desc_zh": "福特汽车经典深蓝椭圆配银白连笔手写体“Ford”徽标，椭圆形外框比例与手写连笔末端卷曲具有极高辨识度。",
    },
    {
        "entity_id": "ip_julius_k9",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Julius-K9",
        "name_zh": "Julius-K9（宠物装备）",
        "wiki_titles": ["Julius-K9"],
        "wiki_file_hints": ["Julius-K9_logo.svg", "Julius_K9_logo.png"],
        "commons_queries": ["Julius-K9 logo", "Julius K9"],
        "desc_zh": "欧洲知名犬用胸背带与宠物装备品牌 JULIUS-K9 魔术贴徽章字标，常见粗体白字黑底织唛贴片形式。",
    },
    {
        "entity_id": "ip_bmw",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "BMW",
        "name_zh": "宝马汽车 BMW",
        "wiki_titles": ["BMW"],
        "wiki_file_hints": ["BMW.svg", "BMW_logo_(gray).svg"],
        "commons_queries": ["BMW.svg", "BMW logo"],
        "local_existing": [],
        "desc_zh": "宝马圆形蓝白四象限内圈配黑色外环与“BMW”三字母徽标，核心特征为左上蓝、右上白、左下白、右下蓝的对角交替扇形格。",
    },
    {
        "entity_id": "ip_triumph_motorcycles",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Triumph Motorcycles",
        "name_zh": "凯旋摩托车 Triumph Motorcycles",
        "template_override": ["197_IP_Triumph"],
        "wiki_titles": ["Triumph Motorcycles Ltd"],
        "wiki_file_hints": ["Triumph_Motorcycles_logo.svg", "Triumph_motorcycles_logo_2013.svg"],
        "commons_queries": ["Triumph Motorcycles logo"],
        "desc_zh": "英国凯旋摩托车（Triumph Motorcycles）经典长尾“R”延伸下划线字标或三角形徽记，与内衣品牌凯黛芬妮（Triumph International）完全区分。",
    },
    {
        "entity_id": "ip_triumph_international",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Triumph International",
        "name_zh": "黛安芬 Triumph International（内衣服饰）",
        "template_override": ["197_IP_Triumph"],
        "wiki_titles": ["Triumph International"],
        "wiki_file_hints": ["Triumph_International_logo.svg", "Triumph_logo_2022.svg"],
        "commons_queries": ["Triumph International logo"],
        "desc_zh": "黛安芬（Triumph International）服饰与内衣品牌字标，线条纤细柔顺，与英国凯旋摩托车标在品类与字体结构上截然不同。",
    },
    {
        "entity_id": "ip_van_cleef_arpels",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Van Cleef & Arpels",
        "name_zh": "梵克雅宝 Van Cleef & Arpels",
        "wiki_titles": ["Van Cleef & Arpels"],
        "wiki_file_hints": ["Van_Cleef_%26_Arpels_logo.svg", "Van_Cleef_&_Arpels_logo.svg"],
        "commons_queries": ["Van Cleef Arpels logo"],
        "desc_zh": "法国高级珠宝世家梵克雅宝（Van Cleef & Arpels）官方徽标与字母字标，常伴随四叶草 Alhambra 经典轮廓或 VCA 连体花押字。",
    },
    {
        "entity_id": "ip_champion",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Champion",
        "name_zh": "冠军 Champion（运动服饰）",
        "wiki_titles": ["Champion (sportswear)"],
        "wiki_file_hints": ["Champion_logo.svg", "Champion_athleticwear_logo.svg"],
        "commons_queries": ["Champion sportswear logo", "Champion C logo"],
        "desc_zh": "美国运动休闲品牌 Champion 经典的红蓝双色大“C”字袖标及手写连笔草书“Champion”文字徽标。",
    },
    {
        "entity_id": "ip_balmain",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Balmain",
        "name_zh": "巴尔曼 Balmain",
        "wiki_titles": ["Balmain"],
        "wiki_file_hints": ["Balmain_logo.svg"],
        "commons_queries": ["Balmain logo"],
        "local_existing": [],
        "desc_zh": "法国高奢时装屋 Balmain 几何衬线“BALMAIN PARIS”官方文字标识与交错 BP 迷宫徽记。",
    },
    {
        "entity_id": "ip_apple_watch",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Apple / Apple Watch",
        "name_zh": "苹果 / Apple Watch",
        "wiki_titles": ["Apple Watch", "Apple Inc."],
        "wiki_file_hints": ["Apple_Watch_official_logo.svg", "Apple_logo_black.svg"],
        "commons_queries": ["Apple Watch logo", "Apple_logo_black.svg"],
        "local_existing": [],
        "desc_zh": "苹果公司缺口苹果轮廓徽标与 Apple Watch 组合字标，高频出现在智能手表表带外包装、扣具与配件说明卡。",
    },
    {
        "entity_id": "ip_zig_zag",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Zig-Zag",
        "name_zh": "Zig-Zag 品牌标识",
        "wiki_titles": ["Zig-Zag (company)"],
        "wiki_file_hints": ["Zig-Zag_logo.svg", "Zig-Zag_logo.png", "ZZ-Boris-w-frame-bw.jpg"],
        "commons_queries": ["Zig-Zag logo", "Zouave Zig-Zag"],
        "desc_zh": "百年法式品牌 Zig-Zag 标志性佐阿夫士兵人物头像与“ZIG-ZAG”双行标题标识。",
    },
    {
        "entity_id": "ip_dominos",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Domino's Pizza",
        "name_zh": "达美乐披萨 Domino's",
        "wiki_titles": ["Domino's"],
        "wiki_file_hints": ["Dominos_pizza_logo.svg", "Domino's_pizza_logo.svg"],
        "commons_queries": ["Domino's pizza logo"],
        "desc_zh": "达美乐披萨倾斜45度红蓝双色骨牌徽标，核心特征为上方红色格含1个白点、下方蓝色格含2个斜对白点。",
    },
    {
        "entity_id": "ip_new_holland",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "New Holland Agriculture",
        "name_zh": "纽荷兰农机 New Holland",
        "wiki_titles": ["New Holland Agriculture"],
        "wiki_file_hints": ["New_Holland_Agriculture_logo.svg", "New_Holland_logo.svg"],
        "commons_queries": ["New Holland Agriculture logo", "New Holland logo"],
        "desc_zh": "全球农机巨头纽荷兰（New Holland）蓝底金黄麦穗叶片与“NEW HOLLAND”组合徽标。",
    },
    {
        "entity_id": "ip_bp",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "BP",
        "name_zh": "英国石油 BP",
        "wiki_titles": ["BP"],
        "wiki_file_hints": ["BP_Helios_logo.svg", "BP_logo.svg"],
        "commons_queries": ["BP Helios logo", "BP_Helios_logo.svg"],
        "desc_zh": "英国石油公司（BP）绿黄白放射状“太阳花（Helios）”向日葵几何徽标及小写绿字“bp”。",
    },
    {
        "entity_id": "ip_mms",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "M&M's",
        "name_zh": "M&M's 巧克力豆",
        "wiki_titles": ["M&M's"],
        "wiki_file_hints": ["M&M's_logo.svg", "M%26M%27s_logo.svg"],
        "commons_queries": ["M&M's logo"],
        "desc_zh": "M&M's 标志性厚实棕色描边倾斜圆润小写字母“m&m's”商标标识，常见于糖果包装与潮玩服饰印花。",
    },
    {
        "entity_id": "ip_rusty",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Rusty",
        "name_zh": "Rusty 冲浪服饰（R Dot）",
        "wiki_titles": ["Rusty (surfwear)", "Rusty Preisendorfer"],
        "wiki_file_hints": ["Rusty_R_dot_logo.svg", "Rusty_Surfboards_logo.png", "Rusty_surf_logo.svg", "Rusty_logo.svg"],
        "commons_queries": ["\"Rusty\" surf logo", "Rusty Preisendorfer"],
        "desc_zh": "冲浪与滑板服饰品牌 Rusty 的标志性“R Dot”实心圆点镂空“R”几何图形标识及“RUSTY”字标。",
    },
    {
        "entity_id": "ip_suzuki",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Suzuki",
        "name_zh": "铃木汽车/摩托 Suzuki",
        "wiki_titles": ["Suzuki"],
        "wiki_file_hints": ["Suzuki_logo_2.svg", "Suzuki_logo_2025.svg"],
        "commons_queries": ["Suzuki_logo_2.svg", "Suzuki logo"],
        "local_existing": [],
        "desc_zh": "铃木公司标志性红色折角菱形“S”立体徽记配深蓝“SUZUKI”全大写字标。",
    },
    {
        "entity_id": "ip_budweiser",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Budweiser",
        "name_zh": "百威啤酒 Budweiser",
        "wiki_titles": ["Budweiser"],
        "wiki_file_hints": ["Budweiser_logo_2016.svg", "Budweiser_logo.svg"],
        "commons_queries": ["Budweiser logo"],
        "desc_zh": "百威啤酒红色蝴蝶结状缎带徽章或连笔斜体手写“Budweiser”与皇冠徽记。",
    },
    {
        "entity_id": "ip_ralph_lauren",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Ralph Lauren",
        "name_zh": "拉夫劳伦 Ralph Lauren",
        "wiki_titles": ["Ralph Lauren Corporation"],
        "wiki_file_hints": ["Ralph_Lauren_logo.svg", "Polo_Ralph_Lauren_logo.svg"],
        "commons_queries": ["Ralph Lauren logo"],
        "local_existing": [],
        "desc_zh": "拉夫劳伦经典衬线体“RALPH LAUREN”字标与挥杆骑马打马球人物刺绣小标。",
    },
    {
        "entity_id": "ip_the_new_yorker",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "The New Yorker",
        "name_zh": "纽约客 The New Yorker",
        "wiki_titles": ["The New Yorker"],
        "wiki_file_hints": ["The_New_Yorker_logo.svg", "Eustace_Tilley_logo.svg"],
        "commons_queries": ["The New Yorker logo"],
        "desc_zh": "《纽约客》杂志标志性高瘦修长衬线体刊头“THE NEW YORKER”及佩戴高礼帽与单片眼镜的尤斯塔斯·蒂利侧影徽记。",
    },
    {
        "entity_id": "ip_ugg",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "UGG",
        "name_zh": "UGG 雪地靴品牌",
        "wiki_titles": ["UGG (brand)"],
        "wiki_file_hints": ["UGG_logo.svg", "Ugg_logo.svg"],
        "commons_queries": ["UGG brand logo"],
        "desc_zh": "Deckers 旗下雪地靴品牌 UGG 粗体字母徽标，常见大小写交错“UGG”或雪地靴后跟织唛标牌。",
    },
    {
        "entity_id": "ip_loewe",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Loewe",
        "name_zh": "罗意威 LOEWE",
        "wiki_titles": ["Loewe (fashion brand)"],
        "wiki_file_hints": ["Loewe_logo.svg", "Loewe_Anagram.svg"],
        "commons_queries": ["Loewe logo", "Loewe Anagram"],
        "local_existing": [],
        "desc_zh": "西班牙高奢品牌罗意威经典“LOEWE”字标及四枚对称“L”字母缠绕构成的 Anagram 徽标。",
    },
    {
        "entity_id": "ip_gulf",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Gulf Oil",
        "name_zh": "海湾石油 Gulf",
        "wiki_titles": ["Gulf Oil"],
        "wiki_file_hints": ["Gulf_Oil_logo.svg", "Gulf_logo.svg"],
        "commons_queries": ["Gulf Oil logo"],
        "desc_zh": "海湾石油经典橙色圆形底盘配深蓝粗体斜写“Gulf”字标及海湾赛车蓝橙条纹涂装锚点。",
    },
    {
        "entity_id": "ip_atari",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Atari",
        "name_zh": "雅达利 Atari",
        "wiki_titles": ["Atari"],
        "wiki_file_hints": ["Atari_logo_red.svg", "Atari_official_2012_logo.svg"],
        "commons_queries": ["Atari logo"],
        "local_existing": [],
        "desc_zh": "电子游戏先驱雅达利经典对称“富士山/A字”三岔竖条纹徽标及“ATARI”字体。",
    },
    {
        "entity_id": "ip_louis_vuitton",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Louis Vuitton",
        "name_zh": "路易威登 Louis Vuitton",
        "wiki_titles": ["Louis Vuitton"],
        "wiki_file_hints": ["Louis_Vuitton_logo_and_wordmark.svg", "Louis_Vuitton_Monogram_LV.svg"],
        "commons_queries": ["Louis Vuitton logo"],
        "local_existing": [],
        "desc_zh": "路易威登交叠“LV”花押字徽标与四瓣花卉/四角星老花图谱及“LOUIS VUITTON”无衬线字标。",
    },
    {
        "entity_id": "ip_audi",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Audi",
        "name_zh": "奥迪汽车 Audi",
        "wiki_titles": ["Audi"],
        "wiki_file_hints": ["Audi-Logo_2016.svg", "Audi_logo_detail.svg"],
        "commons_queries": ["Audi-Logo_2016.svg", "Audi logo"],
        "local_existing": [],
        "desc_zh": "奥迪标志性水平并排且逐个等距互扣的四个圆环徽标，环数严格为4个，常见银色立体或纯黑扁平形式。",
    },
    {
        "entity_id": "ip_costa_del_mar",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "Costa Del Mar",
        "name_zh": "Costa Del Mar 偏光镜",
        "wiki_titles": ["Costa Del Mar"],
        "wiki_file_hints": ["Costa_Del_Mar_logo.svg", "Costa_Del_Mar_logo.png", "Costa_Del_Mar_logo.jpg"],
        "commons_queries": ["Costa Del Mar logo"],
        "desc_zh": "美国海钓偏光太阳镜品牌 Costa Del Mar 圆形海浪双“C”融合字母徽标与“COSTA”标识。",
    },
    {
        "entity_id": "ip_guess",
        "subdir": "brands",
        "category": "brand",
        "v2_domain": "brand",
        "name_en": "GUESS",
        "name_zh": "GUESS 时装品牌",
        "wiki_titles": ["Guess (clothing)"],
        "wiki_file_hints": ["Guess_logo.svg", "GUESS_triangle_logo.svg"],
        "commons_queries": ["Guess clothing logo"],
        "desc_zh": "美国时装品牌 GUESS 红色边框倒等腰三角形徽标，内含“GUESS ? U.S.A.”字样及底部红色问号。",
    },
    # --- Music, Celebrities & Individual Athletes ---
    {
        "entity_id": "ip_metallica",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Metallica",
        "name_zh": "金属乐队 Metallica",
        "wiki_titles": ["Metallica"],
        "wiki_file_hints": ["Metallica_logo.svg", "Metallica_wordmark.svg"],
        "commons_queries": ["Metallica logo"],
        "desc_zh": "重金属传奇乐队 Metallica 标志性首尾字母“M”和“A”呈尖锐闪电倒钩延展的对称字体徽标。",
    },
    {
        "entity_id": "ip_slayer",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Slayer",
        "name_zh": "杀手乐队 Slayer",
        "wiki_titles": ["Slayer"],
        "wiki_file_hints": ["Slayer_Logo.svg", "Slayer_logo.png", "Slayer_band_logo.svg", "Slayer_logo.svg", "Slayer-Logo.svg"],
        "commons_queries": ["Slayer band logo"],
        "desc_zh": "激流金属乐队 Slayer 锐利锯齿状“SLAYER”字标及经典的剑十字五芒星徽记。",
    },
    {
        "entity_id": "ip_nirvana",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Nirvana",
        "name_zh": "涅槃乐队 Nirvana",
        "wiki_titles": ["Nirvana (band)"],
        "wiki_file_hints": ["Nirvana_album_cover_logo.svg", "Nirvana_logo.svg"],
        "commons_queries": ["Nirvana band logo", "Nirvana smiley logo"],
        "desc_zh": "涅槃乐队（Nirvana）经典拉长衬线体“NIRVANA”字标，常配黑底黄色手绘叉眼吐舌笑脸涂鸦。",
    },
    {
        "entity_id": "ip_beyonce",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Beyoncé",
        "name_zh": "碧昂丝 Beyoncé",
        "wiki_titles": ["Beyoncé"],
        "wiki_file_hints": ["Beyonce_wordmark.svg", "Beyoncé_logo.svg"],
        "commons_queries": ["Beyoncé logo", "Beyonce wordmark"],
        "desc_zh": "流行天后碧昂丝（Beyoncé）官方演出与巡演周边字标，常见金属质感“BEYONCÉ”及文艺复兴/牛仔卡特专辑标志。",
    },
    {
        "entity_id": "ip_twenty_one_pilots",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Twenty One Pilots",
        "name_zh": "二十一号飞行员乐队 Twenty One Pilots",
        "wiki_titles": ["Twenty One Pilots"],
        "wiki_file_hints": ["Twenty_One_Pilots_logo_(2024).svg", "Twenty_One_Pilots_logo.svg"],
        "commons_queries": ["Twenty One Pilots logo"],
        "desc_zh": "美国双人乐队 Twenty One Pilots 经典的几何竖杠斜杠符号“|-/”或“||-//”极简几何徽标。",
    },
    {
        "entity_id": "ip_evel_knievel",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Evel Knievel",
        "name_zh": "Evel Knievel 特技车手",
        "wiki_titles": ["Evel Knievel"],
        "wiki_file_hints": ["Evel_Knievel_logo.svg", "Evel_Knievel_logo.png"],
        "commons_queries": ["Evel Knievel logo"],
        "desc_zh": "美国传奇摩托车特技车手 Evel Knievel 标志性红白蓝星条“V”形徽标及复古粗体字标。",
    },
    {
        "entity_id": "ip_novak_djokovic",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Novak Djokovic",
        "name_zh": "诺瓦克·德约科维奇 Novak Djokovic",
        "wiki_titles": ["Novak Djokovic"],
        "wiki_file_hints": ["Novak_Djokovic_logo.svg", "Novak_Djokovic_signature.svg"],
        "commons_queries": ["Novak Djokovic logo", "Novak Djokovic signature"],
        "desc_zh": "网球天王德约科维奇个人“ND”花押字徽标（负空间形成展翅飞鸟轮廓）及官方个人签名标识。",
    },
    {
        "entity_id": "ip_guns_n_roses",
        "subdir": "music_celebrity_sports",
        "category": "music_celebrity_sports",
        "v2_domain": "brand",
        "name_en": "Guns N' Roses",
        "name_zh": "枪炮与玫瑰乐队 Guns N' Roses",
        "wiki_titles": ["Guns N' Roses"],
        "wiki_file_hints": ["Guns_N'_Roses_logo.svg", "Guns_N_Roses_logo.svg"],
        "commons_queries": ["Guns N Roses logo"],
        "desc_zh": "美国硬摇滚乐队枪炮与玫瑰经典圆形金环徽标：双左轮手枪交叉配两朵红玫瑰缠绕，环绕“GUNS N' ROSES”字样。",
    },
    # --- Anime, Games, Film, TV, Comics & Toys ---
    {
        "entity_id": "ip_ohayou_spank",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Ohayou! Spank",
        "name_zh": "早上好！斯潘克（Ohayou! Spank）",
        "wiki_titles": ["Hello! Spank"],
        "wiki_file_hints": ["Hello_Spank_logo.png", "Ohayo_Spank_logo.png", "Ohayouspank.jpg"],
        "commons_queries": ["Hello Spank", "Ohayou Spank"],
        "desc_zh": "日本经典复古少女漫《早上好！斯潘克（Hello! Spank）》主角小白犬（大垂耳圆脸小狗）与经典日语标题徽标。",
    },
    {
        "entity_id": "ip_friends",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Friends",
        "name_zh": "老友记 Friends",
        "wiki_titles": ["Friends"],
        "wiki_file_hints": ["Friends_logo.svg"],
        "commons_queries": ["Friends_logo.svg", "Friends TV series logo"],
        "desc_zh": "美剧《老友记（Friends）》标志性手写体大写“F·R·I·E·N·D·S”字标，核心识别锚点为字母间红、蓝、黄三色交替圆点。",
    },
    {
        "entity_id": "ip_bleach",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Bleach",
        "name_zh": "死神 BLEACH",
        "wiki_titles": ["Bleach (TV series)", "Bleach (manga)"],
        "wiki_file_hints": ["Bleach_(manga)_Logo.png", "Bleach_(anime)_logo.png", "Bleach_Thousand-Year_Blood_War_Logo.svg"],
        "commons_queries": ["Bleach anime logo", "Bleach manga logo"],
        "desc_zh": "热血日漫《死神（BLEACH）》官方标题徽标，常见极粗黑体倾斜大写“BLEACH”配橙红骷髅或死霸装刀锋元素。",
    },
    {
        "entity_id": "ip_squishmallows",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Squishmallows",
        "name_zh": "Squishmallows 毛绒玩偶",
        "wiki_titles": ["Squishmallows"],
        "wiki_file_hints": ["Squishmallows_logo.svg", "Squishmallows_logo.png", "Squishmallows_logo.jpg"],
        "commons_queries": ["Squishmallows logo"],
        "desc_zh": "热门圆润毛绒玩偶品牌 Squishmallows 的彩色渐变气泡字体官方徽标，常见于吊牌、包装盒与联名服饰。",
    },
    {
        "entity_id": "ip_rezero",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Re:Zero - Starting Life in Another World",
        "name_zh": "Re:从零开始的异世界生活",
        "wiki_titles": ["Re:Zero − Starting Life in Another World", "Re:Zero - Starting Life in Another World"],
        "wiki_file_hints": ["ReZero_logo.svg", "Re-Zero_logo.png"],
        "commons_queries": ["Re:Zero logo", "Re Zero logo"],
        "desc_zh": "轻小说与动画《Re:从零开始的异世界生活》官方标题标识，以紫粉渐变“Re:”前缀配合“ゼロから始める異世界生活”字样。",
    },
    {
        "entity_id": "ip_demon_slayer",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Demon Slayer: Kimetsu no Yaiba",
        "name_zh": "鬼灭之刃 Demon Slayer",
        "wiki_titles": ["Demon Slayer: Kimetsu no Yaiba"],
        "wiki_file_hints": ["Kimetsu_no_Yaiba_logo.svg", "Demon_Slayer_Kimetsu_no_Yaiba_logo.svg"],
        "commons_queries": ["Kimetsu no Yaiba logo", "Demon Slayer logo"],
        "local_existing": [],
        "desc_zh": "超人气动画《鬼灭之刃》毛笔书法风标题字标与绿黑市松格纹等代表性视觉元素（关联模板含花纹变体）。",
    },
    {
        "entity_id": "ip_dragon_ball",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Dragon Ball",
        "name_zh": "七龙珠 Dragon Ball",
        "wiki_titles": ["Dragon Ball"],
        "wiki_file_hints": ["Dragon_Ball_logo.svg", "Dragon_Ball_Z_logo.svg"],
        "commons_queries": ["Dragon Ball logo", "Dragon Ball Z logo"],
        "local_existing": [],
        "desc_zh": "鸟山明经典作品《七龙珠》黄红渐变粗体字标，常见四星龙珠嵌入“O”字母或右侧红色神龙剪影。",
    },
    {
        "entity_id": "ip_hatsune_miku",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Hatsune Miku",
        "name_zh": "初音未来 Hatsune Miku",
        "wiki_titles": ["Hatsune Miku"],
        "wiki_file_hints": ["Hatsune_Miku_logo.svg", "Hatsune_Miku_V4X.png"],
        "commons_queries": ["Hatsune Miku logo", "Hatsune Miku V4X"],
        "desc_zh": "虚拟歌手初音未来（Hatsune Miku）葱绿与桃红科技线条字标及葱绿色双马尾形象（关联 V4 与 1103 双模板）。",
    },
    {
        "entity_id": "ip_street_fighter",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Street Fighter",
        "name_zh": "街头霸王 Street Fighter",
        "wiki_titles": ["Street Fighter"],
        "wiki_file_hints": ["Street_Fighter_old_logo.svg", "Street_Fighter_Logo.png"],
        "commons_queries": ["Street Fighter logo"],
        "local_existing": [],
        "desc_zh": "卡普空经典格斗游戏《街头霸王（Street Fighter）》黄橙渐变立体倾斜喷漆风格标题字标。",
    },
    {
        "entity_id": "ip_seven_deadly_sins",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "The Seven Deadly Sins",
        "name_zh": "七大罪 The Seven Deadly Sins",
        "wiki_titles": ["The Seven Deadly Sins (manga)"],
        "wiki_file_hints": ["The_Seven_Deadly_Sins_logo.svg", "Nanatsu_no_Taizai_logo.png"],
        "commons_queries": ["The Seven Deadly Sins manga logo", "Nanatsu no Taizai logo"],
        "desc_zh": "奇幻日漫《七大罪（七つの大罪）》官方标题徽标及七宗罪动物纹章系列图腾。",
    },
    {
        "entity_id": "ip_tom_and_jerry",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Tom and Jerry",
        "name_zh": "猫和老鼠 Tom and Jerry",
        "wiki_titles": ["Tom and Jerry"],
        "wiki_file_hints": ["Tom_and_Jerry_logo.svg", "Tom_&_Jerry_logo.svg"],
        "commons_queries": ["Tom and Jerry logo"],
        "desc_zh": "经典动画《猫和老鼠（Tom and Jerry）》官方红黄配色立体卡通标题字标与角色剪影。",
    },
    {
        "entity_id": "ip_dav_pilkey",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Dav Pilkey (Dog Man / Captain Underpants)",
        "name_zh": "Dav Pilkey（神探狗狗 / 内裤超人）",
        "wiki_titles": ["Dog Man", "Dav Pilkey", "Captain Underpants"],
        "wiki_file_hints": ["Dog_Man_logo.png", "Captain_Underpants_logo.svg"],
        "commons_queries": ["Dog Man logo", "Captain Underpants logo"],
        "desc_zh": "美国童书作家 Dav Pilkey 代表作《神探狗狗（Dog Man）》与《内裤超人（Captain Underpants）》官方书标与角色标识。",
    },
    {
        "entity_id": "ip_miffy",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Miffy",
        "name_zh": "米菲兔 Miffy",
        "wiki_titles": ["Miffy"],
        "wiki_file_hints": ["Miffy_logo.svg", "Nijntje.svg"],
        "commons_queries": ["Miffy logo", "Nijntje"],
        "desc_zh": "荷兰迪克·布鲁纳创作的经典极简线条小白兔米菲（Miffy）：黑色粗轮廓双圆点眼睛配交叉“×”形小嘴。",
    },
    {
        "entity_id": "ip_super_mario",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Super Mario",
        "name_zh": "超级马力欧 Super Mario",
        "wiki_titles": ["Super Mario"],
        "wiki_file_hints": ["Super_Mario_Logo.svg", "Super_Mario_wordmark.svg"],
        "commons_queries": ["Super Mario logo"],
        "local_existing": [],
        "desc_zh": "任天堂经典游戏《超级马力欧（Super Mario）》红蓝黄绿多色粗描边立体字母标题字标。",
    },
    {
        "entity_id": "ip_tintin",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "The Adventures of Tintin",
        "name_zh": "丁丁历险记 Tintin",
        "wiki_titles": ["The Adventures of Tintin"],
        "wiki_file_hints": ["The_Adventures_of_Tintin_logo.svg", "Tintin_logo.svg"],
        "commons_queries": ["Tintin logo", "Adventures of Tintin logo"],
        "desc_zh": "比利时埃尔热经典漫画《丁丁历险记》手写标题字标及一撮前翘金发配小白狗米卢（Snowy）标志性剪影。",
    },
    {
        "entity_id": "ip_adventure_time",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Adventure Time",
        "name_zh": "探险活宝 Adventure Time",
        "wiki_titles": ["Adventure Time"],
        "wiki_file_hints": ["Adventure_Time_logo.png", "Adventure_Time_logo.svg", "Adventure_Time_-_Title_card.png"],
        "commons_queries": ["Adventure Time logo"],
        "desc_zh": "卡通频道经典动画《探险活宝（Adventure Time）》红色长剑贯穿白字金属标题牌官方徽标。",
    },
    {
        "entity_id": "ip_one_piece",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "One Piece",
        "name_zh": "海贼王 One Piece",
        "wiki_titles": ["One Piece"],
        "wiki_file_hints": ["One_Piece_Anime_Logo_International.png", "One_piece_logo_1.svg", "One_Piece_Logo.svg", "One_Piece_anime_logo.svg"],
        "commons_queries": ["One Piece logo", "Straw Hat Pirates Jolly Roger"],
        "local_existing": [],
        "desc_zh": "尾田荣一郎代表作《海贼王（ONE PIECE）》官方标题字标，特征为红带黄草帽覆盖字母“O”骷髅、铁锚构成的“I”及路飞拉长手臂“E”。",
    },
    {
        "entity_id": "ip_jujutsu_kaisen",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Jujutsu Kaisen",
        "name_zh": "咒术回战 Jujutsu Kaisen",
        "wiki_titles": ["Jujutsu Kaisen"],
        "wiki_file_hints": ["Jujutsu_Kaisen_logo.svg", "Jujutsu_Kaisen_logo.png"],
        "commons_queries": ["Jujutsu Kaisen logo"],
        "desc_zh": "热门日漫《咒术回战》硬朗破笔书法风标题字标与涡旋诅咒符号徽标。",
    },
    {
        "entity_id": "ip_secret_life_of_pets",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "The Secret Life of Pets",
        "name_zh": "爱宠大机密 The Secret Life of Pets",
        "wiki_titles": ["The Secret Life of Pets"],
        "wiki_file_hints": ["The_Secret_Life_of_Pets_logo.svg", "The_Secret_Life_of_Pets_logo.png"],
        "commons_queries": ["The Secret Life of Pets logo"],
        "desc_zh": "照明娱乐动画电影《爱宠大机密》蓝黄拼色手绘感英文标题徽标，常附带小狗麦克与兔子小白形象。",
    },
    {
        "entity_id": "ip_star_trek",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Star Trek",
        "name_zh": "星际迷航 Star Trek",
        "wiki_titles": ["Star Trek"],
        "wiki_file_hints": ["Star_Trek_logo.svg", "Starfleet_insignia.svg"],
        "commons_queries": ["Star Trek logo", "Starfleet insignia"],
        "local_existing": [],
        "desc_zh": "科幻巨制《星际迷航（Star Trek）》锐利前卫标题字体与星际舰队不对称三角形箭头（Delta）徽章。",
    },
    {
        "entity_id": "ip_the_simpsons",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "The Simpsons",
        "name_zh": "辛普森一家 The Simpsons",
        "wiki_titles": ["The Simpsons"],
        "wiki_file_hints": ["The_Simpsons_yellow_logo.svg", "The_Simpsons_logo.svg"],
        "commons_queries": ["The Simpsons logo"],
        "local_existing": [],
        "desc_zh": "长寿美漫《辛普森一家（The Simpsons）》明黄色手绘俏皮黑描边标题字标及蓝天白云背景主题。",
    },
    {
        "entity_id": "ip_fallout",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Fallout",
        "name_zh": "辐射 Fallout",
        "wiki_titles": ["Fallout (franchise)"],
        "wiki_file_hints": ["Fallout_logo.svg", "Vault_Boy_artwork.svg"],
        "commons_queries": ["Fallout logo", "Fallout video game logo"],
        "local_existing": [],
        "desc_zh": "贝塞斯达末世 RPG《辐射（Fallout）》复古未来主义闪电斜切字标，常见避难所科技齿轮与蓝黄配色避难所小子。",
    },
    {
        "entity_id": "ip_my_hero_academia",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "My Hero Academia",
        "name_zh": "我的英雄学院 My Hero Academia",
        "wiki_titles": ["My Hero Academia"],
        "wiki_file_hints": ["My_Hero_Academia_-_international_logo.png", "My_Hero_Academia_logo_in_Japan_20150106.png", "My_Hero_Academia_logo.svg", "Boku_no_Hero_Academia_logo.svg"],
        "commons_queries": ["My Hero Academia logo"],
        "desc_zh": "热血少年漫《我的英雄学院》美漫爆炸边框配红黄渐变立体字标。",
    },
    {
        "entity_id": "ip_jenny_urquhart",
        "subdir": "anime_games_entertainment",
        "category": "needs_manual_ref",
        "v2_domain": "ip",
        "name_en": "Jenny Urquhart",
        "name_zh": "Jenny Urquhart 英国插画家",
        "wiki_titles": ["Jenny Urquhart"],
        "wiki_file_hints": [],
        "commons_queries": ["\"Jenny Urquhart\""],
        "desc_zh": "英国当代风景与动物插画家 Jenny Urquhart 个人署名与画作版权体系（若无开源官标，建议人工补充参考图）。",
    },
    {
        "entity_id": "ip_godzilla",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Godzilla",
        "name_zh": "哥斯拉 Godzilla",
        "wiki_titles": ["Godzilla", "Godzilla (franchise)"],
        "wiki_file_hints": ["Godzilla_logo.svg", "Godzilla_fr_logo.svg"],
        "commons_queries": ["Godzilla logo"],
        "local_existing": [],
        "desc_zh": "东宝特摄怪兽之王《哥斯拉（GODZILLA）》经典锯齿锋利电影字标及背鳍放射光线怪兽剪影。",
    },
    {
        "entity_id": "ip_strawberry_shortcake",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Strawberry Shortcake",
        "name_zh": "草莓甜心 Strawberry Shortcake",
        "wiki_titles": ["Strawberry Shortcake"],
        "wiki_file_hints": ["Strawberry_Shortcake_logo.svg", "Strawberry_Shortcake_logo.png"],
        "commons_queries": ["Strawberry Shortcake logo"],
        "desc_zh": "经典怀旧动漫玩具形象《草莓甜心（Strawberry Shortcake）》粉红草莓花边字母徽标与戴草莓帽小女孩形象。",
    },
    {
        "entity_id": "ip_rilakkuma",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Rilakkuma",
        "name_zh": "轻松小熊 Rilakkuma",
        "wiki_titles": ["Rilakkuma"],
        "wiki_file_hints": ["Rilakkuma_logo.svg", "Rilakkuma_logo.png"],
        "commons_queries": ["Rilakkuma logo", "Rilakkuma"],
        "desc_zh": "San-X 旗下治愈系卡通形象轻松小熊（Rilakkuma）：棕熊外耳内黄、白肚皮及圆润棕黄日英文标题字标。",
    },
    {
        "entity_id": "ip_trolls",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "DreamWorks Trolls",
        "name_zh": "魔发精灵 Trolls",
        "wiki_titles": ["Trolls (franchise)", "Trolls (film)"],
        "wiki_file_hints": ["Trolls_logo.svg", "DreamWorks_Trolls_logo.png"],
        "commons_queries": ["DreamWorks Trolls logo", "Trolls film logo"],
        "desc_zh": "梦工厂动画系列《魔发精灵（Trolls）》彩色亮片毛绒立体标题徽标与彩色直立爆炸发造型形象。",
    },
    {
        "entity_id": "ip_peanuts",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Peanuts (Snoopy)",
        "name_zh": "花生漫画 / 史努比 Peanuts",
        "wiki_titles": ["Peanuts"],
        "wiki_file_hints": ["Peanuts_logo.svg", "Snoopy_Peanuts.png"],
        "commons_queries": ["Peanuts comic strip logo", "Peanuts logo"],
        "desc_zh": "查尔斯·舒尔茨经典漫画《花生漫画（PEANUTS）》黄红手绘字体标题及垂耳黑白比格犬史努比（Snoopy）经典轮廓。",
    },
    {
        "entity_id": "ip_disney",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Walt Disney",
        "name_zh": "迪士尼 Disney",
        "wiki_titles": ["The Walt Disney Company", "Walt Disney Pictures"],
        "wiki_file_hints": ["Disney_wordmark.svg", "Walt_Disney_Pictures_2011_logo.svg"],
        "commons_queries": ["Disney_wordmark.svg", "Walt Disney logo"],
        "local_existing": [],
        "desc_zh": "华特迪士尼标志性环形花体签名式“Disney”字标及童话城堡拱弧剪影。",
    },
    {
        "entity_id": "ip_dc_comics",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "DC Comics",
        "name_zh": "DC 漫画 DC Comics",
        "wiki_titles": ["DC Comics"],
        "wiki_file_hints": ["DC_Comics_2024.svg", "DC_Comics_logo.svg"],
        "commons_queries": ["DC Comics logo"],
        "local_existing": [],
        "desc_zh": "DC 漫画经典圆形双线外环配粗体直角“DC”字母徽标（含 2016/2024 经典圆盾与“bullet”版本）。",
    },
    {
        "entity_id": "ip_steal_a_brainrot",
        "subdir": "anime_games_entertainment",
        "category": "needs_manual_ref",
        "v2_domain": "ip",
        "name_en": "Steal a Brainrot",
        "name_zh": "Steal a Brainrot（Roblox 游戏）",
        "wiki_titles": ["Steal a Brainrot"],
        "wiki_file_hints": ["Steal_a_Brainrot_logo.png"],
        "commons_queries": ["\"Steal a Brainrot\""],
        "skip_fetch": True,
        "desc_zh": "Roblox 热门体验《Steal a Brainrot》游戏标题徽标与代表角色图元。",
    },
    {
        "entity_id": "ip_tokyo_ghoul",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Tokyo Ghoul",
        "name_zh": "东京喰种 Tokyo Ghoul",
        "wiki_titles": ["Tokyo Ghoul"],
        "wiki_file_hints": ["Tokyo_Ghoul_logo.svg", "Tokyo_Ghoul_logo.png"],
        "commons_queries": ["Tokyo Ghoul logo"],
        "desc_zh": "暗黑奇幻动漫《东京喰种》高对比红黑断裂手写体标题及金木研拉链面罩独眼赫眼形象。",
    },
    {
        "entity_id": "ip_chainsaw_man",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Chainsaw Man",
        "name_zh": "电锯人 Chainsaw Man",
        "wiki_titles": ["Chainsaw Man"],
        "wiki_file_hints": ["Chainsaw_Man_logo.svg", "Chainsaw_Man_English_logo.svg"],
        "commons_queries": ["Chainsaw Man logo"],
        "desc_zh": "藤本树漫画《电锯人（CHAINSAW MAN）》锯齿切割金属红黄配色标题及波奇塔（Pochita）橙色电锯小狗形象。",
    },
    {
        "entity_id": "ip_paw_patrol",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "PAW Patrol",
        "name_zh": "汪汪队立大功 PAW Patrol",
        "wiki_titles": ["PAW Patrol"],
        "wiki_file_hints": ["PAW_Patrol_logo.svg", "Paw_Patrol_Logo.png"],
        "commons_queries": ["PAW Patrol logo"],
        "desc_zh": "儿童动画《汪汪队立大功（PAW Patrol）》蓝边金红盾牌造型徽标：顶部印“PAW”及白色狗爪印，下方黄色“PATROL”字带。",
    },
    {
        "entity_id": "ip_warhammer",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "Warhammer",
        "name_zh": "战锤 Warhammer",
        "wiki_titles": ["Warhammer 40,000", "Warhammer (game)"],
        "wiki_file_hints": ["Warhammer_40,000_logo.svg", "Warhammer_40k_logo.svg", "Warhammer_logo.svg"],
        "commons_queries": ["Warhammer 40,000 logo", "Warhammer logo"],
        "desc_zh": "Games Workshop 桌面战棋《战锤（Warhammer / 40K）》哥特金属风铁鹰翼标题徽标与双头鹰天鹰徽（Aquila）。",
    },
    {
        "entity_id": "ip_my_dress_up_darling",
        "subdir": "anime_games_entertainment",
        "category": "anime_games_entertainment",
        "v2_domain": "ip",
        "name_en": "My Dress-Up Darling",
        "name_zh": "更衣人偶坠入爱河 My Dress-Up Darling",
        "wiki_titles": ["My Dress-Up Darling"],
        "wiki_file_hints": ["My_Dress-Up_Darling_logo.svg", "Sono_Bisque_Doll_wa_Koi_wo_Suru_logo.png"],
        "commons_queries": ["My Dress-Up Darling logo", "Sono Bisque Doll logo"],
        "desc_zh": "恋爱喜剧动漫《更衣人偶坠入爱河》粉红针线裁缝主题标题字标与女主角喜多川海梦代表性形象。",
    },
    # --- Ambiguous Entries (fetch clean primary candidate + explicitly flag in coverage) ---
    {
        "entity_id": "ip_cars_aurelia_ambig",
        "subdir": "anime_games_entertainment",
        "category": "ambiguous_needs_confirm",
        "v2_domain": "ip",
        "name_en": "Cars (Pixar) / Lancia Aurelia (Ambiguous)",
        "name_zh": "歧义待核：皮克斯《赛车总动员 Cars》/ 蓝旗亚 Aurelia",
        "wiki_titles": ["Cars (franchise)", "Cars (film)"],
        "wiki_file_hints": ["Cars_logo.svg", "Cars_2006_logo.svg"],
        "commons_queries": ["Pixar Cars logo"],
        "desc_zh": "【模板待确认项】已优先采录皮克斯《赛车总动员（Cars）》经典镀铬红底汽车标题徽标；若业务模板实际指向经典汽车 Lancia Aurelia，需再行二次确认。",
    },
    {
        "entity_id": "ip_spirit_ambig",
        "subdir": "anime_games_entertainment",
        "category": "ambiguous_needs_confirm",
        "v2_domain": "ip",
        "name_en": "Spirit: Stallion of the Cimarron / Spirit Halloween (Ambiguous)",
        "name_zh": "歧义待核：梦工厂《小马王 Spirit》/ Spirit Halloween",
        "wiki_titles": ["Spirit: Stallion of the Cimarron", "Spirit (franchise)"],
        "wiki_file_hints": ["Spirit_Stallion_of_the_Cimarron_logo.png", "Spirit_Riding_Free_logo.png"],
        "commons_queries": ["Spirit Stallion of the Cimarron logo", "Spirit Halloween logo"],
        "desc_zh": "【模板待确认项】已优先采录梦工厂动画《小马王（Spirit）》官方标题标识；亦存在美国万圣节零售品牌 Spirit Halloween 同名可能，需结合原样本核对。",
    },
]

# Non-downloadable / unidentifiable templates explicitly accounted for in coverage ledger
NON_FETCHABLE_SPECS: Dict[str, Dict[str, Any]] = {
    "ip_badcutebunny_manual": {
        "category": "needs_manual_ref",
        "name_en": "badcutebunny (Unverified E-Commerce Keyword)",
        "name_zh": "待人工核对：badcutebunny（非标准注册 IP 词或待核对 Bad Bunny）",
        "note": "经查无官方统一商标“badcutebunny”；多为电商贴纸泛词或与歌手 Bad Bunny 混淆，禁止臆测抓取。",
    },
    "ip_generic_317": {
        "category": "generic_unmapped",
        "name_en": "317_IP (Numeric Template ID Only)",
        "name_zh": "未标注核心名（仅模板编号 317_IP）",
        "note": "模板名仅含编号无实体名称，需人工从业务样本库反查对应 IP 后再补采。",
    },
    "ip_generic_band": {
        "category": "generic_unmapped",
        "name_en": "444_ip_band (Generic Band Category)",
        "name_zh": "泛化类目模板（乐队集合，无指定唯一实体）",
        "note": "通用乐队审核类目模板，非单一官标。",
    },
    "ip_generic_ball": {
        "category": "generic_unmapped",
        "name_en": "442_ip_ball (Generic Ball / Sports Category)",
        "name_zh": "泛化类目模板（球类集合，无指定唯一实体）",
        "note": "通用球类审核类目模板，非单一官标。",
    },
    "ip_generic_artist": {
        "category": "generic_unmapped",
        "name_en": "438_ip_artist (Generic Artist Category)",
        "name_zh": "泛化类目模板（艺术家集合，无指定唯一实体）",
        "note": "通用艺术家/插画家审核类目模板，非单一官标。",
    },
}

# Filenames/patterns strictly rejected when parsing Wikipedia/Commons images
WIKI_UI_BLACKLIST = (
    "commons-logo",
    "wikimedia",
    "wikipedia",
    "ambox",
    "padlock",
    "disambig",
    "question_book",
    "wiki_letter",
    "oojs",
    "crystal_clear",
    "nuvola",
    "folder_",
    "red_pog",
    "locator_map",
    "map_of_",
    "edit-clear",
    "speaker_icon",
    "flag_of_",
    "increase2",
    "decrease2",
    "steady2",
    "symbol_support",
    "symbol_question",
    "semi-protection",
    "lock-green",
    "sound-icon",
    "gnome-",
    "tango-",
)


# ---------------------------------------------------------------------------
# HTTP & Text Utilities
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return s or "item"


def http_get_bytes(
    url: str,
    *,
    headers: Dict[str, str],
    timeout: int = 20,
    retries: int = 3,
    delay: float = 0.25,
) -> bytes:
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if delay > 0:
                time.sleep(delay)
            return data
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if exc.code in (404, 410):
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            wait = float(retry_after) if (retry_after and retry_after.isdigit()) else 1.5 * (attempt + 1)
            time.sleep(min(wait, 12.0))
        except Exception as exc:
            last_exc = exc
            time.sleep(1.0 * (attempt + 1))
    assert last_exc is not None
    raise last_exc


def http_get_json(url: str, *, headers: Dict[str, str], delay: float = 0.25) -> Dict[str, Any]:
    raw = http_get_bytes(url, headers=headers, delay=delay)
    return json.loads(raw.decode("utf-8"))


def save_png_rgba(raw_bytes: bytes, dst: Path, min_side: int = 96) -> Dict[str, Any]:
    """Decode image bytes, normalize to RGBA PNG cleanly, verify dimensions and non-blank content."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(raw_bytes)) as im:
        im.load()
        if im.mode == "P":
            rgba = im.convert("RGBA")
        elif im.mode in ("LA", "RGBa", "RGBA"):
            rgba = im.convert("RGBA")
        else:
            rgba = im.convert("RGBA")

        w, h = rgba.size
        if max(w, h) < min_side:
            raise ValueError(f"image too small ({w}x{h} < {min_side})")

        arr = np.asarray(rgba)
        if float(np.std(arr[:, :, :3])) < 1.0 and float(np.std(arr[:, :, 3])) < 1.0:
            raise ValueError("image appears completely uniform/blank")

        # Save cleanly as RGBA PNG
        rgba.save(dst, format="PNG", optimize=True)
    return {"width": w, "height": h, "bytes": dst.stat().st_size}


def render_svg_to_png(svg_bytes: bytes, dst: Path, target_width: int = 512) -> Dict[str, Any]:
    if resvg_py is None:
        raise RuntimeError("resvg_py is unavailable for local SVG rendering")
    svg_str = svg_bytes.decode("utf-8", errors="ignore")
    png_bytes = resvg_py.svg_to_bytes(svg_str, width=target_width, dpi=96.0)
    return save_png_rgba(png_bytes, dst, min_side=64)


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sanitize_no_jargon(text: str) -> str:
    """Assert/verify zero forbidden internal terms in generated prose."""
    for term in FORBIDDEN_JARGON:
        if term in text:
            raise AssertionError(f"Forbidden internal term {term!r} found in text: {text!r}")
    return text


# ---------------------------------------------------------------------------
# Sports Fetching Logic (Part 1: GitHub Big-5 Rosters + Batched Wikipedia/Wikimedia)
# ---------------------------------------------------------------------------

def _search_wikipedia_title(query: str) -> Optional[str]:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": "3",
            "format": "json",
        }
    )
    try:
        data = http_get_json(f"https://en.wikipedia.org/w/api.php?{params}", headers=WIKI_HEADERS, delay=0.2)
        hits = ((data.get("query") or {}).get("search")) or []
        if hits:
            return str(hits[0].get("title") or "").strip() or None
    except Exception:
        return None
    return None


def fetch_github_big5_rosters(force: bool = False) -> Dict[str, List[Dict[str, str]]]:
    """Fetch current Big-5 football club rosters & PNG fallback URLs from `luukhopman/football-logos`."""
    RAW_API_DIR.mkdir(parents=True, exist_ok=True)
    rosters: Dict[str, List[Dict[str, str]]] = {}
    for cfg in LEAGUE_CONFIGS:
        github_dir = cfg.get("github_dir")
        if not github_dir:
            continue
        lid = cfg["league_id"]
        cache_path = RAW_API_DIR / f"github_{lid}.json"
        if cache_path.exists() and not force:
            entries = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            enc_dir = urllib.parse.quote(github_dir)
            url = f"https://api.github.com/repos/luukhopman/football-logos/contents/logos/{enc_dir}"
            print(f"==> [Sports/{lid}] Fetching GitHub roster: {github_dir}")
            entries = json.loads(http_get_bytes(url, headers=GITHUB_HEADERS, delay=0.15).decode("utf-8"))
            cache_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

        clubs: List[Dict[str, str]] = []
        for item in entries:
            if not isinstance(item, dict):
                continue
            fname = str(item.get("name") or "")
            if not fname.lower().endswith(".png"):
                continue
            club_name = fname[:-4].strip()
            clubs.append(
                {
                    "name_en": club_name,
                    "github_png_url": str(item.get("download_url") or ""),
                }
            )
        clubs.sort(key=lambda x: x["name_en"])
        rosters[lid] = clubs
    return rosters


def fetch_sports_leagues_and_teams(force: bool = False, prev_sports: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    RAW_API_DIR.mkdir(parents=True, exist_ok=True)
    SPORTS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    raw_svg_dir = SPORTS_ASSETS_DIR / "raw_svg"
    raw_svg_dir.mkdir(parents=True, exist_ok=True)

    prev_sports = prev_sports or {}
    prev_leagues = {l["league_id"]: l for l in (prev_sports.get("leagues") or []) if isinstance(l, dict) and l.get("league_id")}
    prev_teams = {t["entity_id"]: t for t in (prev_sports.get("teams") or []) if isinstance(t, dict) and t.get("entity_id")}

    big5_rosters = fetch_github_big5_rosters(force=force)

    # 1. Build complete task list for leagues + teams + NCAA
    leagues_out: List[Dict[str, Any]] = []
    teams_out: List[Dict[str, Any]] = []
    unmapped_names: List[str] = []
    failures: List[Dict[str, str]] = []

    leagues_dir = SPORTS_ASSETS_DIR / "leagues"
    leagues_dir.mkdir(parents=True, exist_ok=True)

    # First resolve the 9 League Logos via Wikipedia/Wikimedia (or local simple_icons fallback)
    for cfg in LEAGUE_CONFIGS:
        lid = cfg["league_id"]
        l_dst = leagues_dir / f"{lid}.png"
        l_svg = raw_svg_dir / f"league_{lid}.svg"
        prev_lg = prev_leagues.get(lid) or {}
        l_ok = False
        l_source_used = ""
        l_source_url = ""

        if l_dst.exists() and l_dst.stat().st_size > 256 and not force:
            l_ok = True
            l_source_used = prev_lg.get("source_tier") or "cached_local"
            l_source_url = prev_lg.get("source_url") or ""
        else:
            print(f"==> [Sports/League] Fetching {lid} ({cfg['name_en']})")
            ok_w, src_w, url_w, err_w = fetch_wikimedia_best_logo(
                name_en=cfg["name_en"],
                wiki_titles=cfg["wiki_titles"],
                file_hints=cfg["wiki_file_hints"],
                commons_queries=[f"{cfg['name_en']} logo"],
                dst_png=l_dst,
                dst_svg=l_svg,
                allow_jpg=False,
                category="sports",
            )
            if ok_w:
                l_ok = True
                l_source_used = src_w
                l_source_url = url_w
            elif cfg.get("simple_icon"):
                si_path = ASSETS_DIR / "brand_logos" / "icons" / f"{cfg['simple_icon']}.svg"
                if si_path.exists():
                    render_svg_to_png(si_path.read_bytes(), l_dst, target_width=512)
                    l_ok = True
                    l_source_used = "local_simple_icons"
                    l_source_url = str(si_path.relative_to(PROJECT_ROOT))
            if not l_ok:
                failures.append({"scope": "league", "id": lid, "error": err_w or "no_logo"})

        leagues_out.append(
            {
                "entity_id": f"sports_league_{lid}",
                "league_id": lid,
                "league_group": cfg["league_group"],
                "sport": cfg["sport"],
                "sport_zh": cfg["sport_zh"],
                "country_zh": cfg["country_zh"],
                "name_en": cfg["name_en"],
                "name_zh": cfg["name_zh"],
                "short_zh": cfg["short_zh"],
                "local_path": str(l_dst.relative_to(PROJECT_ROOT)),
                "source_url": l_source_url,
                "source_tier": l_source_used,
                "fetch_ok": l_ok,
                "template_ids": cfg["template_ids"],
            }
        )

    # 2. Assemble all team items across Big-5, NBA/NFL/MLB/NHL, and NCAA
    pending_team_specs: List[Dict[str, Any]] = []
    for cfg in LEAGUE_CONFIGS:
        lid = cfg["league_id"]
        if lid in big5_rosters:
            for club in big5_rosters[lid]:
                name_en = club["name_en"]
                slug = slugify(name_en)
                wiki_title = FOOTBALL_WIKI_ALIASES.get(name_en, name_en)
                pending_team_specs.append(
                    {
                        "entity_id": f"sports_{lid}_{slug}",
                        "league_id": lid,
                        "league_group": cfg["league_group"],
                        "sport": cfg["sport"],
                        "sport_zh": cfg["sport_zh"],
                        "league_name_zh": cfg["short_zh"],
                        "name_en": name_en,
                        "abbreviation": "",
                        "wiki_title": wiki_title,
                        "fallback_url": club.get("github_png_url") or "",
                        "fallback_tier": "github_luukhopman_png",
                        "local_path": str((SPORTS_ASSETS_DIR / lid / f"{slug}.png").relative_to(PROJECT_ROOT)),
                        "svg_path": str((raw_svg_dir / f"{lid}_{slug}.svg").relative_to(PROJECT_ROOT)),
                        "template_ids": [],
                        "category": "sports_football_club",
                    }
                )
        else:
            for name_en, wiki_title, abbr in cfg.get("teams") or []:
                slug = slugify(name_en)
                pending_team_specs.append(
                    {
                        "entity_id": f"sports_{lid}_{slug}",
                        "league_id": lid,
                        "league_group": cfg["league_group"],
                        "sport": cfg["sport"],
                        "sport_zh": cfg["sport_zh"],
                        "league_name_zh": cfg["short_zh"],
                        "name_en": name_en,
                        "abbreviation": abbr,
                        "wiki_title": wiki_title,
                        "fallback_url": "",
                        "fallback_tier": "",
                        "local_path": str((SPORTS_ASSETS_DIR / lid / f"{slug}.png").relative_to(PROJECT_ROOT)),
                        "svg_path": str((raw_svg_dir / f"{lid}_{slug}.svg").relative_to(PROJECT_ROOT)),
                        "template_ids": [],
                        "category": "sports_us_pro",
                    }
                )

    for spec in NCAA_TARGETS:
        slug = spec["slug"]
        pending_team_specs.append(
            {
                "entity_id": f"sports_ncaa_{slug}",
                "league_id": "ncaa",
                "league_group": "ncaa",
                "sport": "collegiate_sports",
                "sport_zh": "美国大学体育（NCAA）",
                "league_name_zh": "NCAA",
                "name_en": spec["name_en"],
                "abbreviation": "",
                "wiki_title": spec["name_en"],
                "fallback_url": "",
                "fallback_tier": "",
                "local_path": str((SPORTS_ASSETS_DIR / "ncaa" / f"{slug}_{spec['espn_id']}.png").relative_to(PROJECT_ROOT)),
                "svg_path": str((raw_svg_dir / f"ncaa_{slug}.svg").relative_to(PROJECT_ROOT)),
                "template_ids": list(spec["template_ids"]),
                "category": "sports_ncaa",
                "explicit_zh": spec["name_zh"],
            }
        )

    # 3. Identify teams that actually need fetching, then batch Wikipedia queries!
    need_wiki_titles: List[str] = []
    need_hint_files: List[str] = []
    for item in pending_team_specs:
        dst = PROJECT_ROOT / item["local_path"]
        if force or not (dst.exists() and dst.stat().st_size > 256):
            need_wiki_titles.append(item["wiki_title"])
            for hf in SPORTS_TEAM_FILE_HINTS.get(item["entity_id"]) or []:
                if hf not in need_hint_files:
                    need_hint_files.append(hf)

    infobox_map: Dict[str, List[str]] = {}
    if need_wiki_titles:
        print(f"==> [Sports] Batch querying Wikipedia infoboxes for {len(need_wiki_titles)} teams...")
        infobox_map = query_wiki_infobox_files(need_wiki_titles, category="sports")

        # Search fallback only for titles that returned zero candidates
        missed = [t for t in dict.fromkeys(need_wiki_titles) if not infobox_map.get(t)]
        if missed:
            print(f"  -> {len(missed)} titles had empty infobox; searching Wikipedia titles...")
            remapped_titles: Dict[str, str] = {}
            for t in missed:
                hit = _search_wikipedia_title(f"{t} club OR team")
                if hit and hit != t:
                    remapped_titles[t] = hit
            if remapped_titles:
                extra_map = query_wiki_infobox_files(list(remapped_titles.values()), category="sports")
                for orig_t, alt_t in remapped_titles.items():
                    if extra_map.get(alt_t):
                        infobox_map[orig_t] = extra_map[alt_t]

    # Batch resolve imageinfo for all candidate File:... names
    all_candidate_files: List[str] = list(need_hint_files)
    for fns in infobox_map.values():
        for fn in fns[:3]:
            if fn not in all_candidate_files:
                all_candidate_files.append(fn)

    imageinfo_map: Dict[str, Dict[str, Any]] = {}
    if all_candidate_files:
        print(f"==> [Sports] Batch resolving Wikimedia imageinfo for {len(all_candidate_files)} candidate files...")
        imageinfo_map = resolve_wiki_imageinfo(all_candidate_files, thumb_width=512)

    # 4. Download / validate each team crest
    for item in pending_team_specs:
        dst = PROJECT_ROOT / item["local_path"]
        dst_svg = PROJECT_ROOT / item["svg_path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        eid = item["entity_id"]
        prev_t = prev_teams.get(eid) or {}

        name_zh = item.get("explicit_zh") or resolve_team_zh(item["name_en"])
        if not name_zh:
            unmapped_names.append(f"{item['league_id']}: {item['name_en']}")

        ok = False
        source_tier = ""
        source_url = ""
        err_msg = ""

        if dst.exists() and dst.stat().st_size > 256 and not force:
            ok = True
            source_tier = prev_t.get("source_tier") or "cached_local"
            source_url = prev_t.get("source_url") or ""
        else:
            hint_fns = SPORTS_TEAM_FILE_HINTS.get(eid) or []
            cands = list(dict.fromkeys(hint_fns + (infobox_map.get(item["wiki_title"]) or [])))
            for fn in cands:
                info = imageinfo_map.get(fn)
                if not info:
                    continue
                mime = str(info.get("mime") or "").lower()
                if "jpeg" in mime:
                    continue
                orig_url = str(info.get("url") or "")
                thumb_url = str(info.get("thumburl") or "")
                width = int(info.get("width") or 0)
                is_svg = "svg" in mime or fn.lower().endswith(".svg")
                dl_url = thumb_url if (is_svg and thumb_url) else (thumb_url if (width > 1200 and thumb_url) else orig_url)
                if not dl_url:
                    continue
                try:
                    raw_img = http_get_bytes(dl_url, headers=WIKI_HEADERS, delay=0.22)
                    save_png_rgba(raw_img, dst, min_side=96)
                    if is_svg and orig_url:
                        try:
                            svg_bytes = http_get_bytes(orig_url, headers=WIKI_HEADERS, delay=0.18)
                            if b"<svg" in svg_bytes.lower():
                                dst_svg.write_bytes(svg_bytes)
                        except Exception:
                            pass
                    ok = True
                    source_tier = "wikimedia_svg_512" if is_svg else "wikimedia_png"
                    source_url = orig_url or dl_url
                    break
                except Exception as exc:
                    err_msg = f"{fn}: {exc}"
                    if is_svg and orig_url and resvg_py is not None:
                        try:
                            svg_bytes = http_get_bytes(orig_url, headers=WIKI_HEADERS, delay=0.18)
                            render_svg_to_png(svg_bytes, dst, target_width=512)
                            dst_svg.write_bytes(svg_bytes)
                            ok = True
                            source_tier = "wikimedia_svg_resvg"
                            source_url = orig_url
                            break
                        except Exception as exc2:
                            err_msg = f"{fn}: {exc2}"

            # Fallback to `luukhopman/football-logos` GitHub PNG for Big-5 clubs if Wikimedia didn't yield one
            if not ok and item.get("fallback_url"):
                try:
                    fb_url = urllib.parse.quote(item["fallback_url"], safe=":/%")
                    raw_fb = http_get_bytes(fb_url, headers=GITHUB_HEADERS, delay=0.08)
                    save_png_rgba(raw_fb, dst, min_side=96)
                    ok = True
                    source_tier = item["fallback_tier"]
                    source_url = fb_url
                    err_msg = ""
                except Exception as exc:
                    err_msg = f"wiki({err_msg}) + github({exc})"

            # Last resort per-team Wikimedia File: search for any remaining missed US pro/NCAA team
            if not ok and not item.get("fallback_url"):
                ok_w, src_w, url_w, err_w = fetch_wikimedia_best_logo(
                    name_en=item["name_en"],
                    wiki_titles=[],
                    file_hints=[],
                    commons_queries=[f'"{item["name_en"]}" logo'],
                    dst_png=dst,
                    dst_svg=dst_svg,
                    allow_jpg=False,
                    category="sports",
                )
                if ok_w:
                    ok = True
                    source_tier = src_w
                    source_url = url_w
                    err_msg = ""
                else:
                    err_msg = err_msg or err_w

        if not ok:
            failures.append({"scope": f"team/{item['league_id']}", "id": item["name_en"], "error": err_msg})

        teams_out.append(
            {
                "entity_id": eid,
                "league_id": item["league_id"],
                "league_group": item["league_group"],
                "sport": item["sport"],
                "sport_zh": item["sport_zh"],
                "league_name_zh": item["league_name_zh"],
                "name_en": item["name_en"],
                "short_name_en": item["name_en"],
                "abbreviation": item["abbreviation"],
                "name_zh": name_zh,
                "team_color": "",
                "team_alt_color": "",
                "local_path": item["local_path"],
                "raw_svg_path": item["svg_path"] if dst_svg.exists() else "",
                "source_url": source_url,
                "source_tier": source_tier,
                "fetch_ok": ok,
                "template_ids": item["template_ids"],
            }
        )

    return {
        "leagues": leagues_out,
        "teams": teams_out,
        "unmapped_names": unmapped_names,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# Wikipedia & Wikimedia Official Logo Fetcher (Part 2)
# ---------------------------------------------------------------------------

def _clean_wiki_filename(raw: str) -> Optional[str]:
    if not raw:
        return None
    s = re.sub(r"<!--.*?-->", "", raw, flags=re.S).strip()
    # Extract [[File:...]] or [[Image:...]]
    m = re.search(r"\[\[(?:File|Image):([^|\]]+)", s, flags=re.I)
    if m:
        s = m.group(1)
    else:
        # Remove template noise / leading brackets
        s = s.split("|")[0].split("\n")[0].strip()
        s = re.sub(r"^(?:File|Image):", "", s, flags=re.I).strip()
        s = s.strip("[]{} ")
    if not s or "{{" in s or "}}" in s or len(s) < 4:
        return None
    if not re.search(r"\.(svg|png|webp|jpg|jpeg)$", s, flags=re.I):
        return None
    low = s.lower()
    if any(bad in low for bad in WIKI_UI_BLACKLIST):
        return None
    return s.replace(" ", "_")


def _parse_infobox_logo_candidates(wikitext: str, category: str) -> List[str]:
    """Extract candidate File:... names from Wikipedia infobox wikitext."""
    candidates: List[str] = []
    # High-priority explicit logo fields (ordered carefully: primary logo before cap/secondary)
    logo_keys = (
        "logo",
        "current_logo",
        "team_logo",
        "image_logo",
        "company_logo",
        "brand_logo",
        "franchise_logo",
        "title_logo",
        "series_logo",
        "show_logo",
        "logo_image",
        "crest",
        "badge",
        "emblem",
        "symbol",
        "cap_logo",
        "uniform_logo",
        "wordmark",
    )
    for key in logo_keys:
        for m in re.finditer(rf"^\s*\|\s*{key}\s*=\s*(.+)$", wikitext, flags=re.I | re.M):
            val = m.group(1)
            fn = _clean_wiki_filename(val)
            if fn and fn not in candidates:
                candidates.append(fn)
            # Also check inline File: references inside multi-image or template values
            for fm in re.finditer(r"(?:File|Image):([^|\}\]\n]+?\.(?:svg|png|webp))", val, flags=re.I):
                fn2 = _clean_wiki_filename(fm.group(1))
                if fn2 and fn2 not in candidates:
                    candidates.append(fn2)

    # Secondary `image` field: accept for football clubs/sports/anime or when filename looks like a logo
    for m in re.finditer(r"^\s*\|\s*image\s*=\s*(.+)$", wikitext, flags=re.I | re.M):
        fn = _clean_wiki_filename(m.group(1))
        if not fn:
            continue
        low = fn.lower()
        is_logo_like = any(
            tok in low for tok in ("logo", "wordmark", "emblem", "crest", "insignia", "title", "symbol", "badge", "shield")
        )
        if (
            is_logo_like
            or (category in ("anime_games_entertainment", "sports") and low.endswith((".svg", ".png")))
        ):
            if fn not in candidates:
                candidates.append(fn)

    # Check `image1` (used inside {{multiple image}} in some infoboxes) ONLY if SVG/PNG and logo-like or sports
    for m in re.finditer(r"^\s*\|\s*image1\s*=\s*(.+)$", wikitext, flags=re.I | re.M):
        fn = _clean_wiki_filename(m.group(1))
        if not fn:
            continue
        low = fn.lower()
        if low.endswith((".svg", ".png")) and (
            category == "sports" or any(tok in low for tok in ("logo", "wordmark", "emblem", "crest", "cap"))
        ):
            if fn not in candidates:
                candidates.append(fn)

    return candidates


def query_wiki_infobox_files(titles: Sequence[str], *, category: str = "anime_games_entertainment") -> Dict[str, List[str]]:
    """Batch-fetch lead wikitext from en.wikipedia.org and extract logo file candidates."""
    out: Dict[str, List[str]] = {}
    clean_titles = list(dict.fromkeys(t for t in titles if t))
    for i in range(0, len(clean_titles), 20):
        batch = clean_titles[i : i + 20]
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "rvsection": "0",
                "redirects": "1",
                "titles": "|".join(batch),
                "format": "json",
            }
        )
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        data = http_get_json(url, headers=WIKI_HEADERS, delay=0.22)
        query = data.get("query") or {}
        norm_map = {n["from"]: n["to"] for n in (query.get("normalized") or [])}
        redir_map = {r["from"]: r["to"] for r in (query.get("redirects") or [])}
        pages = query.get("pages") or {}
        by_title: Dict[str, str] = {}
        for page in pages.values():
            if "missing" in page:
                continue
            revs = page.get("revisions") or []
            if not revs:
                continue
            slots = revs[0].get("slots") or {}
            main_slot = slots.get("main") or {}
            wt = main_slot.get("*") or revs[0].get("*") or ""
            if wt:
                by_title[page.get("title", "")] = wt

        for orig in batch:
            t1 = norm_map.get(orig, orig)
            t2 = redir_map.get(t1, t1)
            wt = by_title.get(t2) or by_title.get(t1) or by_title.get(orig) or ""
            out[orig] = _parse_infobox_logo_candidates(wt, category) if wt else []
    return out


def search_wiki_files(api_base: str, query_text: str, limit: int = 8) -> List[str]:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srnamespace": "6",
            "srsearch": query_text,
            "srlimit": str(limit),
            "format": "json",
        }
    )
    url = f"{api_base}?{params}"
    data = http_get_json(url, headers=WIKI_HEADERS, delay=0.25)
    hits = ((data.get("query") or {}).get("search")) or []
    files: List[str] = []
    for h in hits:
        title = str(h.get("title") or "")
        if title.lower().startswith("file:"):
            fn = title[5:].replace(" ", "_")
            low = fn.lower()
            if any(bad in low for bad in WIKI_UI_BLACKLIST):
                continue
            if low.endswith((".svg", ".png", ".webp")):
                files.append(fn)
    return files


def resolve_wiki_imageinfo(filenames: Sequence[str], *, thumb_width: int = 512) -> Dict[str, Dict[str, Any]]:
    """Resolve authoritative imageinfo (url, thumburl, mime, size) via en.wikipedia.org (supports both enwiki & Commons)."""
    resolved: Dict[str, Dict[str, Any]] = {}
    unique_files = list(dict.fromkeys(f for f in filenames if f))
    for i in range(0, len(unique_files), 20):
        batch = unique_files[i : i + 20]
        titles = "|".join(f"File:{f}" for f in batch)
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "prop": "imageinfo",
                "iiprop": "url|mime|size",
                "iiurlwidth": str(thumb_width),
                "titles": titles,
                "format": "json",
            }
        )
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        data = http_get_json(url, headers=WIKI_HEADERS, delay=0.25)
        query = data.get("query") or {}
        norm_map = {n["from"]: n["to"] for n in (query.get("normalized") or [])}
        pages = (query.get("pages") or {}).values()
        by_title: Dict[str, Dict[str, Any]] = {}
        for page in pages:
            # Note: Commons-hosted files returned via en.wikipedia.org include "missing" + "known" + "imageinfo"
            iis = page.get("imageinfo") or []
            if iis:
                by_title[page.get("title", "")] = iis[0]

        for fn in batch:
            key = f"File:{fn}"
            key_norm = norm_map.get(key, key)
            info = by_title.get(key_norm) or by_title.get(key)
            if info:
                resolved[fn] = info
    return resolved


def _score_candidate_filename(fn: str, name_en: str, hint_set: set[str]) -> Tuple[int, int, int]:
    low = fn.lower()
    if fn in hint_set:
        return (100, 1 if low.endswith(".svg") else 0, -len(fn))
    tokens = [tok for tok in re.split(r"[^a-z0-9]+", name_en.lower()) if len(tok) >= 3]
    token_hits = sum(1 for tok in tokens if tok in low)
    is_svg = 2 if low.endswith(".svg") else (1 if low.endswith(".png") else 0)
    has_logo_word = 2 if any(k in low for k in ("logo", "wordmark", "emblem", "crest", "insignia")) else 0
    bad_penalty = -5 if any(k in low for k in ("cover", "poster", "building", "headquarters", "store", "stadium", "concert")) else 0
    return (token_hits * 3 + has_logo_word + bad_penalty, is_svg, -len(fn))


def fetch_wikimedia_best_logo(
    *,
    name_en: str,
    wiki_titles: Sequence[str],
    file_hints: Sequence[str],
    commons_queries: Sequence[str],
    dst_png: Path,
    dst_svg: Optional[Path],
    allow_jpg: bool = False,
    category: str = "brand",
) -> Tuple[bool, str, str, str]:
    """Resolve and download an official logo from Wikipedia/Wikimedia.

    Returns (ok, source_tier, source_url, error_msg).
    """
    candidates: List[str] = list(file_hints)
    hint_set = set(file_hints)

    # 1. Try Wikipedia infobox first (for all explicit article titles)
    if wiki_titles:
        try:
            # Fetch raw lead section and parse with category-aware filtering
            for wt_title in wiki_titles:
                params = urllib.parse.urlencode(
                    {
                        "action": "query",
                        "prop": "revisions",
                        "rvprop": "content",
                        "rvslots": "main",
                        "rvsection": "0",
                        "redirects": "1",
                        "titles": wt_title,
                        "format": "json",
                    }
                )
                data = http_get_json(f"https://en.wikipedia.org/w/api.php?{params}", headers=WIKI_HEADERS, delay=0.22)
                for page in ((data.get("query") or {}).get("pages") or {}).values():
                    if "missing" in page:
                        continue
                    revs = page.get("revisions") or []
                    if not revs:
                        continue
                    wt = ((revs[0].get("slots") or {}).get("main") or {}).get("*") or ""
                    for fn in _parse_infobox_logo_candidates(wt, category):
                        if fn not in candidates:
                            candidates.append(fn)
        except Exception:
            pass

    # 2. Check Commons & enwiki File: search if we don't yet have a clean resolved candidate
    info_map = resolve_wiki_imageinfo(candidates, thumb_width=512) if candidates else {}

    if not info_map:
        search_cands: List[str] = []
        for q in commons_queries:
            for api_base in (
                "https://commons.wikimedia.org/w/api.php",
                "https://en.wikipedia.org/w/api.php",
            ):
                try:
                    hits = search_wiki_files(api_base, q, limit=8)
                    for fn in hits:
                        if fn not in search_cands:
                            search_cands.append(fn)
                except Exception:
                    continue
        if search_cands:
            search_cands.sort(key=lambda f: _score_candidate_filename(f, name_en, hint_set), reverse=True)
            info_map = resolve_wiki_imageinfo(search_cands[:10], thumb_width=512)
            candidates = search_cands

    # Try downloading candidates in ranked order
    ordered = [fn for fn in candidates if fn in info_map]
    # Ensure explicit hints come first if resolved, then ranked
    ordered.sort(key=lambda f: _score_candidate_filename(f, name_en, hint_set), reverse=True)

    last_err = "no_wiki_candidate_resolved"
    for fn in ordered:
        info = info_map[fn]
        mime = str(info.get("mime") or "").lower()
        orig_url = str(info.get("url") or "")
        thumb_url = str(info.get("thumburl") or "")
        width = int(info.get("width") or 0)
        if not allow_jpg and "jpeg" in mime and fn not in hint_set:
            continue

        is_svg = "svg" in mime or fn.lower().endswith(".svg")
        download_url = thumb_url if (is_svg and thumb_url) else (thumb_url if (width > 1200 and thumb_url) else orig_url)
        if not download_url:
            continue

        try:
            img_bytes = http_get_bytes(download_url, headers=WIKI_HEADERS, delay=0.28)
            save_png_rgba(img_bytes, dst_png, min_side=96)
            if is_svg and dst_svg is not None and orig_url:
                try:
                    svg_bytes = http_get_bytes(orig_url, headers=WIKI_HEADERS, delay=0.22)
                    if b"<svg" in svg_bytes.lower():
                        dst_svg.parent.mkdir(parents=True, exist_ok=True)
                        dst_svg.write_bytes(svg_bytes)
                except Exception:
                    pass
            return True, "wikimedia_svg_512" if is_svg else "wikimedia_png", orig_url or download_url, ""
        except Exception as exc:
            last_err = f"{fn}: {exc}"
            # If SVG server-side thumb failed, try downloading raw SVG and rendering locally
            if is_svg and orig_url and resvg_py is not None:
                try:
                    svg_bytes = http_get_bytes(orig_url, headers=WIKI_HEADERS, delay=0.22)
                    render_svg_to_png(svg_bytes, dst_png, target_width=512)
                    if dst_svg is not None:
                        dst_svg.parent.mkdir(parents=True, exist_ok=True)
                        dst_svg.write_bytes(svg_bytes)
                    return True, "wikimedia_svg_resvg", orig_url, ""
                except Exception as exc2:
                    last_err = f"{fn}: {exc2}"
            continue

    return False, "failed", "", last_err


def _try_render_local_assets(local_paths: Sequence[str], dst_png: Path, *, is_fallback: bool) -> Tuple[bool, str, str, str]:
    """Render first valid SVG/PNG in local_paths into dst_png."""
    last_err = ""
    suffix = "_fallback" if is_fallback else ""
    for rel_p in local_paths:
        src = PROJECT_ROOT / rel_p
        if not src.exists():
            continue
        try:
            if src.suffix.lower() == ".svg":
                render_svg_to_png(src.read_bytes(), dst_png, target_width=512)
                return True, f"local_reference_svg{suffix}", rel_p, ""
            save_png_rgba(src.read_bytes(), dst_png, min_side=96)
            return True, f"local_reference_png{suffix}", rel_p, ""
        except Exception as exc:
            last_err = f"local_asset({rel_p}): {exc}"
    return False, "", "", last_err


def fetch_sch96_ips(
    force: bool = False,
    prev_entities: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    SCH96_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    raw_svg_dir = SCH96_ASSETS_DIR / "raw_svg"
    raw_svg_dir.mkdir(parents=True, exist_ok=True)
    prev_entities = prev_entities or {}

    entities_out: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    # Map entity_id -> list of template names
    tmpl_by_eid: Dict[str, List[str]] = defaultdict(list)
    for _, t_name, eid, _ in TEMPLATE_96_REGISTRY:
        tmpl_by_eid[eid].append(t_name)

    for spec in SCH96_ENTITY_SPECS:
        eid = spec["entity_id"]
        subdir = spec["subdir"]
        out_dir = SCH96_ASSETS_DIR / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        dst_png = out_dir / f"{eid}.png"
        dst_svg = raw_svg_dir / f"{eid}.svg"

        t_ids = list(spec.get("template_override") or tmpl_by_eid.get(eid, []))
        local_existing = list(spec.get("local_existing") or [])

        ok = False
        source_tier = ""
        source_url = ""
        err_msg = ""

        if dst_png.exists() and dst_png.stat().st_size > 256 and not force:
            ok = True
            prev = prev_entities.get(eid) or {}
            source_tier = prev.get("source_tier") or "cached_local"
            source_url = prev.get("source_url") or ""
        elif spec.get("skip_fetch"):
            err_msg = "manual_ref_required"
        else:
            print(f"==> [SCH96/{spec['category']}] Resolving {eid} ({spec['name_en']})")
            if spec.get("prefer_local_existing") and local_existing:
                ok, source_tier, source_url, err_msg = _try_render_local_assets(local_existing, dst_png, is_fallback=False)

            if not ok:
                ok, source_tier, source_url, err_msg = fetch_wikimedia_best_logo(
                    name_en=spec["name_en"],
                    wiki_titles=spec.get("wiki_titles") or [],
                    file_hints=spec.get("wiki_file_hints") or [],
                    commons_queries=spec.get("commons_queries") or [f"{spec['name_en']} logo"],
                    dst_png=dst_png,
                    dst_svg=dst_svg,
                    allow_jpg=False,
                    category=spec["category"],
                )

            # Fallback to package-local verified SVG/PNG if Wikimedia did not yield a logo
            if not ok and local_existing:
                ok, fb_tier, fb_url, fb_err = _try_render_local_assets(local_existing, dst_png, is_fallback=True)
                if ok:
                    source_tier, source_url, err_msg = fb_tier, fb_url, ""
                elif fb_err:
                    err_msg = fb_err

        if not ok and spec["category"] != "needs_manual_ref":
            failures.append({"scope": f"sch96/{spec['category']}", "id": eid, "error": err_msg})
        elif not ok and spec["category"] == "needs_manual_ref":
            print(f"  [info] {eid} marked needs_manual_ref ({err_msg})")

        entities_out.append(
            {
                "entity_id": eid,
                "category": spec["category"],
                "v2_domain": spec["v2_domain"],
                "name_en": spec["name_en"],
                "name_zh": spec["name_zh"],
                "desc_zh": spec["desc_zh"],
                "template_ids": t_ids,
                "local_path": str(dst_png.relative_to(PROJECT_ROOT)) if ok else "",
                "raw_svg_path": str(dst_svg.relative_to(PROJECT_ROOT)) if dst_svg.exists() else "",
                "existing_reference_paths": [p for p in local_existing if (PROJECT_ROOT / p).exists()],
                "source_tier": source_tier if ok else "needs_manual_ref",
                "source_url": source_url,
                "fetch_ok": ok,
                "error": "" if ok else err_msg,
            }
        )

    return {"entities": entities_out, "failures": failures}


# ---------------------------------------------------------------------------
# Offline Pack Builder, Visual Indexing, QA Sheets & JSONL Exporters
# ---------------------------------------------------------------------------

def analyze_png(path: Path) -> Dict[str, Any]:
    with Image.open(path) as raw:
        raw.verify()
    with Image.open(path) as img:
        rgba = img.convert("RGBA")
        w, h = rgba.size
        thumb = rgba.copy()
        thumb.thumbnail((96, 96), Image.Resampling.LANCZOS)
        arr = np.asarray(thumb)
        alpha = arr[:, :, 3]
        active = arr[alpha > 40]
        if len(active) == 0:
            active = arr.reshape(-1, 4)
        rgb = active[:, :3].astype(np.float32)
        if len(rgb) > 4000:
            rgb = rgb[np.linspace(0, len(rgb) - 1, 4000).astype(np.int64)]
        med = np.median(rgb, axis=0)
        color_zh, color_en = rgb_to_color_name(float(med[0]), float(med[1]), float(med[2]))
        aspect = round(float(w) / max(h, 1), 3)
        geom_zh, geom_en = geometry_from_aspect(aspect)
        return {
            "width": w,
            "height": h,
            "aspect_ratio": aspect,
            "geometry_zh": geom_zh,
            "geometry_en": geom_en,
            "dominant_color_zh": color_zh,
            "dominant_color_en": color_en,
            "alpha_ratio": round(float(np.mean(alpha > 40)), 3),
            "dhash": dhash64(thumb),
            "md5": file_md5(path),
        }


def _rewrite_path(rel_path: str, prefix: Optional[str]) -> str:
    if not prefix:
        return rel_path
    return prefix.rstrip("/") + "/" + rel_path.lstrip("/")


def _load_font(size: int = 13) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in candidates:
        p = Path(fp)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _make_checkerboard(w: int, h: int, cell: int = 12) -> Image.Image:
    ys, xs = np.indices((h, w))
    mask = ((xs // cell) + (ys // cell)) % 2 == 0
    arr = np.empty((h, w, 3), dtype=np.uint8)
    arr[mask] = (232, 236, 240)
    arr[~mask] = (206, 212, 218)
    return Image.fromarray(arr, mode="RGB")


def render_contact_sheet(
    items: List[Dict[str, str]],
    *,
    title: str,
    out_path: Path,
    cols: int = 6,
    thumb_size: int = 150,
) -> None:
    """Render a crisp checkerboard-backed contact sheet with labels for visual QA."""
    if not items:
        return
    pad = 14
    label_h = 40
    header_h = 46
    cell_w = thumb_size + pad
    cell_h = thumb_size + label_h + pad
    rows = (len(items) + cols - 1) // cols
    canvas_w = max(800, cols * cell_w + pad)
    canvas_h = header_h + rows * cell_h + pad

    canvas = Image.new("RGB", (canvas_w, canvas_h), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    title_font = _load_font(18)
    label_font = _load_font(12)

    draw.rectangle([0, 0, canvas_w, header_h], fill=(24, 34, 48))
    draw.text((16, 12), title, fill=(255, 255, 255), font=title_font)

    checker_tpl = _make_checkerboard(thumb_size, thumb_size)

    for idx, item in enumerate(items):
        r = idx // cols
        c = idx % cols
        x = pad + c * cell_w
        y = header_h + pad + r * cell_h

        bg = checker_tpl.copy()
        img_p = PROJECT_ROOT / item["local_path"]
        if img_p.exists():
            try:
                with Image.open(img_p) as raw:
                    rgba = raw.convert("RGBA")
                    rgba.thumbnail((thumb_size - 12, thumb_size - 12), Image.Resampling.LANCZOS)
                    ox = (thumb_size - rgba.width) // 2
                    oy = (thumb_size - rgba.height) // 2
                    bg_rgba = bg.convert("RGBA")
                    bg_rgba.alpha_composite(rgba, (ox, oy))
                    bg = bg_rgba.convert("RGB")
            except Exception:
                draw.rectangle([x, y, x + thumb_size, y + thumb_size], fill=(255, 220, 220))

        canvas.paste(bg, (x, y))
        draw.rectangle([x, y, x + thumb_size, y + thumb_size], outline=(148, 163, 184), width=1)

        l1 = item.get("label1", "")[:22]
        l2 = item.get("label2", "")[:22]
        draw.text((x + 2, y + thumb_size + 4), l1, fill=(15, 23, 42), font=label_font)
        draw.text((x + 2, y + thumb_size + 21), l2, fill=(71, 85, 105), font=label_font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, format="JPEG", quality=92)


def _format_color_phrase(color_zh: str) -> str:
    return color_zh.replace("/", "与")


def build_pack_artifacts(image_root_prefix: Optional[str] = None, bundle_tar: bool = False) -> Dict[str, Any]:
    if not FETCH_LEDGER_PATH.exists():
        raise FileNotFoundError(
            f"Missing {FETCH_LEDGER_PATH}. Run `--fetch` first to download official crests/logos."
        )
    ledger = json.loads(FETCH_LEDGER_PATH.read_text(encoding="utf-8"))
    sports_data = ledger.get("sports") or {"leagues": [], "teams": []}
    sch96_data = ledger.get("sch96") or {"entities": []}

    leagues = sports_data.get("leagues") or []
    teams = sports_data.get("teams") or []
    sch96_entities = sch96_data.get("entities") or []

    # 1. Analyze every local PNG & compute dHash neighbors within each league / group
    missing_zh: List[str] = []
    md5_buckets: Dict[str, List[str]] = defaultdict(list)

    for rec in leagues:
        p = PROJECT_ROOT / rec["local_path"]
        if rec.get("fetch_ok") and p.exists():
            vis = analyze_png(p)
            rec["visual"] = vis
            md5_buckets[vis["md5"]].append(rec["entity_id"])
        else:
            rec["visual"] = {}

    by_league: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in teams:
        if not rec.get("name_zh"):
            missing_zh.append(f"{rec['league_id']}: {rec['name_en']}")
        p = PROJECT_ROOT / rec["local_path"]
        if rec.get("fetch_ok") and p.exists():
            vis = analyze_png(p)
            rec["visual"] = vis
            md5_buckets[vis["md5"]].append(rec["entity_id"])
            by_league[rec["league_id"]].append(rec)
        else:
            rec["visual"] = {}

    # Compute top-4 visual neighbors within same league (for hard-negative contrast pairs)
    team_by_id: Dict[str, Dict[str, Any]] = {}
    for lid, group in by_league.items():
        for rec in group:
            team_by_id[rec["entity_id"]] = rec
            h = rec["visual"]["dhash"]
            ranked = sorted(
                (
                    {"entity_id": other["entity_id"], "name_zh": other["name_zh"], "distance": hamming(h, other["visual"]["dhash"])}
                    for other in group
                    if other["entity_id"] != rec["entity_id"]
                ),
                key=lambda x: x["distance"],
            )[:4]
            rec["visual_neighbors"] = ranked

    sch96_ok: List[Dict[str, Any]] = []
    for rec in sch96_entities:
        if rec.get("fetch_ok") and rec.get("local_path"):
            p = PROJECT_ROOT / rec["local_path"]
            if p.exists():
                vis = analyze_png(p)
                rec["visual"] = vis
                sch96_ok.append(rec)
                md5_buckets[vis["md5"]].append(rec["entity_id"])
                continue
        rec["visual"] = {}

    for rec in sch96_ok:
        h = rec["visual"]["dhash"]
        ranked = sorted(
            (
                {"entity_id": other["entity_id"], "name_zh": other["name_zh"], "distance": hamming(h, other["visual"]["dhash"])}
                for other in sch96_ok
                if other["entity_id"] != rec["entity_id"]
            ),
            key=lambda x: x["distance"],
        )[:4]
        rec["visual_neighbors"] = ranked

    # 2. Save structured manifests under Assert/output/sports_ip_supplement/manifests/
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    league_counts = Counter(t["league_id"] for t in teams if t.get("fetch_ok"))

    sports_manifest = {
        "schema": "assert_sports_crests_supplement_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_leagues": sum(1 for l in leagues if l.get("fetch_ok")),
        "total_teams": sum(1 for t in teams if t.get("fetch_ok")),
        "counts_by_league": dict(sorted(league_counts.items())),
        "missing_zh_count": len(missing_zh),
        "leagues": leagues,
        "teams": teams,
    }
    SPORTS_MANIFEST_PATH.write_text(json.dumps(sports_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sch96_manifest = {
        "schema": "assert_sch96_ip_supplement_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_entities": len(sch96_entities),
        "resolved_images": len(sch96_ok),
        "entities": sch96_entities,
    }
    SCH96_MANIFEST_PATH.write_text(json.dumps(sch96_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 3. Build 96-template coverage ledger (every #1..#96 accounted for)
    league_by_id = {l["league_id"]: l for l in leagues}
    ncaa_by_id = {t["entity_id"]: t for t in teams if t["league_id"] == "ncaa"}
    sch96_by_id = {e["entity_id"]: e for e in sch96_entities}

    coverage_rows: List[Dict[str, Any]] = []
    for rank, tmpl_name, eid, note in TEMPLATE_96_REGISTRY:
        row: Dict[str, Any] = {
            "rank": rank,
            "template_name": tmpl_name,
            "entity_id": eid,
            "note": note,
            "status": "unresolved",
            "name_zh": "",
            "name_en": "",
            "local_paths": [],
            "existing_reference_paths": [],
        }
        if eid.startswith("sports_ncaa_"):
            t = ncaa_by_id.get(eid)
            if t and t.get("fetch_ok"):
                row.update(
                    {
                        "status": "resolved_sports_ncaa",
                        "name_zh": t["name_zh"],
                        "name_en": t["name_en"],
                        "local_paths": [t["local_path"]],
                    }
                )
        elif eid.startswith("sports_"):
            lid = eid.replace("sports_", "", 1)
            lg = league_by_id.get(lid)
            if lg and lg.get("fetch_ok"):
                row.update(
                    {
                        "status": "resolved_sports_league",
                        "name_zh": lg["name_zh"],
                        "name_en": lg["name_en"],
                        "local_paths": [lg["local_path"]],
                    }
                )
        elif eid == "ip_triumph":
            paths = []
            for sub_id in ("ip_triumph_motorcycles", "ip_triumph_international"):
                ent = sch96_by_id.get(sub_id)
                if ent and ent.get("fetch_ok") and ent.get("local_path"):
                    paths.append(ent["local_path"])
            row.update(
                {
                    "status": "resolved_multi_brand" if paths else "unresolved",
                    "name_zh": "凯旋摩托 Triumph Motorcycles / 黛安芬 Triumph International",
                    "name_en": "Triumph Motorcycles / Triumph International",
                    "local_paths": paths,
                }
            )
        elif eid in NON_FETCHABLE_SPECS:
            ns = NON_FETCHABLE_SPECS[eid]
            row.update(
                {
                    "status": ns["category"],
                    "name_zh": ns["name_zh"],
                    "name_en": ns["name_en"],
                    "note": ns["note"],
                }
            )
        else:
            ent = sch96_by_id.get(eid)
            if ent:
                st = ent["category"] if ent["category"] in ("ambiguous_needs_confirm", "needs_manual_ref") else (
                    "resolved_official_logo" if ent.get("fetch_ok") else "needs_manual_ref"
                )
                paths = [ent["local_path"]] if ent.get("local_path") else []
                if ent.get("raw_svg_path"):
                    paths.append(ent["raw_svg_path"])
                row.update(
                    {
                        "status": st,
                        "name_zh": ent["name_zh"],
                        "name_en": ent["name_en"],
                        "local_paths": paths,
                        "existing_reference_paths": ent.get("existing_reference_paths") or [],
                    }
                )
        coverage_rows.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov_json_path = OUT_DIR / "sch96_template_coverage.json"
    cov_json_path.write_text(json.dumps(coverage_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cov_status_counts = Counter(r["status"] for r in coverage_rows)
    cov_md_lines = [
        "# 96 模板 IP 官标覆盖审计台账 (`sch96_template_coverage`)",
        "",
        f"- 总模板数：**{len(coverage_rows)}**",
        f"- 状态分布：`{dict(sorted(cov_status_counts.items()))}`",
        "",
        "| # | 模板名 | 归属实体 (中/英) | 状态 | 本地图片/参考路径 | 备注 |",
        "|---:|---|---|---|---|---|",
    ]
    for r in coverage_rows:
        p_str = "<br>".join(f"`{p}`" for p in (r["local_paths"] + r["existing_reference_paths"])) or "—"
        cov_md_lines.append(
            f"| {r['rank']} | `{r['template_name']}` | {r['name_zh']} ({r['name_en']}) | `{r['status']}` | {p_str} | {r['note']} |"
        )
    (OUT_DIR / "sch96_template_coverage.md").write_text("\n".join(cov_md_lines) + "\n", encoding="utf-8")

    # 4. Generate CPT JSONL Packs (MS-SWIFT compatible, real images: is_synthetic_image=False, synth_count=0)
    cpt_sports_rows: List[Dict[str, Any]] = []

    # 4a. League official logo docs
    for lg in leagues:
        if not lg.get("fetch_ok"):
            continue
        vis = lg.get("visual") or {}
        color_desc = _format_color_phrase(vis.get("dominant_color_zh") or "多色")
        img_ref = _rewrite_path(lg["local_path"], image_root_prefix)
        text = sanitize_no_jargon(
            f"<image>\n"
            f"【官方体育赛事标识 · {lg['name_zh']}】\n"
            f"标准实体：{lg['name_zh']}（英文：{lg['name_en']}；运动项目：{lg['sport_zh']}；所在地区：{lg['country_zh']}）。\n"
            f"视觉特征：标准赛事标志主色调偏向{color_desc}，整体长宽比约 {vis.get('aspect_ratio', 1.0)}。\n"
            f"商品应用：常印制于官方授权球衣袖标、球迷围巾、棒球帽及正版联名周边包装。"
        )
        cpt_sports_rows.append(
            {
                "sample_id": f"supp_sports_league_{lg['league_id']}",
                "doc_family_id": f"fam_sports_{lg['league_id']}",
                "entity_id": lg["entity_id"],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sports_league_canonical",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [img_ref],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    # 4b. Club / Team / NCAA single-crest canonical docs
    for rec in teams:
        if not rec.get("fetch_ok"):
            continue
        vis = rec.get("visual") or {}
        color_desc = _format_color_phrase(vis.get("dominant_color_zh") or "多色")
        img_ref = _rewrite_path(rec["local_path"], image_root_prefix)
        abbr_str = f"；官方简称：{rec['abbreviation']}" if rec.get("abbreviation") else ""
        palette_str = f"；球队主色：{rec['team_color']}" if rec.get("team_color") else ""
        text = sanitize_no_jargon(
            f"<image>\n"
            f"【官方球队队徽 · {rec['league_name_zh']} · {rec['name_zh']}】\n"
            f"标准实体：{rec['name_zh']}（英文：{rec['name_en']}{abbr_str}；所属赛事：{rec['league_name_zh']} · {rec['sport_zh']}）。\n"
            f"视觉特征：队徽主色调呈现{color_desc}，长宽比约 {vis.get('aspect_ratio', 1.0)}{palette_str}。\n"
            f"商品应用：常见于主客场球衣左胸刺绣或热转印徽章、针织围巾、棒球帽冠正面及官方授权周边产品，须精确核对盾牌外廓、字母拼写及内部纹样元素，严禁与其他同联赛或近色队徽混淆。"
        )
        cpt_sports_rows.append(
            {
                "sample_id": f"supp_crest_{rec['entity_id']}",
                "doc_family_id": f"fam_sports_{rec['league_id']}",
                "entity_id": rec["entity_id"],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sports_crest_canonical",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [img_ref],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    # 4c. Derby & visual-neighbor dual-image contrast pairs
    paired_keys: set[Tuple[str, str]] = set()
    for lid, q1, q2, derby_name in ICONIC_RIVALS:
        group = by_league.get(lid, [])
        t1 = next((t for t in group if q1.lower() in t["name_en"].lower()), None)
        t2 = next((t for t in group if q2.lower() in t["name_en"].lower() and (not t1 or t["entity_id"] != t1["entity_id"])), None)
        if not t1 or not t2:
            continue
        pair_key = tuple(sorted((t1["entity_id"], t2["entity_id"])))
        if pair_key in paired_keys:
            continue
        paired_keys.add(pair_key)
        v1 = t1.get("visual") or {}
        v2 = t2.get("visual") or {}
        text = sanitize_no_jargon(
            f"图1：<image>\n图2：<image>\n"
            f"【同联赛易混队徽对比 · {t1['league_name_zh']}（{derby_name}）】\n"
            f"图1对应【{t1['name_zh']}（{t1['name_en']}）】，主色偏向{_format_color_phrase(v1.get('dominant_color_zh', '多色'))}；\n"
            f"图2对应【{t2['name_zh']}（{t2['name_en']}）】，主色偏向{_format_color_phrase(v2.get('dominant_color_zh', '多色'))}。\n"
            f"辨析要点：两支同赛区宿敌常出现在同款赛事主题商品或对比审核场景中，判别时须锁定中心吉祥物或字母缩写、盾徽轮廓及边框配色序列，切忌因同城或近色误判。"
        )
        cpt_sports_rows.append(
            {
                "sample_id": f"supp_derby_{t1['entity_id']}_vs_{t2['entity_id']}",
                "doc_family_id": f"fam_sports_{lid}",
                "entity_id": t1["entity_id"],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sports_crest_contrast_pair",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [
                    _rewrite_path(t1["local_path"], image_root_prefix),
                    _rewrite_path(t2["local_path"], image_root_prefix),
                ],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    # Also add top visual-neighbor pairs per league (up to 4 extra per league using dHash distance)
    for lid, group in by_league.items():
        added_extra = 0
        for rec in group:
            if added_extra >= 4:
                break
            nb_list = rec.get("visual_neighbors") or []
            if not nb_list:
                continue
            nb = team_by_id.get(nb_list[0]["entity_id"])
            if not nb:
                continue
            pair_key = tuple(sorted((rec["entity_id"], nb["entity_id"])))
            if pair_key in paired_keys:
                continue
            paired_keys.add(pair_key)
            added_extra += 1
            v1 = rec.get("visual") or {}
            v2 = nb.get("visual") or {}
            text = sanitize_no_jargon(
                f"图1：<image>\n图2：<image>\n"
                f"【近邻队徽外观辨析 · {rec['league_name_zh']}】\n"
                f"图1为【{rec['name_zh']}（{rec['name_en']}）】，图2为视觉轮廓接近的同联赛球队【{nb['name_zh']}（{nb['name_en']}）】。\n"
                f"图1主色调为{_format_color_phrase(v1.get('dominant_color_zh', '多色'))}，长宽比约 {v1.get('aspect_ratio', 1.0)}；"
                f"图2主色调为{_format_color_phrase(v2.get('dominant_color_zh', '多色'))}，长宽比约 {v2.get('aspect_ratio', 1.0)}。"
                f"审核比对时应重点核验主图形结构、字符缩写与核心色块分布。"
            )
            cpt_sports_rows.append(
                {
                    "sample_id": f"supp_neighbor_{rec['entity_id']}_{nb['entity_id']}",
                    "doc_family_id": f"fam_sports_{lid}",
                    "entity_id": rec["entity_id"],
                    "channel": "ch2_std_logo_flag",
                    "source_kind": "sports_crest_visual_neighbor",
                    "is_synthetic_image": False,
                    "synthetic_image_count": 0,
                    "doc_text_repeat": 1,
                    "images": [
                        _rewrite_path(rec["local_path"], image_root_prefix),
                        _rewrite_path(nb["local_path"], image_root_prefix),
                    ],
                    "messages": [{"role": "assistant", "content": text}],
                }
            )

    # 4d. Multi-image league roster summary packs (4 clubs per doc, ch_sports_expanded, real images)
    for lid, group in by_league.items():
        sorted_group = sorted(group, key=lambda x: x["name_en"])
        for chunk_idx in range(0, len(sorted_group), 4):
            chunk = sorted_group[chunk_idx : chunk_idx + 4]
            if len(chunk) < 2:
                continue
            prefixes = "\n".join(f"图{i}：<image>" for i in range(1, len(chunk) + 1))
            desc_items = "\n".join(
                f"- 图{i}：{c['name_zh']}（{c['name_en']}），主色偏向{_format_color_phrase((c.get('visual') or {}).get('dominant_color_zh', '多色'))}"
                for i, c in enumerate(chunk, start=1)
            )
            text = sanitize_no_jargon(
                f"{prefixes}\n"
                f"【{chunk[0]['league_name_zh']} 球队队徽图谱分组 #{chunk_idx // 4 + 1}】\n"
                f"{desc_items}\n"
                f"以上均为{chunk[0]['league_name_zh']}官方球队队徽标准参考图，用于商品印花与刺绣徽章精确识别。"
            )
            cpt_sports_rows.append(
                {
                    "sample_id": f"supp_roster_{lid}_{chunk_idx // 4 + 1:02d}",
                    "doc_family_id": f"fam_sports_{lid}",
                    "entity_id": f"sports_roster_{lid}_{chunk_idx // 4 + 1:02d}",
                    "channel": "ch_sports_expanded",
                    "source_kind": "sports_league_roster_pack",
                    "is_synthetic_image": False,
                    "synthetic_image_count": 0,
                    "doc_text_repeat": 1,
                    "images": [_rewrite_path(c["local_path"], image_root_prefix) for c in chunk],
                    "messages": [{"role": "assistant", "content": text}],
                }
            )

    # 4e. 96-template IP official logo docs + visual contrast pairs
    cpt_sch96_rows: List[Dict[str, Any]] = []
    for ent in sch96_ok:
        vis = ent.get("visual") or {}
        img_ref = _rewrite_path(ent["local_path"], image_root_prefix)
        tmpl_str = "、".join(ent.get("template_ids") or []) or "通用补充"
        ambig_warn = (
            "（注意：该条目标识存在跨品类同名或待核对情形，审核时请结合商品载体语境复核）"
            if ent["category"] == "ambiguous_needs_confirm"
            else ""
        )
        text = sanitize_no_jargon(
            f"<image>\n"
            f"【品牌与文化 IP 官方标识 · {ent['name_zh']}】\n"
            f"标准实体：{ent['name_zh']}（英文：{ent['name_en']}；关联模板：{tmpl_str}）。\n"
            f"视觉特征：官方图形主色偏向{_format_color_phrase(vis.get('dominant_color_zh', '多色'))}，长宽比约 {vis.get('aspect_ratio', 1.0)}。\n"
            f"识别要点：{ent['desc_zh']}{ambig_warn}"
        )
        cpt_sch96_rows.append(
            {
                "sample_id": f"supp_sch96_{ent['entity_id']}",
                "doc_family_id": f"fam_sch96_{ent['entity_id']}",
                "entity_id": ent["entity_id"],
                "template_ids": ent.get("template_ids") or [],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sch96_ip_canonical",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [img_ref],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    # Triumph dual-brand explicit contrast pair (Motorcycles vs Lingerie) + top visual neighbors
    sch96_ok_by_id = {e["entity_id"]: e for e in sch96_ok}
    sch96_paired: set[Tuple[str, str]] = set()
    if "ip_triumph_motorcycles" in sch96_ok_by_id and "ip_triumph_international" in sch96_ok_by_id:
        tm = sch96_ok_by_id["ip_triumph_motorcycles"]
        ti = sch96_ok_by_id["ip_triumph_international"]
        sch96_paired.add(tuple(sorted((tm["entity_id"], ti["entity_id"]))))
        text = sanitize_no_jargon(
            f"图1：<image>\n图2：<image>\n"
            f"【同名双品牌标识消歧 · Triumph】\n"
            f"图1为【{tm['name_zh']}】官方徽标，属机车与骑士服饰品类，字体硬朗且常见长尾 R 字形；\n"
            f"图2为【{ti['name_zh']}】官方字标，属贴身内衣与时尚品类，字形圆润柔和。\n"
            f"商品审核命中 Triumph 关键词时，必须依据字体细节与商品品类精准区分，严禁混为一谈。"
        )
        cpt_sch96_rows.append(
            {
                "sample_id": "supp_sch96_triumph_disambiguation",
                "doc_family_id": "fam_sch96_ip_triumph_disambig",
                "entity_id": "ip_triumph_motorcycles",
                "template_ids": ["197_IP_Triumph"],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sch96_ip_contrast_pair",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [
                    _rewrite_path(tm["local_path"], image_root_prefix),
                    _rewrite_path(ti["local_path"], image_root_prefix),
                ],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    for ent in sch96_ok:
        nbs = ent.get("visual_neighbors") or []
        if not nbs:
            continue
        nb = sch96_ok_by_id.get(nbs[0]["entity_id"])
        if not nb:
            continue
        pk = tuple(sorted((ent["entity_id"], nb["entity_id"])))
        if pk in sch96_paired or len(sch96_paired) >= 16:
            continue
        sch96_paired.add(pk)
        text = sanitize_no_jargon(
            f"图1：<image>\n图2：<image>\n"
            f"【官方标识近邻对比 · {ent['name_zh']} vs {nb['name_zh']}】\n"
            f"图1为【{ent['name_zh']}（{ent['name_en']}）】，图2为外轮廓结构相近的【{nb['name_zh']}（{nb['name_en']}）】。\n"
            f"审校时请逐一核对字标字母、图形轮廓及品牌核心特征，防止跨品牌误召回。"
        )
        cpt_sch96_rows.append(
            {
                "sample_id": f"supp_sch96_pair_{ent['entity_id']}_{nb['entity_id']}",
                "doc_family_id": f"fam_sch96_{ent['entity_id']}",
                "entity_id": ent["entity_id"],
                "channel": "ch2_std_logo_flag",
                "source_kind": "sch96_ip_visual_neighbor",
                "is_synthetic_image": False,
                "synthetic_image_count": 0,
                "doc_text_repeat": 1,
                "images": [
                    _rewrite_path(ent["local_path"], image_root_prefix),
                    _rewrite_path(nb["local_path"], image_root_prefix),
                ],
                "messages": [{"role": "assistant", "content": text}],
            }
        )

    cpt_all_rows = cpt_sports_rows + cpt_sch96_rows

    def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    cpt_sports_path = OUT_DIR / "cpt_sports_crests_supplement.jsonl"
    cpt_sch96_path = OUT_DIR / "cpt_sch96_ip_supplement.jsonl"
    cpt_all_path = OUT_DIR / "cpt_all_supplement.jsonl"
    _write_jsonl(cpt_sports_path, cpt_sports_rows)
    _write_jsonl(cpt_sch96_path, cpt_sch96_rows)
    _write_jsonl(cpt_all_path, cpt_all_rows)

    # 5. Build ImageGen v2 Entities JSONL (`v2_entities_sports_and_ip_supplement.jsonl`)
    #    Compatible directly with `CPT-SFT/training/flash/build_v2_image_pipeline.py --entities ...`
    v2_entities: List[Dict[str, Any]] = []
    for lg in leagues:
        lid = lg["league_id"]
        club_group = [t for t in by_league.get(lid, []) if t.get("fetch_ok")]
        if not club_group:
            continue
        sub_entities = []
        for club in club_group:
            ref_p = _rewrite_path(club["local_path"], image_root_prefix)
            sub_entities.append(
                {
                    "sub_id": club["entity_id"],
                    "sub_kind": "crest",
                    "title": f"{club['name_zh']}（{club['name_en']}）官方队徽",
                    "doc_text": sanitize_no_jargon(
                        f"{club['name_zh']}官方标准队徽，隶属{club['league_name_zh']}，常用于主客场球衣左胸刺绣徽章、围巾与帽饰授权印花，须严格保持原参考徽章的盾形轮廓、字样与配色。"
                    ),
                    "ref_images": [ref_p],
                    "visual_prompts": [
                        f"woven embroidered crest patch of {club['name_en']} on jersey chest, macro studio photo, faithful to reference crest",
                        f"flat authentic club crest badge print of {club['name_en']} on cotton scarf, crisp detail",
                    ],
                }
            )
        v2_entities.append(
            {
                "entity_id": f"ent_sports_league_{lid}",
                "domain": "sports_league",
                "title": f"{lg['name_zh']}俱乐部知识父条目",
                "doc_family_id": f"fam_sports_{lid}",
                "doc_text": sanitize_no_jargon(
                    f"{lg['name_zh']}旗下官方俱乐部队徽集合，所有子俱乐部均绑定真实标准队徽参考图，生图编辑须严格锚定参考队徽的几何元素与色序。"
                ),
                "mm": True,
                "has_concrete_prop": True,
                "ref_images": [_rewrite_path(lg["local_path"], image_root_prefix)] if lg.get("fetch_ok") else [],
                "sub_entities": sub_entities,
            }
        )

    # NCAA sports parent
    ncaa_group = [t for t in by_league.get("ncaa", []) if t.get("fetch_ok")]
    if ncaa_group:
        v2_entities.append(
            {
                "entity_id": "ent_sports_league_ncaa",
                "domain": "sports_league",
                "title": "NCAA 美国大学体育代表校徽与运动队徽集合",
                "doc_family_id": "fam_sports_ncaa",
                "doc_text": "包含杜克、佐治亚（UGA）、佛罗里达、俄克拉荷马、自由大学等 NCAA 名校官方体育队徽参考。",
                "mm": True,
                "has_concrete_prop": True,
                "sub_entities": [
                    {
                        "sub_id": c["entity_id"],
                        "sub_kind": "crest",
                        "title": f"{c['name_zh']}（{c['name_en']}）官方校队徽标",
                        "doc_text": sanitize_no_jargon(
                            f"{c['name_zh']}官方校队标识，常见于美式大学卫衣前胸印花、棒球帽冠正面刺绣与校队周边。"
                        ),
                        "ref_images": [_rewrite_path(c["local_path"], image_root_prefix)],
                        "visual_prompts": [
                            f"embroidered varsity emblem of {c['name_en']} on cotton cap front panel, faithful to reference",
                            f"printed college sweatshirt graphic of {c['name_en']}, studio product lighting",
                        ],
                    }
                    for c in ncaa_group
                ],
            }
        )

    # Resolved 96-template entities with REAL ref_images
    for ent in sch96_ok:
        ref_p = _rewrite_path(ent["local_path"], image_root_prefix)
        v2_entities.append(
            {
                "entity_id": f"ent_{ent['entity_id']}",
                "domain": ent["v2_domain"],
                "title": ent["name_zh"],
                "doc_family_id": f"fam_sch96_{ent['entity_id']}",
                "doc_text": sanitize_no_jargon(ent["desc_zh"]),
                "mm": True,
                "has_concrete_prop": True,
                "ref_images": [ref_p],
                "visual_prompts": [
                    f"authentic printed patch or hangtag featuring exact {ent['name_en']} official mark on apparel, faithful to reference",
                    f"macro studio photo of woven label or badge with exact {ent['name_en']} emblem",
                ],
            }
        )

    v2_entities_path = OUT_DIR / "v2_entities_sports_and_ip_supplement.jsonl"
    _write_jsonl(v2_entities_path, v2_entities)

    # 6. Render Checkerboard Visual QA Contact Sheets
    sheets_generated: List[str] = []

    # 6a. Leagues + NCAA
    league_ncaa_items = [
        {"local_path": l["local_path"], "label1": l["name_en"], "label2": l["short_zh"]}
        for l in leagues
        if l.get("fetch_ok")
    ] + [
        {"local_path": t["local_path"], "label1": t["name_en"], "label2": t["name_zh"]}
        for t in by_league.get("ncaa", [])
    ]
    p_ln = CONTACT_SHEETS_DIR / "contact_sheet_leagues_and_ncaa.jpg"
    render_contact_sheet(league_ncaa_items, title="Leagues (9) + NCAA Top Programs (20)", out_path=p_ln, cols=6)
    sheets_generated.append(str(p_ln.relative_to(PROJECT_ROOT)))

    # 6b. Big-5 European Football (split into 2 readable sheets)
    big5_a = []
    for lid in ("premier_league", "la_liga", "serie_a"):
        for t in sorted(by_league.get(lid, []), key=lambda x: x["name_en"]):
            big5_a.append({"local_path": t["local_path"], "label1": f"[{t['league_name_zh']}] {t['name_en']}", "label2": t["name_zh"]})
    p_fb_a = CONTACT_SHEETS_DIR / "contact_sheet_football_epl_laliga_seriea.jpg"
    render_contact_sheet(big5_a, title="Big-5 Football Part A: Premier League + La Liga + Serie A", out_path=p_fb_a, cols=6)
    sheets_generated.append(str(p_fb_a.relative_to(PROJECT_ROOT)))

    big5_b = []
    for lid in ("bundesliga", "ligue_1"):
        for t in sorted(by_league.get(lid, []), key=lambda x: x["name_en"]):
            big5_b.append({"local_path": t["local_path"], "label1": f"[{t['league_name_zh']}] {t['name_en']}", "label2": t["name_zh"]})
    p_fb_b = CONTACT_SHEETS_DIR / "contact_sheet_football_bundesliga_ligue1.jpg"
    render_contact_sheet(big5_b, title="Big-5 Football Part B: Bundesliga + Ligue 1", out_path=p_fb_b, cols=6)
    sheets_generated.append(str(p_fb_b.relative_to(PROJECT_ROOT)))

    # 6c. NBA + NFL
    nba_nfl = []
    for lid in ("nba", "nfl"):
        for t in sorted(by_league.get(lid, []), key=lambda x: x["name_en"]):
            nba_nfl.append({"local_path": t["local_path"], "label1": f"[{t['league_name_zh']}] {t['name_en']}", "label2": t["name_zh"]})
    p_nn = CONTACT_SHEETS_DIR / "contact_sheet_nba_nfl.jpg"
    render_contact_sheet(nba_nfl, title="NBA (30) + NFL (32) Official Team Logos", out_path=p_nn, cols=8)
    sheets_generated.append(str(p_nn.relative_to(PROJECT_ROOT)))

    # 6d. MLB + NHL
    mlb_nhl = []
    for lid in ("mlb", "nhl"):
        for t in sorted(by_league.get(lid, []), key=lambda x: x["name_en"]):
            mlb_nhl.append({"local_path": t["local_path"], "label1": f"[{t['league_name_zh']}] {t['name_en']}", "label2": t["name_zh"]})
    p_mn = CONTACT_SHEETS_DIR / "contact_sheet_mlb_nhl.jpg"
    render_contact_sheet(mlb_nhl, title="MLB (30) + NHL (32) Official Team Logos", out_path=p_mn, cols=8)
    sheets_generated.append(str(p_mn.relative_to(PROJECT_ROOT)))

    # 6e. 96-template IPs (split cleanly so every tile is large)
    sch_items = [
        {"local_path": e["local_path"], "label1": e["name_en"], "label2": f"{e['category']} | {e['name_zh']}"}
        for e in sch96_ok
    ]
    mid = (len(sch_items) + 1) // 2
    if sch_items[:mid]:
        p_s1 = CONTACT_SHEETS_DIR / "contact_sheet_sch96_part1.jpg"
        render_contact_sheet(sch_items[:mid], title="96-Template IPs Part 1 (Brands & Music/Sports)", out_path=p_s1, cols=6)
        sheets_generated.append(str(p_s1.relative_to(PROJECT_ROOT)))
    if sch_items[mid:]:
        p_s2 = CONTACT_SHEETS_DIR / "contact_sheet_sch96_part2.jpg"
        render_contact_sheet(sch_items[mid:], title="96-Template IPs Part 2 (Anime, Games & Entertainment)", out_path=p_s2, cols=6)
        sheets_generated.append(str(p_s2.relative_to(PROJECT_ROOT)))

    # 7. Write README.md and Pack manifest.json
    readme_text = "\n".join(
        [
            "# 体育联赛队徽 + 96 模板 IP 官标独立补充包 (`sports_ip_supplement`)",
            "",
            "本目录由 Assert 独立生成，只通过显式文件导出交付外部消费者。",
            "",
            "## 产物清单",
            "",
            "| 文件 | 用途 |",
            "|---|---|",
            "| `cpt_sports_crests_supplement.jsonl` | 五大联赛 / NBA / NFL / MLB / NHL / NCAA 球队单图锚定 + 同联赛德比/近邻双图辨析 + 分组图谱行（`is_synthetic_image=false`, `synthetic_image_count=0`） |",
            "| `cpt_sch96_ip_supplement.jsonl` | 96 模板中可定位品牌/乐队/动漫游戏官方图标锚定与同名消歧行（`is_synthetic_image=false`） |",
            "| `cpt_all_supplement.jsonl` | 上述两部分合集，可直接传入 `CPT-SFT/training/flash/build_mm_wiki_cpt.py --mode midtrain` |",
            "| `v2_entities_sports_and_ip_supplement.jsonl` | 直接传入 `CPT-SFT/training/flash/build_v2_image_pipeline.py --entities ...`，全部绑定真实 `ref_images`，强制走 Edit 保真路线、杜绝纯 T2I 幻觉 |",
            "| `sch96_template_coverage.{json,md}` | 96 模板逐条覆盖审计台账（含重名模板归并、多义待确认与泛化类目说明） |",
            "| `contact_sheets/*.jpg` | 棋盘格透明底可视化质检拼图 |",
            "",
            "## 文件交付",
            "",
            "图片路径相对 Assert 项目根目录。消费者显式配置资源根目录；不要求相邻仓库、共享源码或共享环境。",
            "本目录为候选补充包，验收状态以统一注册表为准。",
        ]
    ) + "\n"
    (OUT_DIR / "README.md").write_text(readme_text, encoding="utf-8")

    # Verify duplicate MD5s across distinct entities (ignore intentional shared refs if any)
    dup_md5s = {m: ids for m, ids in md5_buckets.items() if len(ids) > 1}

    pack_manifest = {
        "schema": "sports_ip_supplement_pack_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_root_prefix": image_root_prefix or "",
        "sports": {
            "leagues_count": sum(1 for l in leagues if l.get("fetch_ok")),
            "teams_count": sum(1 for t in teams if t.get("fetch_ok")),
            "counts_by_league": dict(sorted(league_counts.items())),
            "missing_zh_count": len(missing_zh),
            "missing_zh_sample": missing_zh[:20],
        },
        "sch96": {
            "total_templates": len(coverage_rows),
            "template_status_counts": dict(sorted(cov_status_counts.items())),
            "resolved_unique_ip_images": len(sch96_ok),
        },
        "jsonl_rows": {
            "cpt_sports_crests_supplement": len(cpt_sports_rows),
            "cpt_sch96_ip_supplement": len(cpt_sch96_rows),
            "cpt_all_supplement": len(cpt_all_rows),
            "v2_entities_sports_and_ip_supplement": len(v2_entities),
        },
        "duplicate_md5_groups": dup_md5s,
        "contact_sheets": sheets_generated,
        "sha256": {
            "cpt_sports_crests_supplement.jsonl": file_sha256(cpt_sports_path),
            "cpt_sch96_ip_supplement.jsonl": file_sha256(cpt_sch96_path),
            "cpt_all_supplement.jsonl": file_sha256(cpt_all_path),
            "v2_entities_sports_and_ip_supplement.jsonl": file_sha256(v2_entities_path),
            "sch96_template_coverage.json": file_sha256(cov_json_path),
        },
    }

    if bundle_tar:
        tar_path = OUT_DIR / "sports_ip_supplement_bundle.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tf:
            for sub in (
                SPORTS_ASSETS_DIR,
                SCH96_ASSETS_DIR,
                SPORTS_MANIFEST_PATH,
                SCH96_MANIFEST_PATH,
                cpt_sports_path,
                cpt_sch96_path,
                cpt_all_path,
                v2_entities_path,
                cov_json_path,
                OUT_DIR / "sch96_template_coverage.md",
                OUT_DIR / "README.md",
            ):
                if sub.exists():
                    tf.add(sub, arcname=str(sub.relative_to(PROJECT_ROOT)))
        pack_manifest["bundle_tar"] = {
            "path": str(tar_path.relative_to(PROJECT_ROOT)),
            "bytes": tar_path.stat().st_size,
            "sha256": file_sha256(tar_path),
        }

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(pack_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return pack_manifest


def run_fetch(only: str, retry_failed: bool, force: bool) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger: Dict[str, Any] = {}
    if FETCH_LEDGER_PATH.exists():
        ledger = json.loads(FETCH_LEDGER_PATH.read_text(encoding="utf-8"))

    # Default run or --retry-failed skips already downloaded valid PNGs; --force re-downloads all
    effective_force = bool(force and not retry_failed) if force else False

    if only in ("all", "sports"):
        prev_sports = ledger.get("sports") or {}
        sports_res = fetch_sports_leagues_and_teams(force=effective_force, prev_sports=prev_sports)
        ledger["sports"] = sports_res
        print(
            f"[Fetch Sports Done] leagues={len(sports_res['leagues'])}, "
            f"teams={len(sports_res['teams'])}, "
            f"unmapped_zh={len(sports_res['unmapped_names'])}, "
            f"failures={len(sports_res['failures'])}"
        )
        if sports_res["unmapped_names"]:
            print("  Unmapped Chinese team names:", sports_res["unmapped_names"])
        if sports_res["failures"]:
            print("  Sports fetch failures:", sports_res["failures"][:15])

    if only in ("all", "sch96"):
        prev_map = {
            e["entity_id"]: e
            for e in ((ledger.get("sch96") or {}).get("entities") or [])
            if isinstance(e, dict) and e.get("entity_id")
        }
        sch96_res = fetch_sch96_ips(force=effective_force, prev_entities=prev_map)
        ledger["sch96"] = sch96_res
        ok_cnt = sum(1 for e in sch96_res["entities"] if e.get("fetch_ok"))
        print(
            f"[Fetch SCH96 Done] resolved={ok_cnt}/{len(sch96_res['entities'])}, "
            f"failures={len(sch96_res['failures'])}"
        )
        if sch96_res["failures"]:
            print("  SCH96 fetch failures:", sch96_res["failures"])

    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    FETCH_LEDGER_PATH.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Fetch raw official crests/logos from Wikipedia, Wikimedia & GitHub")
    parser.add_argument("--build-pack", action="store_true", help="Offline build of manifests, JSONL packs, and QA sheets")
    parser.add_argument("--only", choices=["all", "sports", "sch96"], default="all")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry only missing or previously failed assets while keeping valid cached PNGs",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch of all cached API JSONs and images",
    )
    parser.add_argument("--image-root-prefix", default=None, help="Optional path prefix for image paths in exported JSONLs")
    parser.add_argument("--bundle-tar", action="store_true", help="Also build sports_ip_supplement_bundle.tar.gz")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if not args.fetch and not args.build_pack:
        raise SystemExit("Specify --fetch and/or --build-pack.")
    if args.fetch:
        run_fetch(only=args.only, retry_failed=args.retry_failed, force=args.force)
    if args.build_pack:
        summary = build_pack_artifacts(image_root_prefix=args.image_root_prefix, bundle_tar=args.bundle_tar)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
