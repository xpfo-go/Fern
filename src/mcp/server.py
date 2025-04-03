import asyncio
import argparse
import uvicorn
from mcp.server import Server, FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount


def build_sse_server(mcp_server: Server, *, debug: bool = False) -> Starlette:
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


async def run_server(mcp_server: FastMCP, args: argparse.Namespace) -> (asyncio.Task, uvicorn.Server):
    server = build_sse_server(mcp_server._mcp_server, debug=args.debug)
    uvicorn_server = uvicorn.Server(uvicorn.Config(
        server,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info"
    ))

    server_task = asyncio.create_task(uvicorn_server.serve())

    while not uvicorn_server.started:
        await asyncio.sleep(0.1)

    return server_task, uvicorn_server

