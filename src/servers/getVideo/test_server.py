import asyncio
from pathlib import Path
from ...MCPClient import MCPClient
from ...utils import log_title


async def test_get_video_server():
    """测试 GetVideo Server 的功能"""
    
    log_title("测试 Get Video MCP Server")
    
    # 获取正确的文件路径
    # current_dir = Path(__file__).parent.parent.parent.parent  # 项目根目录
    # server_path = current_dir / 'src' / 'servers' / 'getVideo' / 'mcp_server_get_video.py'
    
    # print(f"Server 路径: {server_path}")
    # print(f"文件存在: {server_path.exists()}")
    # breakpoint()
    # 创建 MCP 客户端连接到 Get Video Server
    get_video_client = MCPClient(
        name='get-video-client',
        command='python',
        args=['-m','src.servers.getVideo.server']  # 使用绝对路径
    )

    try:
        # 初始化连接
        await get_video_client.init()
        
        # 获取工具列表
        tools = get_video_client.get_tools()
        print(f"\n📦 可用工具: {[t['name'] for t in tools]}")

        # 打印工具详情
        for tool in tools:
            print(f"\n工具名称: {tool['name']}")
            print(f"描述: {tool['description']}")
        
        # 测试视频获取工具
        log_title("测试 Get Video 运算")
        
        test_cases = [
            {"url": "https://example.com/video1"},
            {"url": "https://example.com/video2"},
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n测试 {i}: url={params['url']}")
            result = await get_video_client.call_tool("get_video", params)
            print(f"结果: {result}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await get_video_client.close()
        print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_get_video_server())
