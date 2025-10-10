"""
测试自定义的 PKP MCP Server
"""

import asyncio
from MCPClient import MCPClient
from utils import log_title


async def test_pkp_server():
    """测试 PKP Server 的功能"""
    
    log_title("测试 PKP MCP Server")
    
    # 创建 MCP 客户端连接到 PKP Server
    pkp_client = MCPClient(
        name='pkp-client',
        command='python',
        args=['mcp_server_pkp.py']
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
            print(f"参数: {tool['inputSchema']}")
        
        # 测试 PKP 运算
        log_title("测试 PKP 运算")
        
        test_cases = [
            {"a": 3, "b": 5, "c": 2},      # (3 + 5) * 2 = 16
            {"a": 10, "b": -5, "c": 3},    # (10 + -5) * 3 = 15
            {"a": 0, "b": 0, "c": 100},    # (0 + 0) * 100 = 0
            {"a": 7.5, "b": 2.5, "c": 4},  # (7.5 + 2.5) * 4 = 40
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n测试 {i}:")
            print(f"  参数: a={params['a']}, b={params['b']}, c={params['c']}")
            
            result = await pkp_client.call_tool("pkp", params)
            print(f"  结果: {result}")
        
        # 测试错误处理
        log_title("测试错误处理")
        
        print("\n测试缺少参数:")
        result = await pkp_client.call_tool("pkp", {"a": 1, "b": 2})
        print(f"  结果: {result}")
        
        print("\n测试未知工具:")
        result = await pkp_client.call_tool("unknown_tool", {})
        print(f"  结果: {result}")
        
    finally:
        # 关闭连接
        await pkp_client.close()
        print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_pkp_server())
