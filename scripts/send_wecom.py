"""将日报以手机可直接阅读的企业微信 Markdown 消息发送。"""
import html, json, os, re, urllib.request

webhook = os.environ["WECHAT_WORK_WEBHOOK"]
summary = json.load(open("docs/summary.json", encoding="utf-8"))
page = open("docs/index.html", encoding="utf-8").read()

def send(content):
    body = json.dumps({"msgtype": "markdown", "markdown": {"content": content}}).encode()
    request = urllib.request.Request(webhook, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read())
    if result.get("errcode") != 0:
        raise SystemExit(result.get("errmsg", "WeCom push failed"))

send("## 中国讨论度新闻梗概（%s 条）\n过去 24 小时；不足不补。" % summary["count"])
text = re.sub(r"<a href=\"([^\"]+)\">(.*?)</a>", r"[\2](\1)", page)
text = re.sub(r"</?(?:section|article|body|html)[^>]*>", "\n", text)
text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", text)
text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", text)
text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n", text)
text = re.sub(r"<[^>]+>", "", text)
text = html.unescape(text)
text = re.sub(r"\n{3,}", "\n\n", text).strip()
chunks, current = [], ""
for line in text.splitlines():
    candidate = current + line + "\n"
    if len(candidate.encode()) > 3500 and current:
        chunks.append(current)
        current = line + "\n"
    else:
        current = candidate
if current:
    chunks.append(current)
for chunk in chunks:
    send(chunk)
