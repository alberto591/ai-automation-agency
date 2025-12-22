#!/usr/bin/env python3
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)

def generate_embeddings(table_name="properties"):
    print(f"🚀 Generating embeddings for {table_name}...")
    
    # 1. Fetch all properties without embeddings or all of them
    try:
        res = container.db.client.table(table_name).select("id, title, description").execute()
        properties = res.data
        print(f"Found {len(properties)} properties.")
        
        for p in properties:
            text = f"{p['title']}. {p['description']}"
            print(f"  Processing: {p['title']}...")
            
            embedding = container.ai.get_embedding(text)
            
            container.db.client.table(table_name).update({
                "embedding": embedding
            }).eq("id", p["id"]).execute()
            
        print(f"✅ Successfully updated {len(properties)} properties in {table_name}.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error("EMBEDDING_GEN_FAILED", context={"table": table_name, "error": str(e)})

if __name__ == "__main__":
    # Generate for both tables
    generate_embeddings("properties")
    generate_embeddings("mock_properties")
