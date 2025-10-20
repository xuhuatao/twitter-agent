#!/usr/bin/env python3
"""设置不使用 OpenAI 向量化的 Weaviate Schema"""

import weaviate
import json

# 连接到 Weaviate
client = weaviate.Client("http://localhost:8080")

# 先删除旧的 schema
try:
    client.schema.delete_class("Tweets")
    print("✅ 删除旧的 Tweets schema")
except:
    print("ℹ️  Tweets schema 不存在")

try:
    client.schema.delete_class("Remilio")
    print("✅ 删除旧的 Remilio schema")
except:
    print("ℹ️  Remilio schema 不存在")

# 定义不使用向量化的 Tweets schema
class_obj = {
    "class": "Tweets",
    "description": "Recent tweet from the timeline",
    "properties": [
        {
            "dataType": ["text"],
            "description": "tweet text",
            "name": "tweet",
        },
        {
            "dataType": ["text"],
            "description": "tweet id",
            "name": "tweet_id",
        },
        {
            "dataType": ["text"],
            "description": "agent id",
            "name": "agent_id",
        },
        {
            "dataType": ["text"],
            "description": "author id",
            "name": "author_id",
        },
        {
            "dataType": ["date"],
            "description": "date",
            "name": "date",
        },
        {
            "dataType": ["int"],
            "description": "follower count",
            "name": "follower_count",
        },
        {
            "dataType": ["int"],
            "description": "like count",
            "name": "like_count",
        },
    ],
    "vectorizer": "none",  # 不使用向量化
}

# 定义不使用向量化的 Remilio schema
remilio_class_obj = {
    "class": "Remilio",
    "description": "Remilio content for vector store",
    "properties": [
        {
            "dataType": ["text"],
            "description": "content",
            "name": "content",
        },
    ],
    "vectorizer": "none",  # 不使用向量化
}

try:
    # 创建 Tweets class
    client.schema.create_class(class_obj)
    print("✅ 创建新的 'Tweets' schema (无向量化)")
    
    # 创建 Remilio class
    client.schema.create_class(remilio_class_obj)
    print("✅ 创建新的 'Remilio' schema (无向量化)")
    
    # 获取并打印最终的 schema
    schema = client.schema.get()
    print("\n📋 当前 Weaviate Schema:")
    for cls in schema.get('classes', []):
        print(f"  - {cls['class']}: vectorizer = {cls.get('vectorizer', 'default')}")
    
except Exception as e:
    print(f"❌ 设置 schema 时出错: {e}")
    exit(1)

print("\n✅ Schema 设置完成!")
print("\n💡 提示: 现在可以运行 'python collect_trending.py' 来收集推文")

