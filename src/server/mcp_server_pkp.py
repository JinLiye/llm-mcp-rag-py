"""
自定义 MCP Server - PKP 运算
提供一个 pkp 工具，实现自定义的 PKP 运算
"""

import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 定义 PKP 运算函数
def pkp_operation(a: float, b: float, c: float) -> float:
    """
    PKP 运算：(a + b) * c
    
    Args:
        a: 第一个数字
        b: 第二个数字
        c: 第三个数字
        
    Returns:
        运算结果
    """
    result = (a + b) * c
    return result


# 创建 MCP Server 实例
app = Server("pkp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    列出服务器提供的所有工具
    """
    return [
        Tool(
            name="pkp",
            description="执行 PKP 运算：(a + b) * c，返回计算结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    },
                    "c": {
                        "type": "number",
                        "description": "第三个数字（乘数）"
                    }
                },
                "required": ["a", "b", "c"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    处理工具调用
    
    Args:
        name: 工具名称
        arguments: 工具参数
        
    Returns:
        工具执行结果
    """
    if name == "pkp":
        # 提取参数
        a = arguments.get("a")
        b = arguments.get("b")
        c = arguments.get("c")
        
        # 参数验证
        if a is None or b is None or c is None:
            return [
                TextContent(
                    type="text",
                    text="错误：缺少必需参数 a, b 或 c"
                )
            ]
        
        try:
            # 执行 PKP 运算
            result = pkp_operation(float(a), float(b), float(c))
            
            # 返回结果
            return [
                TextContent(
                    type="text",
                    text=f"PKP 运算结果：({a} + {b}) * {c} = {result}"
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"错误：运算失败 - {str(e)}"
                )
            ]
    
    else:
        return [
            TextContent(
                type="text",
                text=f"错误：未知工具 '{name}'"
            )
        ]


async def main():
    """
    启动 MCP Server
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
