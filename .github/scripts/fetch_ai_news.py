#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI科技热点日报采集脚本
功能: 从多个来源收集并汇总最新的 AI 科技热点
输出: digest_output.md 文件，用于创建 GitHub Issue
"""

import os
import sys
import json
import time
import requests
import feedparser
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from urllib.parse import urljoin, quote

# ==================== 配置信息 ====================

# RSS 源列表 (可自行扩展)
RSS_FEEDS = [
    ('https://feeds.arstechnica.com/arstechnica/index', 'Ars Technica'),
    ('https://feeds.theverge.com/rss/index.xml', 'The Verge'),
    ('https://news.ycombinator.com/rss', 'Hacker News'),
    ('https://feeds.bloomberg.com/markets/news.rss', 'Bloomberg'),
]

# 搜索关键词 (用于过滤相关内容)
AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'LLM', 'GPT', 'transformer', 'ChatGPT', 'Claude',
    'algorithm', 'data science', 'NLP', 'computer vision', 'automation',
    'robotics', '人工智能', '机器学习', '深度学习', '算法', '神经网络'
]

REQUEST_TIMEOUT = 10  # 请求超时时间 (秒)

# ==================== 核心函数 ====================

def get_beijing_time() -> datetime:
    """获取北京时间"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def fetch_rss_feed(url: str, timeout: int = REQUEST_TIMEOUT) -> List[Dict]:
    """
    获取 RSS 源内容
    
    Args:
        url: RSS 源 URL
        timeout: 请求超时时间
        
    Returns:
        文章列表
    """
    try:
        response = requests.get(url, timeout=timeout)
        feed = feedparser.parse(response.content)
        
        articles = []
        for entry in feed.entries[:10]:  # 每个源取前10条
            article = {
                'title': entry.get('title', 'N/A'),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'source': feed.feed.get('title', 'Unknown'),
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"⚠️  获取 RSS 源失败: {url}")
        print(f"   错误: {str(e)}")
        return []

def fetch_hacker_news() -> List[Dict]:
    """
    从 Hacker News API 获取热门话题
    """
    try:
        # 获取热门故事 IDs
        response = requests.get(
            'https://hacker-news.firebaseio.com/v0/topstories.json',
            timeout=REQUEST_TIMEOUT
        )
        story_ids = response.json()[:15]  # 改为获取 15 个候选
        
        articles = []
        for story_id in story_ids[:10]:  # 详细获取前10条
            try:
                story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                story = requests.get(story_url, timeout=5).json()  # ✅ 减少单个请求超时
                
                if story and 'title' in story:
                    # 检查是否包含 AI 相关关键词
                    title_lower = story['title'].lower()
                    if any(keyword.lower() in title_lower for keyword in AI_KEYWORDS):
                        article = {
                            'title': story['title'],
                            'link': story.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                            'published': '',
                            'source': 'Hacker News',
                        }
                        articles.append(article)
            except Exception as e:
                # ✅ 单个故事获取失败不影响整体
                print(f"   ⚠️  获取故事 {story_id} 失败: {str(e)}")
                continue
        
        return articles
    except Exception as e:
        print(f"⚠️  获取 Hacker News 失败: {str(e)}")
        return []

def fetch_github_trending() -> List[Dict]:
    """
    从 GitHub Trending 获取热门项目
    """
    try:
        headers = {}
        # ✅ 使用 GitHub Token 提高速率限制
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'token {token}'
        
        response = requests.get(
            'https://api.github.com/search/repositories',
            params={
                'q': 'language:python stars:>1000 created:>' + (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'sort': 'stars',
                'order': 'desc'
            },
            headers=headers,  # ✅ 添加认证头
            timeout=REQUEST_TIMEOUT
        )
        
        articles = []
        for repo in response.json().get('items', [])[:10]:
            # 简单过滤 AI 相关项目
            full_name = repo.get('full_name', '').lower()
            description = repo.get('description', '').lower() if repo.get('description') else ''
            
            if any(keyword.lower() in (full_name + ' ' + description) for keyword in ['ai', 'ml', 'llm', 'gpt', 'transformer', 'neural']):
                article = {
                    'title': f"[{repo['full_name']}] {repo.get('description', 'No description')}",
                    'link': repo['html_url'],
                    'published': repo.get('updated_at', ''),
                    'source': 'GitHub Trending',
                }
                articles.append(article)
        
        return articles
    except Exception as e:
        print(f"⚠️  获取 GitHub Trending 失败: {str(e)}")
        return []

def filter_by_keywords(articles: List[Dict], keywords: List[str]) -> List[Dict]:
    """
    按关键词过滤文章
    
    Args:
        articles: 文章列表
        keywords: 关键词列表
        
    Returns:
        过滤后的文章列表
    """
    filtered = []
    for article in articles:
        title_lower = article.get('title', '').lower()
        # 如果标题包含任何 AI 相关关键词
        if any(keyword.lower() in title_lower for keyword in keywords):
            filtered.append(article)
    
    return filtered

def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """
    去除重复文章 (基于 URL)
    """
    seen_urls = set()
    deduplicated = []
    
    for article in articles:
        url = article.get('link', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduplicated.append(article)
    
    return deduplicated

def generate_markdown_report(articles: List[Dict]) -> str:
    """
    生成 Markdown 格式的日报
    """
    current_time = get_beijing_time()
    date_str = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%H:%M:%S')
    
    # 按源分组
    articles_by_source = {}
    for article in articles:
        source = article.get('source', 'Unknown')
        if source not in articles_by_source:
            articles_by_source[source] = []
        articles_by_source[source].append(article)
    
    # 生成 Markdown
    md_content = f"""# 📰 AI科技热点日报

**生成时间**: {date_str} {time_str} (北京时间)

---

## 📊 本期统计

- **总热点数**: {len(articles)}
- **信息源**: {len(articles_by_source)}
- **更新频率**: 每日北京时间 13:00

---

## 🔥 今日热点

"""
    
    # 如果没有任何文章，显示特殊提示
    if not articles:
        md_content += """
> ⚠️ 今日未收集到 AI 相关热点，请稍后重试或检查数据源

"""
    else:
        # 按源组织内容
        for source in sorted(articles_by_source.keys()):
            articles_list = articles_by_source[source]
            md_content += f"\n### 📌 {source} ({len(articles_list)} 条)\n\n"
            
            for i, article in enumerate(articles_list, 1):
                title = article.get('title', 'N/A')
                link = article.get('link', '#')
                
                # 转义 Markdown 特殊字符
                title = title.replace('[', '\\[').replace(']', '\\]')
                
                if link and link != '#':
                    md_content += f"{i}. [{title}]({link})\n"
                else:
                    md_content += f"{i}. {title}\n"
    
    # 页脚
    md_content += f"""

---

## 💡 说明

- 本日报由 GitHub Actions 自动生成
- 信息来源包括：RSS 源、Hacker News、GitHub Trending
- 仅展示包含 AI 相关关键词的内容
- 建议点击链接访问原文获取完整信息

---

## 🔔 订阅方式

- 📧 邮件订阅 (配置 Secrets 后启用)
- 🔔 GitHub Issue 订阅 (默认已启用)
- 📱 Webhook 集成 (钉钉/企业微信，配置文档参见 README.md)

**生成于**: {date_str} {time_str}

"""
    
    return md_content

def main():
    """主函数"""
    try:
        print("=" * 50)
        print("🤖 开始采集 AI 科技热点...")
        print("=" * 50)
        
        beijing_time = get_beijing_time()
        print(f"⏰ 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_articles = []
        
        # 1. 从 RSS 源获取数据
        print("📡 获取 RSS 源数据...")
        for url, source_name in RSS_FEEDS:
            print(f"   → {source_name}...", end=' ')
            articles = fetch_rss_feed(url)
            all_articles.extend(articles)
            print(f"✓ {len(articles)} 条")
            time.sleep(0.5)  # 减少延迟
        
        # 2. 从 Hacker News 获取数据
        print("📡 获取 Hacker News 数据...", end=' ')
        articles = fetch_hacker_news()
        all_articles.extend(articles)
        print(f"✓ {len(articles)} 条")
        time.sleep(0.5)
        
        # 3. 从 GitHub Trending 获取数据
        print("📡 获取 GitHub Trending 数据...", end=' ')
        articles = fetch_github_trending()
        all_articles.extend(articles)
        print(f"✓ {len(articles)} 条")
        
        print(f"\n📊 初始数据: {len(all_articles)} 条\n")
        
        # 4. 过滤 AI 相关内容
        print("🔍 过滤 AI 相关内容...", end=' ')
        filtered_articles = filter_by_keywords(all_articles, AI_KEYWORDS)
        print(f"✓ {len(filtered_articles)} 条\n")
        
        # 5. 去除重复
        print("🧹 去除重复数据...", end=' ')
        deduplicated = deduplicate_articles(filtered_articles)
        print(f"✓ {len(deduplicated)} 条\n")
        
        # 6. 生成报告
        print("📝 生成 Markdown 报告...")
        report = generate_markdown_report(deduplicated)
        
        # 7. 保存输出文件
        output_path = '.github/scripts/digest_output.md'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 报告已保存到: {output_path}\n")
        
        # 8. 输出摘要
        print("=" * 50)
        print("✨ 采集完成！")
        print("=" * 50)
        print(f"📈 最终收集 {len(deduplicated)} 条 AI 热点")
        print(f"📝 报告将以 GitHub Issue 形式发布")
        print()
        
    except Exception as e:
        # ✅ 全局异常处理
        print(f"\n❌ 采集失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 生成错误报告
        error_report = f"""# ❌ AI科技热点日报采集失败

**错误时间**: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}

**错误信息**: {str(e)}

## 🔍 调试建议

1. 检查网络连接是否正常
2. 检查 RSS 源是否可访问
3. 查看完整错误日志
4. 尝试手动运行脚本进行调试

## 📝 错误堆栈

```
{traceback.format_exc()}
```
"""
        output_path = '.github/scripts/digest_output.md'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(error_report)
        
        sys.exit(1)

if __name__ == '__main__':
    main()
