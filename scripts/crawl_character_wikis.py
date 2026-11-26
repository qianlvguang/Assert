#!/usr/bin/env python3
"""Multi-source Wiki Character Dossier Crawler (Fandom + Moegirlpedia + Wikipedia).

Targets all 87 `B2_specific_anime_game_media_ip` audit template families in
`Assert/templete/` to extract structured character appearance descriptions,
visual anchors (hair, eyes, outfits, props, moe traits), aliases, and portraits.

Usage:
  .venv/bin/python scripts/crawl_character_wikis.py --fetch
  .venv/bin/python scripts/crawl_character_wikis.py --build

Respects `docs/standard_image_policy.md` and `AGENTS.md`:
  - Separates online `--fetch` (resumable cache) from offline `--build`.
  - Uses documented MediaWiki APIs (Fandom, en/zh Wikipedia) and polite public
    GET on Moegirlpedia (`mzh.moegirl.org.cn`). Never bypasses CAPTCHAs/anti-bot.
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAXONOMY_JSON = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.json"
DEFAULT_TEMPLETE_DIR = PROJECT_ROOT / "templete"
DEFAULT_OUT_DIR = PROJECT_ROOT / "output" / "character_wiki_crawl"
DEFAULT_CACHE_PATH = DEFAULT_OUT_DIR / "_crawl_cache.json"
DEFAULT_DOSSIERS_JSONL = PROJECT_ROOT / "manifests" / "character_wiki_dossiers.jsonl"
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "manifests" / "character_wiki_summary.json"
DEFAULT_CPT_PROSE_JSONL = PROJECT_ROOT / "manifests" / "character_wiki_cpt_prose.jsonl"

USER_AGENT = "AssertCharacterWikiCrawler/1.0 (https://github.com/qianlvguang; standalone-audit-catalog)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# All 87 B2_specific_anime_game_media_ip families mapped to multi-source wiki endpoints
FRANCHISE_WIKI_CONFIG: dict[str, dict[str, Any]] = {
    "adventuretime": {
        "fandom": "adventuretime.fandom.com",
        "chars_en": ["Finn Mertens", "Jake the Dog", "Princess Bubblegum", "Marceline Abadeer", "BMO", "Ice King"],
        "moegirl": ["探险活宝", "芬恩(探险活宝)", "泡泡糖公主", "玛瑟琳"],
        "enwiki": "List of Adventure Time characters",
        "zhwiki": "探險活寶角色列表",
    },
    "amongus": {
        "fandom": "among-us.fandom.com",
        "chars_en": ["Crewmate", "Impostor"],
        "moegirl": ["Among Us"],
        "enwiki": "Among Us",
        "zhwiki": "Among Us",
    },
    "angry_birds": {
        "fandom": "angrybirds.fandom.com",
        "chars_en": ["Red", "Chuck", "Bomb", "Matilda", "The Blues", "Leonard"],
        "moegirl": ["愤怒的小鸟"],
        "enwiki": "Angry Birds",
        "zhwiki": "憤怒鳥",
    },
    "annabelle": {
        "fandom": "conjuring.fandom.com",
        "chars_en": ["Annabelle (doll)", "Annabelle Higgins"],
        "moegirl": [],
        "enwiki": "Annabelle (doll)",
        "zhwiki": "安娜貝爾",
    },
    "anpanman": {
        "fandom": "anpanman.fandom.com",
        "chars_en": ["Anpanman", "Baikinman", "Dokin-chan", "Currypanman", "Shokupanman"],
        "moegirl": ["面包超人", "细菌小子"],
        "enwiki": "Anpanman",
        "zhwiki": "麵包超人",
    },
    "atari": {
        "fandom": "atari.fandom.com",
        "chars_en": ["Atari", "Centipede", "Asteroids"],
        "moegirl": [],
        "enwiki": "Atari",
        "zhwiki": "雅達利",
    },
    "attack_on_titan": {
        "fandom": "attackontitan.fandom.com",
        "chars_en": ["Eren Yeager", "Mikasa Ackerman", "Armin Arlert", "Levi Ackerman", "Erwin Smith", "Hange Zoë"],
        "moegirl": ["进击的巨人", "艾伦·耶格尔", "三笠·阿克曼", "利威尔·阿克曼"],
        "enwiki": "List of Attack on Titan characters",
        "zhwiki": "進擊的巨人角色列表",
    },
    "badcutebunny": {
        "fandom": "",
        "chars_en": [],
        "moegirl": [],
        "enwiki": "",
        "zhwiki": "",
    },
    "berserk": {
        "fandom": "berserk.fandom.com",
        "chars_en": ["Guts", "Griffith", "Casca", "Puck", "Skull Knight"],
        "moegirl": ["剑风传奇", "格斯(剑风传奇)", "格里菲斯(剑风传奇)"],
        "enwiki": "List of Berserk characters",
        "zhwiki": "烙印勇士角色列表",
    },
    "bleach": {
        "fandom": "bleach.fandom.com",
        "chars_en": ["Ichigo Kurosaki", "Rukia Kuchiki", "Orihime Inoue", "Uryū Ishida", "Byakuya Kuchiki", "Tōshirō Hitsugaya", "Kenpachi Zaraki"],
        "moegirl": ["死神(漫画)", "黑崎一护", "朽木露琪亚", "井上织姬"],
        "enwiki": "List of Bleach characters",
        "zhwiki": "BLEACH角色列表",
    },
    "brawl_stars": {
        "fandom": "brawlstars.fandom.com",
        "chars_en": ["Shelly", "Colt", "Spike", "El Primo", "Poco", "Edgar"],
        "moegirl": ["荒野乱斗"],
        "enwiki": "Brawl Stars",
        "zhwiki": "荒野亂鬥",
    },
    "chainsawman": {
        "fandom": "chainsaw-man.fandom.com",
        "chars_en": ["Denji", "Power", "Makima", "Aki Hayakawa", "Pochita", "Reze"],
        "moegirl": ["链锯人", "电次", "帕瓦(链锯人)", "玛奇玛"],
        "enwiki": "List of Chainsaw Man characters",
        "zhwiki": "鏈鋸人角色列表",
    },
    "clash_royale": {
        "fandom": "clashroyale.fandom.com",
        "chars_en": ["King", "Hog Rider", "P.E.K.K.A", "Mega Knight", "Princess"],
        "moegirl": ["皇室战争"],
        "enwiki": "Clash Royale",
        "zhwiki": "部落衝突：皇室戰爭",
    },
    "cobra": {
        "fandom": "cobra.fandom.com",
        "chars_en": ["Cobra", "Armaroid Lady", "Crystal Bowie"],
        "moegirl": ["哥普拉"],
        "enwiki": "Cobra (manga)",
        "zhwiki": "哥普拉",
    },
    "cookie_run": {
        "fandom": "cookierunkingdom.fandom.com",
        "chars_en": ["GingerBrave", "Strawberry Cookie", "Wizard Cookie", "Pure Vanilla Cookie", "Shadow Milk Cookie"],
        "moegirl": ["跑跑姜饼人:王国"],
        "enwiki": "Cookie Run",
        "zhwiki": "跑跑薑餅人：王國",
    },
    "coraline": {
        "fandom": "coraline.fandom.com",
        "chars_en": ["Coraline Jones", "The Cat", "Other Mother", "Wybie Lovat"],
        "moegirl": ["鬼妈妈"],
        "enwiki": "Coraline (film)",
        "zhwiki": "第十四道門",
    },
    "cowboybebop": {
        "fandom": "cowboybebop.fandom.com",
        "chars_en": ["Spike Spiegel", "Jet Black", "Faye Valentine", "Edward Wong Hau Pepelu Tivrusky IV", "Ein"],
        "moegirl": ["星际牛仔", "斯派克·斯皮格尔", "菲·瓦伦丁"],
        "enwiki": "List of Cowboy Bebop characters",
        "zhwiki": "星際牛仔",
    },
    "crayonshinchan": {
        "fandom": "crayonshinchan.fandom.com",
        "chars_en": ["Shinnosuke Nohara", "Shiro", "Misae Nohara", "Hiroshi Nohara", "Himawari Nohara"],
        "moegirl": ["蜡笔小新", "野原新之助"],
        "enwiki": "List of Crayon Shin-chan characters",
        "zhwiki": "蠟筆小新角色列表",
    },
    "dandys_world": {
        "fandom": "dandys-world-robloxhorror.fandom.com",
        "chars_en": ["Dandy", "Pebble", "Astro", "Shelly", "Vee", "Sprout"],
        "moegirl": [],
        "enwiki": "Dandy's World",
        "zhwiki": "",
    },
    "dav_pilkey_dogman": {
        "fandom": "dogman.fandom.com",
        "chars_en": ["Dog Man", "Petey", "Li'l Petey", "Chief", "Captain Underpants"],
        "moegirl": [],
        "enwiki": "Dog Man",
        "zhwiki": "神探狗狗",
    },
    "dc_comics": {
        "fandom": "dc.fandom.com",
        "chars_en": ["Superman (Clark Kent)", "Batman (Bruce Wayne)", "Wonder Woman (Diana Prince)", "Joker", "Harley Quinn", "Flash (Barry Allen)"],
        "moegirl": ["DC漫画", "蝙蝠侠", "超人", "神奇女侠", "哈莉·奎茵"],
        "enwiki": "DC Comics",
        "zhwiki": "DC漫畫",
    },
    "demon_slayer": {
        "fandom": "kimetsu-no-yaiba.fandom.com",
        "chars_en": ["Tanjiro Kamado", "Nezuko Kamado", "Zenitsu Agatsuma", "Inosuke Hashibira", "Giyu Tomioka", "Shinobu Kocho", "Kyojuro Rengoku"],
        "moegirl": ["鬼灭之刃", "灶门炭治郎", "灶门祢豆子", "我妻善逸", "嘴平伊之助"],
        "enwiki": "List of Demon Slayer: Kimetsu no Yaiba characters",
        "zhwiki": "鬼滅之刃角色列表",
    },
    "disney": {
        "fandom": "disney.fandom.com",
        "chars_en": ["Mickey Mouse", "Minnie Mouse", "Donald Duck", "Stitch", "Elsa", "Winnie the Pooh"],
        "moegirl": ["迪士尼", "米老鼠", "史迪奇"],
        "enwiki": "Mickey Mouse",
        "zhwiki": "华特迪士尼公司",
    },
    "dragonball": {
        "fandom": "dragonball.fandom.com",
        "chars_en": ["Goku", "Vegeta", "Gohan", "Piccolo", "Bulma", "Frieza", "Trunks"],
        "moegirl": ["龙珠", "孙悟空(龙珠)", "贝吉塔", "布尔玛"],
        "enwiki": "List of Dragon Ball characters",
        "zhwiki": "七龍珠角色列表",
    },
    "dune": {
        "fandom": "dune.fandom.com",
        "chars_en": ["Paul Atreides", "Chani", "Lady Jessica", "Duncan Idaho", "Baron Vladimir Harkonnen"],
        "moegirl": ["沙丘(系列)"],
        "enwiki": "List of Dune characters",
        "zhwiki": "沙丘_(小說)",
    },
    "et": {
        "fandom": "et.fandom.com",
        "chars_en": ["E.T.", "Elliott Taylor", "Gertie Taylor"],
        "moegirl": [],
        "enwiki": "E.T. the Extra-Terrestrial",
        "zhwiki": "E.T.外星人",
    },
    "fallout": {
        "fandom": "fallout.fandom.com",
        "chars_en": ["Vault Boy", "T-60 power armor", "Dogmeat", "Nick Valentine", "Lucy MacLean"],
        "moegirl": ["辐射(游戏系列)", "避难所小子"],
        "enwiki": "Fallout (franchise)",
        "zhwiki": "異塵餘生系列",
    },
    "forza": {
        "fandom": "forza.fandom.com",
        "chars_en": ["Forza Horizon", "Forza Motorsport"],
        "moegirl": ["极限竞速系列"],
        "enwiki": "Forza",
        "zhwiki": "極限競速系列",
    },
    "friends": {
        "fandom": "friends.fandom.com",
        "chars_en": ["Rachel Green", "Monica Geller", "Phoebe Buffay", "Joey Tribbiani", "Chandler Bing", "Ross Geller"],
        "moegirl": ["老友记"],
        "enwiki": "Friends",
        "zhwiki": "老友記",
    },
    "godzilla": {
        "fandom": "godzilla.fandom.com",
        "chars_en": ["Godzilla", "King Ghidorah", "Mothra", "Rodan", "Mechagodzilla"],
        "moegirl": ["哥斯拉"],
        "enwiki": "Godzilla",
        "zhwiki": "哥吉拉",
    },
    "harrypotter": {
        "fandom": "harrypotter.fandom.com",
        "chars_en": ["Harry Potter", "Hermione Granger", "Ron Weasley", "Albus Dumbledore", "Severus Snape", "Draco Malfoy", "Voldemort"],
        "moegirl": ["哈利·波特", "哈利·詹姆·波特", "赫敏·格兰杰"],
        "enwiki": "List of Harry Potter characters",
        "zhwiki": "哈利·波特角色列表",
    },
    "hatsune_miku": {
        "fandom": "vocaloid.fandom.com",
        "chars_en": ["Hatsune Miku", "Kagamine Rin & Len", "Megurine Luka", "KAITO", "MEIKO"],
        "moegirl": ["初音未来", "镜音铃·连", "巡音流歌"],
        "enwiki": "Hatsune Miku",
        "zhwiki": "初音未來",
    },
    "hotstuff": {
        "fandom": "hotstuff.fandom.com",
        "chars_en": ["Hot Stuff the Little Devil"],
        "moegirl": [],
        "enwiki": "Hot Stuff the Little Devil",
        "zhwiki": "",
    },
    "itmovie": {
        "fandom": "stephenking.fandom.com",
        "chars_en": ["Pennywise", "Georgie Denbrough", "Bill Denbrough", "Beverly Marsh"],
        "moegirl": ["小丑回魂"],
        "enwiki": "It (character)",
        "zhwiki": "牠_(電影)",
    },
    "jujutsukaisen": {
        "fandom": "jujutsu-kaisen.fandom.com",
        "chars_en": ["Yuji Itadori", "Megumi Fushiguro", "Nobara Kugisaki", "Satoru Gojo", "Ryomen Sukuna", "Suguru Geto", "Yuta Okkotsu"],
        "moegirl": ["咒术回战", "虎杖悠仁", "五条悟", "伏黑惠", "钉崎野蔷薇"],
        "enwiki": "List of Jujutsu Kaisen characters",
        "zhwiki": "咒術迴戰角色列表",
    },
    "kirby": {
        "fandom": "kirby.fandom.com",
        "chars_en": ["Kirby", "Meta Knight", "King Dedede", "Bandana Waddle Dee"],
        "moegirl": ["星之卡比系列", "卡比(星之卡比)"],
        "enwiki": "Kirby (character)",
        "zhwiki": "卡比_(星之卡比)",
    },
    "legorelated": {
        "fandom": "lego.fandom.com",
        "chars_en": ["Minifigure", "Lloyd Garmadon", "Kai (Ninjago)"],
        "moegirl": ["乐高"],
        "enwiki": "Lego minifigure",
        "zhwiki": "樂高",
    },
    "lupinthethird": {
        "fandom": "lupin.fandom.com",
        "chars_en": ["Arsène Lupin III", "Daisuke Jigen", "Goemon Ishikawa XIII", "Fujiko Mine", "Inspector Zenigata"],
        "moegirl": ["鲁邦三世", "亚森·鲁邦三世", "峰不二子"],
        "enwiki": "List of Lupin III characters",
        "zhwiki": "魯邦三世角色列表",
    },
    "marvel": {
        "fandom": "marvel.fandom.com",
        "chars_en": ["Peter Parker (Earth-616)", "Anthony Stark (Earth-616)", "Steven Rogers (Earth-616)", "Thor Odinson (Earth-616)", "Wade Wilson (Earth-616)", "Bruce Banner (Earth-616)"],
        "moegirl": ["漫威漫画", "蜘蛛侠", "钢铁侠", "美国队长", "死侍"],
        "enwiki": "Marvel Comics",
        "zhwiki": "漫威漫畫角色列表",
    },
    "megaman": {
        "fandom": "megaman.fandom.com",
        "chars_en": ["Mega Man", "Proto Man", "Zero", "Mega Man X", "Roll"],
        "moegirl": ["洛克人系列", "洛克人(角色)"],
        "enwiki": "Mega Man (character)",
        "zhwiki": "洛克人_(角色)",
    },
    "meitanteikonan": {
        "fandom": "detectiveconan.fandom.com",
        "chars_en": ["Conan Edogawa", "Shinichi Kudo", "Ran Mouri", "Ai Haibara", "Kaito Kuroba", "Shuichi Akai"],
        "moegirl": ["名侦探柯南", "江户川柯南", "工藤新一", "灰原哀", "毛利兰"],
        "enwiki": "List of Case Closed characters",
        "zhwiki": "名偵探柯南角色列表",
    },
    "miffyrabbit": {
        "fandom": "miffy.fandom.com",
        "chars_en": ["Miffy", "Boris Bear", "Melanie"],
        "moegirl": ["米菲"],
        "enwiki": "Miffy",
        "zhwiki": "米菲兔",
    },
    "minions": {
        "fandom": "despicableme.fandom.com",
        "chars_en": ["Minions", "Kevin", "Stuart", "Bob", "Gru"],
        "moegirl": ["小黄人大眼萌", "小黄人"],
        "enwiki": "Minions (Despicable Me)",
        "zhwiki": "小小兵",
    },
    "monchhichi": {
        "fandom": "",
        "chars_en": [],
        "moegirl": [],
        "enwiki": "Monchhichi",
        "zhwiki": "夢奇奇",
    },
    "money_heist_la_casa_de_papel": {
        "fandom": "money-heist.fandom.com",
        "chars_en": ["The Professor", "Tokyo", "Berlin", "Nairobi", "Denver", "Rio"],
        "moegirl": [],
        "enwiki": "Money Heist",
        "zhwiki": "紙房子",
    },
    "monopoly": {
        "fandom": "monopoly.fandom.com",
        "chars_en": ["Mr. Monopoly", "Monopoly"],
        "moegirl": ["大富翁(游戏)"],
        "enwiki": "Rich Uncle Pennybags",
        "zhwiki": "地產大亨",
    },
    "monsterhigh": {
        "fandom": "monsterhigh.fandom.com",
        "chars_en": ["Frankie Stein", "Draculaura", "Clawdeen Wolf", "Cleo de Nile", "Lagoona Blue"],
        "moegirl": ["精灵高中"],
        "enwiki": "Monster High",
        "zhwiki": "精靈高中",
    },
    "mr_men_little_miss": {
        "fandom": "mrmen.fandom.com",
        "chars_en": ["Mr. Happy", "Little Miss Sunshine", "Mr. Tickle", "Mr. Bump", "Little Miss Chatterbox"],
        "moegirl": [],
        "enwiki": "Mr. Men",
        "zhwiki": "奇先生妙小姐",
    },
    "my_dress": {
        "fandom": "sono-bisque-doll-wa-koi-wo-suru.fandom.com",
        "chars_en": ["Marin Kitagawa", "Wakana Gojo", "Sajuna Inui", "Shinju Inui"],
        "moegirl": ["更衣人偶坠入爱河", "喜多川海梦", "五条新菜"],
        "enwiki": "My Dress-Up Darling",
        "zhwiki": "戀上換裝娃娃",
    },
    "my_hero_academia": {
        "fandom": "myheroacademia.fandom.com",
        "chars_en": ["Izuku Midoriya", "Katsuki Bakugo", "Shoto Todoroki", "Ochaco Uraraka", "All Might", "Tomura Shigaraki"],
        "moegirl": ["我的英雄学院", "绿谷出久", "爆豪胜己", "轰焦冻"],
        "enwiki": "List of My Hero Academia characters",
        "zhwiki": "我的英雄學院角色列表",
    },
    "naruto": {
        "fandom": "naruto.fandom.com",
        "chars_en": ["Naruto Uzumaki", "Sasuke Uchiha", "Sakura Haruno", "Kakashi Hatake", "Itachi Uchiha", "Gaara", "Hinata Hyuga"],
        "moegirl": ["火影忍者", "漩涡鸣人", "宇智波佐助", "旗木卡卡西", "宇智波鼬"],
        "enwiki": "List of Naruto characters",
        "zhwiki": "火影忍者角色列表",
    },
    "ohayou_spank": {
        "fandom": "",
        "chars_en": [],
        "moegirl": ["早上好!Spank"],
        "enwiki": "Ohayō! Spank",
        "zhwiki": "早安!史賓克",
    },
    "one_piece": {
        "fandom": "onepiece.fandom.com",
        "chars_en": ["Monkey D. Luffy", "Roronoa Zoro", "Nami", "Sanji", "Tony Tony Chopper", "Nico Robin", "Trafalgar D. Water Law", "Shanks"],
        "moegirl": ["航海王", "蒙奇·D·路飞", "罗罗诺亚·索隆", "娜美(航海王)", "托尼托尼·乔巴"],
        "enwiki": "List of One Piece characters",
        "zhwiki": "ONE PIECE角色列表",
    },
    "pandorobo": {
        "fandom": "",
        "chars_en": [],
        "moegirl": ["面包小偷"],
        "enwiki": "Pan Dorobou",
        "zhwiki": "麵包小偷",
    },
    "paw_patrol": {
        "fandom": "pawpatrol.fandom.com",
        "chars_en": ["Chase", "Marshall", "Skye", "Rubble", "Rocky", "Zuma", "Ryder"],
        "moegirl": ["汪汪队立大功"],
        "enwiki": "PAW Patrol",
        "zhwiki": "汪汪隊立大功",
    },
    "peanuts": {
        "fandom": "peanuts.fandom.com",
        "chars_en": ["Snoopy", "Charlie Brown", "Woodstock", "Lucy van Pelt", "Linus van Pelt"],
        "moegirl": ["花生漫画", "史努比", "查理·布朗"],
        "enwiki": "List of Peanuts characters",
        "zhwiki": "花生漫畫角色列表",
    },
    "pikmin": {
        "fandom": "pikmin.fandom.com",
        "chars_en": ["Red Pikmin", "Yellow Pikmin", "Blue Pikmin", "Captain Olimar", "Oatchi"],
        "moegirl": ["皮克敏系列", "皮克敏"],
        "enwiki": "Pikmin",
        "zhwiki": "皮克敏",
    },
    "pinkpanther": {
        "fandom": "pinkpanther.fandom.com",
        "chars_en": ["The Pink Panther", "Inspector Clouseau"],
        "moegirl": ["粉红豹"],
        "enwiki": "Pink Panther (character)",
        "zhwiki": "頑皮豹",
    },
    "pokemon": {
        "fandom": "pokemon.fandom.com",
        "chars_en": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle", "Eevee", "Mewtwo", "Ash Ketchum"],
        "moegirl": ["宝可梦", "皮卡丘", "喷火龙", "伊布", "超梦"],
        "enwiki": "Pikachu",
        "zhwiki": "寶可夢列表",
    },
    "rezero": {
        "fandom": "rezero.fandom.com",
        "chars_en": ["Subaru Natsuki", "Emilia", "Rem", "Ram", "Beatrice", "Puck", "Echidna"],
        "moegirl": ["Re:从零开始的异世界生活", "雷姆(Re:从零开始的异世界生活)", "爱蜜莉雅", "菜月昴", "拉姆(Re:从零开始的异世界生活)"],
        "enwiki": "List of Re:Zero characters",
        "zhwiki": "Re:從零開始的異世界生活角色列表",
    },
    "rickandmorty": {
        "fandom": "rickandmorty.fandom.com",
        "chars_en": ["Rick Sanchez", "Morty Smith", "Summer Smith", "Mr. Meeseeks", "Pickle Rick"],
        "moegirl": ["瑞克和莫蒂"],
        "enwiki": "List of Rick and Morty characters",
        "zhwiki": "瑞克和莫蒂角色列表",
    },
    "rilakkuma": {
        "fandom": "san-x.fandom.com",
        "chars_en": ["Rilakkuma", "Korilakkuma", "Kiiroitori", "Chairoikoguma"],
        "moegirl": ["轻松小熊"],
        "enwiki": "Rilakkuma",
        "zhwiki": "拉拉熊",
    },
    "rockybalboa": {
        "fandom": "rocky.fandom.com",
        "chars_en": ["Rocky Balboa", "Apollo Creed", "Ivan Drago"],
        "moegirl": [],
        "enwiki": "Rocky Balboa",
        "zhwiki": "洛基·巴波亞",
    },
    "sandmaennchen": {
        "fandom": "",
        "chars_en": [],
        "moegirl": [],
        "enwiki": "Sandmännchen",
        "zhwiki": "沙人_(德國電視節目)",
    },
    "scoobydoo": {
        "fandom": "scoobydoo.fandom.com",
        "chars_en": ["Scooby-Doo", "Shaggy Rogers", "Velma Dinkley", "Daphne Blake", "Fred Jones"],
        "moegirl": ["史酷比"],
        "enwiki": "Scooby-Doo (character)",
        "zhwiki": "史酷比",
    },
    "sesame_street": {
        "fandom": "muppet.fandom.com",
        "chars_en": ["Elmo", "Cookie Monster", "Big Bird", "Oscar the Grouch", "Kermit the Frog"],
        "moegirl": ["芝麻街"],
        "enwiki": "List of Sesame Street Muppets",
        "zhwiki": "芝麻街",
    },
    "sevendeadlysins": {
        "fandom": "nanatsu-no-taizai.fandom.com",
        "chars_en": ["Meliodas", "Elizabeth Liones", "Ban", "King", "Diane", "Escanor"],
        "moegirl": ["七大罪(漫画)", "梅利奥达斯", "伊丽莎白·里昂妮丝"],
        "enwiki": "List of The Seven Deadly Sins characters",
        "zhwiki": "七大罪角色列表",
    },
    "slamdunk": {
        "fandom": "slamdunk.fandom.com",
        "chars_en": ["Hanamichi Sakuragi", "Kaede Rukawa", "Takenori Akagi", "Hisashi Mitsui", "Ryota Miyagi"],
        "moegirl": ["灌篮高手", "樱木花道", "流川枫", "三井寿"],
        "enwiki": "List of Slam Dunk characters",
        "zhwiki": "灌籃高手角色列表",
    },
    "spirit": {
        "fandom": "dreamworks.fandom.com",
        "chars_en": ["Spirit (Spirit: Stallion of the Cimarron)", "Rain", "Little Creek"],
        "moegirl": [],
        "enwiki": "Spirit: Stallion of the Cimarron",
        "zhwiki": "小馬王",
    },
    "spongebobsquarepants": {
        "fandom": "spongebob.fandom.com",
        "chars_en": ["SpongeBob SquarePants", "Patrick Star", "Squidward Tentacles", "Mr. Krabs", "Sandy Cheeks", "Plankton"],
        "moegirl": ["海绵宝宝", "派大星", "章鱼哥"],
        "enwiki": "List of SpongeBob SquarePants characters",
        "zhwiki": "海綿寶寶角色列表",
    },
    "spotit": {
        "fandom": "",
        "chars_en": [],
        "moegirl": [],
        "enwiki": "Dobble",
        "zhwiki": "多寶牌",
    },
    "squishmallows": {
        "fandom": "squishmallowsquad.fandom.com",
        "chars_en": ["Cam", "Wendy", "Fifi", "Connor", "Archie"],
        "moegirl": [],
        "enwiki": "Squishmallows",
        "zhwiki": "Squishmallows",
    },
    "startrek": {
        "fandom": "memory-alpha.fandom.com",
        "chars_en": ["Spock", "James T. Kirk", "Jean-Luc Picard", "Data", "USS Enterprise (NCC-1701)"],
        "moegirl": ["星际迷航", "史波克"],
        "enwiki": "Star Trek",
        "zhwiki": "星際爭霸戰",
    },
    "stealabrainrot": {
        "fandom": "brainrot.fandom.com",
        "chars_en": ["Tralalero Tralala", "Bombardiro Crocodilo", "Tung Tung Tung Sahur", "Ballerina Cappuccina"],
        "moegirl": [],
        "enwiki": "Italian brainrot",
        "zhwiki": "",
    },
    "strawberryshortcake": {
        "fandom": "strawberryshortcake.fandom.com",
        "chars_en": ["Strawberry Shortcake", "Blueberry Muffin", "Orange Blossom", "Lemon Meringue", "Raspberry Torte"],
        "moegirl": ["草莓甜心"],
        "enwiki": "Strawberry Shortcake",
        "zhwiki": "草莓甜心",
    },
    "streetfighter": {
        "fandom": "streetfighter.fandom.com",
        "chars_en": ["Ryu", "Ken Masters", "Chun-Li", "Guile", "Akuma", "Cammy"],
        "moegirl": ["街头霸王", "隆(街头霸王)", "春丽", "肯·马斯达斯"],
        "enwiki": "List of Street Fighter characters",
        "zhwiki": "快打旋風系列角色列表",
    },
    "super_mario": {
        "fandom": "mario.fandom.com",
        "chars_en": ["Mario", "Luigi", "Princess Peach", "Bowser", "Yoshi", "Toad"],
        "moegirl": ["超级马力欧", "马力欧", "路易吉", "酷霸王"],
        "enwiki": "Mario",
        "zhwiki": "瑪利歐",
    },
    "thebadguys": {
        "fandom": "the-bad-guys.fandom.com",
        "chars_en": ["Mr. Wolf", "Mr. Snake", "Mr. Shark", "Mr. Piranha", "Ms. Tarantula", "Diane Foxington"],
        "moegirl": ["坏蛋联盟"],
        "enwiki": "The Bad Guys (film)",
        "zhwiki": "壞蛋聯盟",
    },
    "thesecretlifeofpets": {
        "fandom": "secretlifeofpets.fandom.com",
        "chars_en": ["Max", "Duke", "Snowball", "Gidget", "Chloe"],
        "moegirl": ["爱宠大机密"],
        "enwiki": "The Secret Life of Pets",
        "zhwiki": "寵物當家",
    },
    "thesimpsonver2": {
        "fandom": "simpsons.fandom.com",
        "chars_en": ["Homer Simpson", "Marge Simpson", "Bart Simpson", "Lisa Simpson", "Maggie Simpson", "Krusty the Clown"],
        "moegirl": ["辛普森一家", "霍默·辛普森", "巴特·辛普森"],
        "enwiki": "List of The Simpsons characters",
        "zhwiki": "辛普森一家角色列表",
    },
    "thomasandfriends": {
        "fandom": "ttte.fandom.com",
        "chars_en": ["Thomas", "Percy", "James", "Gordon", "Sir Topham Hatt"],
        "moegirl": ["托马斯和他的朋友们"],
        "enwiki": "List of Thomas & Friends characters",
        "zhwiki": "湯瑪士小火車角色列表",
    },
    "tokyoghoul": {
        "fandom": "tokyoghoul.fandom.com",
        "chars_en": ["Ken Kaneki", "Touka Kirishima", "Juuzou Suzuya", "Rize Kamishiro", "Kishou Arima"],
        "moegirl": ["东京喰种", "金木研", "雾岛董香", "铃屋什造"],
        "enwiki": "List of Tokyo Ghoul characters",
        "zhwiki": "東京喰種角色列表",
    },
    "tomandjerry": {
        "fandom": "tomandjerry.fandom.com",
        "chars_en": ["Tom Cat", "Jerry Mouse", "Spike", "Nibbles", "Butch"],
        "moegirl": ["猫和老鼠", "汤姆(猫和老鼠)", "杰瑞(猫和老鼠)"],
        "enwiki": "Tom and Jerry",
        "zhwiki": "湯姆貓與傑利鼠",
    },
    "trolls": {
        "fandom": "trolls.fandom.com",
        "chars_en": ["Poppy", "Branch", "Guy Diamond", "Barb", "Tiny Diamond"],
        "moegirl": ["魔发精灵"],
        "enwiki": "Trolls (franchise)",
        "zhwiki": "魔髮精靈",
    },
    "underdog": {
        "fandom": "underdog.fandom.com",
        "chars_en": ["Underdog", "Sweet Polly Purebred", "Simon Bar Sinister"],
        "moegirl": [],
        "enwiki": "Underdog (TV series)",
        "zhwiki": "",
    },
    "warhammer": {
        "fandom": "warhammer40k.fandom.com",
        "chars_en": ["Space Marine", "Emperor of Mankind", "Roboute Guilliman", "Orks", "Tyranids"],
        "moegirl": ["战锤40000"],
        "enwiki": "Warhammer 40,000",
        "zhwiki": "戰鎚40000",
    },
    "zelda": {
        "fandom": "zelda.fandom.com",
        "chars_en": ["Link", "Princess Zelda", "Ganon", "Midna", "Navi", "Korok"],
        "moegirl": ["塞尔达传说系列", "林克", "塞尔达公主"],
        "enwiki": "List of The Legend of Zelda characters",
        "zhwiki": "薩爾達傳說系列角色列表",
    },
}


def _http_get_text(url: str, *, timeout: float = 15.0, delay: float = 0.25) -> tuple[int, str]:
    if delay > 0:
        time.sleep(delay)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        return resp.status, raw.decode("utf-8", errors="replace")


def _http_get_json(url: str, *, timeout: float = 15.0, delay: float = 0.25) -> dict[str, Any]:
    _, txt = _http_get_text(url, timeout=timeout, delay=delay)
    return json.loads(txt)


def _strip_nested_braces(text: str) -> str:
    """Removes nested `{{...}}` MediaWiki templates cleanly while preserving plain text."""
    out: list[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        if i + 1 < n and text[i : i + 2] == "{{":
            depth += 1
            i += 2
        elif i + 1 < n and text[i : i + 2] == "}}" and depth > 0:
            depth -= 1
            i += 2
        else:
            if depth == 0:
                out.append(text[i])
            i += 1
    return "".join(out)


def clean_wikitext_to_prose(wikitext: str) -> str:
    """Converts MediaWiki markup into clean natural language text with zero wikitext tags."""
    s = str(wikitext or "")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref\b[^>]*>.*?</ref>", "", s, flags=re.I | re.S)
    s = re.sub(r"<ref\b[^>]*/?>", "", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", ", ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\[(?:File|Image):[^\n\]]*\]\]", "", s, flags=re.I)
    s = re.sub(r"\[\[Category:[^\]]+\]\]", "", s, flags=re.I)
    # Replace wiki links [[target|label]] -> label, [[target]] -> target
    s = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    # Strip external links [http://... label] -> label
    s = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", s)
    s = re.sub(r"\[https?://[^\]]+\]", "", s)
    s = _strip_nested_braces(s)
    s = re.sub(r"'{2,5}", "", s)
    s = re.sub(r"^\s*[*#;:]+\s*", "", s, flags=re.M)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return html_lib.unescape(s).strip()


def _extract_wikitext_infobox(wikitext: str) -> dict[str, str]:
    """Extracts visual-relevant Infobox fields from MediaWiki template markup."""
    info: dict[str, str] = {}
    field_map = {
        "hair": "hair_color",
        "hair_color": "hair_color",
        "hair colour": "hair_color",
        "eye": "eye_color",
        "eyes": "eye_color",
        "eye_color": "eye_color",
        "eye colour": "eye_color",
        "gender": "gender",
        "sex": "gender",
        "species": "species",
        "race": "species",
        "alias": "aliases",
        "aliases": "aliases",
        "nickname": "aliases",
        "nicknames": "aliases",
        "affiliation": "affiliation",
        "affiliations": "affiliation",
        "occupation": "occupation",
        "weapons": "weapons_props",
        "weapon": "weapons_props",
        "equipment": "weapons_props",
        "status": "status",
        "height": "height",
    }
    # Scan line-based infobox `| key = value`
    for line in wikitext[:12000].splitlines():
        m = re.match(r"^\s*\|\s*([A-Za-z0-9_ ]{2,25})\s*=\s*(.+)$", line)
        if not m:
            continue
        raw_k = m.group(1).strip().lower()
        norm_k = field_map.get(raw_k)
        if not norm_k or norm_k in info:
            continue
        cleaned_v = clean_wikitext_to_prose(m.group(2))
        cleaned_v = re.sub(r"\s+", " ", cleaned_v).strip(" ,;|")
        if cleaned_v and len(cleaned_v) <= 180:
            info[norm_k] = cleaned_v
    return info


def _split_wikitext_sections(wikitext: str) -> dict[str, str]:
    sections: dict[str, str] = {"_lead": ""}
    cur_sec = "_lead"
    buf: list[str] = []
    for line in wikitext.splitlines():
        m = re.match(r"^(={2,4})\s*([^=]+?)\s*\1\s*$", line)
        if m:
            sections[cur_sec] = "\n".join(buf)
            cur_sec = m.group(2).strip().lower()
            buf = []
        else:
            buf.append(line)
    sections[cur_sec] = "\n".join(buf)
    return sections


def _parse_fandom_wikitext(title: str, wikitext: str, page_url: str, portrait_url: str) -> dict[str, Any]:
    infobox = _extract_wikitext_infobox(wikitext)
    sections = _split_wikitext_sections(wikitext)

    lead_prose = clean_wikitext_to_prose(sections.get("_lead", ""))
    lead_prose = re.sub(r"\s+", " ", lead_prose)[:550].strip()

    appearance_txt = ""
    for k, v in sections.items():
        if any(tok in k for tok in ("appearance", "physical", "design", "visual", "attire", "outfit", "costume")):
            cand = re.sub(r"\s+", " ", clean_wikitext_to_prose(v)).strip()
            if len(cand) > 30:
                appearance_txt = cand[:1000].strip()
                break

    abilities_txt = ""
    for k, v in sections.items():
        if any(tok in k for tok in ("personality", "abilities", "powers", "equipment", "weapons", "history")):
            cand = re.sub(r"\s+", " ", clean_wikitext_to_prose(v)).strip()
            if len(cand) > 30:
                abilities_txt = cand[:420].strip()
                break

    anchors: list[str] = []
    for k, lbl in (
        ("hair_color", "Hair"),
        ("eye_color", "Eyes"),
        ("species", "Species"),
        ("weapons_props", "Props/Weapons"),
        ("affiliation", "Affiliation"),
    ):
        if infobox.get(k):
            anchors.append(f"{lbl}: {infobox[k]}")

    return {
        "character_name": title,
        "source": "fandom",
        "language": "en",
        "source_url": page_url,
        "portrait_url": portrait_url,
        "infobox": infobox,
        "visual_appearance": appearance_txt,
        "overview": lead_prose,
        "personality_or_abilities": abilities_txt,
        "visual_anchors_extracted": anchors,
    }


def _fetch_fandom_for_franchise(domain: str, char_titles: list[str]) -> list[dict[str, Any]]:
    if not domain:
        return []
    entries: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    def _query_titles(titles: list[str]) -> None:
        for start in range(0, len(titles), 8):
            batch = titles[start : start + 8]
            params = {
                "action": "query",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
                "titles": "|".join(batch),
                "prop": "revisions|pageimages|info",
                "rvprop": "content",
                "piprop": "thumbnail|original",
                "pithumbsize": "480",
                "inprop": "url",
            }
            url = f"https://{domain}/api.php?" + urllib.parse.urlencode(params)
            data = _http_get_json(url, timeout=15.0, delay=0.25)
            for page in (data.get("query") or {}).get("pages") or []:
                if page.get("missing"):
                    continue
                t = str(page.get("title") or "").strip()
                if not t or t in seen_titles:
                    continue
                revs = page.get("revisions") or []
                wt = revs[0].get("content", "") if revs else ""
                if not wt or len(wt) < 80:
                    continue
                seen_titles.add(t)
                portrait = ((page.get("thumbnail") or {}).get("source") or (page.get("original") or {}).get("source") or "")
                page_url = str(page.get("fullurl") or f"https://{domain}/wiki/{urllib.parse.quote(t.replace(' ', '_'))}")
                parsed = _parse_fandom_wikitext(t, wt, page_url, portrait)
                if parsed["overview"] or parsed["visual_appearance"] or parsed["infobox"]:
                    entries.append(parsed)

    if char_titles:
        _query_titles(char_titles)

    # Auto-discover Category:Characters if curated titles yielded < 2 entries
    if len(entries) < 2:
        try:
            cat_url = f"https://{domain}/api.php?" + urllib.parse.urlencode(
                {
                    "action": "query",
                    "format": "json",
                    "formatversion": "2",
                    "list": "categorymembers",
                    "cmtitle": "Category:Characters",
                    "cmnamespace": "0",
                    "cmlimit": "8",
                }
            )
            cat_data = _http_get_json(cat_url, timeout=12.0, delay=0.25)
            disc = [
                str(m.get("title") or "")
                for m in (cat_data.get("query") or {}).get("categorymembers") or []
                if m.get("title") and "category:" not in str(m.get("title") or "").lower()
            ]
            disc = [t for t in disc if t not in seen_titles][:6]
            if disc:
                _query_titles(disc)
        except Exception:
            pass

    return entries


class _MoegirlHTMLParser(HTMLParser):
    """Stdlib HTML parser extracting Moegirlpedia infobox facts, lead & appearance prose."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.in_table_cell = False
        self.cell_tag = ""
        self.cur_row: list[str] = []
        self.table_rows: list[list[str]] = []
        self.cell_buf: list[str] = []

        self.in_heading = False
        self.heading_buf: list[str] = []
        self.cur_section = "_lead"

        self.in_p = False
        self.p_buf: list[str] = []
        self.sections_text: dict[str, list[str]] = {"_lead": []}
        self.page_title = ""
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        cls = str(attr_map.get("class") or "")
        if tag in ("script", "style", "nav", "sup", "noscript") or "navbox" in cls or "mw-editsection" in cls:
            self.skip_depth += 1
            return
        if self.skip_depth > 0:
            if tag in ("div", "table", "ul", "ol", "span", "p"):
                self.skip_depth += 1
            return
        if tag == "title":
            self.in_title = True
        elif tag == "tr":
            self.cur_row = []
        elif tag in ("th", "td"):
            self.in_table_cell = True
            self.cell_tag = tag
            self.cell_buf = []
        elif tag in ("h2", "h3", "h4"):
            self.in_heading = True
            self.heading_buf = []
        elif tag == "p":
            self.in_p = True
            self.p_buf = []

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth > 0:
            if tag in ("script", "style", "nav", "sup", "noscript", "div", "table", "ul", "ol", "span", "p"):
                self.skip_depth -= 1
            return
        if tag == "title":
            self.in_title = False
        elif tag in ("th", "td") and self.in_table_cell:
            self.in_table_cell = False
            cell_txt = re.sub(r"\s+", " ", "".join(self.cell_buf)).strip()
            if cell_txt:
                self.cur_row.append(cell_txt)
        elif tag == "tr":
            if len(self.cur_row) == 2:
                self.table_rows.append(self.cur_row)
            self.cur_row = []
        elif tag in ("h2", "h3", "h4") and self.in_heading:
            self.in_heading = False
            h = re.sub(r"\[编辑\]", "", "".join(self.heading_buf)).strip()
            if h:
                self.cur_section = h
                self.sections_text.setdefault(self.cur_section, [])
        elif tag == "p" and self.in_p:
            self.in_p = False
            txt = re.sub(r"\s+", " ", "".join(self.p_buf)).strip()
            if len(txt) >= 18 and "萌娘百科" not in txt[:20]:
                self.sections_text.setdefault(self.cur_section, []).append(txt)

    def handle_data(self, data: str) -> None:
        if self.skip_depth > 0:
            return
        if self.in_title:
            self.page_title += data
        if self.in_table_cell:
            self.cell_buf.append(data)
        if self.in_heading:
            self.heading_buf.append(data)
        if self.in_p:
            self.p_buf.append(data)


def _fetch_moegirl_page(page_title: str) -> tuple[dict[str, Any] | None, str]:
    """Fetches a single public Moegirlpedia zh-hans HTML page; detects any anti-bot challenge."""
    url = f"https://mzh.moegirl.org.cn/zh-hans/{urllib.parse.quote(page_title, safe=':()')}"
    try:
        status, raw_html = _http_get_text(url, timeout=12.0, delay=0.6)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429, 503):
            return None, f"http_{exc.code}"
        return None, f"http_{exc.code}"
    except Exception as exc:
        return None, f"err_{type(exc).__name__}"

    low = raw_html[:6000].lower()
    if any(marker in low for marker in ("cloudflare", "turnstile", "just a moment", "captcha", "verify you are human")):
        return None, "anti_bot_challenge"

    parser = _MoegirlHTMLParser()
    parser.feed(raw_html)

    # Extract clean Chinese visual/moe infobox fields
    moe_keys = {
        "本名": "real_name",
        "别号": "aliases",
        "昵称": "aliases",
        "发色": "hair_color",
        "瞳色": "eye_color",
        "身高": "height",
        "种族": "species",
        "萌点": "moe_traits",
        "出身地区": "origin",
        "所属团体": "affiliation",
        "活动范围": "affiliation",
        "相关人士": "related_characters",
    }
    infobox: dict[str, str] = {}
    for row in parser.table_rows:
        k_raw = row[0].strip().rstrip("：:")
        v_raw = row[1].strip()
        for mk, norm_k in moe_keys.items():
            if mk in k_raw and norm_k not in infobox and 1 <= len(v_raw) <= 180:
                infobox[norm_k] = v_raw
                break

    lead_list = parser.sections_text.get("_lead") or []
    overview = " ".join(lead_list)[:550].strip()

    appearance_txt = ""
    char_summary_txt = ""
    for sec_title, paras in parser.sections_text.items():
        if sec_title == "_lead":
            continue
        joined = " ".join(paras).strip()
        if not joined:
            continue
        if any(k in sec_title for k in ("外貌", "形象", "特征", "服装", "着装", "人设")) and not appearance_txt:
            appearance_txt = joined[:1000]
        elif any(k in sec_title for k in ("简介", "角色", "人物", "登场", "背景", "介绍")) and not char_summary_txt:
            char_summary_txt = joined[:700]

    if not appearance_txt and char_summary_txt:
        appearance_txt = char_summary_txt

    if not overview and not appearance_txt and not infobox:
        return None, "empty_parse"

    anchors: list[str] = []
    for k, lbl in (
        ("hair_color", "发色"),
        ("eye_color", "瞳色"),
        ("moe_traits", "萌点/视觉特征"),
        ("species", "种族"),
        ("affiliation", "所属"),
    ):
        if infobox.get(k):
            anchors.append(f"{lbl}: {infobox[k]}")

    clean_title = parser.page_title.split(" - 萌娘百科")[0].strip() or page_title
    return {
        "character_name": clean_title,
        "source": "moegirl",
        "language": "zh",
        "source_url": url,
        "portrait_url": "",
        "infobox": infobox,
        "visual_appearance": appearance_txt,
        "overview": overview,
        "personality_or_abilities": char_summary_txt if appearance_txt != char_summary_txt else "",
        "visual_anchors_extracted": anchors,
    }, "ok"


def _batch_wikipedia_extracts(titles: list[str], lang: str) -> dict[str, dict[str, Any]]:
    if not titles:
        return {}
    api = f"https://{lang}.wikipedia.org/w/api.php"
    out: dict[str, dict[str, Any]] = {}
    for start in range(0, len(titles), 15):
        batch = titles[start : start + 15]
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "titles": "|".join(batch),
            "prop": "extracts|info",
            "exintro": "1",
            "exlimit": "max",
            "explaintext": "1",
            "inprop": "url",
        }
        if lang == "zh":
            params["variant"] = "zh-hans"
        data = None
        for attempt in range(2):
            try:
                data = _http_get_json(api + "?" + urllib.parse.urlencode(params), timeout=25.0, delay=0.35 + attempt * 0.8)
                break
            except Exception:
                data = None
        if not isinstance(data, dict):
            continue
        q = data.get("query") or {}
        norm = {n["from"]: n["to"] for n in q.get("normalized") or []}
        redir = {r["from"]: r["to"] for r in q.get("redirects") or []}
        by_t = {p.get("title", ""): p for p in q.get("pages") or [] if not p.get("missing")}
        for orig in batch:
            t = norm.get(orig, orig)
            seen = set()
            while t in redir and t not in seen:
                seen.add(t)
                t = redir[t]
            if t in by_t:
                p = by_t[t]
                extract = re.sub(r"\s+", " ", str(p.get("extract") or "")).strip()
                if extract:
                    out[orig] = {
                        "character_name": str(p.get("title") or t),
                        "source": f"{lang}wiki",
                        "language": lang,
                        "source_url": str(p.get("fullurl") or ""),
                        "portrait_url": "",
                        "infobox": {},
                        "visual_appearance": "",
                        "overview": extract[:1200],
                        "personality_or_abilities": "",
                        "visual_anchors_extracted": [],
                    }
    return out


def run_fetch(
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    cache_path: Path = DEFAULT_CACHE_PATH,
    limit: int = 0,
    skip_moegirl: bool = False,
) -> dict[str, Any]:
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    b2_slugs = [f["family_slug"] for f in tax["families"] if f["scope_subtrack"] == "B2_specific_anime_game_media_ip"]
    if limit > 0:
        b2_slugs = b2_slugs[:limit]

    cache: dict[str, Any] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    cache.setdefault("fandom", {})
    cache.setdefault("moegirl", {})
    cache.setdefault("enwiki", {})
    cache.setdefault("zhwiki", {})
    cache.setdefault("fandom_errors", {})
    cache.setdefault("moegirl_status", {})

    # 1. Batch Wikipedia zh/en fallback summaries for all configured B2 titles first (super fast)
    en_titles = sorted({FRANCHISE_WIKI_CONFIG.get(s, {}).get("enwiki", "") for s in b2_slugs} - {""})
    zh_titles = sorted({FRANCHISE_WIKI_CONFIG.get(s, {}).get("zhwiki", "") for s in b2_slugs} - {""})
    en_missing = [t for t in en_titles if t not in cache["enwiki"] or (isinstance(cache["enwiki"].get(t), dict) and cache["enwiki"][t].get("missing"))]
    zh_missing = [t for t in zh_titles if t not in cache["zhwiki"] or (isinstance(cache["zhwiki"].get(t), dict) and cache["zhwiki"][t].get("missing"))]
    if en_missing:
        fetched_en = _batch_wikipedia_extracts(en_missing, "en")
        for t in en_missing:
            cache["enwiki"][t] = fetched_en.get(t, {"missing": True})
    if zh_missing:
        fetched_zh = _batch_wikipedia_extracts(zh_missing, "zh")
        for t in zh_missing:
            cache["zhwiki"][t] = fetched_zh.get(t, {"missing": True})
    # Retry any transient Fandom SSL/timeout errors once
    for err_slug in list(cache["fandom_errors"].keys()):
        if "HTTPError: HTTP Error 404" not in str(cache["fandom_errors"][err_slug]):
            cache["fandom"].pop(err_slug, None)
            cache["fandom_errors"].pop(err_slug, None)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Fandom + Moegirlpedia per franchise
    moegirl_aborted = False
    moegirl_consec_blocks = 0
    for idx, slug in enumerate(b2_slugs, 1):
        cfg = FRANCHISE_WIKI_CONFIG.get(slug) or {}
        domain = str(cfg.get("fandom") or "").strip()
        chars_en = list(cfg.get("chars_en") or [])
        if domain and slug not in cache["fandom"]:
            try:
                rows = _fetch_fandom_for_franchise(domain, chars_en)
                cache["fandom"][slug] = rows
            except Exception as exc:
                cache["fandom"][slug] = []
                cache["fandom_errors"][slug] = f"{domain}: {type(exc).__name__}: {exc}"

        moe_pages = list(cfg.get("moegirl") or [])
        if not skip_moegirl and not moegirl_aborted and moe_pages:
            for mp in moe_pages[:4]:
                if mp in cache["moegirl"]:
                    continue
                parsed, st = _fetch_moegirl_page(mp)
                cache["moegirl_status"][mp] = st
                if st in ("http_403", "http_429", "http_503", "anti_bot_challenge"):
                    moegirl_consec_blocks += 1
                    if moegirl_consec_blocks >= 3:
                        moegirl_aborted = True
                        break
                else:
                    moegirl_consec_blocks = 0
                cache["moegirl"][mp] = parsed if parsed else {"status": st}

        if idx % 10 == 0:
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "target_b2_families": len(b2_slugs),
        "fandom_families_cached": sum(1 for v in cache["fandom"].values() if v),
        "moegirl_pages_ok": sum(1 for v in cache["moegirl"].values() if isinstance(v, dict) and v.get("character_name")),
        "moegirl_aborted_due_to_block": moegirl_aborted,
        "enwiki_ok": sum(1 for v in cache["enwiki"].values() if isinstance(v, dict) and not v.get("missing")),
        "zhwiki_ok": sum(1 for v in cache["zhwiki"].values() if isinstance(v, dict) and not v.get("missing")),
        "fandom_errors_count": len(cache["fandom_errors"]),
    }


def _sanitize_wiki_prose(text: str) -> str:
    """Strips residual MediaWiki table blocks and Moegirlpedia edit-welcome banners."""
    if not text:
        return ""
    s = re.sub(r"\{\|.*?\|\}", " ", str(text), flags=re.S)
    s = re.sub(r"\{\|.*$", " ", s)
    s = re.sub(
        r"欢迎正在阅读这个条目的您协助编辑本条目。\s*(?:编辑前请阅读[^。]*。\s*)?(?:[^。]*?(?:萌娘百科|愉快的时光)[^。☆~]*[。☆~]+\s*)?",
        "",
        s,
    )
    s = s.replace("编辑前请阅读Wiki入门或条目编辑规范，并查找相关资料。", "")
    return re.sub(r"\s+", " ", s).strip()


def run_build(
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    cache_path: Path = DEFAULT_CACHE_PATH,
    dossiers_jsonl: Path = DEFAULT_DOSSIERS_JSONL,
    summary_json: Path = DEFAULT_SUMMARY_JSON,
    cpt_prose_jsonl: Path = DEFAULT_CPT_PROSE_JSONL,
) -> dict[str, Any]:
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    b2_fams = [f for f in tax["families"] if f["scope_subtrack"] == "B2_specific_anime_game_media_ip"]
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    fandom_cache = cache.get("fandom") or {}
    moegirl_cache = cache.get("moegirl") or {}
    enwiki_cache = cache.get("enwiki") or {}
    zhwiki_cache = cache.get("zhwiki") or {}
    now_iso = datetime.now(timezone.utc).isoformat()

    all_dossiers: list[dict[str, Any]] = []
    cpt_docs: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    families_covered = 0
    uncovered_slugs: list[str] = []

    for f in b2_fams:
        slug = str(f["family_slug"])
        disp_name = str(f["display_name"])
        cfg = FRANCHISE_WIKI_CONFIG.get(slug) or {}
        fam_entries: list[dict[str, Any]] = []

        # Collect Moegirlpedia Chinese entries first (rich hair/eye/moe traits)
        for mp in cfg.get("moegirl") or []:
            rec = moegirl_cache.get(mp)
            if isinstance(rec, dict) and rec.get("character_name"):
                fam_entries.append(rec)

        # Collect Fandom English entries (rich Appearance sections)
        for rec in fandom_cache.get(slug) or []:
            if isinstance(rec, dict) and rec.get("character_name"):
                fam_entries.append(rec)

        # Collect zhwiki & enwiki summaries / character roster extracts
        zw_t = cfg.get("zhwiki") or ""
        if zw_t and isinstance(zhwiki_cache.get(zw_t), dict) and not zhwiki_cache[zw_t].get("missing"):
            fam_entries.append(zhwiki_cache[zw_t])
        ew_t = cfg.get("enwiki") or ""
        if ew_t and isinstance(enwiki_cache.get(ew_t), dict) and not enwiki_cache[ew_t].get("missing"):
            fam_entries.append(enwiki_cache[ew_t])

        if fam_entries:
            families_covered += 1
        else:
            uncovered_slugs.append(slug)

        fam_dossiers: list[dict[str, Any]] = []
        for entry in fam_entries:
            source_counts[entry["source"]] += 1
            dossier_rec = {
                "family_slug": slug,
                "franchise_display_name": disp_name,
                "character_name": entry["character_name"],
                "source": entry["source"],
                "language": entry["language"],
                "source_url": entry.get("source_url") or "",
                "portrait_url": entry.get("portrait_url") or "",
                "infobox": entry.get("infobox") or {},
                "visual_appearance": _sanitize_wiki_prose(entry.get("visual_appearance") or ""),
                "overview": _sanitize_wiki_prose(entry.get("overview") or ""),
                "personality_or_abilities": _sanitize_wiki_prose(entry.get("personality_or_abilities") or ""),
                "visual_anchors_extracted": entry.get("visual_anchors_extracted") or [],
                "fetched_at": now_iso,
            }
            all_dossiers.append(dossier_rec)
            fam_dossiers.append(dossier_rec)

            # Build clean CPT natural-language encyclopedia document (zero markup/ChatML/<think>)
            prose_parts = [f"{disp_name} — {entry['character_name']}"]
            if dossier_rec["visual_anchors_extracted"]:
                prose_parts.append("Visual traits: " + "; ".join(dossier_rec["visual_anchors_extracted"]) + ".")
            if dossier_rec["overview"]:
                prose_parts.append(dossier_rec["overview"])
            if dossier_rec["visual_appearance"]:
                prose_parts.append("Appearance details: " + dossier_rec["visual_appearance"])
            doc_text = "\n".join(prose_parts).strip()
            doc_id = "wiki_char_" + hashlib.sha256(f"{slug}|{entry['source']}|{entry['character_name']}".encode("utf-8")).hexdigest()[:12]
            cpt_docs.append(
                {
                    "doc_id": doc_id,
                    "doc_family_id": f"tpl_fam_{slug}",
                    "family_slug": slug,
                    "character_name": entry["character_name"],
                    "source": entry["source"],
                    "language": entry["language"],
                    "is_synthetic_image": False,
                    "text": doc_text,
                }
            )

        # Write per-family `character_dossier.md`
        md_path = templete_dir / slug / "character_dossier.md"
        _write_text(md_path, _render_family_dossier_md(slug, disp_name, fam_dossiers))

    _write_jsonl(dossiers_jsonl, all_dossiers)
    _write_jsonl(cpt_prose_jsonl, cpt_docs)

    summary = {
        "schema": "assert_character_wiki_summary_v1",
        "generated_at": now_iso,
        "total_b2_families": len(b2_fams),
        "families_covered": families_covered,
        "coverage_rate": round(families_covered / max(1, len(b2_fams)), 4),
        "total_character_dossiers": len(all_dossiers),
        "dossiers_with_appearance_section": sum(1 for d in all_dossiers if d["visual_appearance"]),
        "dossiers_with_visual_infobox": sum(1 for d in all_dossiers if d["visual_anchors_extracted"]),
        "source_counts": dict(source_counts.most_common()),
        "uncovered_slugs": uncovered_slugs,
        "fandom_errors": cache.get("fandom_errors") or {},
    }
    _write_json(summary_json, summary)
    return summary


def _render_family_dossier_md(slug: str, disp_name: str, entries: list[dict[str, Any]]) -> str:
    lines = [
        f"# {disp_name} (`{slug}`) · 多源 Wiki 角色视觉与设定档案",
        "",
        f"- **收录条目数**: `{len(entries)}`（来源优先级：萌娘百科中文 / Fandom 英文外貌细节 / 维基百科双语桥接）",
        "",
    ]
    if not entries:
        lines.append("> 暂无公开 Fandom / 萌娘百科 / 维基百科角色页面匹配，需从版权方官网或商品台账补充。")
        return "\n".join(lines) + "\n"

    src_lbl = {
        "moegirl": "萌娘百科 (zh)",
        "fandom": "Fandom Wiki (en)",
        "zhwiki": "中文维基百科",
        "enwiki": "English Wikipedia",
    }
    for e in entries:
        lines.append(f"## {e['character_name']} · `{src_lbl.get(e['source'], e['source'])}`")
        if e.get("source_url"):
            lines.append(f"- **来源**: {e['source_url']}")
        if e.get("visual_anchors_extracted"):
            lines.append("- **视觉关键特征**: " + " · ".join(e["visual_anchors_extracted"]))
        if e.get("infobox"):
            extra = [f"`{k}`={v}" for k, v in e["infobox"].items() if k in {"aliases", "gender", "occupation", "status"}]
            if extra:
                lines.append("- **设定元数据**: " + " · ".join(extra))
        if e.get("overview"):
            lines.extend(["", f"**简介**：{e['overview']}"])
        if e.get("visual_appearance"):
            lines.extend(["", f"**外貌与造型描述**：{e['visual_appearance']}"])
        if e.get("personality_or_abilities"):
            lines.extend(["", f"**补充特征/能力**：{e['personality_or_abilities']}"])
        lines.append("")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Crawl Fandom, Moegirlpedia, and Wikipedia APIs")
    parser.add_argument("--build", action="store_true", help="Build offline dossiers, CPT prose, and character_dossier.md")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of B2 families during --fetch")
    parser.add_argument("--skip-moegirl", action="store_true", help="Skip Moegirlpedia pages during --fetch")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.fetch and not args.build:
        args.build = True
    out: dict[str, Any] = {}
    if args.fetch:
        out["fetch"] = run_fetch(limit=args.limit, skip_moegirl=args.skip_moegirl)
    if args.build:
        out["build"] = run_build()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
