import argparse
import time

from mcp.server import FastMCP

from src.call_tools.system import SystemTools
from src.call_tools.weather import WeatherTools
from src.mcp.client import MCPClient
from src.mcp.server import run_server


async def run():
    parser = argparse.ArgumentParser(description='Run Bonjour Service')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    parser.add_argument('--debug', type=bool, default=False, help='Is debug')
    args = parser.parse_args()

    # 启动sse后台
    app = FastMCP('Bonjour')
    WeatherTools().register_tools(app)
    SystemTools().register_tools(app)

    server_task, uvicorn_server = await run_server(app, args)

    try:
        await server_task
    except KeyboardInterrupt:
        pass
    finally:
        if not uvicorn_server.should_exit:
            uvicorn_server.should_exit = True
            await uvicorn_server.shutdown()

    return

    # 服务启动完成 创建客户端
    # client = MCPClient()
    # try:
    #     await client.connect_to_sse_server(args)
    #     time.sleep(5)
    #     #  这里阻塞
    #     await client.chat_loop()
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     await client.cleanup()
    #     if not uvicorn_server.should_exit:
    #         uvicorn_server.should_exit = True
    #         await uvicorn_server.shutdown()
    #
    # # 阻塞
    # await server_task
