"""Demo script for the Day 19 Bonus Challenge.

Seeds episodic memories for test users, triggers 5 queries, and prints the recalled hybrid context.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bonus.agent import HybridMemoryAgent


def main() -> int:
    print("Initializing HybridMemoryAgent...")
    agent = HybridMemoryAgent(qdrant_mode="memory")

    # 1. Seed some episodic memories for user u_001
    print("Seeding episodic memories for user u_001...")
    
    agent.remember(
        "Kubernetes là một hệ thống điều phối container nguồn mở được phát triển bởi Google. "
        "Tôi đã đọc các bài viết hướng dẫn triển khai Kubernetes cluster trên AWS và GCP.",
        user_id="u_001"
    )
    
    agent.remember(
        "Auto-scaling giúp tự động mở rộng hoặc thu nhỏ hạ tầng máy chủ dựa trên lưu lượng truy cập thực tế. "
        "Cơ chế này giúp tối ưu hóa chi phí sử dụng tài nguyên đám mây đáng kể.",
        user_id="u_001"
    )

    agent.remember(
        "Cloud security đòi hỏi áp dụng mô hình Zero Trust và quản lý phân quyền IAM chặt chẽ. "
        "Việc mã hóa dữ liệu cả khi lưu trữ (at rest) và khi truyền tải (in transit) là bắt buộc.",
        user_id="u_001"
    )

    print("Successfully seeded 3 memories.\n")

    # 2. Run the 5 query scenarios
    scenarios = [
        (
            "1. Keyword Search (Kubernetes)",
            "Tôi đã đọc gì về Kubernetes?",
            "u_001"
        ),
        (
            "2. Profile Recommendation Context",
            "Recommend đọc gì tiếp?",
            "u_001" # Feast will return u_001's topic_affinity (e.g., cloud or ai_ml)
        ),
        (
            "3. Fresh Activity Context",
            "Tôi đang quan tâm gì gần đây?",
            "u_001" # Feast will return queries_last_hour and distinct_topics_24h
        ),
        (
            "4. Paraphrase Search (Auto scaling)",
            "Tài liệu về tự động mở rộng hạ tầng?",
            "u_001"
        ),
        (
            "5. Mixed Context Search (Cloud security)",
            "Cho tôi summary cloud security",
            "u_001"
        )
    ]

    for title, query, user in scenarios:
        print("=" * 60)
        print(f"Scenario: {title}")
        print(f"Query:    '{query}'")
        print("=" * 60)
        
        context = agent.recall(query, user_id=user)
        print(context)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
