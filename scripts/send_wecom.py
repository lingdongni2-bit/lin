#!/usr/bin/env python3
"""将日报摘要推送至企业微信群机器人。Webhook 只从环境变量读取。"""
import json, os, urllib.request

webhook = os.environ["WECHAT_WORK_WEBHOOK"]
owner_repo = os.environ["GITHUB_REPOSITORY"]
summary = json.load(open("docs/summary.json", encoding="utf-8"))
lines = [f"## 中国讨论度新闻梗概（{summary['count']} 条）"]
lines.append("过去 24 小时；不足不补；按政治、经济、科技、社会、文化、外交分类。")
lines.append("分类数量：" + "、".join(f"{k} {v}" for k, v in summary["by_category"].items()))
lines.append(f"报告：[打开完整 HTML 报告](https://github.com/{owner_repo}/blob/main/docs/index.html)")
payload = json.dumps({"msgtype": "markdown", "markdown": {"content": "\n".join(lines)}}).encode()
request = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(request, timeout=20) as response:
    result = json.loads(response.read())
if result.get("errcode") != 0:
    raise SystemExit(f"WeCom push failed: {result.get('errmsg', 'unknown error')}")
