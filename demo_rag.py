#!/usr/bin/env python3
"""
RAG System Demonstration
Shows how the RAG functionality works using the fallback system
"""
import os
import sys
from pathlib import Path

# Temporarily disable Ollama to demonstrate fallback
os.environ["OLLAMA_BASE_URL"] = ""

from skills.rag import RAGSkill

def demo_rag():
    print("🚀 RAG System Demonstration")
    print("=" * 50)
    
    # Initialize RAG skill
    rag = RAGSkill()
    
    # Show initial status
    print("\n📊 Initial Status:")
    status = rag.handle("rag status")
    print(status)
    
    # Add some sample documents
    print("\n📄 Adding test document...")
    result = rag.handle("rag add test_doc.md")
    print(result)
    
    # Create another test document
    sample_doc = Path("sample_knowledge.txt")
    sample_doc.write_text("""
Machine Learning Basics

Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and make decisions from data without being explicitly programmed for each task.

Types of Machine Learning:
1. Supervised Learning - Uses labeled data to train models
2. Unsupervised Learning - Finds patterns in unlabeled data  
3. Reinforcement Learning - Learns through rewards and penalties

Common Algorithms:
- Linear Regression - Predicts continuous values
- Decision Trees - Makes decisions through branching logic
- Neural Networks - Mimics brain structure for complex patterns
- K-Means - Groups data into clusters

Applications:
- Image recognition and computer vision
- Natural language processing
- Recommendation systems
- Fraud detection
- Autonomous vehicles
""")
    
    print(f"\n📄 Adding sample knowledge document...")
    result = rag.handle(f"rag add {sample_doc}")
    print(result)
    
    # Show updated status
    print("\n📊 Updated Status:")
    status = rag.handle("rag status")
    print(status)
    
    # Test queries using fallback (simple similarity)
    print("\n🔍 Testing Queries with Fallback System:")
    
    queries = [
        "What types of machine learning are there?",
        "What are common machine learning algorithms?",
        "Tell me about applications of machine learning",
        "What commands does the bot support?",
        "How is data stored in the RAG system?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        # Use fallback search directly to avoid Ollama timeout
        if hasattr(rag, 'fallback'):
            results = rag.fallback.search(query, k=2)
            if results:
                print("📋 Results from fallback system:")
                for i, (doc_id, score, content) in enumerate(results, 1):
                    snippet = content[:150].replace('\n', ' ').strip()
                    print(f"  {i}. [{score:.3f}] {snippet}... (from: {doc_id})")
            else:
                print("❌ No results found")
        else:
            result = rag.handle(f"rag ask {query}")
            print(result)
    
    # Cleanup
    sample_doc.unlink(missing_ok=True)
    
    print("\n" + "=" * 50)
    print("✅ RAG demonstration complete!")
    print("\nThe RAG system consists of:")
    print("1. Primary system: Advanced RAG with SQLite + Ollama embeddings")
    print("2. Fallback system: Simple character-frequency based similarity")
    print("3. Storage: Documents indexed in rag_storage/ directory")
    print("4. Integration: Available via Discord bot and CLI")

if __name__ == "__main__":
    demo_rag()