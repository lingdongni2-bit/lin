#!/usr/bin/env python3
"""将日报摘要和 HTML 附件推送至企业微信群机器人。"""
import json, os, urllib.parse, urllib.request, uuid

webhook = os.environ["WECHAT_WORK_WEBHOOK"]
summary = json.load(open("docs/summary.json", encoding="utf-8"))
lines = [f"## 中国讨论度新闻梗概（{summary['count']} 条）"]
lines.append("过去 24 小时；不足不补；按政治、经济、科技、社会、文化、外交分类。")
lines.append("分类数量：" + "、".join(f"{k} {v}" for k, v in summary["by_category"].items()))
lines.append("完整网页报告已作为 HTML 文件附在本消息后，可下载后用浏览器打开。")

def post_json(url, body):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())

key = urllib.parse.parse_qs(urllib.parse.urlparse(webhook).query)["key"][0]
boundary = "----CodexNews" + uuid.uuid4().hex
report = open("docs/index.html", "rb").read()
body = b"".join([
    f"--{boundary}\r\n".encode(),
    b'Content-Disposition: form-data; name="media"; filename="china-news-digest.html"\r\n',
    b"Content-Type: text/html\r\n\r\n", report, b"\r\n",
    f"--{boundary}--\r\n".encode(),
])
upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"
upload_request = urllib.request.Request(upload_url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
with urllib.request.urlopen(upload_request, timeout=30) as response:
    upload = json.loads(response.read())
if upload.get("errcode") != 0:
    raise SystemExit(f"WeCom upload failed: {upload.get('errmsg', 'unknown error')}")
for payload in ({"msgtype": "markdown", "markdown": {"content": "\n".join(lines)}}, {"msgtype": "file", "file": {"media_id": upload["media_id"]}}):
    result = post_json(webhook, payload)
    if result.get("errcode") != 0:
        raise SystemExit(f"WeCom push failed: {result.get('errmsg', 'unknown error')}")
