"""HybridMemoryAgent implementation for Day 19 Bonus Challenge.

Combines episodic memory (Qdrant vector store) with user profiles and recent activity (Feast feature store).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastembed import TextEmbedding
from feast import FeatureStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Filter, FieldCondition, MatchValue, PointStruct, VectorParams

# Resolve repository paths
REPO_ROOT = Path(__file__).resolve().parent.parent
FEAST_DIR = REPO_ROOT / "app" / "feast_repo"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384
MEMORY_COLLECTION = "episodic_memories"


class HybridMemoryAgent:
    """Agent that coordinates episodic memory retrieval and Feast online feature lookup to compile RAG context."""

    def __init__(self, qdrant_mode: str = "memory") -> None:
        # 1. Initialize Qdrant Client
        if qdrant_mode == "server":
            self.qdrant = QdrantClient(url="http://127.0.0.1:6333")
        else:
            self.qdrant = QdrantClient(":memory:")

        # Create episodic memory collection if not exists
        existing = {c.name for c in self.qdrant.get_collections().collections}
        if MEMORY_COLLECTION not in existing:
            self.qdrant.create_collection(
                collection_name=MEMORY_COLLECTION,
                vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
            )

        # 2. Initialize Embedder
        self.embedder = TextEmbedding(model_name=EMBED_MODEL)

        # 3. Initialize Feast Feature Store
        self.fs = FeatureStore(repo_path=str(FEAST_DIR))

        # Track point ID counter locally for upserts
        self._next_point_id = 0

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Chunk, embed, and upsert a new piece of episodic memory for a specific user."""
        # Simple sentence-based chunking for this POC
        chunks = [c.strip() for c in text.replace("\n", " ").split(".") if len(c.strip()) > 10]
        if not chunks:
            # Fallback if text has no periods
            chunks = [text.strip()]

        embeddings = list(self.embedder.embed(chunks))

        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append(PointStruct(
                id=self._next_point_id,
                vector=vector.tolist(),
                payload={
                    "user_id": user_id,
                    "text": chunk,
                }
            ))
            self._next_point_id += 1

        self.qdrant.upsert(collection_name=MEMORY_COLLECTION, points=points)

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve user profile parameters from Feast and matching memories from Qdrant, assembling the final context."""
        # 1. Retrieve profile and activity from Feast online store
        request_features = [
            "user_profile_features:reading_speed_wpm",
            "user_profile_features:preferred_language",
            "user_profile_features:topic_affinity",
            "query_velocity_features:queries_last_hour",
            "query_velocity_features:distinct_topics_24h",
        ]
        
        try:
            features = self.fs.get_online_features(
                features=request_features,
                entity_rows=[{"user_id": user_id}],
            ).to_dict()
            
            # Extract scalar values from lists
            profile = {
                "reading_speed_wpm": features.get("reading_speed_wpm", [200])[0],
                "preferred_language": features.get("preferred_language", ["vi"])[0],
                "topic_affinity": features.get("topic_affinity", ["general"])[0],
                "queries_last_hour": features.get("queries_last_hour", [0])[0],
                "distinct_topics_24h": features.get("distinct_topics_24h", [0])[0],
            }
        except Exception as e:
            # Fallback values if Feast is not materialized
            profile = {
                "reading_speed_wpm": 200,
                "preferred_language": "vi",
                "topic_affinity": "general",
                "queries_last_hour": 0,
                "distinct_topics_24h": 0,
            }

        # 2. Retrieve semantic memories from Qdrant (filtered by user_id)
        q_vec = next(self.embedder.embed([query])).tolist()
        
        user_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
        )
        
        hits = self.qdrant.query_points(
            collection_name=MEMORY_COLLECTION,
            query=q_vec,
            query_filter=user_filter,
            limit=3,
        ).points

        memories = [h.payload["text"] for h in hits]

        # 3. Assemble and return context string
        context = (
            f"User Profile & State [ID: {user_id}]:\n"
            f"  - Topic Affinity: {profile['topic_affinity']}\n"
            f"  - Preferred Language: {profile['preferred_language']}\n"
            f"  - Reading Speed: {profile['reading_speed_wpm']} WPM\n"
            f"  - Queries last hour: {profile['queries_last_hour']}\n"
            f"  - Distinct topics 24h: {profile['distinct_topics_24h']}\n"
            f"\n"
            f"Retrieved Episodic Memories:\n"
        )
        if memories:
            for idx, mem in enumerate(memories, 1):
                context += f"  {idx}. {mem}\n"
        else:
            context += "  (No matching episodic memories found)\n"
            
        return context
