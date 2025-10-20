#!/usr/bin/env python3
"""收集热门推文的独立脚本"""

import os
import asyncio
import weaviate
from dotenv import load_dotenv

from src.twitter_client import fetch_clients
from src.collector.trending_collector import TrendingCollector

# 加载环境变量
load_dotenv()


async def main():
    """主函数"""
    print("🚀 热门推文收集器启动!")
    print("=" * 60)
    
    # 获取 Twitter 客户端
    twitter_clients = fetch_clients()
    
    # 连接 Weaviate
    weaviate_client = weaviate.Client("http://localhost:8080")
    
    # 使用第一个客户端
    if not twitter_clients:
        print("❌ 没有找到 Twitter 客户端配置")
        return
    
    twitter_client = twitter_clients[0]
    client = twitter_client["client"]
    agent_id = twitter_client["agent_id"]
    agent_name = twitter_client["user_name"]
    
    print(f"📱 使用账号: {agent_name}")
    print("=" * 60)
    
    # 创建热门推文收集器
    trending_collector = TrendingCollector(agent_id, client, weaviate_client)
    
    # 方式 1: 收集单个查询的最热门推文
    print("\n【方式 1】收集单个查询的最热门推文")
    await trending_collector.collect_trending_tweets(
        query="(crypto OR bitcoin OR ethereum) -is:retweet lang:en",
        max_results=10
    )
    
    # 方式 2: 按主题收集多个热门推文
    print("\n" + "=" * 60)
    print("\n【方式 2】按主题收集多个热门推文")
    topics = ["AI", "crypto", "web3", "blockchain", "NFT"]
    await trending_collector.collect_top_tweets_by_topic(
        topics=topics,
        tweets_per_topic=1  # 每个主题收集 1 条
    )
    
    print("\n" + "=" * 60)
    print("✅ 热门推文收集完成!")
    print("\n💡 提示: 现在运行 'python src/main.py --run-engine --test' 查看效果")


if __name__ == "__main__":
    asyncio.run(main())

