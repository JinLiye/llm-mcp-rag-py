import asyncio
from utils import log_title
from MCPClient import MCPClient  # 注意：文件名通常用下划线


async def main():
    """测试 MCP 客户端连接到 fetch 服务器"""
    
    log_title("测试 MCP Fetch 服务器")
    
    # 创建客户端
    fetch_mcp = MCPClient(
        name='fetch',
        command='uvx',
        args=['mcp-server-fetch']
    )
    
    try:
        # 初始化连接
        await fetch_mcp.init()
        
        # 获取工具列表
        tools = fetch_mcp.get_tools()
        
        # 打印工具信息
        print("\n📦 可用工具列表:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 也可以打印完整的工具定义
        print("\n📋 完整工具定义:")
        import json
        print(json.dumps(tools, indent=2, ensure_ascii=False))
        
    finally:
        # 确保关闭连接
        await fetch_mcp.close()
        print("\n✅ 连接已关闭")


# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
