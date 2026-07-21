# 中国新闻日报

GitHub Actions 在每个工作日北京时间 09:00 自动运行：收集过去 24 小时国际/境外公开媒体索引中的中国新闻、按政治/经济/科技/社会/外交分类、生成 UTF-8 HTML，并将摘要推送到企业微信群。

## 首次配置

在仓库的 **Settings → Secrets and variables → Actions** 新建 Repository secret：

- 名称：`WECHAT_WORK_WEBHOOK`
- 值：企业微信群机器人 Webhook 的完整地址

随后进入 **Actions**，选择“工作日中国新闻日报”，点击 **Run workflow** 测试。生成的网页在仓库 `docs/index.html` 中。

说明：日报严格只使用过去 24 小时可解析的公开媒体条目；数量按实际收录，绝不为凑数补写。它是编辑筛选的讨论度梗概，不是全网真实热度排行榜。
