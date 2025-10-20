import asyncio
from typing import Any, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .operations import get_frame_number,analyze_image_frames
import json

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
                name="get_frame_number",
                description="获取路径下视频帧的数量",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "视频帧文件夹本地路径"
                        }
                    },
                    "required": ["url"]
                },
            ),
            Tool(
                name="analyze_image_frames",
                description="分析视频帧的亮度、对比度、清晰度和噪声水平，为图像增强提供依据",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "frames_folder": {
                            "type": "string", 
                            "description": "视频帧文件夹的本地路径"
                        },
                        "sample_interval": {
                            "type": "number",
                            "description": "采样间隔，每隔多少帧分析一帧，默认30",
                            "default": 30
                        }
                    },
                    "required": ["frames_folder"]
            },
        )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[TextContent]:
        """处理工具调用"""
        if name == "get_frame_number":
            try:
                url = arguments.get("url")
                result = get_frame_number(url)
                
                return [TextContent(
                    type="text",
                    text=f"视频信息: {result}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"错误: {str(e)}"
                )]
        elif name == "analyze_image_frames":
            try:
                frames_folder = arguments.get("frames_folder")
                sample_interval = arguments.get("sample_interval", 30)
                
                result_json = analyze_image_frames(frames_folder, sample_interval)
                analysis_data = json.loads(result_json)
                
                if "error" in analysis_data:
                    return [TextContent(type="text", text=f"错误: {analysis_data['error']}")]
                
                metrics = analysis_data["quality_metrics"]
                
                output_text = f"""视频帧分析完成:   
                        
                📊 基本统计:
                - 总帧数: {analysis_data['frames_info']['total_frames']}
                - 分辨率: {analysis_data['frames_info']['resolution']}

                🎯 质量指标:
                - 亮度: {metrics['brightness']['mean']} ({metrics['brightness']['interpretation']})
                - 对比度: {metrics['contrast']['mean']} ({metrics['contrast']['interpretation']})
                - 清晰度: {metrics['sharpness']['mean']} ({metrics['sharpness']['interpretation']})
                - 噪声: {metrics['noise_level']['mean']} ({metrics['noise_level']['interpretation']})

                💡 建议:
                """
                for rec in analysis_data['enhancement_recommendations']:
                    output_text += f"  • {rec}\n"
                
                return [TextContent(type="text", text=output_text)]
                
            except Exception as e:
                return [TextContent(type="text", text=f"分析失败: {str(e)}")]
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
