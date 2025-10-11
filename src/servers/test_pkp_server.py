"""测试自定义的 PKP MCP Server"""

import asyncio
from pathlib import Path
from ..MCPClient import MCPClient
from ..utils import log_title

async def test_pkp_server():
    """测试 PKP Server 的功能"""
    
    log_title("测试 PKP MCP Server")
    
    # 获取正确的文件路径
    current_dir = Path(__file__).parent.parent.parent  # 项目根目录
    server_path = current_dir / 'src' / 'servers' / 'mcp_server_pkp.py'
    
    print(f"Server 路径: {server_path}")
    print(f"文件存在: {server_path.exists()}")

    # 创建 MCP 客户端连接到 PKP Server
    pkp_client = MCPClient(
        name='pkp-client',
        command='python',
        args=['-m','src.servers.mcp_server_pkp']  # 使用绝对路径
    )

    try:
        # 初始化连接
        await pkp_client.init()
        
        # 获取工具列表
        tools = pkp_client.get_tools()
        print(f"\n📦 可用工具: {[t['name'] for t in tools]}")
        
        # 打印工具详情
        for tool in tools:
            print(f"\n工具名称: {tool['name']}")
            print(f"描述: {tool['description']}")
        
        # 测试 PKP 运算
        log_title("测试 PKP 运算")
        
        test_cases = [
            {"a": 3, "b": 5, "c": 2},
            {"a": 10, "b": -5, "c": 3},
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n测试 {i}: a={params['a']}, b={params['b']}, c={params['c']}")
            result = await pkp_client.call_tool("pkp", params)
            print(f"结果: {result}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await pkp_client.close()
        print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_pkp_server())
