import asyncio
from typing import Any, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .operations import get_video_info


class GetVideoServer:
    """视频获取 Server"""
    
    def __init__(self):
        self.app = Server("getvideo-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置处理器"""
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            return self.get_tools()
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            return await self.handle_tool_call(name, arguments)
    
    def get_tools(self) -> List[Tool]:
        """返回工具列表"""
        return [
            Tool(
                name="get_video",
                description="获取视频信息（占位功能，待实现）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "视频URL"
                        }
                    },
                    "required": ["url"]
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[TextContent]:
        """处理工具调用"""
        if name == "get_video":
            try:
                url = arguments.get("url")
                result = get_video_info(url)
                
                return [TextContent(
                    type="text",
                    text=f"视频信息: {result}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"错误: {str(e)}"
                )]
        
        return [TextContent(
            type="text",
            text=f"未知工具: {name}"
        )]
    
    def run(self):
        """启动 Server"""
        async def main():
            async with stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )
        
        asyncio.run(main())


if __name__ == "__main__":
    server = GetVideoServer()
    server.run()
