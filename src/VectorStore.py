"""
VectorStore 类 - 简单的向量存储和检索
用于存储文档嵌入向量并执行余弦相似度搜索
"""

import math
from typing import List, Dict, Tuple, TypedDict


class VectorStoreItem(TypedDict):
    """向量存储项的类型定义"""
    embedding: List[float]
    document: str


class VectorStore:
    """
    简单的内存向量存储
    支持添加嵌入向量和基于余弦相似度的检索
    """
    
    def __init__(self):
        """初始化空的向量存储"""
        self.vector_store: List[VectorStoreItem] = []
    
    async def add_embedding(self, embedding: List[float], document: str) -> None:
        """
        添加文档及其嵌入向量到存储
        
        Args:
            embedding: 文档的嵌入向量
            document: 文档内容
        """
        self.vector_store.append({
            "embedding": embedding,
            "document": document
        })
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[str]:
        """
        根据查询向量搜索最相似的文档
        
        Args:
            query_embedding: 查询的嵌入向量
            top_k: 返回的文档数量（默认 3）
            
        Returns:
            最相似的 top_k 个文档列表
        """
        # 计算所有文档的相似度分数
        scored: List[Dict[str, float | str]] = [
            {
                "document": item["document"],
                "score": self._cosine_similarity(query_embedding, item["embedding"])
            }
            for item in self.vector_store
        ]
        
        # 按分数降序排序并取前 top_k 个
        top_k_documents = [
            item["document"]
            for item in sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
        ]
        
        return top_k_documents
    
    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec_a: 向量 A
            vec_b: 向量 B
            
        Returns:
            余弦相似度值（范围 -1 到 1）
            
        Raises:
            ZeroDivisionError: 如果任一向量的范数为 0
        """
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        
        # 计算向量范数（模长）
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        # 避免除以零
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        # 返回余弦相似度
        return dot_product / (norm_a * norm_b)
    
    def get_all_documents(self) -> List[str]:
        """
        获取所有存储的文档
        
        Returns:
            文档列表
        """
        return [item["document"] for item in self.vector_store]
    
    def size(self) -> int:
        """
        获取存储的文档数量
        
        Returns:
            文档数量
        """
        return len(self.vector_store)
    
    def clear(self) -> None:
        """清空向量存储"""
        self.vector_store = []


# # ============ 使用示例 ============

# async def example_usage():
#     """VectorStore 使用示例"""
    
#     # 创建向量存储
#     vector_store = VectorStore()
    
#     # 添加一些示例文档（使用简化的 3 维向量）
#     documents = [
#         ("什么是机器学习？", [0.8, 0.2, 0.1]),
#         ("深度学习是机器学习的子集", [0.7, 0.3, 0.15]),
#         ("今天天气很好", [0.1, 0.1, 0.9]),
#         ("Python 是一种编程语言", [0.5, 0.5, 0.2]),
#     ]
    
#     print("📚 添加文档到向量存储...")
#     for doc, embedding in documents:
#         await vector_store.add_embedding(embedding, doc)
    
#     print(f"✅ 已添加 {vector_store.size()} 个文档\n")
    
#     # 搜索与查询最相似的文档
#     query_embedding = [0.75, 0.25, 0.1]  # 与机器学习相关的查询
#     print(f"🔍 搜索查询向量: {query_embedding}")
    
#     results = await vector_store.search(query_embedding, top_k=2)
    
#     print(f"\n📄 搜索结果（Top 2）:")
#     for i, doc in enumerate(results, 1):
#         print(f"  {i}. {doc}")
    
#     # 获取所有文档
#     print(f"\n📚 所有文档:")
#     for i, doc in enumerate(vector_store.get_all_documents(), 1):
#         print(f"  {i}. {doc}")
    
#     # 清空存储
#     vector_store.clear()
#     print(f"\n🗑️ 清空后文档数量: {vector_store.size()}")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(example_usage())
