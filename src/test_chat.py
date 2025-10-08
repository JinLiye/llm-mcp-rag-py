"""
测试 ChatOpenAI 类的完整功能
包括：基础聊天、工具调用、流式输出
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# 导入我们实现的模块
from utils import log_title
from ChatOpenAI import ChatOpenAI, Tool, ToolCall

# 加载环境变量
load_dotenv()


class TestChatOpenAI:
    """测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        # 检查环境变量
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY")
        
        print("✅ 环境变量检查通过")
    
    async def test_basic_chat(self):
        """测试 1：基础聊天功能（无工具）"""
        log_title("测试 1: 基础聊天")
        
        chat = ChatOpenAI(
            model="gpt-4o-mini",  # 使用更经济的模型
            system_prompt="你是一个友好的助手，回答要简洁。",
        )
        
        response = await chat.chat("用一句话介绍什么是 RAG？")
        
        print(f"\n\n✅ 响应内容: {response['content'][:100]}...")
        print(f"✅ 工具调用数量: {len(response['toolCalls'])}")
        assert response['content'], "响应内容不应为空"
        assert len(response['toolCalls']) == 0, "不应有工具调用"
        print("✅ 测试 1 通过！\n")
    
    async def test_multi_turn_chat(self):
        """测试 2：多轮对话"""
        log_title("测试 2: 多轮对话")
        
        chat = ChatOpenAI(
            model="gpt-4o-mini",
            system_prompt="你是一个数学助手。",
        )
        
        # 第一轮
        response1 = await chat.chat("3 + 5 等于多少？")
        print(f"\n第一轮响应: {response1['content'][:50]}")
        
        # 第二轮（基于上下文）
        response2 = await chat.chat("再加 10 呢？")
        print(f"\n第二轮响应: {response2['content'][:50]}")
        
        assert response1['content'], "第一轮响应不应为空"
        assert response2['content'], "第二轮响应不应为空"
        print("\n✅ 测试 2 通过！\n")
    
    async def test_tool_calling(self):
        """测试 3：工具调用功能"""
        log_title("测试 3: 工具调用")
        
        # 定义测试工具
        tools: List[Tool] = [
            {
                "name": "search_database",
                "description": "在知识库中搜索相关文档",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询字符串"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量限制",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_current_time",
                "description": "获取当前时间",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "时区，如 'Asia/Shanghai'"
                        }
                    }
                }
            }
        ]
        
        chat = ChatOpenAI(
            model="openai/gpt-4o-mini",
            system_prompt="你是一个助手，可以使用工具来帮助用户。",
            tools=tools
        )
        
        # 发送会触发工具调用的消息
        response = await chat.chat("请帮我搜索关于'向量数据库'的文档，返回 3 条结果")
        
        print(f"\n\n✅ 响应内容: {response['content']}")
        print(f"✅ 工具调用数量: {len(response['toolCalls'])}")
        
        # 处理工具调用
        if response['toolCalls']:
            for tool_call in response['toolCalls']:
                tool_name = tool_call['function']['name']
                tool_args_str = tool_call['function']['arguments']
                
                print(f"\n📞 工具调用:")
                print(f"   - ID: {tool_call['id']}")
                print(f"   - 名称: {tool_name}")
                print(f"   - 参数: {tool_args_str}")
                
                # 解析参数
                tool_args = json.loads(tool_args_str)
                
                # 模拟工具执行
                tool_result = self.mock_tool_execution(tool_name, tool_args)
                print(f"   - 执行结果: {tool_result[:100]}...")
                
                # 将结果返回给 LLM
                chat.append_tool_result(tool_call['id'], tool_result)
            
            # 继续对话，让 LLM 处理工具结果
            log_title("LLM 处理工具结果")
            final_response = await chat.chat()
            print(f"\n\n✅ 最终响应: {final_response['content']}")
            
            assert len(response['toolCalls']) > 0, "应该有工具调用"
            print("\n✅ 测试 3 通过！\n")
        else:
            print("⚠️ 警告：LLM 没有调用工具，可能需要调整提示词")
    
    def mock_tool_execution(self, tool_name: str, args: Dict[str, Any]) -> str:
        """模拟工具执行"""
        if tool_name == "search_database":
            query = args.get("query", "")
            limit = args.get("limit", 5)
            return json.dumps({
                "results": [
                    {"title": f"向量数据库技术综述 {i+1}", "score": 0.95 - i*0.1}
                    for i in range(min(limit, 3))
                ],
                "total": limit
            }, ensure_ascii=False)
        
        elif tool_name == "get_current_time":
            from datetime import datetime
            timezone = args.get("timezone", "UTC")
            return json.dumps({
                "time": datetime.now().isoformat(),
                "timezone": timezone
            })
        
        return json.dumps({"error": "未知工具"})
    
    async def test_system_prompt_and_context(self):
        """测试 4：系统提示词和初始上下文"""
        log_title("测试 4: 系统提示词和上下文")
        
        chat = ChatOpenAI(
            model="gpt-4o-mini",
            system_prompt="你是一个海盗船长，说话要有海盗风格。",
            context="我们正在寻找传说中的宝藏。"
        )
        
        response = await chat.chat("你好！")
        
        print(f"\n\n✅ 响应内容: {response['content']}")
        print("✅ 测试 4 通过！\n")
    
    async def run_all_tests(self):
        """运行所有测试"""
        log_title("开始测试 ChatOpenAI 类")
        
        try:
            await self.test_basic_chat()
            await self.test_multi_turn_chat()
            await self.test_tool_calling()
            await self.test_system_prompt_and_context()
            
            log_title("所有测试通过 ✅")
            
        except Exception as e:
            log_title("测试失败 ❌")
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    tester = TestChatOpenAI()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("=" * 80)
    print("ChatOpenAI 功能测试")
    print("=" * 80)
    print()
    
    asyncio.run(main())
