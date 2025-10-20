"""
主程序 - RAG + Agent 系统
功能：
1. 从知识库中检索相关文档（RAG）
2. 使用 Agent 执行任务（工具调用）
"""

import asyncio
import os
from pathlib import Path

from .MCPClient import MCPClient
from .Agent import Agent
from .EmbeddingRetriver import EmbeddingRetriever
from .utils import log_title


# ============ 配置 ============

# 输出目录
OUTPUT_PATH = Path.cwd() / 'output'

# 任务描述
# TASK = f"""
# 告诉我 Karianne 的信息，先从我给你的 context 中找到相关信息，总结后创作一个关于这个人的故事。
# 把故事和她的基本信息保存到 {OUTPUT_PATH}/antonette.md，输出一个漂亮的 markdown 文件。
# """
TASK = f"""帮我看看这个视频的信息，视频路径是/media/amax/xiao_20T1/code/jly/agent/llm-mcp-rag-py/data/GOT10k/GOT-10k_Train_009332，分析视频帧的亮度、对比度、清晰度和噪声水平
"""

# ============ 主函数 ============

async def main():
    """主程序入口"""
    
    # 确保输出目录存在
    OUTPUT_PATH.mkdir(exist_ok=True)
    
    # Step 1: 检索上下文（RAG）
    context = ''
    # context = await retrieve_context()
    
    # Step 2: 创建 MCP 客户端
    fetch_mcp = MCPClient(
        name="mcp-server-fetch",
        command="uvx",
        args=['mcp-server-fetch']
    )
    
    # file_mcp = MCPClient(
    #     name="mcp-server-file",
    #     command="npx",
    #     args=['-y', '@modelcontextprotocol/server-filesystem', str(OUTPUT_PATH)]
    # )
    # 创建 PKP MCP 客户端
    # pkp_client = MCPClient(
    #     name='pkp-server',
    #     command='python',
    #     args=['-m', 'src.servers.mcp_server_pkp']
    # )

    # 创建 GetVideo MCP 客户端
    getvideo_mcp = MCPClient(
        name='getvideo-server',
        command='python',
        args=['-m','src.servers.getVideo.server']  # 确保路径正确
    )
    
    # Step 3: 创建 Agent 并执行任务
    agent = Agent(
        model='Qwen/Qwen3-8B',  # 或 'openai/gpt-4o-mini'
        mcp_clients=[getvideo_mcp],
        system_prompt='',
        context=context
    )
    
    try:
        await agent.init()
        result = await agent.invoke(TASK)
        
        log_title('任务完成')
        print(f"✅ 最终结果:\n{result}\n")
        
    finally:
        # 确保关闭所有连接
        await agent.close()


async def retrieve_context() -> str:
    """
    从知识库中检索相关上下文
    
    Returns:
        检索到的上下文文本
    """
    log_title('RAG - 检索上下文')
    
    # 创建嵌入检索器
    embedding_retriever = EmbeddingRetriever(
        embedding_model="BAAI/bge-m3"
    )
    
    # 知识库目录
    knowledge_dir = Path.cwd() / 'knowledge'
    
    # 检查目录是否存在
    if not knowledge_dir.exists():
        print(f"⚠️ 知识库目录不存在: {knowledge_dir}")
        print("创建空目录...")
        knowledge_dir.mkdir(exist_ok=True)
        return ""
    
    # 读取所有知识文件
    files = list(knowledge_dir.iterdir())
    
    if not files:
        print("⚠️ 知识库目录为空")
        return ""
    
    print(f"📚 找到 {len(files)} 个知识文件")
    
    # 为每个文件生成嵌入向量
    for file_path in files:
        if file_path.is_file():
            try:
                # 读取文件内容
                content = file_path.read_text(encoding='utf-8')
                
                print(f"  处理文件: {file_path.name} ({len(content)} 字符)")
                
                # 添加到向量存储
                await embedding_retriever.embed_document(content)
                
            except Exception as e:
                print(f"  ❌ 读取文件失败 {file_path.name}: {e}")
    
    print(f"\n✅ 向量存储大小: {embedding_retriever.get_vector_store_size()}\n")
    
    # 检索相关文档
    relevant_docs = await embedding_retriever.retrieve(TASK, top_k=3)
    
    # 合并为上下文
    context = '\n\n'.join(relevant_docs)
    
    log_title('检索到的上下文')
    print(context[:500] + "..." if len(context) > 500 else context)
    print(f"\n📊 上下文长度: {len(context)} 字符\n")
    
    return context


# ============ 程序入口 ============

if __name__ == "__main__":
    print("=" * 80)
    print("RAG + Agent 系统启动")
    print("=" * 80)
    print()
    
    asyncio.run(main())
