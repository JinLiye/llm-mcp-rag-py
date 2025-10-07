import os
import json
from typing import List, Dict, Any, Optional, TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from utils import log_title  # 假设你已经实现了 log_title

# 加载环境变量
load_dotenv()


class ToolCall(TypedDict):
    """工具调用的类型定义"""
    id: str
    function: Dict[str, str]  # {"name": str, "arguments": str}


class Tool(TypedDict):
    """MCP 工具的类型定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ChatOpenAI:
    """OpenAI 聊天客户端封装类"""
    
    def __init__(
        self,
        model: str,
        system_prompt: str = '',
        tools: Optional[List[Tool]] = None,
        context: str = ''
    ):
        """
        初始化 ChatOpenAI 实例
        
        Args:
            model: OpenAI 模型名称（如 "gpt-4"）
            system_prompt: 系统提示词
            tools: MCP 工具列表
            context: 初始上下文
        """
        self.llm = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = model
        self.messages: List[Dict[str, Any]] = []
        self.tools = tools if tools is not None else []
        
        # 添加系统提示词
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        
        # 添加初始上下文
        if context:
            self.messages.append({"role": "user", "content": context})
    
    async def chat(self, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        发送聊天消息并接收响应（支持流式输出）
        
        Args:
            prompt: 用户输入的消息
            
        Returns:
            包含 content 和 toolCalls 的字典
        """
        log_title('CHAT')
        
        # 添加用户消息
        if prompt:
            self.messages.append({"role": "user", "content": prompt})
        
        # 创建流式聊天完成
        stream = self.llm.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            tools=self._get_tools_definition() if self.tools else None,
        )
        
        content = ""
        tool_calls: List[ToolCall] = []
        
        log_title('RESPONSE')
        
        # 处理流式响应
        for chunk in stream:
            delta = chunk.choices[0].delta
            
            # 处理普通文本内容
            if delta.content:
                content_chunk = delta.content
                content += content_chunk
                print(content_chunk, end='', flush=True)
            
            # 处理工具调用
            if delta.tool_calls:
                for tool_call_chunk in delta.tool_calls:
                    index = tool_call_chunk.index
                    
                    # 第一次出现该索引时创建新的 tool_call
                    if len(tool_calls) <= index:
                        tool_calls.append({
                            "id": "",
                            "function": {"name": "", "arguments": ""}
                        })
                    
                    current_call = tool_calls[index]
                    
                    # 累积工具调用的各个部分
                    if tool_call_chunk.id:
                        current_call["id"] += tool_call_chunk.id
                    if tool_call_chunk.function and tool_call_chunk.function.name:
                        current_call["function"]["name"] += tool_call_chunk.function.name
                    if tool_call_chunk.function and tool_call_chunk.function.arguments:
                        current_call["function"]["arguments"] += tool_call_chunk.function.arguments
        
        print()  # 换行
        
        # 将助手响应添加到消息历史
        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": content,
        }
        
        # 如果有工具调用，添加到消息中
        if tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": call["id"],
                    "type": "function",
                    "function": call["function"]
                }
                for call in tool_calls
            ]
        
        self.messages.append(assistant_message)
        
        return {
            "content": content,
            "toolCalls": tool_calls,
        }
    
    def append_tool_result(self, tool_call_id: str, tool_output: str) -> None:
        """
        将工具执行结果追加到消息历史
        
        Args:
            tool_call_id: 工具调用的 ID
            tool_output: 工具执行的输出结果
        """
        self.messages.append({
            "role": "tool",
            "content": tool_output,
            "tool_call_id": tool_call_id
        })
    
    def _get_tools_definition(self) -> List[Dict[str, Any]]:
        """
        将 MCP 工具格式转换为 OpenAI API 格式
        
        Returns:
            OpenAI 工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"],
                }
            }
            for tool in self.tools
        ]


# ============ 使用示例 ============

async def main():
    # 示例工具定义
    tools: List[Tool] = [
        {
            "name": "search_documents",
            "description": "在文档库中搜索相关内容",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"}
                },
                "required": ["query"]
            }
        }
    ]
    
    # 创建聊天实例
    chat = ChatOpenAI(
        model="gpt-4",
        system_prompt="你是一个有帮助的助手",
        tools=tools,
        context="我们正在讨论 RAG 系统"
    )
    
    # 发送消息
    response = await chat.chat("请帮我搜索关于向量数据库的文档")
    
    # 处理工具调用
    if response["toolCalls"]:
        for tool_call in response["toolCalls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            print(f"\n调用工具: {tool_name}")
            print(f"参数: {tool_args}")
            
            # 模拟工具执行
            tool_result = "找到 3 篇关于向量数据库的文档..."
            
            # 将结果追加到对话
            chat.append_tool_result(tool_call["id"], tool_result)
        
        # 继续对话，让 LLM 处理工具结果
        final_response = await chat.chat()
        print(f"\n最终响应: {final_response['content']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
