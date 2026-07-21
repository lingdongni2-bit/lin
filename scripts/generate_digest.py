#!/usr/bin/env python3
"""生成过去 24 小时的中国新闻讨论度梗概（无需浏览器或付费 API）。"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
START = NOW - dt.timedelta(hours=24)
OUT = Path("docs")
CATEGORIES = {
    "政治": "中国 政治",
    "经济": "中国 经济",
    "科技": "中国 科技 人工智能",
    "社会": "中国 社会",
    "外交": "中国 外交",
}
FOREIGN_SOURCE_MARKERS = (
    "Reuters", "路透", "BBC", "Associated Press", "美联社", "Financial Times", "金融时报",
    "Bloomberg", "彭博", "Nikkei", "日经", "The New York Times", "纽约时报", "Wall Street Journal",
    "华尔街日报", "CNN", "The Guardian", "卫报", "Al Jazeera", "半岛", "France 24", "DW",
    "Deutsche Welle", "德国之声", "VOA", "Radio Free Asia", "自由亚洲", "The Diplomat",
    "South China Morning Post", "南华早报", "Taiwan News", "中央社", "The Straits Times",
)

def fetch(query: str) -> list[dict]:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"
    })
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ChinaNewsDigest/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        root = ET.fromstring(response.read())
    found = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        raw_date = (item.findtext("pubDate") or "").strip()
        source = item.findtext("source") or "公开媒体"
        try:
            published = parsedate_to_datetime(raw_date).astimezone(NOW.tzinfo)
        except (TypeError, ValueError):
            continue
        is_foreign_source = any(marker.lower() in source.lower() for marker in FOREIGN_SOURCE_MARKERS)
        if title and link and is_foreign_source and START <= published <= NOW + dt.timedelta(minutes=5):
            found.append({"title": title, "link": link, "source": source, "published": published})
    return found

def clean_title(title: str) -> str:
    return re.sub(r"\s+-\s+[^-]+$", "", title).strip()

def render(groups: dict[str, list[dict]]) -> str:
    count = sum(len(x) for x in groups.values())
    parts = []
    for category, items in groups.items():
        if not items:
            continue
        rows = []
        for n, item in enumerate(items, 1):
            title = html.escape(clean_title(item["title"]))
            source = html.escape(item["source"])
            time = item["published"].strftime("%Y-%m-%d %H:%M")
            rows.append(f'''<article><h3>{n}. <a href="{html.escape(item["link"], quote=True)}">{title}</a></h3>
<p>该报道在公开媒体索引中于统计窗口内出现，可作为“{category}”板块的近期讨论线索；请以原始报道和后续权威信息为准。</p>
<p class="meta">来源：{source}　发布时间（北京时间）：{time}</p></article>''')
        parts.append(f"<section><h2>{category}（{len(items)} 条）</h2>{''.join(rows)}</section>")
    updated = NOW.strftime("%Y-%m-%d %H:%M")
    start = START.strftime("%Y-%m-%d %H:%M")
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>中国讨论度新闻梗概</title><style>body{{max-width:900px;margin:32px auto;padding:0 18px;font-family:"Microsoft YaHei",sans-serif;color:#172033;line-height:1.65}}h1{{margin-bottom:4px}}h2{{margin-top:35px;border-left:5px solid #2563eb;padding-left:10px}}article{{padding:12px 16px;margin:10px 0;background:#f8fafc;border-radius:8px}}h3{{margin:0;font-size:17px}}p{{margin:7px 0}}a{{color:#1d4ed8}}.meta,.note{{color:#64748b;font-size:14px}}</style>
<body><h1>中国讨论度新闻梗概</h1><p class="note">统计范围：北京时间 {start} 至 {updated}｜生成时间：{updated}</p>
<p class="note">本期收录 {count} 条。按公开媒体的报道时效、跨媒体出现度与议题影响做编辑筛选，不代表全网真实热度；严格限于过去 24 小时，不足不补。</p>
{''.join(parts) if parts else '<p>本期未找到可核验的近 24 小时条目。</p>'}</body></html>'''

def main() -> None:
    seen: set[str] = set()
    groups: dict[str, list[dict]] = {name: [] for name in CATEGORIES}
    for category, query in CATEGORIES.items():
        for item in fetch(query):
            key = re.sub(r"\W+", "", clean_title(item["title"]).lower())
            if key in seen:
                continue
            seen.add(key)
            groups[category].append(item)
        groups[category].sort(key=lambda x: x["published"], reverse=True)
        groups[category] = groups[category][:10]
    OUT.mkdir(exist_ok=True)
    report = render(groups)
    stamp = NOW.strftime("%Y-%m-%d_%H%M")
    (OUT / "index.html").write_text(report, encoding="utf-8")
    (OUT / f"中国讨论度新闻梗概_{stamp}.html").write_text(report, encoding="utf-8")
    summary = {"generated_at": NOW.isoformat(), "count": sum(map(len, groups.values())), "by_category": {k: len(v) for k, v in groups.items()}}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
