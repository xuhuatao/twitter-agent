# 热门推文收集器 (Trending Collector)

## 功能说明

这个新的 Agent 可以自动搜索和收集 Twitter 上的热门推文，并将它们存入 Weaviate 数据库中，供主 Agent 使用。

## 使用方法

### 方式 1: 使用独立脚本

运行独立的收集脚本:

```bash
python collect_trending.py
```

这个脚本会:
1. 搜索单个查询的最热门推文（加密货币相关）
2. 按多个主题收集热门推文（AI、crypto、web3、blockchain、NFT）

### 方式 2: 集成到主程序

在主程序中使用 `--collect-trending` 选项:

```bash
python src/main.py --collect-trending
```

这会为每个配置的 Twitter 账号收集热门推文。

### 方式 3: 与其他功能组合使用

```bash
# 先收集热门推文，然后运行引擎
python src/main.py --collect-trending --run-engine --test
```

## 功能特性

### 1. 单个查询收集

收集特定查询的最热门推文:

```python
await trending_collector.collect_trending_tweets(
    query="(crypto OR bitcoin OR ethereum) -is:retweet lang:en",
    max_results=10
)
```

- 自动按点赞数排序
- 只保存最热门的一条
- 包含推文的所有指标（点赞、转发、回复数）

### 2. 多主题收集

按主题批量收集热门推文:

```python
topics = ["AI", "crypto", "web3", "blockchain", "NFT"]
await trending_collector.collect_top_tweets_by_topic(
    topics=topics,
    tweets_per_topic=1
)
```

- 每个主题收集指定数量的热门推文
- 自动排除转推
- 只收集英文推文

## 数据存储

收集的推文会存储到 Weaviate 数据库的 `Tweets` 类中，包含以下字段:

- `tweet`: 推文内容
- `tweet_id`: 推文 ID
- `agent_id`: 收集者的 Agent ID
- `author_id`: 作者 ID
- `like_count`: 点赞数
- `follower_count`: 作者粉丝数
- `date`: 收集时间

## 自定义搜索

你可以修改搜索查询来收集不同类型的热门推文:

```python
# 科技相关
query = "(technology OR innovation OR startup) -is:retweet lang:en"

# 娱乐相关
query = "(movie OR music OR entertainment) -is:retweet lang:en"

# 新闻相关
query = "(breaking OR news OR update) -is:retweet lang:en"
```

## 查询语法

Twitter 搜索支持以下语法:

- `OR`: 或运算符
- `-is:retweet`: 排除转推
- `lang:en`: 只要英文推文
- `from:username`: 来自特定用户
- `min_faves:100`: 至少 100 个点赞
- `min_retweets:50`: 至少 50 次转发

## 注意事项

1. **API 速率限制**: Twitter API 有速率限制，脚本会自动添加延迟
2. **需要 Twitter API 访问权限**: 确保你的 API 密钥有搜索权限
3. **数据库连接**: 确保 Weaviate 服务正在运行 (`docker-compose up -d`)

## 示例输出

```
🚀 热门推文收集器启动!
============================================================
📱 使用账号: test
============================================================

【方式 1】收集单个查询的最热门推文

🔥 开始搜索热门推文: '(crypto OR bitcoin OR ethereum) -is:retweet lang:en'

✅ 找到最热门的推文!
📝 内容: Bitcoin just hit a new all-time high! 🚀...
❤️  点赞数: 15234
🔄 转发数: 3421
💬 回复数: 892
👥 作者粉丝数: 234567
✅ 推文已成功存入数据库!

============================================================

【方式 2】按主题收集多个热门推文

🔥 开始收集多个主题的热门推文

--- 主题: AI ---
  📝 New breakthrough in AI research shows...
  ❤️  8234 点赞
✅ 推文已成功存入数据库!

--- 主题: crypto ---
  📝 DeFi protocol launches new feature...
  ❤️  5621 点赞
✅ 推文已成功存入数据库!

✅ 总共收集了 6 条热门推文!
```

## 故障排除

### 问题: "没有找到推文"

- 尝试使用更通用的搜索词
- 检查 API 密钥是否有效
- 确认网络连接正常

### 问题: "Twitter API 错误"

- 检查是否超过了速率限制
- 确认 API 密钥有搜索权限
- 查看 Twitter Developer Portal 的使用情况

### 问题: "存入数据库失败"

- 确保 Weaviate 服务正在运行
- 检查 schema 是否已创建 (`python setup_schema.py`)
- 查看 Weaviate 日志: `docker-compose logs weaviate`

