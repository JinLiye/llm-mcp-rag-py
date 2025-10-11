"""
EmbeddingRetriever 类 - 嵌入向量生成和检索
负责生成文档和查询的嵌入向量，并进行相似度检索
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from .utils import log_title
from.VectorStore import VectorStore

# 加载环境变量
load_dotenv()


class EmbeddingRetriever:
    """
    嵌入向量检索器
    负责生成嵌入向量并从向量存储中检索相关文档
    """
    
    def __init__(self, embedding_model: str):
        """
        初始化嵌入检索器
        
        Args:
            embedding_model: 嵌入模型名称（如 "BAAI/bge-large-zh-v1.5"）
        """
        self.embedding_model = embedding_model
        self.vector_store = VectorStore()
        
        # 从环境变量获取配置
        self.embedding_base_url = os.getenv("EMBEDDING_BASE_URL")
        self.embedding_key = os.getenv("EMBEDDING_KEY")
        
        if not self.embedding_base_url or not self.embedding_key:
            raise ValueError(
                "请在 .env 文件中设置 EMBEDDING_BASE_URL 和 EMBEDDING_KEY"
            )
    
    async def embed_document(self, document: str) -> List[float]:
        """
        生成文档的嵌入向量并添加到向量存储
        
        Args:
            document: 文档内容
            
        Returns:
            嵌入向量
        """
        log_title('EMBEDDING DOCUMENT')
        
        embedding = await self._embed(document)
        await self.vector_store.add_embedding(embedding, document)
        
        return embedding
    
    async def embed_query(self, query: str) -> List[float]:
        """
        生成查询的嵌入向量
        
        Args:
            query: 查询文本
            
        Returns:
            嵌入向量
        """
        log_title('EMBEDDING QUERY')
        
        embedding = await self._embed(query)
        
        return embedding
    
    async def _embed(self, text: str) -> List[float]:
        """
        调用 Embedding API 生成嵌入向量（私有方法）
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
            
        Raises:
            requests.RequestException: API 调用失败
            KeyError: 响应格式错误
        """
        url = f"{self.embedding_base_url}/embeddings"
        
        payload = {
            "model": self.embedding_model,
            "input": text,
            "encoding_format": "float"
        }
        
        headers = {
            "Authorization": f"Bearer {self.embedding_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # 检查 HTTP 错误
            
            # 解析响应
            data = response.json()
            
            # 提取嵌入向量
            embedding = data["data"][0]["embedding"]
            
            # 打印嵌入向量的前几个值（用于调试）
            print(f"嵌入向量维度: {len(embedding)}")
            print(f"前 5 个值: {embedding[:5]}")
            
            return embedding
            
        except requests.RequestException as e:
            print(f"❌ API 请求失败: {e}")
            raise
            
        except KeyError as e:
            print(f"❌ 响应格式错误: {e}")
            print(f"响应内容: {data}")
            raise
    
    async def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        检索与查询最相关的文档
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量
            
        Returns:
            最相关的文档列表
        """
        # 生成查询的嵌入向量
        query_embedding = await self.embed_query(query)
        
        # 在向量存储中搜索
        log_title('RETRIEVING DOCUMENTS')
        results = await self.vector_store.search(query_embedding, top_k)
        
        print(f"✅ 检索到 {len(results)} 个相关文档\n")
        
        return results
    
    def get_vector_store_size(self) -> int:
        """
        获取向量存储中的文档数量
        
        Returns:
            文档数量
        """
        return self.vector_store.size()
    
    def clear_vector_store(self) -> None:
        """清空向量存储"""
        self.vector_store.clear()


# ============ 使用示例 ============

async def example_usage():
    """EmbeddingRetriever 使用示例"""
    
    # 创建检索器
    retriever = EmbeddingRetriever(
        embedding_model="BAAI/bge-m3"
    )
    
    # 添加文档
    documents = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的子集，使用多层神经网络进行学习。",
        "自然语言处理是人工智能的重要应用领域，用于处理人类语言。",
        "计算机视觉使机器能够理解和分析图像和视频内容。",
        "强化学习是一种通过与环境交互来学习最优策略的方法。"
    ]
    
    print("📚 添加文档到向量存储...")
    for doc in documents:
        await retriever.embed_document(doc)
    
    print(f"\n✅ 向量存储大小: {retriever.get_vector_store_size()}\n")
    
    # 检索相关文档
    query = "什么是深度学习？"
    print(f"🔍 查询: {query}\n")
    
    results = await retriever.retrieve(query, top_k=3)
    
    print("📄 检索结果:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
