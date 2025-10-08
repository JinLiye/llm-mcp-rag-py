"""
MCP (Model Context Protocol) 客户端封装
支持连接到 MCP 服务器并调用工具
"""

import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool


class MCPClient:
    """MCP 客户端类，用于连接和管理 MCP 服务器"""
    
    def __init__(
        self,
        name: str,
        command: str,
        args: List[str],
        version: str = "0.0.1"
    ):
        """
        初始化 MCP 客户端
        
        Args:
            name: 客户端名称
            command: 服务器启动命令（如 "python", "node"）
            args: 服务器启动参数（如脚本路径）
            version: 客户端版本号
        """
        self.name = name
        self.command = command
        self.args = args
        self.version = version
        
        # 核心组件
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools: List[Tool] = []
        
        # 传输层组件
        self.stdio = None
        self.write = None
    
    async def init(self) -> None:
        """初始化客户端并连接到服务器"""
        await self._connect_to_server()
    
    async def close(self) -> None:
        """关闭客户端连接"""
        await self.exit_stack.aclose()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取服务器提供的工具列表
        
        Returns:
            工具定义列表，格式与 OpenAI Function Calling 兼容
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in self.tools
        ]
    
    async def call_tool(
        self,
        name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        调用 MCP 工具
        
        Args:
            name: 工具名称
            params: 工具参数（字典格式）
            
        Returns:
            工具执行结果
            
        Raises:
            RuntimeError: 如果客户端未初始化
        """
        if not self.session:
            raise RuntimeError("客户端未初始化，请先调用 init() 方法")
        
        result = await self.session.call_tool(
            name=name,
            arguments=params or {}
        )
        
        return result
    
    async def _connect_to_server(self) -> None:
        """
        连接到 MCP 服务器（私有方法）
        
        Raises:
            ValueError: 如果命令或参数无效
            RuntimeError: 如果连接失败
        """
        try:
            # 配置服务器参数
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args,
                env=None  # 可以传入环境变量字典
            )
            
            # 建立传输层连接
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            
            # 创建会话
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            
            # 初始化会话
            await self.session.initialize()
            
            # 获取可用工具列表
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            tool_names = [tool.name for tool in self.tools]
            print(f"✅ 已连接到 MCP 服务器，可用工具: {tool_names}")
            
        except Exception as e:
            print(f"❌ 连接到 MCP 服务器失败: {e}")
            raise RuntimeError(f"无法连接到 MCP 服务器: {e}") from e
    
    async def __aenter__(self):
        """支持异步上下文管理器"""
        await self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持异步上下文管理器"""
        await self.close()


# ============ 便捷工厂函数 ============

async def create_mcp_client_from_script(
    name: str,
    server_script_path: str,
    version: str = "0.0.1"
) -> MCPClient:
    """
    从服务器脚本路径创建 MCP 客户端（便捷方法）
    
    Args:
        name: 客户端名称
        server_script_path: 服务器脚本路径（.py 或 .js）
        version: 客户端版本号
        
    Returns:
        已初始化的 MCPClient 实例
        
    Raises:
        ValueError: 如果脚本类型不支持
    """
    # 根据文件扩展名确定命令
    if server_script_path.endswith('.py'):
        command = "python"
    elif server_script_path.endswith('.js'):
        command = "node"
    else:
        raise ValueError("服务器脚本必须是 .py 或 .js 文件")
    
    # 创建并初始化客户端
    client = MCPClient(
        name=name,
        command=command,
        args=[server_script_path],
        version=version
    )
    await client.init()
    
    return client


# ============ 使用示例 ============

async def example_usage():
    """使用示例"""
    
    # 方式 1: 直接创建（完全控制）
    print("\n=== 方式 1: 直接创建 ===")
    client1 = MCPClient(
        name="my-rag-client",
        command="python",
        args=["path/to/mcp_server.py"],
        version="1.0.0"
    )
    await client1.init()
    
    # 获取工具列表
    tools = client1.get_tools()
    print(f"可用工具: {[t['name'] for t in tools]}")
    
    # 调用工具
    result = await client1.call_tool(
        name="search_documents",
        params={"query": "向量数据库", "limit": 5}
    )
    print(f"工具调用结果: {result}")
    
    # 关闭连接
    await client1.close()
    
    
    # 方式 2: 使用便捷工厂函数
    print("\n=== 方式 2: 工厂函数 ===")
    client2 = await create_mcp_client_from_script(
        name="my-rag-client",
        server_script_path="path/to/mcp_server.py"
    )
    
    tools = client2.get_tools()
    print(f"可用工具: {[t['name'] for t in tools]}")
    
    await client2.close()
    
    
    # 方式 3: 使用上下文管理器（推荐）
    print("\n=== 方式 3: 上下文管理器 ===")
    async with MCPClient(
        name="my-rag-client",
        command="node",
        args=["path/to/mcp_server.js"]
    ) as client3:
        tools = client3.get_tools()
        print(f"可用工具: {[t['name'] for t in tools]}")
        
        result = await client3.call_tool(
            name="get_documents",
            params={"count": 10}
        )
        print(f"结果: {result}")
    
    # 上下文管理器会自动关闭连接


if __name__ == "__main__":
    asyncio.run(example_usage())
