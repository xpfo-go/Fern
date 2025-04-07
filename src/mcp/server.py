import asyncio
import uvicorn
from mcp.server import Server, FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from src.call_tools.system import SystemTools
from src.call_tools.weather import WeatherTools


class MCPServer:
    def __init__(self):
        self.app = FastMCP('Fern')
        WeatherTools().register_tools(self.app)
        SystemTools().register_tools(self.app)

        self.sse_server_task = None
        self.sse_uvicorn_server = None

    async def run_with_console(self):
        pass

    async def run_with_sse(self,
                           host: str = 'localhost',
                           port: int = 18080,
                           is_debug: bool = False,
                           log_level: str = "info"
                           ):
        self.sse_server_task, self.sse_uvicorn_server = await self._run_sse_server(host, port, is_debug, log_level)
        await self.sse_server_task

    async def run_with_sync_sse(self,
                                host: str = 'localhost',
                                port: int = 18080,
                                is_debug: bool = False,
                                log_level: str = "info"
                                ):
        self.sse_server_task, self.sse_uvicorn_server = await self._run_sse_server(host, port, is_debug, log_level)

    async def _run_sse_server(self,
                              host: str,
                              port: int,
                              is_debug: bool,
                              log_level: str
                              ) -> (asyncio.Task, uvicorn.Server):
        server = self._build_sse_server(self.app._mcp_server, debug=is_debug)  # noqa: SLF001
        uvicorn_server = uvicorn.Server(uvicorn.Config(
            server,
            host=host,
            port=port,
            log_level=log_level
        ))

        server_task = asyncio.create_task(uvicorn_server.serve())

        while not uvicorn_server.started:
            await asyncio.sleep(0.1)

        return server_task, uvicorn_server

    @staticmethod
    def _build_sse_server(mcp_server: Server, *, debug: bool = False) -> Starlette:
        """Create a Starlette application that can server the provied mcp server with SSE."""
        sse = SseServerTransport("/messages/")

        async def handle_sse(request: Request) -> None:
            async with sse.connect_sse(
                    request.scope,
                    request.receive,
                    request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )

        return Starlette(
            debug=debug,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

    async def clean_up(self):
        if self.sse_server_task:
            try:
                self.sse_server_task.cancel()
                await self.sse_server_task
            except asyncio.CancelledError:
                pass
        if self.sse_uvicorn_server:
            await self.sse_uvicorn_server.shutdown()

    def __del__(self):
        self.clean_up()
