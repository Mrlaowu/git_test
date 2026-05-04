# AI 科技热点日报系统

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?style=flat-square)](https://github.com/Mrlaowu/git_test/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> 🤖 一个完全自动化的 AI 科技热点日报系统，利用 GitHub Actions 每天北京时间 13:00 自动收集、整理并推送最新的 AI 科技热点。

## ✨ 主要特性

- ⏰ **定时触发**: 每天北京时间 13:00 自动运行（如 OpenClaw 定时任务）
- 📰 **多源聚合**: 从 RSS、Hacker News、GitHub Trending 等多个权威来源收集信息
- 🤖 **智能过滤**: 自动识别 AI 相关内容，去除无关信息
- 📝 **Issue 推送**: 自动创建标签化 GitHub Issue，便于检索和归档
- 📊 **可视化仪表板**: 实时展示日报统计和历史记录
- 🔌 **易于集成**: 支持邮件、钉钉、企业微信等多种推送渠道
- 🚀 **零配置**: 开箱即用，无需复杂的环境配置

## 📁 项目结构

```
.
├── .github/
│   ├── workflows/
│   │   └── ai-daily-digest.yml          # 工作流配置
│   └── scripts/
│       ├── fetch_ai_news.py             # 数据采集脚本
│       └── README.md                    # 详细配置文档
├── docs/
│   └── index.html                       # 可视化仪表板
└── README.md                            # 项目说明（本文件）
```

## 🚀 快速开始

### 1️⃣ 启用工作流

工作流已在 `.github/workflows/ai-daily-digest.yml` 中配置，创建 Pull Request 合并到主分支后即可启用。

### 2️⃣ 手动测试

进入 GitHub 仓库的 **Actions** 标签页：

1. 选择 **📰 AI科技热点日报** 工作流
2. 点击 **Run workflow** 按钮
3. 等待 1-2 分钟后查看 Issues 页面

### 3️⃣ 查看日报

访问仓库的 **Issues** 标签页，过滤标签 `daily-digest` 即可查看所有日报。

### 4️⃣ 可视化仪表板

启用 GitHub Pages 后，可访问 `https://Mrlaowu.github.io/git_test/` 查看实时仪表板。

## ⚙️ 配置说明

### 修改触发时间

编辑 `.github/workflows/ai-daily-digest.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 5 * * *'  # 北京时间 13:00 (UTC 05:00)
```

#### Cron 表达式快速参考

| 需求 | Cron 表达式 | 说明 |
|------|-----------|------|
| 每天 13:00 | `0 5 * * *` | 北京时间中午 |
| 每天 08:00 | `0 0 * * *` | 北京时间早上 |
| 每天 21:00 | `0 13 * * *` | 北京时间晚上 |
| 每周一 08:00 | `0 0 * * 1` | 周一早上 |
| 每月 1 日 | `0 5 1 * *` | 月初 |

参考: [Cron 表达式生成器](https://crontab.guru/)

### 添加更多 RSS 源

编辑 `.github/scripts/fetch_ai_news.py` 中的 `RSS_FEEDS` 列表：

```python
RSS_FEEDS = [
    ('https://feeds.arstechnica.com/arstechnica/index', 'Ars Technica'),
    ('https://feeds.theverge.com/rss/index.xml', 'The Verge'),
    # 添加你的 RSS 源
    ('https://example.com/feed.xml', 'Your Source'),
]
```

### 修改关键词过滤

编辑 `.github/scripts/fetch_ai_news.py` 中的 `AI_KEYWORDS` 列表：

```python
AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 
    'LLM', 'ChatGPT', 'Claude',
    # 添加你关心的关键词
]
```

## 📧 邮件推送集成

### 配置 Gmail

1. 生成 [Google App Password](https://support.google.com/accounts/answer/185833)
2. 在仓库 **Settings > Secrets and variables > Actions** 中添加：
   ```
   EMAIL_FROM: your-email@gmail.com
   EMAIL_PASSWORD: your-app-password
   EMAIL_TO: recipient@example.com
   ```

3. 编辑 `.github/workflows/ai-daily-digest.yml`，在 `jobs.ai-digest.steps` 中添加：
   ```yaml
   - name: 📧 发送邮件通知
     uses: dawidd6/action-send-mail@v3
     with:
       server_address: smtp.gmail.com
       server_port: 465
       username: ${{ secrets.EMAIL_FROM }}
       password: ${{ secrets.EMAIL_PASSWORD }}
       subject: '📰 AI科技热点日报'
       to: ${{ secrets.EMAIL_TO }}
       from: ${{ secrets.EMAIL_FROM }}
       body: |
         今日日报已生成！
         访问: https://github.com/Mrlaowu/git_test/issues
   ```

## 🔗 钉钉机器人集成

1. [创建钉钉机器人](https://open.dingtalk.com/)，获取 Webhook URL
2. 在 Secrets 中添加 `DINGTALK_WEBHOOK`
3. 在 `fetch_ai_news.py` 中调用：
   ```python
   import requests
   
   def send_to_dingtalk(digest, webhook_url):
       payload = {
           "msgtype": "markdown",
           "markdown": {
               "title": "AI科技热点日报",
               "text": digest
           }
       }
       requests.post(webhook_url, json=payload)
   ```

## 🐛 故障排查

### 问题 1: 工作流没有自动运行

**原因**: 工作流未启用或分支配置不正确

**解决**:
- 确保工作流文件在默认分支上
- 进入 Actions 页面检查是否有错误提示
- 点击 "Enable workflow" 手动启用

### 问题 2: RSS 源连接失败

**原因**: 网络问题或源地址变更

**解决**:
- 检查 URL 是否正确
- 尝试手动访问 RSS 源 URL
- 更换备用源或增加重试机制

### 问题 3: Issue 创建失败

**原因**: 权限不足或 Token 过期

**解决**:
```yaml
permissions:
  issues: write
  contents: read
```

### 查看详细日志

1. 进入 GitHub 仓库 **Actions** 标签页
2. 点击对应的工作流运行记录
3. 展开 "🤖 获取 AI 科技热点" 步骤查看详细输出

## 📊 监控和维护

### 查看工作流历史

- 进入 **Actions** > **📰 AI科技热点日报**
- 查看所有历史运行记录和执行时间

### 设置通知

在仓库 **Settings > Notifications** 中：
- ✅ 启用 "Actions required" 通知
- ✅ 选择通知频率

### 分析热点数据

所有 Issues 均可导出为 CSV 格式，便于数据分析：
```bash
# 使用 GitHub CLI
gh issue list --label daily-digest --json title,body,createdAt --limit 100
```

## 🎯 高级用途

### 1. 知识库建设

随时间积累，历史日报成为 AI 领域的完整知识库，支持全文检索。

### 2. 团队信息同步

配置邮件或 Slack 集成，与团队成员每日同步 AI 动态。

### 3. 趋势分析

定期导出历史数据，分析 AI 领域的发展趋势和热点演变。

### 4. 投资决策

融合日报数据和其他信息源，支持投资和战略决策。

## 📝 更新日志

### v1.0 (2026-05-04)

- ✅ 完成工作流配置
- ✅ 实现多源数据聚合
- ✅ 创建 GitHub Issue 推送
- ✅ 开发可视化仪表板
- ✅ 编写完整文档

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 💬 常见问题

**Q: 为什么选择 GitHub Actions?**

A: GitHub Actions 是 GitHub 原生工具，完全免费，无需额外服务器或依赖，最适合小型自动化任务。

**Q: 数据会保留多久?**

A: Issue 会永久保存在仓库中，可作为历史记录查询。

**Q: 支持离线使用吗?**

A: 支持。可以定期导出 Issues 数据到本地文件进行离线分析。

**Q: 如何修改推送时间?**

A: 编辑 `.github/workflows/ai-daily-digest.yml` 中的 `cron` 表达式即可。

## 🔗 相关资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [Python feedparser 库](https://feedparser.readthedocs.io/)
- [Cron 表达式参考](https://crontab.guru/)

---

**快乐使用！** 🚀✨

有问题或建议? 在 [Issues](https://github.com/Mrlaowu/git_test/issues) 中提出！
