"""Twitter-Agent Entry Point"""

import os
import json
import time
import weaviate
import yaml
import pdb
import asyncio
from functools import wraps

import click

from langchain.llms import OpenAI
from langchain.vectorstores import Weaviate
from langchain.embeddings.openai import OpenAIEmbeddings


from twitter_client import fetch_clients
from executor.executor import TwitterExecutor
from collector.collector import TwitterCollector
from collector.trainer import AgentTrainer
from collector.trending_collector import TrendingCollector
from strategy.strategy import TwitterStrategy

# load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USER_ID = os.getenv("USER_ID", "")


def async_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--run-engine", default=False, is_flag=True, help="Run the engine."  # Same as above
)
@click.option(
    "--test", default=False, is_flag=True, help="Test the engine."  # Same as above
)
@click.option(
    "--ingest", default=False, is_flag=True, help="Ingest data into Weaviate."
)
@click.option(
    "--train", default=False, is_flag=True, help="Train Model"
)
@click.option(
    "--collect-trending", default=False, is_flag=True, help="Collect trending tweets"
)
@async_command
async def main(run_engine: bool, test: bool, ingest: bool, train: bool, collect_trending: bool):
    twitter_clients = fetch_clients()
    weaviate_client = weaviate.Client("http://localhost:8080")

    llm = OpenAI(temperature=0.9)
    embeddings = OpenAIEmbeddings()

    # spawn collector, strategy, and executor for each client
    agents = []
    for twitter_client in twitter_clients:
        client = twitter_client["client"]
        agent_id = twitter_client["agent_id"]
        agent_name = twitter_client["user_name"]

        vectorstore = Weaviate(weaviate_client, "Remilio", "content", embeddings)

        collector = TwitterCollector(agent_id, client, vectorstore, weaviate_client)
        strategy = TwitterStrategy(llm, twitter_client, vectorstore)
        executor = TwitterExecutor(agent_id, client)

        if ingest:
            await collector.ingest()

        if train:
            trainer = AgentTrainer(client, weaviate_client, OPENAI_API_KEY)
            await trainer.run()
        
        if collect_trending:
            trending_collector = TrendingCollector(agent_id, client, weaviate_client)
            print(f"\n🔥 收集 {agent_name} 的热门推文")
            # 收集多个主题的热门推文
            topics = ["AI", "crypto", "web3", "blockchain", "technology"]
            await trending_collector.collect_top_tweets_by_topic(topics, tweets_per_topic=1)

        agents.append((collector, strategy, executor, agent_name, agent_id, client, weaviate_client))

    # run
    if run_engine:
        await asyncio.gather(
            *(
                run(collector, strategy, executor, agent_name, agent_id, test, client, weaviate_client)
                for collector, strategy, executor, agent_name, agent_id, client, weaviate_client in agents
            )
        )


async def collect_tweets_from_timeline(client, agent_id, agent_name, weaviate_client):
    """从 Twitter 时间线收集推文的辅助函数"""
    print(f"\033[96m\033[1m\n*****{agent_name} 推文收集 Agent 🌟 *****\n\033[0m\033[0m")
    print(f"📡 正在从时间线获取最新推文...")
    
    try:
        from datetime import datetime, timezone
        
        # 获取时间线推文
        timeline = client.get_home_timeline(
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'author_id', 'text']
        )
        
        if timeline.data:
            print(f"✅ 找到 {len(timeline.data)} 条新推文")
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            
            saved_count = 0
            for tweet in timeline.data:
                properties = {
                    "tweet": tweet.text,
                    "tweet_id": str(tweet.id),
                    "agent_id": str(agent_id),
                    "author_id": str(tweet.author_id),
                    "like_count": tweet.public_metrics['like_count'],
                    "follower_count": 0,
                    "date": now,
                }
                
                try:
                    weaviate_client.data_object.create(properties, "Tweets")
                    saved_count += 1
                except Exception as e:
                    # 可能是重复推文,静默忽略
                    pass
            
            print(f"✅ 成功存入 {saved_count} 条推文到数据库")
        else:
            print("ℹ️  时间线暂时没有新推文")
            
    except Exception as e:
        print(f"⚠️  收集推文时出错: {e}")
        print("ℹ️  将继续使用数据库中的现有推文")


async def run(collector, strategy, executor, agent_name, agent_id, test, client=None, weaviate_client=None):
    print(f"\033[92m\033[1m\n*****Running {agent_name} Engine 🚒 *****\n\033[0m\033[0m")

    while True:
        try:
            # Step 0: 先收集最新推文 (新增!)
            if client and weaviate_client:
                await collect_tweets_from_timeline(client, agent_id, agent_name, weaviate_client)
            
            # Step 1: Run Collector (从数据库读取推文)
            print(
                f"\033[92m\033[1m\n*****Running {agent_name} Collector 🔎 *****\n\033[0m\033[0m"
            )
            twitterstate = await collector.run()

            # Step 2: Pass timeline tweets to Strategy
            print(
                f"\033[92m\033[1m\n*****Running {agent_name} Strategy 🐲*****\n\033[0m\033[0m"
            )
            actions = strategy.run(twitterstate)

            # Step 4: Pass actions to Executor
            print(
                f"\033[92m\033[1m\n*****Running {agent_name} Executor🌠 *****\n\033[0m\033[0m"
            )
            if test:
                pass
            else:
                executor.execute_actions(tweet_actions=actions)

            # Sleep for an hour (3600 seconds) before the next iteration
            print("Sleeping for an hour💤 💤💤")
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Error in run: {e}")


if __name__ == "__main__":
    asyncio.run(main())
