"""
Agent 类 - 智能体编排器
负责协调多个 MCP 客户端和 LLM，处理工具调用循环
"""

import json
from typing import List, Optional, Dict, Any

from MCPClient import MCPClient
from ChatOpenAI import ChatOpenAI
from utils import log_title


class Agent:
    """
    智能体类，整合 MCP 工具和 LLM 进行自主任务执行
    """
    
    def __init__(
        self,
        model: str,
        mcp_clients: List[MCPClient],
        system_prompt: str = '',
        context: str = ''
    ):
        """
        初始化 Agent
        
        Args:
            model: OpenAI 模型名称
            mcp_clients: MCP 客户端列表
            system_prompt: 系统提示词
            context: 初始上下文
        """
        self.mcp_clients = mcp_clients
        self.model = model
        self.system_prompt = system_prompt
        self.context = context
        self.llm: Optional[ChatOpenAI] = None
    
    async def init(self) -> None:
        """
        初始化 Agent
        - 初始化所有 MCP 客户端
        - 收集所有工具
        - 创建 LLM 实例
        """
        log_title('TOOLS')
        
        # 初始化所有 MCP 客户端
        for client in self.mcp_clients:
            await client.init()
        
        # 收集所有工具
        tools = []
        for client in self.mcp_clients:
            tools.extend(client.get_tools())
        
        print(f"✅ 共加载 {len(tools)} 个工具")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool['name']}")
        print()
        
        # 创建 LLM 实例
        self.llm = ChatOpenAI(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=tools,
            context=self.context
        )
    
    async def close(self) -> None:
        """
        关闭所有 MCP 客户端连接
        """
        for client in self.mcp_clients:
            await client.close()
        print("✅ 所有 MCP 连接已关闭")
    
    async def invoke(self, prompt: str) -> str:
        """
        执行一次完整的智能体调用
        - 发送用户输入
        - 处理工具调用循环
        - 返回最终结果
        
        Args:
            prompt: 用户输入
            
        Returns:
            最终的文本响应
            
        Raises:
            RuntimeError: 如果 Agent 未初始化
        """
        if not self.llm:
            raise RuntimeError("Agent 未初始化，请先调用 init() 方法")
        
        # 首次对话
        response = await self.llm.chat(prompt)
        
        # 工具调用循环
        while True:
            # 检查是否有工具调用
            if response['toolCalls'] and len(response['toolCalls']) > 0:
                # 处理所有工具调用
                for tool_call in response['toolCalls']:
                    await self._handle_tool_call(tool_call)
                
                # 工具调用后，让 LLM 处理结果并继续对话
                response = await self.llm.chat()
                continue
            
            # 没有工具调用，结束对话
            await self.close()
            return response['content']
    
    async def _handle_tool_call(self, tool_call: Dict[str, Any]) -> None:
        """
        处理单个工具调用
        
        Args:
            tool_call: 工具调用对象
        """
        tool_name = tool_call['function']['name']
        tool_args_str = tool_call['function']['arguments']
        tool_id = tool_call['id']
        
        log_title('TOOL USE')
        print(f"🔧 调用工具: {tool_name}")
        print(f"📝 参数: {tool_args_str}")
        
        # 查找对应的 MCP 客户端
        mcp_client = self._find_mcp_client_for_tool(tool_name)
        
        if mcp_client:
            try:
                # 解析参数
                tool_args = json.loads(tool_args_str)
                
                # 调用工具
                result_str = await mcp_client.call_tool(tool_name, tool_args)
                # breakpoint()
                # 格式化结果
                result_str = json.dumps(result_str, ensure_ascii=False, indent=2)
                print(f"✅ 结果: {result_str[:200]}...")  # 只打印前 200 字符
                
                # 将结果返回给 LLM
                self.llm.append_tool_result(tool_id, result_str)
                
            except json.JSONDecodeError as e:
                error_msg = f"参数解析失败: {e}"
                print(f"❌ {error_msg}")
                self.llm.append_tool_result(tool_id, error_msg)
                
            except Exception as e:
                error_msg = f"工具调用失败: {e}"
                print(f"❌ {error_msg}")
                self.llm.append_tool_result(tool_id, error_msg)
        else:
            error_msg = f"未找到工具: {tool_name}"
            print(f"❌ {error_msg}")
            self.llm.append_tool_result(tool_id, error_msg)
        
        print()  # 空行分隔
    
    def _find_mcp_client_for_tool(self, tool_name: str) -> Optional[MCPClient]:
        """
        根据工具名称查找对应的 MCP 客户端
        
        Args:
            tool_name: 工具名称
            
        Returns:
            对应的 MCP 客户端，如果未找到则返回 None
        """
        for client in self.mcp_clients:
            tools = client.get_tools()
            if any(tool['name'] == tool_name for tool in tools):
                return client
        return None

    
    
    async def __aenter__(self):
        """支持异步上下文管理器"""
        await self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持异步上下文管理器"""
        await self.close()


# ============ 使用示例 ============

async def example_usage():
    """Agent 使用示例"""
    from MCPClient import MCPClient
    
    # 创建 MCP 客户端
    filesystem_client = MCPClient(
        name='file',
        command='npx',
        args=[
            '-y',  # 自动确认安装（可选但推荐）
            '@modelcontextprotocol/server-filesystem',  # npm 包名
            r'C:\Users\32114\Desktop\code\llm-mcp-rag-py\output'  # 允许访问的目录
        ]
    )

    fetch_client = MCPClient(
        name='fetch',
        command='uvx',
        args=['mcp-server-fetch']
    )
    

    
    # 创建 Agent
    agent = Agent(
        model='gpt-4o-mini',
        mcp_clients=[fetch_client, filesystem_client]
    )

    # 初始化
    await agent.init()
    
    # 执行任务
    result = await agent.invoke(
        r"""爬取https://example.com/网页中的内容，
        并保存到C:\Users\32114\Desktop\code\llm-mcp-rag-py\output目录下的summary.txt中"""
    )
    
    print(f"\n最终结果: {result}")
    


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
