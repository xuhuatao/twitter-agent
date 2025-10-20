"""热门推文收集器 - 查找热门推文并存入数据库"""

import time
import tweepy
from datetime import datetime, timezone
from typing import List, Optional


class TrendingCollector:
    """收集热门推文的 Agent"""
    
    def __init__(self, agent_id: str, client: tweepy.Client, weaviate_client):
        self.agent_id = agent_id
        self.client = client
        self.weaviate_client = weaviate_client
    
    async def collect_trending_tweets(self, query: str = "crypto OR bitcoin OR ethereum", max_results: int = 10):
        """
        搜索热门推文并存入数据库
        
        Args:
            query: 搜索关键词
            max_results: 最多返回多少条推文
        """
        print(f"\n🔥 开始搜索热门推文: '{query}'")
        
        try:
            # 搜索最近的热门推文
            # tweet_fields 包含我们需要的所有字段
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'text'],
                expansions=['author_id'],
                user_fields=['public_metrics']
            )
            
            if not tweets.data:
                print("❌ 没有找到推文")
                return
            
            # 按点赞数排序
            sorted_tweets = sorted(
                tweets.data,
                key=lambda t: t.public_metrics['like_count'],
                reverse=True
            )
            
            # 获取第一条(最热门的)推文
            top_tweet = sorted_tweets[0]
            
            print(f"\n✅ 找到最热门的推文!")
            print(f"📝 内容: {top_tweet.text[:100]}...")
            print(f"❤️  点赞数: {top_tweet.public_metrics['like_count']}")
            print(f"🔄 转发数: {top_tweet.public_metrics['retweet_count']}")
            print(f"💬 回复数: {top_tweet.public_metrics['reply_count']}")
            
            # 获取作者信息
            author_id = top_tweet.author_id
            follower_count = 0
            
            # 从 includes 中获取用户信息
            if tweets.includes and 'users' in tweets.includes:
                for user in tweets.includes['users']:
                    if user.id == author_id:
                        follower_count = user.public_metrics['followers_count']
                        print(f"👥 作者粉丝数: {follower_count}")
                        break
            
            # 存入 Weaviate 数据库
            await self._save_to_database(top_tweet, follower_count)
            
            return top_tweet
            
        except tweepy.TweepyException as e:
            print(f"❌ Twitter API 错误: {e}")
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    async def _save_to_database(self, tweet, follower_count: int):
        """将推文保存到 Weaviate 数据库"""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        
        properties = {
            "tweet": tweet.text,
            "tweet_id": str(tweet.id),
            "agent_id": str(self.agent_id),
            "author_id": str(tweet.author_id),
            "like_count": tweet.public_metrics['like_count'],
            "follower_count": follower_count,
            "date": now,
        }
        
        try:
            self.weaviate_client.data_object.create(
                properties,
                "Tweets",
            )
            print(f"✅ 推文已成功存入数据库!")
        except Exception as e:
            print(f"❌ 存入数据库失败: {e}")
    
    async def collect_top_tweets_by_topic(self, topics: List[str], tweets_per_topic: int = 1):
        """
        按主题收集多个热门推文
        
        Args:
            topics: 主题列表，例如 ["crypto", "AI", "web3"]
            tweets_per_topic: 每个主题收集多少条推文
        """
        print(f"\n🔥 开始收集多个主题的热门推文")
        
        all_tweets = []
        for topic in topics:
            print(f"\n--- 主题: {topic} ---")
            query = f"{topic} -is:retweet lang:en"  # 排除转推，只要英文推文
            
            try:
                tweets = self.client.search_recent_tweets(
                    query=query,
                    max_results=10,
                    tweet_fields=['created_at', 'public_metrics', 'author_id', 'text'],
                    expansions=['author_id'],
                    user_fields=['public_metrics']
                )
                
                if tweets.data:
                    # 按点赞数排序
                    sorted_tweets = sorted(
                        tweets.data,
                        key=lambda t: t.public_metrics['like_count'],
                        reverse=True
                    )
                    
                    # 取前 N 条
                    top_tweets = sorted_tweets[:tweets_per_topic]
                    
                    for tweet in top_tweets:
                        print(f"  📝 {tweet.text[:80]}...")
                        print(f"  ❤️  {tweet.public_metrics['like_count']} 点赞")
                        
                        # 获取粉丝数
                        follower_count = 0
                        if tweets.includes and 'users' in tweets.includes:
                            for user in tweets.includes['users']:
                                if user.id == tweet.author_id:
                                    follower_count = user.public_metrics['followers_count']
                                    break
                        
                        # 保存到数据库
                        await self._save_to_database(tweet, follower_count)
                        all_tweets.append(tweet)
                        
                        # 避免速率限制
                        time.sleep(0.5)
                else:
                    print(f"  ❌ 主题 '{topic}' 没有找到推文")
                    
            except tweepy.TweepyException as e:
                print(f"  ❌ Twitter API 错误: {e}")
            except Exception as e:
                print(f"  ❌ 发生错误: {e}")
        
        print(f"\n✅ 总共收集了 {len(all_tweets)} 条热门推文!")
        return all_tweets

