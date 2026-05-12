# 🤖 AI科技热点日报 - 配置指南

## 📋 功能说明

本工作流每天北京时间 **13:00** 自动运行，收集并总结最新的 AI 科技热点，以 Issue 形式推送到仓库。

### ✨ 主要特性

- ⏰ **定时触发**: 每天北京时间 13:00 自动运行
- 📰 **多源聚合**: RSS、Hacker News、GitHub Trending 等
- 📝 **Issue 推送**: 自动创建标签化 Issue
- 🚀 **零配置**: 开箱即用，无需额外密钥

---

## 🚀 快速开始

### 1. 启用工作流

工作流位于: `.github/workflows/ai-daily-digest.yml`

**首次使用步骤**:
1. 进入 GitHub 仓库的 **Actions** 标签页
2. 找到 **AI科技热点日报** 工作流
3. 点击 **Enable workflow** 启用

### 2. 手动测试

1. 在 Actions 页面选择 **AI科技热点日报**
2. 点击 **Run workflow** 手动触发
3. 等待 1-2 分钟，查看 Issues 页面检查结果

### 3. 查看日报

- 进入仓库 **Issues** 标签页
- 筛选标签 `daily-digest` 查看所有日报
- 每条日报包含当日收集的热点新闻链接

---

## ⚙️ 自定义配置

### 修改触发时间

编辑 `.github/workflows/ai-daily-digest.yml` 中的 `cron` 字段:

```yaml
schedule:
  - cron: '0 5 * * *'  # UTC 05:00 = 北京时间 13:00
```

**Cron 表达式说明**:
```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23, UTC)
│ │ ┌───────────── 日期 (1-31)
│ │ │ ┌───────────── 月份 (1-12)
│ │ │ │ ┌───────────── 星期 (0-6, 0=Sunday)
│ │ │ │ │
│ │ │ │ │
0 5 * * *
```

**常用时间对照**:
- `0 5 * * *` → 北京时间 13:00 (UTC+8)
- `0 13 * * *` → 北京时间 21:00
- `0 0 * * 1` → 每周一北京时间 08:00

### 添加更多 RSS 源

编辑 `.github/scripts/fetch_ai_news.py` 中的 `rss_feeds` 列表:

```python
rss_feeds = [
    ('https://feeds.example.com/ai', 'AI News'),
    ('https://feeds.example.com/tech', 'Tech News'),
    # 添加更多源...
]
```

### 修改 Issue 标签

编辑 `.github/workflows/ai-daily-digest.yml` 中的 `labels` 字段:

```yaml
labels: ['daily-digest', 'ai-tech', 'your-label']
```

---

## 📧 邮件集成 (可选)

如需将日报邮件发送到你的邮箱，按以下步骤操作:

### 1. 配置 Secrets

在仓库 **Settings > Secrets and variables > Actions** 中添加:

```
EMAIL_TO: your-email@example.com
EMAIL_FROM: your-email@example.com
EMAIL_PASSWORD: your-app-password  # 不是密码，是应用密码
```

### 2. 添加邮件发送步骤

在 `.github/workflows/ai-daily-digest.yml` 中的 `jobs` 下添加:

```yaml
      - name: 📧 发送邮件通知
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.EMAIL_FROM }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: '📰 AI科技热点日报 - ${{ github.run_id }}'
          to: ${{ secrets.EMAIL_TO }}
          from: ${{ secrets.EMAIL_FROM }}
          body: |
            日报已生成，请访问：
            ${{ github.server_url }}/${{ github.repository }}/issues
          attachments: .github/scripts/digest_output.md
```

---

## 🔗 钉钉/企业微信集成 (可选)

如需推送到钉钉或企业微信，编辑 `fetch_ai_news.py` 添加:

```python
def send_to_dingtalk(digest, webhook_url):
    """发送到钉钉"""
    import requests
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "AI科技热点日报",
            "text": digest
        }
    }
    requests.post(webhook_url, json=payload)

def send_to_wecom(digest, webhook_url):
    """发送到企业微信"""
    import requests
    payload = {
        "msgtype": "text",
        "text": {
            "content": digest
        }
    }
    requests.post(webhook_url, json=payload)
```

然后在 Secrets 中配置 Webhook URL，在脚本中调用即可。

---

## 🐛 故障排查

### 问题 1: 工作流没有自动运行

**原因**: GitHub Actions 默认处于禁用状态或仓库没有推送权限

**解决**:
1. 检查 Actions 标签页是否启用
2. 确保分支已推送到远程
3. 检查工作流文件是否在 `master` 或 `main` 分支上

### 问题 2: Issue 创建失败

**原因**: 可能缺少 `issues: write` 权限

**解决**:
确保工作流头部包含:
```yaml
permissions:
  issues: write
  contents: read
```

### 问题 3: RSS 源无法连接

**原因**: 网络超时或源地址失效

**解决**:
1. 检查 URL 是否正确
2. 增加超时时间 (`timeout=15`)
3. 更换可靠的 RSS 源

### 问题 4: 脚本执行错误

**查看日志**:
1. 进入 Actions 标签页
2. 点击对应的工作流运行记录
3. 查看 "fetch_ai_news" 步骤的详细输出

---

## 📊 工作流监控

### 查看历史运行记录

1. 进入 **Actions** 标签页
2. 选择 **AI科技热点日报** 工作流
3. 查看所有历史运行和状态

### 设置通知

在仓库 **Settings > Notifications** 中配置:
- ✅ 启用 "Actions required" 通知
- ✅ 启用 "Workflows" 相关通知

---

## 📝 常见用途

### 用途 1: 知识库建设
随时间积累，可将 Issues 作为 AI 热点知识库，便于检索和学习。

### 用途 2: 团队信息同步
配置邮件或 Slack 集成，与团队成员同步每日热点。

### 用途 3: 趋势分析
导出历史数据，分析 AI 领域发展趋势。

---

## 🔗 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cron 表达式参考](https://crontab.guru/)
- [RSS 源列表](https://www.feedspot.com/datasources/rss_feeds/)
- [GitHub API 文档](https://docs.github.com/en/rest)

---

## 💬 支持

有问题？可以:
1. 查看工作流运行日志
2. 检查脚本参数配置
3. 尝试手动运行工作流进行调试

**快乐阅读！** 📚✨
