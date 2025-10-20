#!/usr/bin/env python3
"""插入示例推文数据到 Weaviate 数据库"""

import weaviate
from datetime import datetime, timezone

# 连接到 Weaviate
client = weaviate.Client("http://localhost:8080")

# 示例热门推文数据
sample_tweets = [
    {
        "tweet": "Just launched our new AI model that can generate code 10x faster! 🚀 Check it out at example.com #AI #MachineLearning",
        "tweet_id": "1234567890001",
        "agent_id": "test_agent",
        "author_id": "9876543210",
        "like_count": 15234,
        "follower_count": 234567,
    },
    {
        "tweet": "Bitcoin just hit a new milestone! The future of finance is here 💰 #crypto #bitcoin #blockchain",
        "tweet_id": "1234567890002",
        "agent_id": "test_agent",
        "author_id": "9876543211",
        "like_count": 28456,
        "follower_count": 456789,
    },
    {
        "tweet": "Web3 is revolutionizing how we think about the internet. Here's what you need to know 🌐 #web3 #decentralization",
        "tweet_id": "1234567890003",
        "agent_id": "test_agent",
        "author_id": "9876543212",
        "like_count": 12890,
        "follower_count": 189234,
    },
    {
        "tweet": "New breakthrough in quantum computing! This changes everything for cryptography 🔐 #quantum #technology",
        "tweet_id": "1234567890004",
        "agent_id": "test_agent",
        "author_id": "9876543213",
        "like_count": 9876,
        "follower_count": 123456,
    },
    {
        "tweet": "NFT marketplace just processed $1B in transactions this month 📈 Amazing growth! #NFT #crypto #digitalart",
        "tweet_id": "1234567890005",
        "agent_id": "test_agent",
        "author_id": "9876543214",
        "like_count": 7654,
        "follower_count": 98765,
    },
]

print("🚀 开始插入示例推文数据...")
print("=" * 60)

now = datetime.now(timezone.utc).isoformat(timespec="seconds")

for i, tweet_data in enumerate(sample_tweets, 1):
    try:
        # 添加日期
        tweet_data["date"] = now
        
        # 插入到 Weaviate
        client.data_object.create(
            tweet_data,
            "Tweets",
        )
        
        print(f"\n✅ [{i}/{len(sample_tweets)}] 成功插入推文:")
        print(f"   📝 内容: {tweet_data['tweet'][:80]}...")
        print(f"   ❤️  点赞数: {tweet_data['like_count']}")
        print(f"   👥 粉丝数: {tweet_data['follower_count']}")
        
    except Exception as e:
        print(f"\n❌ [{i}/{len(sample_tweets)}] 插入失败: {e}")

print("\n" + "=" * 60)
print(f"✅ 完成! 成功插入 {len(sample_tweets)} 条示例推文")

# 验证数据
print("\n📊 验证数据库中的推文数量...")
try:
    result = client.query.aggregate("Tweets").with_meta_count().do()
    count = result['data']['Aggregate']['Tweets'][0]['meta']['count']
    print(f"✅ 数据库中共有 {count} 条推文")
except Exception as e:
    print(f"❌ 查询失败: {e}")

print("\n💡 提示: 现在运行 'python src/main.py --run-engine --test' 查看效果!")

