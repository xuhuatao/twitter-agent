#!/usr/bin/env python3
"""从 Twitter 获取真实推文数据的脚本"""

import os
import asyncio
import weaviate
from dotenv import load_dotenv

from src.twitter_client import fetch_clients
from src.collector.trending_collector import TrendingCollector

# 加载环境变量
load_dotenv()


async def collect_from_timeline():
    """从时间线收集推文"""
    print("🚀 从 Twitter 时间线收集推文")
    print("=" * 60)
    
    # 获取 Twitter 客户端
    twitter_clients = fetch_clients()
    
    if not twitter_clients:
        print("❌ 没有找到 Twitter 客户端配置")
        return
    
    # 连接 Weaviate
    weaviate_client = weaviate.Client("http://localhost:8080")
    
    twitter_client = twitter_clients[0]
    client = twitter_client["client"]
    agent_id = twitter_client["agent_id"]
    agent_name = twitter_client["user_name"]
    
    print(f"📱 使用账号: {agent_name}")
    print("=" * 60)
    
    try:
        # 方法 1: 获取时间线推文
        print("\n【方法 1】获取主页时间线推文")
        print("正在获取最新推文...")
        
        timeline = client.get_home_timeline(
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'author_id', 'text']
        )
        
        if timeline.data:
            print(f"✅ 找到 {len(timeline.data)} 条推文")
            
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            
            for i, tweet in enumerate(timeline.data, 1):
                print(f"\n📝 [{i}] {tweet.text[:80]}...")
                print(f"   ❤️  {tweet.public_metrics['like_count']} 点赞")
                
                # 存入数据库
                properties = {
                    "tweet": tweet.text,
                    "tweet_id": str(tweet.id),
                    "agent_id": str(agent_id),
                    "author_id": str(tweet.author_id),
                    "like_count": tweet.public_metrics['like_count'],
                    "follower_count": 0,  # 时间线不包含粉丝数
                    "date": now,
                }
                
                try:
                    weaviate_client.data_object.create(properties, "Tweets")
                    print(f"   ✅ 已存入数据库")
                except Exception as e:
                    print(f"   ❌ 存入失败: {e}")
        else:
            print("❌ 时间线为空")
            
    except Exception as e:
        print(f"❌ 获取时间线失败: {e}")
        print("\n💡 提示: 这可能是因为:")
        print("   1. API 密钥权限不足")
        print("   2. 达到速率限制")
        print("   3. 账号没有关注任何人")
    
    # 方法 2: 获取用户自己的推文
    try:
        print("\n" + "=" * 60)
        print("\n【方法 2】获取用户自己的推文")
        print("正在获取...")
        
        user_tweets = client.get_users_tweets(
            id=agent_id,
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'text']
        )
        
        if user_tweets.data:
            print(f"✅ 找到 {len(user_tweets.data)} 条推文")
            
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            
            for i, tweet in enumerate(user_tweets.data, 1):
                print(f"\n📝 [{i}] {tweet.text[:80]}...")
                print(f"   ❤️  {tweet.public_metrics['like_count']} 点赞")
                
                # 存入数据库
                properties = {
                    "tweet": tweet.text,
                    "tweet_id": str(tweet.id),
                    "agent_id": str(agent_id),
                    "author_id": str(agent_id),
                    "like_count": tweet.public_metrics['like_count'],
                    "follower_count": 0,
                    "date": now,
                }
                
                try:
                    weaviate_client.data_object.create(properties, "Tweets")
                    print(f"   ✅ 已存入数据库")
                except Exception as e:
                    print(f"   ❌ 存入失败: {e}")
        else:
            print("❌ 没有找到推文")
            
    except Exception as e:
        print(f"❌ 获取用户推文失败: {e}")
    
    print("\n" + "=" * 60)
    
    # 验证数据
    print("\n📊 验证数据库中的推文数量...")
    try:
        result = weaviate_client.query.aggregate("Tweets").with_meta_count().do()
        count = result['data']['Aggregate']['Tweets'][0]['meta']['count']
        print(f"✅ 数据库中共有 {count} 条推文")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    print("\n✅ 完成!")
    print("💡 提示: 运行 'python src/main.py --run-engine --test' 查看效果")


async def collect_from_search():
    """使用搜索 API 收集推文"""
    print("🚀 使用搜索 API 收集热门推文")
    print("=" * 60)
    
    # 获取 Twitter 客户端
    twitter_clients = fetch_clients()
    
    if not twitter_clients:
        print("❌ 没有找到 Twitter 客户端配置")
        return
    
    # 连接 Weaviate
    weaviate_client = weaviate.Client("http://localhost:8080")
    
    twitter_client = twitter_clients[0]
    client = twitter_client["client"]
    agent_id = twitter_client["agent_id"]
    agent_name = twitter_client["user_name"]
    
    print(f"📱 使用账号: {agent_name}")
    print("=" * 60)
    
    # 创建热门推文收集器
    trending_collector = TrendingCollector(agent_id, client, weaviate_client)
    
    # 使用简化搜索
    print("\n使用简化搜索模式(减少 API 调用)...")
    await trending_collector.collect_trending_tweets(
        query="python OR javascript OR AI -is:retweet",
        max_results=10,
        use_simple_search=True
    )
    
    print("\n✅ 完成!")


if __name__ == "__main__":
    import sys
    
    print("请选择收集方式:")
    print("1. 从时间线收集 (推荐)")
    print("2. 使用搜索 API (可能遇到速率限制)")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\n请输入选择 (1 或 2, 默认 1): ").strip() or "1"
    
    if choice == "2":
        asyncio.run(collect_from_search())
    else:
        asyncio.run(collect_from_timeline())

