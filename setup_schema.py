#!/usr/bin/env python3
"""Setup Weaviate Schema for Twitter Agent"""

import weaviate
import json

# Connect to Weaviate
client = weaviate.Client("http://localhost:8080")

# Define the Tweets class schema
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
    "vectorizer": "text2vec-openai",
}

# Define the Remilio class schema (used in main.py)
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
    "vectorizer": "text2vec-openai",
}

try:
    # Check if schema already exists
    existing_schema = client.schema.get()
    existing_classes = [cls['class'] for cls in existing_schema.get('classes', [])]
    
    # Create Tweets class if it doesn't exist
    if "Tweets" not in existing_classes:
        client.schema.create_class(class_obj)
        print("✅ Created 'Tweets' schema successfully!")
    else:
        print("ℹ️  'Tweets' schema already exists")
    
    # Create Remilio class if it doesn't exist
    if "Remilio" not in existing_classes:
        client.schema.create_class(remilio_class_obj)
        print("✅ Created 'Remilio' schema successfully!")
    else:
        print("ℹ️  'Remilio' schema already exists")
    
    # Get and print the final schema
    schema = client.schema.get()
    print("\n📋 Current Weaviate Schema:")
    print(json.dumps(schema, indent=2))
    
except Exception as e:
    print(f"❌ Error setting up schema: {e}")
    exit(1)

